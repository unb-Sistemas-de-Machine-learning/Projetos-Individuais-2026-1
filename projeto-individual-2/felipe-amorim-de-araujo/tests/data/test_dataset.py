# tests/data/test_dataset.py
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import numpy as np
import pytest
import torch
from PIL import Image
from src.data.dataset import (
    AstroDetectionDataset,
    collate_fn,
    train_val_split,
    load_annotations,
)


def _make_metadata(n: int) -> list[dict]:
    return [
        {
            "image_file": f"field_{i:04d}.jpg",
            "center_ra": 180.0,
            "center_dec": 0.0,
            "objects": [{"bbox": [0.5, 0.5, 0.1, 0.1], "category_id": 1}],
        }
        for i in range(n)
    ]


def _fake_processor():
    proc = MagicMock()
    proc.return_value = {"pixel_values": torch.zeros(1, 3, 512, 512)}
    return proc


# --- train_val_split ---

def test_train_val_split_sizes():
    meta = _make_metadata(10)
    train, val = train_val_split(meta, val_fraction=0.2)
    assert len(train) == 8
    assert len(val) == 2
    assert len(train) + len(val) == len(meta)


def test_train_val_split_no_leakage():
    meta = _make_metadata(20)
    train, val = train_val_split(meta, val_fraction=0.2)
    train_files = {m["image_file"] for m in train}
    val_files = {m["image_file"] for m in val}
    assert train_files.isdisjoint(val_files)


def test_train_val_split_reproducible():
    meta = _make_metadata(20)
    t1, v1 = train_val_split(meta, seed=42)
    t2, v2 = train_val_split(meta, seed=42)
    assert [m["image_file"] for m in t1] == [m["image_file"] for m in t2]


# --- load_annotations ---

def test_load_annotations(tmp_path):
    meta = _make_metadata(3)
    p = tmp_path / "annotations.json"
    p.write_text(json.dumps(meta))
    loaded = load_annotations(p)
    assert loaded == meta


# --- AstroDetectionDataset ---

def test_dataset_len(tmp_path):
    meta = _make_metadata(4)
    for m in meta:
        img = Image.fromarray(np.random.randint(10, 200, (64, 64, 3), dtype=np.uint8))
        img.save(tmp_path / m["image_file"])
    ds = AstroDetectionDataset(tmp_path, meta, _fake_processor())
    assert len(ds) == 4


def test_dataset_item_shapes(tmp_path):
    meta = _make_metadata(1)
    img = Image.fromarray(np.random.randint(10, 200, (64, 64, 3), dtype=np.uint8))
    img.save(tmp_path / meta[0]["image_file"])
    ds = AstroDetectionDataset(tmp_path, meta, _fake_processor())
    pixel_values, target = ds[0]
    assert pixel_values.shape == (3, 512, 512)
    assert "class_labels" in target
    assert "boxes" in target
    assert target["class_labels"].dtype == torch.long
    assert target["boxes"].dtype == torch.float32


# --- collate_fn ---

def test_collate_fn_stacks_pixels(tmp_path):
    meta = _make_metadata(2)
    for m in meta:
        img = Image.fromarray(np.random.randint(10, 200, (64, 64, 3), dtype=np.uint8))
        img.save(tmp_path / m["image_file"])
    ds = AstroDetectionDataset(tmp_path, meta, _fake_processor())
    batch = [ds[0], ds[1]]
    pixels, targets = collate_fn(batch)
    assert pixels.shape[0] == 2
    assert isinstance(targets, list)
    assert len(targets) == 2
