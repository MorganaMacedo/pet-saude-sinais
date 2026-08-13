import io
import wave

import numpy as np
from fastapi.testclient import TestClient

from app.main import _read_uploaded_signal, app


client = TestClient(app)


def test_health_has_no_persistence():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["persistence"] == "disabled"
    assert response.json()["datasetCatalog"] == 16


def test_dataset_catalog_is_exposed():
    response = client.get("/v1/datasets")
    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["datasets"] == 16
    assert body["summary"]["modalities"] == 7


def test_demo_analysis_is_explicit():
    time = np.arange(2000) / 250
    samples = (np.sin(2 * np.pi * 1.2 * time) + 0.1 * np.sin(2 * np.pi * 8 * time)).tolist()
    response = client.post("/v1/analyze", json={
        "modality": "ppg",
        "samples": samples,
        "sampleRate": 250,
        "recordCode": "TEST-001",
        "symptoms": [],
        "notes": ""
    })
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "Protótipo acadêmico 3.0"
    assert body["probabilityMode"] == "score_only"
    assert body["calibrationStatus"] == "not_available"
    assert body["outOfDistribution"] is True
    assert len(body["probabilities"]) == 6
    assert len(body["evidenceSources"]) == 2


def test_lung_sound_modality_is_available():
    time = np.arange(24000) / 4000
    envelope = np.maximum(np.sin(2 * np.pi * 0.3 * time), 0)
    samples = (0.25 * np.sin(2 * np.pi * 520 * time) * envelope + 0.04 * np.sin(2 * np.pi * 120 * time)).tolist()
    response = client.post("/v1/analyze", json={
        "modality": "lung",
        "samples": samples,
        "sampleRate": 4000,
        "recordCode": "LUNG-001",
        "symptoms": ["Sibilância relatada"],
        "notes": ""
    })
    assert response.status_code == 200
    body = response.json()
    assert body["modality"] == "lung"
    assert len(body["probabilities"]) == 8
    assert {item["id"] for item in body["evidenceSources"]} == {"icbhi-2017", "kauh-lung"}


def test_wav_reader_uses_embedded_sample_rate():
    sample_rate = 4000
    time = np.arange(sample_rate) / sample_rate
    values = np.asarray(np.sin(2 * np.pi * 240 * time) * 16000, dtype="<i2")
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as destination:
        destination.setnchannels(1)
        destination.setsampwidth(2)
        destination.setframerate(sample_rate)
        destination.writeframes(values.tobytes())
    samples, detected_rate = _read_uploaded_signal(buffer.getvalue(), "ausculta.wav")
    assert detected_rate == sample_rate
    assert len(samples) == sample_rate
