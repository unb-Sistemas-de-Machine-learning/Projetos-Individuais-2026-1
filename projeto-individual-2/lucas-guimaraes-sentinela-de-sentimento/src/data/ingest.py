"""Aquisição de dados: carrega SST-2 (GLUE) via Hugging Face `datasets`."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from datasets import DatasetDict, load_dataset


def load_glue_sst2(
    cache_dir: Path | None = None,
    max_train_samples: int | None = None,
    seed: int = 42,
) -> DatasetDict:
    """
    Carrega o conjunto glue/sst2 com splits oficiais (train/validation/test).

    Opcionalmente subsample o treino para execuções mais rápidas em CI/demos,
    mantendo reprodutibilidade via `seed`.
    """
    ds = load_dataset("glue", "sst2", cache_dir=str(cache_dir) if cache_dir else None)
    if max_train_samples is not None and max_train_samples < len(ds["train"]):
        ds["train"] = ds["train"].shuffle(seed=seed).select(range(max_train_samples))
    return ds


def dataset_metadata(ds: DatasetDict) -> dict[str, Any]:
    """Resumo serializável para artefatos MLflow."""
    out: dict[str, Any] = {}
    for split, d in ds.items():
        out[split] = {"num_rows": d.num_rows, "features": list(d.features.keys())}
    return out
