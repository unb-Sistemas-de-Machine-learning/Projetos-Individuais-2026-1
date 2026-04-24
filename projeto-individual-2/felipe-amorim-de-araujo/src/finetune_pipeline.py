# src/finetune_pipeline.py
"""
End-to-end fine-tuning pipeline for YOLOS-small on SDSS astronomical images.

Steps
-----
1. Build annotated dataset  — download SDSS cutouts and auto-label from catalog
2. Train / val split
3. Fine-tune YOLOS-small   — 2-phase: head warm-up then end-to-end
4. Register best checkpoint in MLflow Model Registry

Usage
-----
    uv run python -m src.finetune_pipeline

    # Faster smoke-test (few regions, few epochs):
    uv run python -m src.finetune_pipeline \\
        --n-regions 20 --epochs 5 --freeze-epochs 2 --batch-size 2

    # Use a previously downloaded dataset:
    uv run python -m src.finetune_pipeline \\
        --skip-download --data-dir data/finetune
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import json

import mlflow
import mlflow.pyfunc
from transformers import YolosForObjectDetection, YolosImageProcessor

from src.data.annotate import TRAINING_REGIONS, build_annotated_dataset
from src.data.dataset import load_annotations, train_val_split
from src.model.pyfunc_model import SpaceDetectorPyfunc
from src.model.train import MODEL_NAME, finetune

EXPERIMENT_NAME = "space-object-detection-finetune"


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def run_finetune_pipeline(
    data_dir: Path = Path("data/finetune"),
    n_regions: int = len(TRAINING_REGIONS),
    radius_deg: float = 0.05,
    scale: float = 0.2,
    epochs: int = 50,
    freeze_epochs: int = 10,
    lr_head: float = 1e-4,
    lr_backbone: float = 1e-5,
    weight_decay: float = 1e-4,
    batch_size: int = 4,
    val_fraction: float = 0.2,
    base_model: str = MODEL_NAME,
    skip_download: bool = False,
) -> Path:
    """
    Orchestrate data download, annotation, fine-tuning, and model registration
    under a single MLflow run.

    Returns the path to the best fine-tuned checkpoint directory.
    """
    mlflow.set_experiment(EXPERIMENT_NAME)

    with mlflow.start_run():
        mlflow.set_tags({
            "git_commit": _git_commit(),
            "base_model": base_model,
            "pipeline": "finetune",
        })

        mlflow.log_params({
            "n_regions": n_regions,
            "radius_deg": radius_deg,
            "scale": scale,
            "epochs": epochs,
            "freeze_epochs": freeze_epochs,
            "lr_head": lr_head,
            "lr_backbone": lr_backbone,
            "weight_decay": weight_decay,
            "batch_size": batch_size,
            "val_fraction": val_fraction,
            "base_model": base_model,
        })

        # ------------------------------------------------------------------
        # Step 1: Build annotated dataset
        # ------------------------------------------------------------------
        annotations_path = data_dir / "annotations.json"

        if skip_download and annotations_path.exists():
            print(f"[1/3] Skipping download — using existing {annotations_path}")
        else:
            print(f"[1/3] Building annotated dataset: {n_regions} regions → {data_dir}")
            stats = build_annotated_dataset(
                output_dir=data_dir,
                regions=TRAINING_REGIONS[:n_regions],
                radius_deg=radius_deg,
                scale=scale,
            )
            print(
                f"      downloaded={stats['downloaded']}  "
                f"objects={stats['total_objects']}  "
                f"skipped_no_objects={stats['skipped_no_sdss_objects']}  "
                f"skipped_guardrail={stats['skipped_guardrail']}"
            )
            mlflow.log_metrics({
                "dataset_images": stats["downloaded"],
                "dataset_objects": stats["total_objects"],
                "dataset_skipped_no_objects": stats["skipped_no_sdss_objects"],
                "dataset_skipped_guardrail": stats["skipped_guardrail"],
            })

        # ------------------------------------------------------------------
        # Step 2: Train / val split
        # ------------------------------------------------------------------
        metadata = load_annotations(annotations_path)
        train_meta, val_meta = train_val_split(metadata, val_fraction=val_fraction)
        print(f"[2/3] Split: {len(train_meta)} train / {len(val_meta)} val images")
        mlflow.log_metrics({
            "n_train_images": len(train_meta),
            "n_val_images": len(val_meta),
        })

        # ------------------------------------------------------------------
        # Step 3: Fine-tune
        # ------------------------------------------------------------------
        output_dir = data_dir / "checkpoints"
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"[3/3] Fine-tuning for {epochs} epochs "
              f"(freeze_epochs={freeze_epochs}, batch_size={batch_size})")
        best_checkpoint = finetune(
            train_metadata=train_meta,
            val_metadata=val_meta,
            image_dir=data_dir / "raw",
            output_dir=output_dir,
            base_model=base_model,
            epochs=epochs,
            freeze_epochs=freeze_epochs,
            lr_head=lr_head,
            lr_backbone=lr_backbone,
            weight_decay=weight_decay,
            batch_size=batch_size,
        )

        # ------------------------------------------------------------------
        # Register best checkpoint as pyfunc (full pipeline: guardrails + preprocessing + model)
        # ------------------------------------------------------------------
        config_path = data_dir / "model_config.json"
        config_path.write_text(json.dumps({
            "confidence_threshold": 0.4,
            "model_name": str(best_checkpoint),
        }, indent=2))

        mlflow.pyfunc.log_model(
            artifact_path="finetuned-model",
            python_model=SpaceDetectorPyfunc(),
            artifacts={
                "checkpoint": str(best_checkpoint),
                "config": str(config_path),
            },
            code_paths=["src"],
            registered_model_name="space-detector-finetuned",
        )

        print(f"\nDone. Best checkpoint: {best_checkpoint}")
        return best_checkpoint


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune YOLOS-small on SDSS astronomical images")
    parser.add_argument("--data-dir", type=Path, default=Path("data/finetune"))
    parser.add_argument("--n-regions", type=int, default=len(TRAINING_REGIONS))
    parser.add_argument("--radius-deg", type=float, default=0.05)
    parser.add_argument("--scale", type=float, default=0.2)
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--freeze-epochs", type=int, default=10)
    parser.add_argument("--lr-head", type=float, default=1e-4)
    parser.add_argument("--lr-backbone", type=float, default=1e-5)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--val-fraction", type=float, default=0.2)
    parser.add_argument("--base-model", type=str, default=MODEL_NAME)
    parser.add_argument("--skip-download", action="store_true",
                        help="Skip SDSS download if annotations.json already exists")
    args = parser.parse_args()

    run_finetune_pipeline(
        data_dir=args.data_dir,
        n_regions=args.n_regions,
        radius_deg=args.radius_deg,
        scale=args.scale,
        epochs=args.epochs,
        freeze_epochs=args.freeze_epochs,
        lr_head=args.lr_head,
        lr_backbone=args.lr_backbone,
        weight_decay=args.weight_decay,
        batch_size=args.batch_size,
        val_fraction=args.val_fraction,
        base_model=args.base_model,
        skip_download=args.skip_download,
    )
