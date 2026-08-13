import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, f1_score, log_loss, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit, train_test_split


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.signals import FEATURE_NAMES, extract_features, prepare_signal


def resolve_column(frame: pd.DataFrame, value):
    if value is None:
        return None
    if isinstance(value, int):
        return frame.columns[value]
    return value


def resolve_path(value: str, base_dir: Path) -> Path:
    path = Path(value).expanduser()
    return (base_dir / path).resolve() if not path.is_absolute() else path.resolve()


def read_frame(config: dict, base_dir: Path) -> tuple[pd.DataFrame, Path]:
    path = resolve_path(config["dataset_path"], base_dir)
    if not path.exists():
        raise FileNotFoundError(f"Base não encontrada: {path}")
    header = config.get("header", "infer")
    return pd.read_csv(path, header=None if header is None else header), path


def load_records(config: dict, base_dir: Path) -> tuple[list[np.ndarray], np.ndarray, np.ndarray | None, Path]:
    frame, path = read_frame(config, base_dir)
    dataset_format = config.get("format", "wide_csv")
    label_column = resolve_column(frame, config["label_column"])
    group_column = resolve_column(frame, config.get("group_column"))
    label_map = {str(key): value for key, value in config.get("label_map", {}).items()}
    signals = []
    labels = []
    groups = []
    if dataset_format == "long_csv":
        record_column = resolve_column(frame, config["record_column"])
        value_column = resolve_column(frame, config["value_column"])
        time_column = resolve_column(frame, config.get("time_column"))
        for _, record in frame.groupby(record_column, sort=False):
            if time_column is not None:
                record = record.sort_values(time_column)
            values = pd.to_numeric(record[value_column], errors="coerce").dropna().to_numpy(dtype=float)
            if values.size < 64:
                continue
            label = record[label_column].iloc[0]
            signals.append(values)
            labels.append(label_map.get(str(label), str(label)))
            if group_column is not None:
                groups.append(str(record[group_column].iloc[0]))
    else:
        excluded = {column for column in [label_column, group_column] if column is not None}
        configured_columns = config.get("signal_columns")
        if configured_columns:
            signal_columns = [resolve_column(frame, column) for column in configured_columns]
        else:
            signal_columns = list(frame.columns[slice(config.get("signal_start", 0), config.get("signal_end"))])
        signal_columns = [column for column in signal_columns if column not in excluded]
        for _, row in frame.iterrows():
            values = pd.to_numeric(row[signal_columns], errors="coerce").dropna().to_numpy(dtype=float)
            if values.size < 64:
                continue
            label = row[label_column]
            signals.append(values)
            labels.append(label_map.get(str(label), str(label)))
            if group_column is not None:
                groups.append(str(row[group_column]))
    if not signals:
        raise ValueError(f"Nenhum registro válido foi extraído de {config.get('dataset_name', path.name)}.")
    return signals, np.asarray(labels), np.asarray(groups) if group_column is not None else None, path


def build_features(signals: list[np.ndarray], modality: str, sample_rate: int) -> tuple[pd.DataFrame, list[int]]:
    rows = []
    valid_indices = []
    for index, values in enumerate(signals):
        try:
            prepared = prepare_signal(values.tolist(), sample_rate, modality)
            rows.append(extract_features(prepared))
            valid_indices.append(index)
        except ValueError:
            continue
    if not rows:
        raise ValueError("Nenhum sinal permaneceu após o pré-processamento.")
    return pd.DataFrame(rows, columns=FEATURE_NAMES), valid_indices


def load_plan(config: dict, config_path: Path) -> tuple[dict, list[dict]]:
    defaults = {key: value for key, value in config.items() if key != "sources"}
    sources = config.get("sources") or [config]
    resolved = []
    for index, source in enumerate(sources):
        if isinstance(source, str):
            source_path = resolve_path(source, config_path.parent)
            source_config = json.loads(source_path.read_text(encoding="utf-8"))
            source_base = source_path.parent
        else:
            source_config = source
            source_base = config_path.parent
        merged = {**defaults, **source_config}
        merged["base_dir"] = source_base
        merged["dataset_id"] = merged.get("dataset_id", merged.get("dataset_handle", f"source-{index + 1}"))
        resolved.append(merged)
    return defaults, resolved


def assemble_dataset(plan: dict, sources: list[dict]) -> tuple[pd.DataFrame, np.ndarray, np.ndarray | None, np.ndarray, list[dict]]:
    modality = plan["modality"]
    frames = []
    labels = []
    groups = []
    roles = []
    metadata = []
    missing_groups = []
    for source in sources:
        if source.get("modality", modality) != modality:
            raise ValueError("Todas as bases do plano precisam pertencer à mesma modalidade.")
        signals, source_labels, source_groups, path = load_records(source, Path(source["base_dir"]))
        feature_frame, valid_indices = build_features(signals, modality, int(source["sample_rate"]))
        source_labels = source_labels[valid_indices]
        source_id = str(source["dataset_id"])
        if source_groups is None:
            missing_groups.append(source_id)
            normalized_groups = np.asarray([f"{source_id}:record:{index}" for index in valid_indices])
        else:
            normalized_groups = np.asarray([f"{source_id}:{value}" for value in source_groups[valid_indices]])
        frames.append(feature_frame)
        labels.append(source_labels)
        groups.append(normalized_groups)
        roles.extend([source.get("role", "development")] * len(valid_indices))
        metadata.append({
            "id": source_id,
            "name": source.get("dataset_name", source_id),
            "role": source.get("role", "development"),
            "records": len(valid_indices),
            "sha256": dataset_digest(path)
        })
    if missing_groups and not plan.get("allow_record_level_split", False):
        joined = ", ".join(missing_groups)
        raise ValueError(f"Identificador de participante ausente em: {joined}. Defina group_column ou autorize explicitamente allow_record_level_split.")
    group_values = np.concatenate(groups) if not missing_groups else None
    return pd.concat(frames, ignore_index=True), np.concatenate(labels), group_values, np.asarray(roles), metadata


def all_classes_present(labels: np.ndarray, partitions: list[np.ndarray]) -> bool:
    expected = set(labels.tolist())
    return all(set(labels[indices].tolist()) == expected for indices in partitions)


def stratified_three_way_split(labels: np.ndarray, test_size: float, calibration_size: float, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    indices = np.arange(len(labels))
    development, test = train_test_split(indices, test_size=test_size, random_state=seed, stratify=labels)
    relative_calibration = calibration_size / (1 - test_size)
    train, calibration = train_test_split(development, test_size=relative_calibration, random_state=seed + 1, stratify=labels[development])
    return train, calibration, test


def grouped_three_way_split(labels: np.ndarray, groups: np.ndarray, test_size: float, calibration_size: float, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    for offset in range(100):
        first = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=seed + offset)
        development, test = next(first.split(np.zeros(len(labels)), labels, groups))
        relative_calibration = calibration_size / (1 - test_size)
        second = GroupShuffleSplit(n_splits=1, test_size=relative_calibration, random_state=seed + 100 + offset)
        local_train, local_calibration = next(second.split(np.zeros(len(development)), labels[development], groups[development]))
        train = development[local_train]
        calibration = development[local_calibration]
        if all_classes_present(labels, [train, calibration, test]):
            return train, calibration, test
    raise ValueError("Não foi possível criar partições por participante contendo todas as classes. Revise a amostra ou o agrupamento.")


def split_dataset(labels: np.ndarray, groups: np.ndarray | None, roles: np.ndarray, test_size: float, calibration_size: float, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, bool]:
    external = np.flatnonzero(roles == "external_validation")
    development = np.flatnonzero(roles != "external_validation")
    if external.size:
        if set(labels[external].tolist()) != set(labels[development].tolist()):
            raise ValueError("Desenvolvimento e validação externa precisam conter o mesmo conjunto de classes harmonizadas.")
        if groups is not None:
            local_train = local_calibration = None
            for offset in range(100):
                splitter = GroupShuffleSplit(n_splits=1, test_size=calibration_size / (1 - test_size), random_state=seed + offset)
                candidate_train, candidate_calibration = next(splitter.split(np.zeros(len(development)), labels[development], groups[development]))
                if all_classes_present(labels[development], [candidate_train, candidate_calibration]):
                    local_train, local_calibration = candidate_train, candidate_calibration
                    break
            if local_train is None or local_calibration is None:
                raise ValueError("Não foi possível separar treino e calibração por participante com todas as classes.")
        else:
            local_train, local_calibration = train_test_split(np.arange(len(development)), test_size=calibration_size / (1 - test_size), random_state=seed, stratify=labels[development])
        train = development[local_train]
        calibration = development[local_calibration]
        if not all_classes_present(labels, [train, calibration]):
            raise ValueError("Treino e calibração precisam conter todas as classes.")
        return train, calibration, external, True
    if groups is not None:
        train, calibration, test = grouped_three_way_split(labels, groups, test_size, calibration_size, seed)
    else:
        train, calibration, test = stratified_three_way_split(labels, test_size, calibration_size, seed)
    return train, calibration, test, False


def temperature_scale(probabilities: np.ndarray, temperature: float) -> np.ndarray:
    logits = np.log(np.clip(probabilities, 1e-12, 1.0)) / max(float(temperature), 0.05)
    logits -= logits.max(axis=1, keepdims=True)
    scaled = np.exp(logits)
    return scaled / scaled.sum(axis=1, keepdims=True)


def fit_temperature(labels: np.ndarray, probabilities: np.ndarray, classes: np.ndarray) -> float:
    def objective(value: float) -> float:
        return float(log_loss(labels, temperature_scale(probabilities, value), labels=classes))
    result = minimize_scalar(objective, bounds=(0.2, 5.0), method="bounded", options={"xatol": 1e-4})
    return float(result.x) if result.success else 1.0


def expected_calibration_error(labels: np.ndarray, probabilities: np.ndarray, classes: np.ndarray, bins: int = 10) -> float:
    predictions = classes[np.argmax(probabilities, axis=1)]
    confidence = np.max(probabilities, axis=1)
    correct = predictions == labels
    edges = np.linspace(0, 1, bins + 1)
    error = 0.0
    for lower, upper in zip(edges[:-1], edges[1:]):
        mask = (confidence > lower) & (confidence <= upper)
        if mask.any():
            error += mask.mean() * abs(float(correct[mask].mean()) - float(confidence[mask].mean()))
    return float(error)


def evaluate(labels: np.ndarray, predictions: np.ndarray, probabilities: np.ndarray, classes: np.ndarray) -> dict:
    matrix = confusion_matrix(labels, predictions, labels=classes)
    per_class = {}
    for index, label in enumerate(classes):
        true_positive = matrix[index, index]
        false_negative = matrix[index, :].sum() - true_positive
        false_positive = matrix[:, index].sum() - true_positive
        true_negative = matrix.sum() - true_positive - false_negative - false_positive
        per_class[str(label)] = {
            "sensitivity": round(float(true_positive / max(true_positive + false_negative, 1)), 6),
            "specificity": round(float(true_negative / max(true_negative + false_positive, 1)), 6),
            "support": int(matrix[index, :].sum())
        }
    class_index = {label: index for index, label in enumerate(classes)}
    one_hot = np.eye(len(classes))[[class_index[label] for label in labels]]
    metrics = {
        "accuracy": round(float(accuracy_score(labels, predictions)), 6),
        "balanced_accuracy": round(float(balanced_accuracy_score(labels, predictions)), 6),
        "f1_macro": round(float(f1_score(labels, predictions, average="macro")), 6),
        "log_loss": round(float(log_loss(labels, probabilities, labels=classes)), 6),
        "brier_multiclass": round(float(np.mean(np.sum(np.square(one_hot - probabilities), axis=1))), 6),
        "expected_calibration_error": round(expected_calibration_error(labels, probabilities, classes), 6),
        "per_class": per_class,
        "confusion_matrix": matrix.tolist()
    }
    try:
        metrics["auroc_macro_ovr"] = round(float(roc_auc_score(labels, probabilities, labels=classes, multi_class="ovr", average="macro")), 6)
    except ValueError:
        metrics["auroc_macro_ovr"] = None
    return metrics


def dataset_digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest()


def train(config: dict, config_path: Path) -> tuple[Path, Path]:
    plan, sources = load_plan(config, config_path)
    features, labels, groups, roles, source_metadata = assemble_dataset(plan, sources)
    counts = pd.Series(labels).value_counts()
    if counts.size < 2 or counts.min() < 15:
        raise ValueError("Cada classe precisa conter pelo menos quinze registros válidos para treino, calibração e teste.")
    test_size = float(plan.get("test_size", 0.2))
    calibration_size = float(plan.get("calibration_size", 0.15))
    if not 0.1 <= test_size <= 0.4 or not 0.1 <= calibration_size <= 0.3 or test_size + calibration_size >= 0.6:
        raise ValueError("As proporções de teste e calibração são inválidas.")
    seed = int(plan.get("random_seed", 42))
    train_indices, calibration_indices, test_indices, external_validation = split_dataset(labels, groups, roles, test_size, calibration_size, seed)
    model = RandomForestClassifier(
        n_estimators=int(plan.get("n_estimators", 600)),
        max_depth=plan.get("max_depth"),
        min_samples_leaf=int(plan.get("min_samples_leaf", 2)),
        class_weight="balanced_subsample",
        random_state=seed,
        n_jobs=-1
    )
    model.fit(features.iloc[train_indices].to_numpy(), labels[train_indices])
    calibration_raw = model.predict_proba(features.iloc[calibration_indices].to_numpy())
    temperature = fit_temperature(labels[calibration_indices], calibration_raw, model.classes_)
    test_probabilities = temperature_scale(model.predict_proba(features.iloc[test_indices].to_numpy()), temperature)
    predictions = model.classes_[np.argmax(test_probabilities, axis=1)]
    metrics = evaluate(labels[test_indices], predictions, test_probabilities, model.classes_)
    version = plan.get("version") or f"{plan['modality']}-3.0-{datetime.now(UTC).strftime('%Y%m%d%H%M')}"
    output_root = resolve_path(str(plan.get("output_dir", BACKEND_ROOT / "models" / plan["modality"])), config_path.parent)
    output_root.mkdir(parents=True, exist_ok=True)
    artifact_path = output_root / f"model-{version}.joblib"
    manifest_path = output_root / "manifest.json"
    training_features = features.iloc[train_indices]
    feature_mean = training_features.mean().to_dict()
    feature_scale = training_features.std().replace(0, 1).to_dict()
    feature_median = training_features.median().to_dict()
    feature_mad = (training_features - training_features.median()).abs().median().replace(0, 1).to_dict()
    joblib.dump({
        "model": model,
        "temperature": temperature,
        "feature_names": FEATURE_NAMES,
        "classes": model.classes_.tolist()
    }, artifact_path, compress=3)
    limitations = list(plan.get("limitations", []))
    if groups is None:
        limitations.insert(0, "Separação em nível de registro autorizada; existe risco de vazamento entre participantes.")
    if not external_validation:
        limitations.append("Validação externa independente não realizada")
    limitations.append("Uso restrito a ensino e pesquisa até validação clínica prospectiva e revisão regulatória")
    manifest = {
        "modality": plan["modality"],
        "version": version,
        "artifact": artifact_path.name,
        "status": "research_only",
        "probability_mode": "calibrated_research",
        "calibration": {
            "status": "fitted",
            "method": "temperature_scaling",
            "temperature": round(temperature, 8),
            "records": int(len(calibration_indices))
        },
        "dataset": "; ".join(source["name"] for source in source_metadata),
        "dataset_ids": [source["id"] for source in source_metadata],
        "sources": source_metadata,
        "intended_use": plan.get("intended_use", "Pesquisa e ensino"),
        "labels": model.classes_.tolist(),
        "sample_rate": int(plan.get("sample_rate", sources[0]["sample_rate"])),
        "metrics": metrics,
        "patient_level_split": groups is not None,
        "external_validation": external_validation,
        "test_records": int(len(test_indices)),
        "calibration_records": int(len(calibration_indices)),
        "training_records": int(len(train_indices)),
        "abstention_threshold": float(plan.get("abstention_threshold", 0.55)),
        "feature_mean": {key: float(value) for key, value in feature_mean.items()},
        "feature_scale": {key: float(value) for key, value in feature_scale.items()},
        "feature_median": {key: float(value) for key, value in feature_median.items()},
        "feature_mad": {key: float(value) for key, value in feature_mad.items()},
        "limitations": list(dict.fromkeys(limitations)),
        "trained_at": datetime.now(UTC).isoformat(),
        "random_seed": seed
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return artifact_path, manifest_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    arguments = parser.parse_args()
    config_path = Path(arguments.config).expanduser().resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    artifact, manifest = train(config, config_path)
    print(json.dumps({"artifact": str(artifact), "manifest": str(manifest)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
