# src/model/train.py
"""
Two-phase fine-tuning of YOLOS-small for astronomical object detection.
Phase 1: frozen backbone, head warm-up. Phase 2: full end-to-end with differential LRs.
"""
from __future__ import annotations

import time
from pathlib import Path

import mlflow
import torch
from torch.utils.data import DataLoader
from transformers import YolosForObjectDetection, YolosImageProcessor

from src.data.dataset import AstroDetectionDataset, collate_fn, train_val_split

MODEL_NAME = "hustvl/yolos-small"
ID2LABEL = {0: "star", 1: "galaxy", 2: "quasar"}
LABEL2ID = {v: k for k, v in ID2LABEL.items()}


def load_model_for_finetuning(base_model: str = MODEL_NAME) -> tuple[YolosForObjectDetection, YolosImageProcessor]:
    """Load YOLOS-small with a fresh 3-class head, keeping pretrained backbone weights."""
    processor = YolosImageProcessor.from_pretrained(base_model)
    model = YolosForObjectDetection.from_pretrained(
        base_model,
        num_labels=3,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
        ignore_mismatched_sizes=True,
    )
    return model, processor


def _make_optimizer(
    model: YolosForObjectDetection,
    lr_head: float,
    lr_backbone: float,
    weight_decay: float,
) -> torch.optim.AdamW:
    backbone_params = [p for n, p in model.named_parameters() if "vit" in n and p.requires_grad]
    head_params = [p for n, p in model.named_parameters() if "vit" not in n and p.requires_grad]
    return torch.optim.AdamW(
        [
            {"params": backbone_params, "lr": lr_backbone},
            {"params": head_params, "lr": lr_head},
        ],
        weight_decay=weight_decay,
    )


def _train_epoch(
    model: YolosForObjectDetection,
    loader: DataLoader,
    optimizer: torch.optim.AdamW,
    device: torch.device,
) -> dict[str, float]:
    model.train()
    totals: dict[str, float] = {}
    count = 0

    for pixel_values, targets in loader:
        pixel_values = pixel_values.to(device)
        labels = [{k: v.to(device) for k, v in t.items()} for t in targets]

        optimizer.zero_grad()
        outputs = model(pixel_values=pixel_values, labels=labels)
        outputs.loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        for key, val in outputs.loss_dict.items():
            totals[key] = totals.get(key, 0.0) + val.item()
        totals["loss"] = totals.get("loss", 0.0) + outputs.loss.item()
        count += 1

    return {k: v / count for k, v in totals.items()}


@torch.no_grad()
def _val_epoch(
    model: YolosForObjectDetection,
    loader: DataLoader,
    device: torch.device,
) -> dict[str, float]:
    model.eval()
    totals: dict[str, float] = {}
    count = 0

    for pixel_values, targets in loader:
        pixel_values = pixel_values.to(device)
        labels = [{k: v.to(device) for k, v in t.items()} for t in targets]

        outputs = model(pixel_values=pixel_values, labels=labels)

        for key, val in outputs.loss_dict.items():
            totals[key] = totals.get(key, 0.0) + val.item()
        totals["loss"] = totals.get("loss", 0.0) + outputs.loss.item()
        count += 1

    return {k: v / count for k, v in totals.items()}


def finetune(
    train_metadata: list[dict],
    val_metadata: list[dict],
    image_dir: Path,
    output_dir: Path,
    base_model: str = MODEL_NAME,
    epochs: int = 50,
    freeze_epochs: int = 10,
    lr_head: float = 1e-4,
    lr_backbone: float = 1e-5,
    weight_decay: float = 1e-4,
    batch_size: int = 4,
    num_workers: int = 0,
    device_str: str = "auto",
) -> Path:
    """Fine-tune YOLOS-small. Logs to the active MLflow run. Returns path to best checkpoint."""
    device = _resolve_device(device_str)
    print(f"[train] Using device: {device}")

    model, processor = load_model_for_finetuning(base_model)
    model.to(device)

    train_ds = AstroDetectionDataset(image_dir, train_metadata, processor, augment=True)
    val_ds = AstroDetectionDataset(image_dir, val_metadata, processor, augment=False)

    train_loader = DataLoader(
        train_ds, batch_size=batch_size, shuffle=True,
        collate_fn=collate_fn, num_workers=num_workers,
    )
    val_loader = DataLoader(
        val_ds, batch_size=batch_size, shuffle=False,
        collate_fn=collate_fn, num_workers=num_workers,
    )

    _set_backbone_grad(model, requires_grad=False)
    optimizer = _make_optimizer(model, lr_head=lr_head, lr_backbone=lr_backbone, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    best_val_loss = float("inf")
    best_model_dir = output_dir / "best"

    for epoch in range(epochs):
        if epoch == freeze_epochs:
            print(f"[train] Epoch {epoch}: unfreezing backbone")
            _set_backbone_grad(model, requires_grad=True)
            optimizer = _make_optimizer(model, lr_head=lr_head, lr_backbone=lr_backbone, weight_decay=weight_decay)
            scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                optimizer, T_max=epochs - freeze_epochs, last_epoch=-1
            )

        t0 = time.perf_counter()
        train_metrics = _train_epoch(model, train_loader, optimizer, device)
        val_metrics = _val_epoch(model, val_loader, device)
        scheduler.step()
        elapsed = time.perf_counter() - t0

        mlflow.log_metrics(
            {
                "train_loss": train_metrics.get("loss", 0.0),
                "train_loss_ce": train_metrics.get("loss_ce", 0.0),
                "train_loss_bbox": train_metrics.get("loss_bbox", 0.0),
                "train_loss_giou": train_metrics.get("loss_giou", 0.0),
                "val_loss": val_metrics.get("loss", 0.0),
                "val_loss_ce": val_metrics.get("loss_ce", 0.0),
                "val_loss_bbox": val_metrics.get("loss_bbox", 0.0),
                "val_loss_giou": val_metrics.get("loss_giou", 0.0),
                "epoch_time_s": round(elapsed, 1),
            },
            step=epoch,
        )

        print(
            f"[train] Epoch {epoch:3d}/{epochs}  "
            f"train_loss={train_metrics.get('loss', 0):.4f}  "
            f"val_loss={val_metrics.get('loss', 0):.4f}  "
            f"({elapsed:.1f}s)"
        )

        if val_metrics.get("loss", float("inf")) < best_val_loss:
            best_val_loss = val_metrics["loss"]
            model.save_pretrained(best_model_dir)
            processor.save_pretrained(best_model_dir)
            print(f"[train]   -> new best val_loss={best_val_loss:.4f}, saved to {best_model_dir}")

    final_model_dir = output_dir / "final"
    model.save_pretrained(final_model_dir)
    processor.save_pretrained(final_model_dir)

    mlflow.log_metric("best_val_loss", best_val_loss)
    return best_model_dir


def _set_backbone_grad(model: YolosForObjectDetection, requires_grad: bool) -> None:
    for name, param in model.named_parameters():
        if "vit" in name:
            param.requires_grad = requires_grad


def _resolve_device(device_str: str) -> torch.device:
    if device_str == "auto":
        if torch.cuda.is_available():
            return torch.device("cuda")
        if torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")
    return torch.device(device_str)
