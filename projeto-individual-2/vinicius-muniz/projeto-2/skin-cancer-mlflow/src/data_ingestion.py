"""Ingestão de dados do ISIC Archive."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Optional
import pandas as pd
from .config import load_config, project_root


def index_raw_images(raw_dir: Path) -> pd.DataFrame:
    rows = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"):
        for p in raw_dir.rglob(ext):
            rows.append({
                "path": str(p.relative_to(raw_dir)),
                "label": p.parent.name.lower(),
                "bytes": p.stat().st_size,
                "sha1": _sha1(p),
            })
    return pd.DataFrame(rows)


def _sha1(path: Path) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_dataset(df: pd.DataFrame, allowed_labels: list[str]) -> dict:
    issues = {
        "empty": int((df["bytes"] == 0).sum()),
        "duplicates": int(df["sha1"].duplicated().sum()),
        "unknown_labels": df.loc[~df["label"].isin(allowed_labels), "label"].unique().tolist(),
        "per_class_count": df["label"].value_counts().to_dict(),
        "total": int(len(df)),
    }
    return issues


def build_index(config: Optional[dict] = None) -> pd.DataFrame:
    cfg = config or load_config()
    raw = project_root() / cfg["data"]["raw_dir"]
    raw.mkdir(parents=True, exist_ok=True)
    df = index_raw_images(raw)
    out = project_root() / cfg["data"]["processed_dir"] / "index.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    report = validate_dataset(df, cfg["model"]["labels"])
    with open(out.parent / "quality_report.json", "w") as f:
        json.dump(report, f, indent=2)
    return df


if __name__ == "__main__":
    df = build_index()
    print(f"Indexed {len(df)} images")
