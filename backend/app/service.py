from datetime import UTC, datetime
from uuid import uuid4

from .registry import ModelRegistry
from .schemas import AnalysisResponse, AnalyzeRequest, EvidenceSource, FeatureContribution, Probability, QualityReport
from .signals import assess_quality, extract_features, prepare_signal


class Analyzer:
    def __init__(self, registry: ModelRegistry):
        self.registry = registry

    def analyze(self, request: AnalyzeRequest) -> AnalysisResponse:
        prepared = prepare_signal(request.samples, request.sample_rate, request.modality)
        quality_data = assess_quality(prepared)
        if quality_data["quality"] < 35:
            raise ValueError("A qualidade do sinal é insuficiente para gerar uma pré-análise responsável.")
        extracted = extract_features(prepared)
        inference = self.registry.predict(request.modality, extracted, quality_data["quality"])
        probabilities = [Probability(**item) for item in inference["probabilities"]]
        primary = probabilities[0]
        warning_symptoms = {"Dor torácica", "Síncope ou pré-síncope", "Dispneia importante", "Convulsão", "Cianose"}
        urgent_context = bool(warning_symptoms.intersection(request.symptoms))
        recommendations = [
            "Correlacionar o resultado com história clínica, exame físico e traçado completo.",
            "Confirmar posicionamento dos sensores, parâmetros e qualidade da aquisição.",
            "Submeter o traçado e as hipóteses à revisão de profissional habilitado."
        ]
        if inference.get("abstained"):
            recommendations.insert(0, "O sistema se absteve de classificar por baixa confiança ou por sinal fora da distribuição de referência.")
        elif inference["out_of_distribution"]:
            recommendations.insert(0, "O sinal difere da distribuição de referência ou o modelo não possui referência treinada; não utilizar a classificação para decisão clínica.")
        return AnalysisResponse(
            id=f"PET-{datetime.now(UTC).year}-{uuid4().hex[:6].upper()}",
            created_at=datetime.now(UTC),
            modality=request.modality,
            modality_name=request.modality.upper(),
            record_code=request.record_code,
            model=inference["model"],
            status=inference["status"],
            probability_mode=inference["probability_mode"],
            calibration_status=inference["calibration_status"],
            primary_finding=primary.label,
            confidence=round(primary.value * 100),
            uncertainty=inference["uncertainty"],
            inspection=QualityReport(**quality_data),
            probabilities=probabilities,
            features=[FeatureContribution(**item) for item in inference["features"]],
            symptoms=request.symptoms,
            notes=request.notes,
            urgent_context=urgent_context,
            recommendations=recommendations,
            evidence_sources=[EvidenceSource(**item) for item in inference["evidence_sources"]],
            decision_support_notice="Esta saída organiza evidências para revisão profissional e não constitui diagnóstico, prognóstico ou indicação terapêutica.",
            out_of_distribution=inference["out_of_distribution"]
        )
