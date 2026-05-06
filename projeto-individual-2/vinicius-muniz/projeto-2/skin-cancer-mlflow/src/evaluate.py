"""Avaliação com MLflow tracking."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
import mlflow
import numpy as np
import pandas as pd
import torch
from PIL import Image
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from .config import load_config, project_root
from .model import load_local_model, _aggregate_binary
from .guardrails import check_input, apply_confidence_guard


def _predict_df(df: pd.DataFrame, processor, model, labels, cfg_guard, raw_dir: Path, label_map=None):
    rows = []
    for _, r in df.iterrows():
        path = raw_dir / r["path"]
        img = Image.open(path).convert("RGB")
        guard = check_input(img, cfg_guard)
        with torch.no_grad():
            inputs = processor(images=img, return_tensors="pt")
            logits = model(**inputs).logits
            probs = torch.softmax(logits, dim=-1)[0].cpu().numpy()
        fine_map = {model.config.id2label[i]: float(p) for i, p in enumerate(probs)}
        prob_map = _aggregate_binary(fine_map, label_map) if label_map else fine_map
        decision = apply_confidence_guard(prob_map, cfg_guard["min_confidence"])
        rows.append({
            "path": r["path"],
            "label_true": r["label"],
            "label_pred": decision["label"],
            "confidence": decision["confidence"],
            "decision": decision["decision"],
            "guardrail_allowed": guard.allowed,
            "ita": guard.skin_tone_ita,
            **{f"p_{k}": v for k, v in prob_map.items()},
        })
    return pd.DataFrame(rows)


def _metrics(df: pd.DataFrame, labels: list[str]) -> dict:
    mask = df["label_pred"].notna() & df["guardrail_allowed"]
    d = df[mask]
    if len(d) == 0:
        return {"coverage": 0.0, "n_evaluated": 0}
    y_true = d["label_true"].tolist()
    y_pred = d["label_pred"].tolist()
    metrics = {
        "coverage": float(mask.mean()),
        "n_evaluated": int(len(d)),
        "n_total": int(len(df)),
        "n_rejected_guardrail": int((~df["guardrail_allowed"]).sum()),
        "n_uncertain": int((df["decision"] == "uncertain").sum()),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
    }
    if len(labels) == 2 and f"p_{labels[1]}" in d.columns:
        try:
            metrics["roc_auc"] = float(
                roc_auc_score((d["label_true"] == labels[1]).astype(int), d[f"p_{labels[1]}"])
            )
        except ValueError:
            pass
    return metrics


def run(split: str = "test", config: Optional[dict] = None) -> dict:
    cfg = config or load_config()
    mlflow.set_tracking_uri(cfg["mlflow"]["tracking_uri"])
    mlflow.set_experiment(cfg["mlflow"]["experiment_name"])
    processor, model = load_local_model(cfg)
    proc_dir = project_root() / cfg["data"]["processed_dir"]
    raw_dir = project_root() / cfg["data"]["raw_dir"]
    df_split = pd.read_csv(proc_dir / "splits" / f"{split}.csv")
    labels = cfg["model"]["labels"]

    with mlflow.start_run(run_name=f"eval-{split}") as run:
        mlflow.log_params({
            "hf_model_id": cfg["model"]["hf_model_id"],
            "split": split,
            "min_confidence": cfg["guardrails"]["min_confidence"],
            "skin_tone_ita_min": cfg["guardrails"]["skin_tone_ita_min"],
            "n_images": len(df_split),
        })
        preds = _predict_df(df_split, processor, model, labels, cfg["guardrails"], raw_dir, cfg["model"].get("label_map"))
        metrics = _metrics(preds, labels)
        mlflow.log_metrics(metrics)

        out_dir = proc_dir / "eval" / split
        out_dir.mkdir(parents=True, exist_ok=True)
        preds.to_csv(out_dir / "predictions.csv", index=False)
        with open(out_dir / "metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)
        mlflow.log_artifacts(str(out_dir), artifact_path=f"eval/{split}")

        cm_df = pd.DataFrame(
            confusion_matrix(
                preds.loc[preds["label_pred"].notna(), "label_true"],
                preds.loc[preds["label_pred"].notna(), "label_pred"],
                labels=labels,
            ),
            index=[f"true_{l}" for l in labels],
            columns=[f"pred_{l}" for l in labels],
        )
        cm_path = out_dir / "confusion_matrix.csv"
        cm_df.to_csv(cm_path)
        mlflow.log_artifact(str(cm_path), artifact_path=f"eval/{split}")

        print(f"Run id: {run.info.run_id}")
        print(json.dumps(metrics, indent=2))
    return metrics


if __name__ == "__main__":
    run()
