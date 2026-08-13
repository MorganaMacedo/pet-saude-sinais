import json
import os
from pathlib import Path

import joblib
import numpy as np

from .datasets import sources_for
from .schemas import ModelCard
from .signals import FEATURE_LABELS, FEATURE_NAMES


LABELS = {
    "ecg": ["Ritmo sinusal", "Padrão compatível com fibrilação atrial", "Extrassístoles ventriculares suspeitas", "Taquicardia suspeita", "Bradicardia suspeita", "Alteração de ST-T inespecífica", "ECG não classificável por artefato"],
    "emg": ["Padrão eletromiográfico fisiológico", "Padrão neuropático suspeito", "Padrão miopático suspeito", "Atividade espontânea suspeita", "Padrão de fadiga neuromuscular", "EMG não classificável por artefato"],
    "eeg": ["Ritmo de base preservado", "Atividade epileptiforme suspeita", "Predomínio de atividade lenta", "Atividade rápida predominante", "EEG não classificável por artefato"],
    "ppg": ["Pulso periférico regular", "Pulso irregular compatível com arritmia", "Baixa perfusão periférica suspeita", "Taquicardia periférica suspeita", "Bradicardia periférica suspeita", "PPG não classificável por movimento"],
    "resp": ["Padrão ventilatório preservado", "Evento de apneia ou hipopneia suspeito", "Taquipneia suspeita", "Bradipneia suspeita", "Respiração periódica suspeita", "Padrão obstrutivo suspeito", "Sinal respiratório não classificável"],
    "lung": ["Som respiratório sem alteração predominante", "Sibilância compatível com obstrução brônquica", "Padrão acústico associado a doença obstrutiva crônica", "Estertores focais compatíveis com acometimento pulmonar", "Roncos compatíveis com secreção em vias aéreas", "Estertores finos persistentes", "Sibilos e estertores combinados", "Ausculta pulmonar não classificável"],
    "pcg": ["Bulhas sem alteração predominante", "Sopro sistólico suspeito", "Sopro diastólico suspeito", "Sopro contínuo suspeito", "Bulha adicional suspeita", "PCG não classificável por ruído"]
}


DATASETS = {modality: ", ".join(item["title"] for item in sources_for(modality)) for modality in LABELS}


def evidence_sources(modality: str, selected: list[str] | None = None) -> list[dict]:
    available = sources_for(modality)
    if selected:
        available = [item for item in available if item["id"] in selected]
    return [{"id": item["id"], "title": item["title"], "role": item["role"], "readiness": item["readiness"]} for item in available]


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
                probability_mode = manifest.get("probability_mode", "score_only")
                calibration = manifest.get("calibration", {})
                cards.append(ModelCard(
                    modality=modality,
                    version=manifest.get("version", "sem versão"),
                    status=manifest.get("status", "research_only"),
                    probability_mode=probability_mode,
                    calibration_status=calibration.get("status", "not_documented"),
                    dataset=manifest.get("dataset", DATASETS[modality]),
                    intended_use=manifest.get("intended_use", "Pesquisa e ensino"),
                    labels=manifest.get("labels", labels),
                    metrics=manifest.get("metrics", {}),
                    limitations=manifest.get("limitations", []),
                    patient_level_split=bool(manifest.get("patient_level_split", False)),
                    external_validation=bool(manifest.get("external_validation", False)),
                    evidence_sources=evidence_sources(modality, manifest.get("dataset_ids"))
                ))
            else:
                cards.append(ModelCard(
                    modality=modality,
                    version="não treinado",
                    status="configuration_only",
                    probability_mode="score_only",
                    calibration_status="not_available",
                    dataset=DATASETS[modality],
                    intended_use="Ensino e desenvolvimento metodológico",
                    labels=labels,
                    metrics={},
                    limitations=["Modelo não treinado", "Sem validação externa", "Não apropriado para uso assistencial"],
                    patient_level_split=False,
                    external_validation=False,
                    evidence_sources=evidence_sources(modality)
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
        model = bundle.get("model", bundle.get("pipeline"))
        if model is None:
            raise LookupError("O artefato registrado não contém um classificador compatível.")
        raw_probabilities = np.asarray(model.predict_proba(vector)[0], dtype=np.float64)
        temperature = max(float(bundle.get("temperature", 1.0)), 0.05)
        logits = np.log(np.clip(raw_probabilities, 1e-12, 1.0)) / temperature
        probabilities = np.exp(logits - np.max(logits))
        probabilities = probabilities / probabilities.sum()
        classes = [str(value) for value in bundle.get("classes", model.classes_)]
        order = np.argsort(probabilities)[::-1]
        output = [{"label": classes[index], "value": float(probabilities[index])} for index in order]
        entropy = float(-np.sum(probabilities * np.log(np.maximum(probabilities, 1e-12))) / np.log(max(len(probabilities), 2)))
        contributions = self._contributions(model, vector, int(order[0]), feature_names, manifest, temperature)
        out_of_distribution = self._out_of_distribution(vector[0], feature_names, manifest)
        threshold = float(manifest.get("abstention_threshold", 0.55))
        abstained = out_of_distribution or float(probabilities[order[0]]) < threshold
        uncertainty = "Elevada" if abstained or entropy >= 0.68 else "Baixa" if entropy < 0.38 else "Moderada"
        probability_mode = manifest.get("probability_mode", "score_only")
        calibration = manifest.get("calibration", {})
        return {
            "model": manifest.get("version", "modelo registrado"),
            "status": "Abstenção por baixa confiança" if abstained else "Modelo de pesquisa calibrado" if probability_mode == "calibrated_research" else "Modelo de pesquisa",
            "probability_mode": probability_mode,
            "calibration_status": calibration.get("status", "not_documented"),
            "evidence_sources": evidence_sources(manifest["modality"], manifest.get("dataset_ids")),
            "probabilities": output,
            "uncertainty": uncertainty,
            "features": contributions,
            "out_of_distribution": out_of_distribution,
            "abstained": abstained
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
            "name": FEATURE_LABELS.get(name, name),
            "value": int(np.clip(round(abs(value) / maximum * 88), 12, 88)),
            "direction": "Maior desvio no sinal" if value >= 0 else "Menor desvio no sinal"
        } for name, value in ranked]
        return {
            "model": f"{modality.upper()}-PathClass 3.0",
            "status": "Protótipo acadêmico 3.0",
            "probability_mode": "score_only",
            "calibration_status": "not_available",
            "evidence_sources": evidence_sources(modality),
            "probabilities": output,
            "uncertainty": "Elevada",
            "features": contributions,
            "out_of_distribution": True,
            "abstained": True
        }

    def _contributions(self, model, vector: np.ndarray, class_index: int, feature_names: list[str], manifest: dict, temperature: float) -> list[dict]:
        means = manifest.get("feature_mean", {})
        baseline = float(self._temperature_scale(model.predict_proba(vector)[0], temperature)[class_index])
        contributions = []
        for index, name in enumerate(feature_names):
            perturbed = vector.copy()
            perturbed[0, index] = float(means.get(name, 0.0))
            changed = float(self._temperature_scale(model.predict_proba(perturbed)[0], temperature)[class_index])
            contributions.append((name, baseline - changed))
        selected = sorted(contributions, key=lambda item: abs(item[1]), reverse=True)[:4]
        maximum = max((abs(value) for _, value in selected), default=1.0) or 1.0
        return [{
            "name": FEATURE_LABELS.get(name, name),
            "value": int(np.clip(round(abs(value) / maximum * 92), 5, 92)),
            "direction": "Aumenta a prioridade" if value >= 0 else "Reduz a prioridade"
        } for name, value in selected]

    @staticmethod
    def _temperature_scale(probabilities: np.ndarray, temperature: float) -> np.ndarray:
        logits = np.log(np.clip(np.asarray(probabilities, dtype=np.float64), 1e-12, 1.0)) / max(temperature, 0.05)
        scaled = np.exp(logits - np.max(logits))
        return scaled / scaled.sum()

    def _out_of_distribution(self, vector: np.ndarray, feature_names: list[str], manifest: dict) -> bool:
        medians = manifest.get("feature_median", {})
        deviations = manifest.get("feature_mad", {})
        if medians and deviations:
            robust_scores = [abs(vector[index] - float(medians.get(name, 0))) / max(float(deviations.get(name, 1)) * 1.4826, 1e-9) for index, name in enumerate(feature_names)]
            return bool(np.mean(np.asarray(robust_scores) > 5.0) > 0.15)
        means = manifest.get("feature_mean", {})
        scales = manifest.get("feature_scale", {})
        if not means or not scales:
            return True
        z_scores = [abs(vector[index] - float(means.get(name, 0))) / max(float(scales.get(name, 1)), 1e-9) for index, name in enumerate(feature_names)]
        return bool(np.mean(np.asarray(z_scores) > 4.0) > 0.15)
