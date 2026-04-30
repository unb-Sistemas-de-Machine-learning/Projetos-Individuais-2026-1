"""Pré-processamento leve e particionamento documentado."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from datasets import DatasetDict


def save_split_manifest(
    ds: DatasetDict,
    out_dir: Path,
    seed: int,
    extra: dict[str, Any] | None = None,
) -> Path:
    """
    Exporta um manifesto com contagens e hash estável dos splits (versionamento de dados).

    Não grava textos completos (privacidade/tamanho); apenas metadados reproduzíveis.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {
        "seed": seed,
        "splits": {},
    }
    for name, split in ds.items():
        # Hash do schema + tamanho + primeiras linhas de ids se existirem
        payload = f"{name}:{split.num_rows}:{split.column_names}".encode()
        manifest["splits"][name] = {
            "num_rows": split.num_rows,
            "columns": split.column_names,
            "fingerprint": hashlib.sha256(payload).hexdigest()[:16],
        }
    if extra:
        manifest["extra"] = extra
    path = out_dir / "split_manifest.json"
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def basic_text_cleanup(text: str) -> str:
    """Normalização mínima para inferência (espaços)."""
    return " ".join(text.strip().split())
