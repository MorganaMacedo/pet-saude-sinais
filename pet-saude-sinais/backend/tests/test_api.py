import numpy as np
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_has_no_persistence():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["persistence"] == "disabled"


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
    assert body["status"] == "Simulação acadêmica"
    assert body["outOfDistribution"] is True
    assert len(body["probabilities"]) == 4
