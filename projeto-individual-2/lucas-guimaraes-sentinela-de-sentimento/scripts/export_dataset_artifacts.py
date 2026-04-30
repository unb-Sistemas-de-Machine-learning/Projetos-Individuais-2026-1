#!/usr/bin/env python3
"""
Exporta artefatos de dados para evidência do requisito 1:
- train.csv / validation.csv / test.csv
- quality_train.json / quality_validation.json / quality_test.json
- dataset_metadata.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.ingest import dataset_metadata, load_glue_sst2  # noqa: E402
from src.data.quality import dataset_quality_report  # noqa: E402


def load_config() -> dict:
    with (ROOT / "config" / "config.yaml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    cfg = load_config()
    seed = int(cfg["seed"])
    dataset_cfg = cfg["dataset"]

    out_dir = ROOT / "data" / "processed"
    raw_dir = ROOT / "data" / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    ds = load_glue_sst2(cache_dir=raw_dir, seed=seed)

    # Exporta splits completos para CSV (evidência direta).
    for split_name in ["train", "validation", "test"]:
        split = ds[split_name]
        df = split.to_pandas()
        out_path = out_dir / f"{split_name}.csv"
        df.to_csv(out_path, index=False)
        print(f"Split exportado: {out_path} ({len(df)} linhas)")

    # Exporta qualidade por split.
    for split_name in ["train", "validation", "test"]:
        report = dataset_quality_report(
            ds[split_name],
            text_column=dataset_cfg["text_column"],
            label_column=dataset_cfg["label_column"],
        )
        report_path = out_dir / f"quality_{split_name}.json"
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Relatório de qualidade: {report_path}")

    meta = dataset_metadata(ds)
    meta_path = out_dir / "dataset_metadata.json"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Metadados: {meta_path}")


if __name__ == "__main__":
    main()
