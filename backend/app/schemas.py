from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


def to_camel(value: str) -> str:
    parts = value.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


class Schema(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class AnalyzeRequest(Schema):
    modality: Literal["ecg", "emg", "eeg", "ppg", "resp", "pcg"]
    samples: list[float | None] = Field(min_length=64, max_length=1_000_000)
    sample_rate: int = Field(ge=20, le=20_000)
    record_code: str = Field(default="Sem identificação", max_length=64)
    symptoms: list[str] = Field(default_factory=list, max_length=24)
    notes: str = Field(default="", max_length=4_000)
    model_version: str | None = Field(default=None, max_length=80)


class QualityReport(Schema):
    quality: int
    duration: float
    samples: int
    valid_samples: int
    missing_ratio: float
    noise_ratio: float
    clipping: float
    flatline_ratio: float
    dynamic_range: float
    status: str
    message: str


class Probability(Schema):
    label: str
    value: float


class FeatureContribution(Schema):
    name: str
    value: int
    direction: str


class AnalysisResponse(Schema):
    id: str
    created_at: datetime
    modality: str
    modality_name: str
    record_code: str
    model: str
    status: str
    primary_finding: str
    confidence: int
    uncertainty: str
    inspection: QualityReport
    probabilities: list[Probability]
    features: list[FeatureContribution]
    symptoms: list[str]
    notes: str
    urgent_context: bool
    recommendations: list[str]
    decision_support_notice: str
    out_of_distribution: bool


class ModelCard(Schema):
    modality: str
    version: str
    status: str
    dataset: str
    intended_use: str
    labels: list[str]
    metrics: dict[str, float | int | str | bool | None]
    limitations: list[str]
    patient_level_split: bool
    external_validation: bool


class HealthResponse(Schema):
    status: str
    mode: str
    trained_models: int
    persistence: str
