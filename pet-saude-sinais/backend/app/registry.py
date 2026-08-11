import json
import os
from pathlib import Path

import joblib
import numpy as np

from .schemas import ModelCard
from .signals import FEATURE_LABELS, FEATURE_NAMES


LABELS = {
    "ecg": ["Ritmo sinusal", "Extrassístole ventricular", "Irregularidade compatível com FA", "Alteração morfológica inespecífica"],
    "emg": ["Padrão fisiológico", "Padrão neuropático", "Padrão miopático", "Atividade espontânea"],
    "eeg": ["Ritmo de base esperado", "Descarga epileptiforme suspeita", "Lentificação focal", "Predomínio de artefato"],
    "ppg": ["Pulso regular", "Irregularidade de pulso", "Baixa perfusão", "Artefato de movimento"],
    "resp": ["Padrão ventilatório preservado", "Padrão obstrutivo suspeito", "Padrão restritivo suspeito", "Evento respiratório suspeito"],
    "pcg": ["Bulhas sem alteração detectável", "Sopro sistólico suspeito", "Sopro diastólico suspeito", "Ruído de aquisição"]
}


DATASETS = {
    "ecg": "Kaggle ECG Heartbeat Categorization / MIT-BIH derivado",
    "emg": "Kaggle EMAHA-DB1 ou conjunto EMG definido pelo projeto",
    "eeg": "PhysioNet Sleep-EDF Expanded",
    "ppg": "Kaggle WESAD",
    "resp": "PhysioNet Apnea-ECG",
    "pcg": "PhysioNet CirCor DigiScope"
}


class ModelRegistry:
    def __init__(self, root: Path | None = None):
        self.root = root or Path(__file__).resolve().parents[1] / "models"
        self.demo_mode = os.getenv("PET_SAUDE_DEMO_MODE", "true").lower() == "true"
        self.bundles: dict[str, dict] = {}
        self.reload()

    def reload(self) -> None:
        self.bundles = {}
        if not self.root.exists():
            return
        for manifest_path in self.root.glob("*/manifest.json"):
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                artifact = manifest_path.parent / manifest["artifact"]
                bundle = joblib.load(artifact)
                self.bundles[manifest["modality"]] = {"manifest": manifest, "bundle": bundle}
            except (OSError, ValueError, KeyError, json.JSONDecodeError):
                continue

    @property
    def trained_count(self) -> int:
        return len(self.bundles)

    def cards(self) -> list[ModelCard]:
        cards = []
        for modality, labels in LABELS.items():
            registered = self.bundles.get(modality)
            if registered:
                manifest = registered["manifest"]
                cards.append(ModelCard(
                    modality=modality,
                    version=manifest.get("version", "sem versão"),
                    status=manifest.get("status", "research_only"),
                    dataset=manifest.get("dataset", DATASETS[modality]),
                    intended_use=manifest.get("intended_use", "Pesquisa e ensino"),
                    labels=manifest.get("labels", labels),
                    metrics=manifest.get("metrics", {}),
                    limitations=manifest.get("limitations", []),
                    patient_level_split=bool(manifest.get("patient_level_split", False)),
                    external_validation=bool(manifest.get("external_validation", False))
                ))
            else:
                cards.append(ModelCard(
                    modality=modality,
                    version="não treinado",
                    status="configuration_only",
                    dataset=DATASETS[modality],
                    intended_use="Ensino e desenvolvimento metodológico",
                    labels=labels,
                    metrics={},
                    limitations=["Modelo não treinado", "Sem validação externa", "Não apropriado para uso assistencial"],
                    patient_level_split=False,
                    external_validation=False
                ))
        return cards

    def predict(self, modality: str, features: dict[str, float], quality: int) -> dict:
        registered = self.bundles.get(modality)
        if registered:
            return self._predict_registered(registered, features)
        if not self.demo_mode:
            raise LookupError(f"Não há modelo treinado e registrado para {modality.upper()}.")
        return self._predict_demo(modality, features, quality)

    def _predict_registered(self, registered: dict, features: dict[str, float]) -> dict:
        manifest = registered["manifest"]
        bundle = registered["bundle"]
        feature_names = bundle.get("feature_names", FEATURE_NAMES)
        vector = np.asarray([[features[name] for name in feature_names]], dtype=np.float64)
        pipeline = bundle["pipeline"]
        probabilities = pipeline.predict_proba(vector)[0]
        classes = [str(value) for value in bundle.get("classes", pipeline.classes_)]
        order = np.argsort(probabilities)[::-1]
        output = [{"label": classes[index], "value": float(probabilities[index])} for index in order]
        entropy = float(-np.sum(probabilities * np.log(np.maximum(probabilities, 1e-12))) / np.log(max(len(probabilities), 2)))
        uncertainty = "Baixa" if entropy < 0.38 else "Moderada" if entropy < 0.68 else "Elevada"
        contributions = self._contributions(pipeline, vector, int(order[0]), feature_names, manifest)
        out_of_distribution = self._out_of_distribution(vector[0], feature_names, manifest)
        return {
            "model": manifest.get("version", "modelo registrado"),
            "status": "Modelo de pesquisa",
            "probabilities": output,
            "uncertainty": uncertainty,
            "features": contributions,
            "out_of_distribution": out_of_distribution
        }

    def _predict_demo(self, modality: str, features: dict[str, float], quality: int) -> dict:
        focus = 0
        if quality < 55:
            focus = len(LABELS[modality]) - 1
        primary = 0.55 + min(quality, 95) / 500
        remaining = (1 - primary) / (len(LABELS[modality]) - 1)
        probabilities = [primary if index == focus else remaining for index in range(len(LABELS[modality]))]
        output = sorted(
            [{"label": label, "value": float(probabilities[index])} for index, label in enumerate(LABELS[modality])],
            key=lambda item: item["value"],
            reverse=True
        )
        ranked = sorted(features.items(), key=lambda item: abs(item[1]), reverse=True)[:4]
        maximum = max((abs(value) for _, value in ranked), default=1.0)
        contributions = [{
            "name": FEATURE_LABELS[name],
            "value": int(np.clip(round(abs(value) / maximum * 88), 12, 88)),
            "direction": "Maior desvio no sinal" if value >= 0 else "Menor desvio no sinal"
        } for name, value in ranked]
        return {
            "model": f"{modality.upper()}-demo 0.4",
            "status": "Simulação acadêmica",
            "probabilities": output,
            "uncertainty": "Elevada",
            "features": contributions,
            "out_of_distribution": True
        }

    def _contributions(self, pipeline, vector: np.ndarray, class_index: int, feature_names: list[str], manifest: dict) -> list[dict]:
        means = manifest.get("feature_mean", {})
        baseline = float(pipeline.predict_proba(vector)[0][class_index])
        contributions = []
        for index, name in enumerate(feature_names):
            perturbed = vector.copy()
            perturbed[0, index] = float(means.get(name, 0.0))
            changed = float(pipeline.predict_proba(perturbed)[0][class_index])
            contributions.append((name, baseline - changed))
        selected = sorted(contributions, key=lambda item: abs(item[1]), reverse=True)[:4]
        maximum = max((abs(value) for _, value in selected), default=1.0) or 1.0
        return [{
            "name": FEATURE_LABELS.get(name, name),
            "value": int(np.clip(round(abs(value) / maximum * 92), 5, 92)),
            "direction": "Aumenta a prioridade" if value >= 0 else "Reduz a prioridade"
        } for name, value in selected]

    def _out_of_distribution(self, vector: np.ndarray, feature_names: list[str], manifest: dict) -> bool:
        means = manifest.get("feature_mean", {})
        scales = manifest.get("feature_scale", {})
        if not means or not scales:
            return True
        z_scores = [abs(vector[index] - float(means.get(name, 0))) / max(float(scales.get(name, 1)), 1e-9) for index, name in enumerate(feature_names)]
        return bool(np.mean(np.asarray(z_scores) > 4.0) > 0.15)
