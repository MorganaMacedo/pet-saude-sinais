import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
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


def read_frame(config: dict) -> pd.DataFrame:
    path = Path(config["dataset_path"]).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Base não encontrada: {path}")
    header = config.get("header", "infer")
    return pd.read_csv(path, header=None if header is None else header)


def load_records(config: dict) -> tuple[list[np.ndarray], np.ndarray, np.ndarray | None]:
    frame = read_frame(config)
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
            start = config.get("signal_start", 0)
            end = config.get("signal_end")
            signal_columns = list(frame.columns[slice(start, end)])
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
        raise ValueError("Nenhum registro válido foi extraído da base.")
    group_values = np.asarray(groups) if group_column is not None else None
    return signals, np.asarray(labels), group_values


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


def split_data(features: pd.DataFrame, labels: np.ndarray, groups: np.ndarray | None, test_size: float, seed: int):
    indices = np.arange(len(labels))
    patient_level = groups is not None and np.unique(groups).size >= 4
    if patient_level:
        splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
        train_indices, test_indices = next(splitter.split(features, labels, groups))
    else:
        train_indices, test_indices = train_test_split(indices, test_size=test_size, random_state=seed, stratify=labels)
    return train_indices, test_indices, patient_level


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
        sensitivity = true_positive / max(true_positive + false_negative, 1)
        specificity = true_negative / max(true_negative + false_positive, 1)
        per_class[str(label)] = {
            "sensitivity": round(float(sensitivity), 6),
            "specificity": round(float(specificity), 6),
            "support": int(matrix[index, :].sum())
        }
    one_hot = np.eye(len(classes))[np.searchsorted(classes, labels)]
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


def dataset_digest(path: str) -> str:
    hasher = hashlib.sha256()
    with Path(path).expanduser().resolve().open("rb") as source:
        while chunk := source.read(1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest()


def train(config: dict) -> tuple[Path, Path]:
    signals, labels, groups = load_records(config)
    feature_frame, valid_indices = build_features(signals, config["modality"], int(config["sample_rate"]))
    labels = labels[valid_indices]
    groups = groups[valid_indices] if groups is not None else None
    counts = pd.Series(labels).value_counts()
    if counts.size < 2 or counts.min() < 5:
        raise ValueError("Cada classe precisa conter pelo menos cinco registros válidos.")
    seed = int(config.get("random_seed", 42))
    train_indices, test_indices, patient_level = split_data(feature_frame, labels, groups, float(config.get("test_size", 0.2)), seed)
    base = RandomForestClassifier(
        n_estimators=int(config.get("n_estimators", 400)),
        max_depth=config.get("max_depth"),
        min_samples_leaf=int(config.get("min_samples_leaf", 2)),
        class_weight="balanced_subsample",
        random_state=seed,
        n_jobs=-1
    )
    minimum_train_class = int(pd.Series(labels[train_indices]).value_counts().min())
    folds = max(2, min(5, minimum_train_class))
    pipeline = CalibratedClassifierCV(base, method="sigmoid", cv=folds, n_jobs=-1)
    pipeline.fit(feature_frame.iloc[train_indices].to_numpy(), labels[train_indices])
    probabilities = pipeline.predict_proba(feature_frame.iloc[test_indices].to_numpy())
    predictions = pipeline.classes_[np.argmax(probabilities, axis=1)]
    metrics = evaluate(labels[test_indices], predictions, probabilities, pipeline.classes_)
    version = config.get("version") or datetime.now(UTC).strftime("%Y.%m.%d.%H%M")
    output_root = Path(config.get("output_dir", BACKEND_ROOT / "models" / config["modality"])).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    artifact_path = output_root / f"model-{version}.joblib"
    manifest_path = output_root / "manifest.json"
    feature_mean = feature_frame.iloc[train_indices].mean().to_dict()
    feature_scale = feature_frame.iloc[train_indices].std().replace(0, 1).to_dict()
    joblib.dump({
        "pipeline": pipeline,
        "feature_names": FEATURE_NAMES,
        "classes": pipeline.classes_.tolist()
    }, artifact_path, compress=3)
    limitations = list(config.get("limitations", []))
    if not patient_level:
        limitations.insert(0, "A base não forneceu identificador de participante; a separação não elimina possível vazamento entre pacientes.")
    limitations.extend(["Validação externa não realizada", "Uso restrito a ensino e pesquisa até validação clínica formal"])
    manifest = {
        "modality": config["modality"],
        "version": version,
        "artifact": artifact_path.name,
        "status": "research_only",
        "dataset": config["dataset_name"],
        "dataset_handle": config.get("dataset_handle"),
        "dataset_sha256": dataset_digest(config["dataset_path"]),
        "intended_use": config.get("intended_use", "Pesquisa e ensino"),
        "labels": pipeline.classes_.tolist(),
        "sample_rate": int(config["sample_rate"]),
        "metrics": metrics,
        "patient_level_split": patient_level,
        "external_validation": False,
        "test_records": int(len(test_indices)),
        "training_records": int(len(train_indices)),
        "feature_mean": {key: float(value) for key, value in feature_mean.items()},
        "feature_scale": {key: float(value) for key, value in feature_scale.items()},
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
    config = json.loads(Path(arguments.config).read_text(encoding="utf-8"))
    artifact, manifest = train(config)
    print(json.dumps({"artifact": str(artifact), "manifest": str(manifest)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
