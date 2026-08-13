import numpy as np

from app.signals import FEATURE_NAMES, assess_quality, extract_features, prepare_signal


def synthetic_ecg(sample_rate: int = 360, seconds: int = 8) -> np.ndarray:
    time = np.arange(sample_rate * seconds) / sample_rate
    baseline = 0.05 * np.sin(2 * np.pi * 0.4 * time)
    beats = np.zeros_like(time)
    for center in np.arange(0.5, seconds, 0.82):
        beats += np.exp(-np.square((time - center) / 0.018))
        beats -= 0.22 * np.exp(-np.square((time - center - 0.035) / 0.025))
    return baseline + beats


def test_signal_pipeline_returns_fixed_features():
    prepared = prepare_signal(synthetic_ecg().tolist(), 360, "ecg")
    quality = assess_quality(prepared)
    features = extract_features(prepared)
    assert quality["status"] in {"Adequado", "Revisar"}
    assert list(features) == FEATURE_NAMES
    assert all(np.isfinite(value) for value in features.values())


def test_missing_values_are_interpolated():
    values = synthetic_ecg().tolist()
    values[40:55] = [None] * 15
    prepared = prepare_signal(values, 360, "ecg")
    quality = assess_quality(prepared)
    assert quality["missing_ratio"] > 0
    assert np.isfinite(prepared.filtered).all()


def test_lung_sound_pipeline_accepts_wide_band_signal():
    sample_rate = 4000
    time = np.arange(sample_rate * 5) / sample_rate
    values = 0.2 * np.sin(2 * np.pi * 520 * time) + 0.08 * np.sin(2 * np.pi * 145 * time)
    prepared = prepare_signal(values.tolist(), sample_rate, "lung")
    quality = assess_quality(prepared)
    features = extract_features(prepared)
    assert quality["duration"] == 5
    assert features["dominant_frequency"] > 100
