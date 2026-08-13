import io
import json
import os
import wave

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from .datasets import catalog_summary, load_catalog
from .registry import LABELS, ModelRegistry
from .schemas import AnalysisResponse, AnalyzeRequest, HealthResponse, ModelCard
from .service import Analyzer


registry = ModelRegistry()
analyzer = Analyzer(registry)
origins = [item.strip() for item in os.getenv("PET_SAUDE_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:4173").split(",") if item.strip()]

app = FastAPI(
    title="PET-Saúde Sinais Clínicos API",
    version="3.0.0",
    description="API de pesquisa para controle de qualidade e classificação de sinais fisiológicos."
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"]
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        mode="research" if registry.trained_count else "educational_demo",
        trained_models=registry.trained_count,
        dataset_catalog=len(load_catalog()),
        persistence="disabled"
    )


@app.get("/v1/modalities")
def list_modalities() -> list[dict]:
    return [{"id": modality, "name": modality.upper(), "labels": labels} for modality, labels in LABELS.items()]


@app.get("/v1/models", response_model=list[ModelCard])
def list_models() -> list[ModelCard]:
    return registry.cards()


@app.get("/v1/datasets")
def list_datasets() -> dict:
    return {"summary": catalog_summary(), "items": load_catalog()}


@app.post("/v1/models/reload", response_model=list[ModelCard])
def reload_models() -> list[ModelCard]:
    registry.reload()
    return registry.cards()


@app.post("/v1/analyze", response_model=AnalysisResponse)
def analyze_signal(request: AnalyzeRequest) -> AnalysisResponse:
    try:
        return analyzer.analyze(request)
    except LookupError as exception:
        raise HTTPException(status_code=409, detail=str(exception)) from exception
    except ValueError as exception:
        raise HTTPException(status_code=422, detail=str(exception)) from exception


@app.post("/v1/analyze/file", response_model=AnalysisResponse)
async def analyze_file(
    file: UploadFile = File(...),
    modality: str = Form(...),
    sample_rate: int = Form(...),
    record_code: str = Form("Sem identificação"),
    symptoms: str = Form("[]"),
    notes: str = Form("")
) -> AnalysisResponse:
    if modality not in LABELS:
        raise HTTPException(status_code=422, detail="Modalidade inválida.")
    data = await file.read()
    if len(data) > 25_000_000:
        raise HTTPException(status_code=413, detail="O arquivo excede 25 MB.")
    try:
        samples, detected_rate = _read_uploaded_signal(data, file.filename or "signal.csv")
        parsed_symptoms = json.loads(symptoms)
        request = AnalyzeRequest(
            modality=modality,
            samples=samples,
            sample_rate=detected_rate or sample_rate,
            record_code=record_code,
            symptoms=parsed_symptoms if isinstance(parsed_symptoms, list) else [],
            notes=notes
        )
        return analyzer.analyze(request)
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exception:
        raise HTTPException(status_code=422, detail=str(exception)) from exception


def _read_uploaded_signal(data: bytes, filename: str) -> tuple[list[float], int | None]:
    lowered = filename.lower()
    detected_rate = None
    if lowered.endswith(".wav"):
        values, detected_rate = _read_wav(data)
    elif lowered.endswith(".json"):
        parsed = json.loads(data.decode("utf-8"))
        source = parsed if isinstance(parsed, list) else parsed.get("signal", parsed.get("samples", []))
        values = pd.to_numeric(pd.Series(source), errors="coerce").dropna().to_numpy(dtype=float)
    else:
        frame = pd.read_csv(io.BytesIO(data), sep=None, engine="python", header=None)
        numeric = frame.apply(pd.to_numeric, errors="coerce")
        if numeric.shape[1] > 8 and numeric.shape[0] < 10:
            values = numeric.iloc[0].dropna().to_numpy(dtype=float)
        else:
            valid_columns = [column for column in numeric.columns if numeric[column].notna().sum() >= 32]
            if not valid_columns:
                raise ValueError("Não foi encontrada uma coluna com ao menos 32 amostras.")
            values = numeric[valid_columns[-1]].dropna().to_numpy(dtype=float)
    values = values[np.isfinite(values)]
    if values.size < 64:
        raise ValueError("O arquivo precisa conter ao menos 64 amostras numéricas válidas.")
    return values[:1_000_000].tolist(), detected_rate


def _read_wav(data: bytes) -> tuple[np.ndarray, int]:
    with wave.open(io.BytesIO(data), "rb") as source:
        channels = source.getnchannels()
        sample_width = source.getsampwidth()
        sample_rate = source.getframerate()
        frames = source.readframes(source.getnframes())
    dtypes = {1: np.uint8, 2: "<i2", 4: "<i4"}
    if sample_width not in dtypes:
        raise ValueError("O WAV precisa usar amostras PCM de 8, 16 ou 32 bits.")
    values = np.frombuffer(frames, dtype=dtypes[sample_width]).astype(np.float64)
    if channels > 1:
        values = values.reshape(-1, channels)[:, 0]
    if sample_width == 1:
        values = (values - 128.0) / 128.0
    else:
        values /= float(2 ** (sample_width * 8 - 1))
    return values, sample_rate
