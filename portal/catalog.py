import numpy as np


MODALITIES = {
    "ecg": {
        "name": "ECG",
        "full_name": "Eletrocardiografia",
        "target": "Ritmo e morfologia cardíaca",
        "sample_rate": 360,
        "channel": "DII",
        "unit": "mV",
        "color": "#0f766e"
    },
    "emg": {
        "name": "EMG",
        "full_name": "Eletromiografia",
        "target": "Atividade neuromuscular",
        "sample_rate": 1000,
        "channel": "Canal 1",
        "unit": "mV",
        "color": "#7c3aed"
    },
    "eeg": {
        "name": "EEG",
        "full_name": "Eletroencefalografia",
        "target": "Atividade elétrica cerebral",
        "sample_rate": 256,
        "channel": "C3-A2",
        "unit": "µV",
        "color": "#2563eb"
    },
    "ppg": {
        "name": "PPG",
        "full_name": "Fotopletismografia",
        "target": "Pulso e perfusão periférica",
        "sample_rate": 125,
        "channel": "Infravermelho",
        "unit": "u.a.",
        "color": "#c2410c"
    },
    "resp": {
        "name": "RESP",
        "full_name": "Sinal respiratório",
        "target": "Padrão ventilatório",
        "sample_rate": 100,
        "channel": "Fluxo",
        "unit": "L/s",
        "color": "#047857"
    },
    "pcg": {
        "name": "PCG",
        "full_name": "Fonocardiografia",
        "target": "Bulhas e sopros cardíacos",
        "sample_rate": 2000,
        "channel": "Foco mitral",
        "unit": "u.a.",
        "color": "#be123c"
    }
}


SYMPTOMS = [
    "Assintomático",
    "Palpitações",
    "Dor torácica",
    "Síncope ou pré-síncope",
    "Dispneia importante",
    "Fraqueza muscular",
    "Tremor",
    "Alteração do sono"
]


SEEDS = {"ecg": 101, "emg": 211, "eeg": 307, "ppg": 401, "resp": 503, "pcg": 601}


def generate_signal(modality: str, length: int = 2400) -> np.ndarray:
    rng = np.random.default_rng(SEEDS[modality])
    index = np.arange(length)
    time = index / max(length, 1)
    noise = (rng.random(length) - 0.5) * 0.08
    if modality == "ecg":
        phase = np.mod(time * 12, 1)
        values = (
            0.12 * np.exp(-np.square((phase - 0.18) / 0.055))
            - 0.18 * np.exp(-np.square((phase - 0.37) / 0.018))
            + 1.15 * np.exp(-np.square((phase - 0.4) / 0.013))
            - 0.28 * np.exp(-np.square((phase - 0.43) / 0.022))
            + 0.27 * np.exp(-np.square((phase - 0.68) / 0.1))
        )
        return values + noise * 0.45
    if modality == "emg":
        burst = np.power(np.maximum(0, np.sin(time * np.pi * 7)), 3)
        return burst * ((rng.random(length) - 0.5) * 1.8 + np.sin(index * 0.7) * 0.16) + noise
    if modality == "eeg":
        return 0.46 * np.sin(time * np.pi * 28) + 0.22 * np.sin(time * np.pi * 74) + noise * 1.6
    if modality == "ppg":
        phase = np.mod(time * 9, 1)
        return np.exp(-np.square((phase - 0.22) / 0.1)) + 0.24 * np.exp(-np.square((phase - 0.52) / 0.07)) + noise * 0.35
    if modality == "resp":
        return 0.82 * np.sin(time * np.pi * 6) + 0.12 * np.sin(time * np.pi * 12) + noise * 0.5
    phase = np.mod(time * 11, 1)
    shifted = np.maximum(0, phase - 0.38)
    first = np.sin(phase * 90) * np.exp(-phase * 45)
    second = np.sin(shifted * 100) * np.exp(-shifted * 60)
    return first + second * 0.7 + noise * 0.3
