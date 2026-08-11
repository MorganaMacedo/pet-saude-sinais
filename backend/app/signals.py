from dataclasses import dataclass

import numpy as np
from scipy import signal as scipy_signal
from scipy.stats import kurtosis, skew


FEATURE_NAMES = [
    "mean",
    "standard_deviation",
    "rms",
    "peak_to_peak",
    "skewness",
    "kurtosis",
    "zero_crossing_rate",
    "mean_absolute_difference",
    "line_length",
    "crest_factor",
    "spectral_entropy",
    "dominant_frequency",
    "median_frequency",
    "delta_power",
    "theta_power",
    "alpha_power",
    "beta_power",
    "gamma_power",
    "low_high_power_ratio",
    "peak_rate",
    "interval_variability"
]


FEATURE_LABELS = {
    "mean": "Média do sinal",
    "standard_deviation": "Variabilidade da amplitude",
    "rms": "Energia RMS",
    "peak_to_peak": "Amplitude pico a pico",
    "skewness": "Assimetria da distribuição",
    "kurtosis": "Curtose",
    "zero_crossing_rate": "Cruzamentos por zero",
    "mean_absolute_difference": "Variação entre amostras",
    "line_length": "Comprimento de linha",
    "crest_factor": "Fator de crista",
    "spectral_entropy": "Entropia espectral",
    "dominant_frequency": "Frequência dominante",
    "median_frequency": "Frequência mediana",
    "delta_power": "Potência delta",
    "theta_power": "Potência teta",
    "alpha_power": "Potência alfa",
    "beta_power": "Potência beta",
    "gamma_power": "Potência gama",
    "low_high_power_ratio": "Relação baixa/alta frequência",
    "peak_rate": "Taxa de picos",
    "interval_variability": "Variabilidade entre eventos"
}


MODALITY_SPECS = {
    "ecg": {"band": (0.5, 45.0), "peak_distance": 0.25, "min_duration": 2.5},
    "emg": {"band": (10.0, 450.0), "peak_distance": 0.02, "min_duration": 1.0},
    "eeg": {"band": (0.5, 70.0), "peak_distance": 0.08, "min_duration": 4.0},
    "ppg": {"band": (0.3, 12.0), "peak_distance": 0.35, "min_duration": 5.0},
    "resp": {"band": (0.05, 4.0), "peak_distance": 1.0, "min_duration": 10.0},
    "pcg": {"band": (20.0, 500.0), "peak_distance": 0.08, "min_duration": 2.5}
}


@dataclass
class PreparedSignal:
    raw: np.ndarray
    filtered: np.ndarray
    missing_ratio: float
    sample_rate: int
    modality: str


def prepare_signal(values: list[float | None], sample_rate: int, modality: str) -> PreparedSignal:
    raw = np.asarray([np.nan if value is None else float(value) for value in values], dtype=np.float64)
    finite = np.isfinite(raw)
    missing_ratio = float(1.0 - finite.mean())
    if finite.sum() < 64:
        raise ValueError("O sinal contém menos de 64 amostras válidas.")
    if not finite.all():
        indices = np.arange(raw.size)
        raw[~finite] = np.interp(indices[~finite], indices[finite], raw[finite])
    raw = scipy_signal.detrend(raw, type="linear")
    spec = MODALITY_SPECS[modality]
    nyquist = sample_rate / 2
    low = max(spec["band"][0], 0.01)
    high = min(spec["band"][1], nyquist * 0.92)
    filtered = raw.copy()
    if low < high and raw.size > 40:
        try:
            sos = scipy_signal.butter(4, [low, high], btype="bandpass", fs=sample_rate, output="sos")
            filtered = scipy_signal.sosfiltfilt(sos, raw)
        except ValueError:
            filtered = raw.copy()
    scale = float(np.std(filtered))
    if scale > 1e-12:
        filtered = (filtered - np.mean(filtered)) / scale
    return PreparedSignal(raw=raw, filtered=filtered, missing_ratio=missing_ratio, sample_rate=sample_rate, modality=modality)


def assess_quality(prepared: PreparedSignal) -> dict:
    raw = prepared.raw
    filtered = prepared.filtered
    sample_rate = prepared.sample_rate
    duration = raw.size / sample_rate
    lower, upper = np.quantile(raw, [0.01, 0.99])
    dynamic_range = float(upper - lower)
    tolerance = max(dynamic_range * 1e-5, 1e-12)
    clipping = float(np.mean((np.abs(raw - np.min(raw)) <= tolerance) | (np.abs(raw - np.max(raw)) <= tolerance)))
    differences = np.abs(np.diff(raw))
    flatline_ratio = float(np.mean(differences <= tolerance))
    filtered_scale = float(np.std(filtered)) or 1.0
    residual = raw - scipy_signal.savgol_filter(raw, min(raw.size // 2 * 2 - 1, 31), 3)
    noise_ratio = float(np.std(residual) / (float(np.std(raw)) or filtered_scale))
    minimum = MODALITY_SPECS[prepared.modality]["min_duration"]
    duration_penalty = max(0.0, (minimum - duration) / minimum) * 22
    score = 100
    score -= prepared.missing_ratio * 180
    score -= min(clipping, 0.3) * 130
    score -= min(flatline_ratio, 0.5) * 110
    score -= min(noise_ratio, 1.4) * 20
    score -= duration_penalty
    quality = int(np.clip(round(score), 0, 98))
    status = "Adequado" if quality >= 80 else "Revisar" if quality >= 60 else "Insuficiente"
    messages = {
        "Adequado": "Sinal adequado para análise exploratória.",
        "Revisar": "Há indícios de ruído, artefatos ou duração limitada. Revise a aquisição.",
        "Insuficiente": "A qualidade limita a interpretação. Recomenda-se nova aquisição."
    }
    return {
        "quality": quality,
        "duration": round(duration, 4),
        "samples": int(raw.size),
        "valid_samples": int(round(raw.size * (1 - prepared.missing_ratio))),
        "missing_ratio": round(prepared.missing_ratio, 6),
        "noise_ratio": round(noise_ratio, 6),
        "clipping": round(clipping, 6),
        "flatline_ratio": round(flatline_ratio, 6),
        "dynamic_range": round(dynamic_range, 6),
        "status": status,
        "message": messages[status]
    }


def _band_power(frequencies: np.ndarray, density: np.ndarray, low: float, high: float) -> float:
    mask = (frequencies >= low) & (frequencies < high)
    if mask.sum() < 2:
        return 0.0
    return float(np.trapezoid(density[mask], frequencies[mask]))


def extract_features(prepared: PreparedSignal) -> dict[str, float]:
    values = prepared.filtered
    sample_rate = prepared.sample_rate
    absolute = np.abs(values)
    rms = float(np.sqrt(np.mean(np.square(values))))
    frequencies, density = scipy_signal.welch(values, fs=sample_rate, nperseg=min(values.size, 1024))
    density = np.maximum(density, np.finfo(float).eps)
    normalized_density = density / density.sum()
    spectral_entropy = float(-np.sum(normalized_density * np.log2(normalized_density)) / np.log2(normalized_density.size))
    dominant_frequency = float(frequencies[int(np.argmax(density))])
    cumulative = np.cumsum(density)
    median_frequency = float(frequencies[int(np.searchsorted(cumulative, cumulative[-1] / 2))])
    delta = _band_power(frequencies, density, 0.5, 4)
    theta = _band_power(frequencies, density, 4, 8)
    alpha = _band_power(frequencies, density, 8, 13)
    beta = _band_power(frequencies, density, 13, 30)
    gamma = _band_power(frequencies, density, 30, min(100, sample_rate / 2))
    total_power = max(delta + theta + alpha + beta + gamma, np.finfo(float).eps)
    distance = max(1, int(MODALITY_SPECS[prepared.modality]["peak_distance"] * sample_rate))
    peaks, _ = scipy_signal.find_peaks(values, distance=distance, prominence=max(0.2, float(np.std(values)) * 0.35))
    intervals = np.diff(peaks) / sample_rate if peaks.size > 1 else np.asarray([0.0])
    interval_variability = float(np.std(intervals) / np.mean(intervals)) if np.mean(intervals) > 0 else 0.0
    features = {
        "mean": float(np.mean(values)),
        "standard_deviation": float(np.std(values)),
        "rms": rms,
        "peak_to_peak": float(np.ptp(values)),
        "skewness": float(np.nan_to_num(skew(values, bias=False))),
        "kurtosis": float(np.nan_to_num(kurtosis(values, bias=False))),
        "zero_crossing_rate": float(np.mean(np.signbit(values[1:]) != np.signbit(values[:-1]))),
        "mean_absolute_difference": float(np.mean(np.abs(np.diff(values)))),
        "line_length": float(np.sum(np.abs(np.diff(values))) / values.size),
        "crest_factor": float(np.max(absolute) / max(rms, np.finfo(float).eps)),
        "spectral_entropy": spectral_entropy,
        "dominant_frequency": dominant_frequency,
        "median_frequency": median_frequency,
        "delta_power": delta / total_power,
        "theta_power": theta / total_power,
        "alpha_power": alpha / total_power,
        "beta_power": beta / total_power,
        "gamma_power": gamma / total_power,
        "low_high_power_ratio": float((delta + theta + alpha) / max(beta + gamma, np.finfo(float).eps)),
        "peak_rate": float(peaks.size / max(values.size / sample_rate, np.finfo(float).eps)),
        "interval_variability": interval_variability
    }
    return {name: float(np.nan_to_num(features[name], nan=0.0, posinf=1e6, neginf=-1e6)) for name in FEATURE_NAMES}
