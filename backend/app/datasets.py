import json
from functools import lru_cache
from pathlib import Path


CATALOG_PATH = Path(__file__).resolve().parents[1] / "configs" / "dataset_catalog.json"


@lru_cache(maxsize=1)
def load_catalog() -> list[dict]:
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("O catálogo de bases precisa ser uma lista.")
    return data


def sources_for(modality: str) -> list[dict]:
    return [item for item in load_catalog() if item.get("modality") == modality]


def catalog_summary() -> dict:
    catalog = load_catalog()
    return {
        "datasets": len(catalog),
        "modalities": len({item["modality"] for item in catalog}),
        "open": sum(item.get("access") == "open" for item in catalog),
        "credentialed": sum(item.get("access") == "credentialed" for item in catalog)
    }
