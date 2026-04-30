"""Carregamento do modelo pré-treinado do HuggingFace + wrapper pyfunc MLflow."""
from __future__ import annotations
from pathlib import Path
from typing import Optional
import io
import base64
import numpy as np
import pandas as pd
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification
import mlflow.pyfunc
from .config import load_config, project_root
from .guardrails import check_input, apply_confidence_guard, DISCLAIMER


def download_model(cfg: Optional[dict] = None) -> Path:
    cfg = cfg or load_config()
    target = project_root() / cfg["model"]["local_dir"]
    target.mkdir(parents=True, exist_ok=True)
    mid = cfg["model"]["hf_model_id"]
    processor = AutoImageProcessor.from_pretrained(mid)
    model = AutoModelForImageClassification.from_pretrained(mid)
    processor.save_pretrained(target)
    model.save_pretrained(target)
    return target


class SkinCancerPyfunc(mlflow.pyfunc.PythonModel):
    """Wrapper MLflow com guardrails embutidos."""

    def load_context(self, context):
        import yaml
        cfg_path = context.artifacts["config"]
        with open(cfg_path) as f:
            self.cfg = yaml.safe_load(f)
        model_path = context.artifacts["model_dir"]
        self.processor = AutoImageProcessor.from_pretrained(model_path)
        self.model = AutoModelForImageClassification.from_pretrained(model_path)
        self.model.eval()
        self.id2label = self.model.config.id2label

    def _predict_image(self, image: Image.Image) -> dict:
        guard = check_input(image, self.cfg["guardrails"])
        if not guard.allowed:
            return {
                "decision": "rejected",
                "label": None,
                "confidence": None,
                "message": guard.reason,
                "skin_tone_ita": guard.skin_tone_ita,
                "disclaimer": DISCLAIMER,
            }
        with torch.no_grad():
            inputs = self.processor(images=image, return_tensors="pt")
            logits = self.model(**inputs).logits
            probs = torch.softmax(logits, dim=-1)[0].cpu().numpy()
        fine_map = {self.id2label[i]: float(p) for i, p in enumerate(probs)}
        prob_map = _aggregate_binary(fine_map, self.cfg["model"]["label_map"])
        result = apply_confidence_guard(prob_map, self.cfg["guardrails"]["min_confidence"])
        result["fine_probabilities"] = fine_map
        result["skin_tone_ita"] = guard.skin_tone_ita
        result["disclaimer"] = DISCLAIMER
        return result

    def predict(self, context, model_input):
        if isinstance(model_input, pd.DataFrame):
            rows = model_input.to_dict(orient="records")
        else:
            rows = model_input
        out = []
        for row in rows:
            img = _row_to_image(row)
            out.append(self._predict_image(img))
        return out


def _aggregate_binary(fine: dict, label_map: dict) -> dict:
    out = {}
    for coarse, fines in label_map.items():
        out[coarse] = float(sum(fine.get(f, 0.0) for f in fines))
    total = sum(out.values())
    if total > 0:
        out = {k: v / total for k, v in out.items()}
    return out


def _row_to_image(row: dict) -> Image.Image:
    if "path" in row and row["path"]:
        return Image.open(row["path"]).convert("RGB")
    if "image_b64" in row and row["image_b64"]:
        data = base64.b64decode(row["image_b64"])
        return Image.open(io.BytesIO(data)).convert("RGB")
    raise ValueError("Registro requer 'path' ou 'image_b64'.")


def load_local_model(cfg: Optional[dict] = None):
    cfg = cfg or load_config()
    mdir = project_root() / cfg["model"]["local_dir"]
    processor = AutoImageProcessor.from_pretrained(mdir)
    model = AutoModelForImageClassification.from_pretrained(mdir)
    model.eval()
    return processor, model
