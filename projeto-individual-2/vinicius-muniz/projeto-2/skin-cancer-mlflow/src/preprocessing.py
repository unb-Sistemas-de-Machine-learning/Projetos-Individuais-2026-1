"""Pré-processamento e particionamento."""
from __future__ import annotations
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split
from .config import load_config, project_root


def load_image(path: Path, size: int) -> Image.Image:
    img = Image.open(path).convert("RGB")
    img = img.resize((size, size), Image.BILINEAR)
    return img


def split_dataset(df: pd.DataFrame, test_size: float, val_size: float, seed: int) -> dict:
    train, test = train_test_split(df, test_size=test_size, random_state=seed, stratify=df["label"])
    rel_val = val_size / (1 - test_size)
    train, val = train_test_split(train, test_size=rel_val, random_state=seed, stratify=train["label"])
    return {"train": train, "val": val, "test": test}


def persist_splits(splits: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, part in splits.items():
        part.to_csv(out_dir / f"{name}.csv", index=False)


def run(config: Optional[dict] = None) -> dict:
    cfg = config or load_config()
    proc = project_root() / cfg["data"]["processed_dir"]
    index_csv = proc / "index.csv"
    if not index_csv.exists():
        raise FileNotFoundError("Run data_ingestion first")
    df = pd.read_csv(index_csv)
    df = df[df["label"].isin(cfg["model"]["labels"])].reset_index(drop=True)
    splits = split_dataset(df, cfg["data"]["test_split"], cfg["data"]["val_split"], cfg["data"]["random_seed"])
    persist_splits(splits, proc / "splits")
    return {k: len(v) for k, v in splits.items()}


if __name__ == "__main__":
    print(run())
