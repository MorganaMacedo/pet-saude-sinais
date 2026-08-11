import io
import json

import numpy as np
import pandas as pd


MAX_FILE_SIZE = 25_000_000
MAX_SAMPLES = 1_000_000


def read_signal_bytes(data: bytes, filename: str) -> np.ndarray:
    if len(data) > MAX_FILE_SIZE:
        raise ValueError("O arquivo excede 25 MB.")
    lowered = filename.lower()
    if lowered.endswith(".json"):
        parsed = json.loads(data.decode("utf-8"))
        source = parsed if isinstance(parsed, list) else parsed.get("signal", parsed.get("samples", []))
        values = pd.to_numeric(pd.Series(source), errors="coerce").dropna().to_numpy(dtype=float)
    else:
        frame = pd.read_csv(io.BytesIO(data), sep=None, engine="python", header=None)
        numeric = frame.apply(pd.to_numeric, errors="coerce")
        if numeric.shape[1] > 8 and numeric.shape[0] < 10:
            values = numeric.iloc[0].dropna().to_numpy(dtype=float)
        else:
            valid_columns = [column for column in numeric.columns if numeric[column].notna().sum() >= 64]
            if not valid_columns:
                raise ValueError("Não foi encontrada uma coluna com ao menos 64 amostras numéricas.")
            values = numeric[valid_columns[-1]].dropna().to_numpy(dtype=float)
    values = values[np.isfinite(values)]
    if values.size < 64:
        raise ValueError("O arquivo precisa conter ao menos 64 amostras numéricas válidas.")
    return values[:MAX_SAMPLES]


def compact_signal(values: np.ndarray, maximum: int = 2500) -> pd.DataFrame:
    step = max(1, int(np.ceil(values.size / maximum)))
    sampled = values[::step]
    return pd.DataFrame({"Amplitude": sampled}, index=np.arange(sampled.size) * step)
