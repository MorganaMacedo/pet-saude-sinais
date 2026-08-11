import json

import numpy as np

from portal.catalog import MODALITIES, generate_signal
from portal.signal_io import compact_signal, read_signal_bytes


def test_demo_signals_cover_all_modalities():
    for modality in MODALITIES:
        values = generate_signal(modality, 800)
        assert values.shape == (800,)
        assert np.isfinite(values).all()
        assert float(np.std(values)) > 0


def test_json_signal_is_read():
    payload = json.dumps({"samples": list(range(80))}).encode()
    values = read_signal_bytes(payload, "signal.json")
    assert values.size == 80


def test_csv_uses_numeric_signal_column():
    rows = "\n".join(f"{index},{np.sin(index / 10)}" for index in range(80)).encode()
    values = read_signal_bytes(rows, "signal.csv")
    assert values.size == 80


def test_compact_signal_limits_points():
    frame = compact_signal(np.arange(10000, dtype=float), maximum=500)
    assert len(frame) <= 500
