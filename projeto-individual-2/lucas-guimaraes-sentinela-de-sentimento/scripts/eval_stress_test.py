#!/usr/bin/env python3
"""
Avaliação de robustez (stress test) para o modelo base.

Cria um conjunto sintético com casos difíceis:
- fora de domínio
- português
- sarcasmo/ironia
- ruído e ambiguidades

Uso:
  source .venv/bin/activate
  python scripts/eval_stress_test.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import mlflow
import numpy as np
import yaml
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.model.hf_predictor import _labels_from_outputs, build_pipeline  # noqa: E402


def load_config() -> dict:
    with (ROOT / "config" / "config.yaml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def stress_dataset() -> list[dict[str, Any]]:
    # label: 0 negativo, 1 positivo
    return [
        {"text": "The product just works and saves me hours every week.", "label": 1, "group": "out_of_domain"},
        {"text": "The service keeps failing and support never replies.", "label": 0, "group": "out_of_domain"},
        {"text": "Stocks rallied after the company beat expectations.", "label": 1, "group": "out_of_domain"},
        {"text": "The policy caused confusion and many complaints.", "label": 0, "group": "out_of_domain"},
        {"text": "O filme foi maravilhoso, adorei cada minuto.", "label": 1, "group": "portuguese"},
        {"text": "Esse filme e uma perda de tempo total.", "label": 0, "group": "portuguese"},
        {"text": "Atuacao boa, roteiro fraco e final estranho.", "label": 0, "group": "portuguese"},
        {"text": "Gostei bastante, veria de novo sem pensar.", "label": 1, "group": "portuguese"},
        {"text": "Great, another masterpiece of boredom.", "label": 0, "group": "sarcasm"},
        {"text": "Fantastic, I waited two hours for this disaster.", "label": 0, "group": "sarcasm"},
        {"text": "Wow, what an amazing way to waste my evening.", "label": 0, "group": "sarcasm"},
        {"text": "Sure, this is exactly the quality I did not ask for.", "label": 0, "group": "sarcasm"},
        {"text": "@@@@ #### !!!! 12345", "label": 0, "group": "noisy"},
        {"text": "ok", "label": 1, "group": "noisy"},
        {"text": "fine", "label": 1, "group": "noisy"},
        {"text": "good?? bad?? maybe", "label": 0, "group": "noisy"},
        {"text": "The movie was released in 2022 and runs for two hours.", "label": 0, "group": "ambiguous"},
        {"text": "Actors speak quietly for most scenes.", "label": 0, "group": "ambiguous"},
        {"text": "The camera stays still for long shots.", "label": 0, "group": "ambiguous"},
        {"text": "There are many dialogues and a short ending.", "label": 0, "group": "ambiguous"},
    ]


def evaluate_group(y_true: list[int], y_pred: list[int]) -> dict[str, float]:
    y_t = np.array(y_true)
    y_p = np.array(y_pred)
    return {
        "accuracy": float(accuracy_score(y_t, y_p)),
        "f1_macro": float(f1_score(y_t, y_p, average="macro", zero_division=0)),
        "precision_macro": float(precision_score(y_t, y_p, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_t, y_p, average="macro", zero_division=0)),
    }


def main() -> None:
    cfg = load_config()
    mlflow_cfg = cfg["mlflow"]
    model_cfg = cfg["model"]

    os.environ.setdefault("MLFLOW_TRACKING_URI", mlflow_cfg["tracking_uri"])
    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    mlflow.set_experiment(mlflow_cfg["experiment_name"])

    model_hf_id = os.environ.get("PIPELINE_MODEL_HF_ID", model_cfg["hf_id"])
    rows = stress_dataset()
    texts = [r["text"] for r in rows]
    y_true = [int(r["label"]) for r in rows]
    groups = [str(r["group"]) for r in rows]

    clf = build_pipeline(model_hf_id, task=model_cfg["task"])
    out = clf(texts)
    if not isinstance(out, list):
        out = [out]
    y_pred = _labels_from_outputs(out)

    overall = evaluate_group(y_true, y_pred)

    grouped_metrics: dict[str, dict[str, float]] = {}
    for g in sorted(set(groups)):
        idx = [i for i, grp in enumerate(groups) if grp == g]
        g_true = [y_true[i] for i in idx]
        g_pred = [y_pred[i] for i in idx]
        grouped_metrics[g] = evaluate_group(g_true, g_pred)

    predictions_rows = []
    for i, r in enumerate(rows):
        predictions_rows.append(
            {
                "text": r["text"],
                "group": r["group"],
                "label_true": int(y_true[i]),
                "label_pred": int(y_pred[i]),
                "correct": int(y_true[i] == y_pred[i]),
                "raw_label": str(out[i].get("label", "")),
                "score": float(out[i].get("score", 0.0)),
            }
        )

    artifact_dir = ROOT / "data" / "processed"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    pred_path = artifact_dir / "stress_test_predictions.json"
    pred_path.write_text(json.dumps(predictions_rows, indent=2, ensure_ascii=False), encoding="utf-8")

    with mlflow.start_run(run_name="stress-test-baseline") as run:
        mlflow.log_param("dataset", "synthetic_stress_test")
        mlflow.log_param("samples", len(rows))
        mlflow.log_param("model_hf_id", model_hf_id)
        mlflow.log_param("task", model_cfg["task"])
        mlflow.log_metric("stress_accuracy", overall["accuracy"])
        mlflow.log_metric("stress_f1_macro", overall["f1_macro"])
        mlflow.log_metric("stress_precision_macro", overall["precision_macro"])
        mlflow.log_metric("stress_recall_macro", overall["recall_macro"])

        for g, m in grouped_metrics.items():
            prefix = f"stress_{g}"
            mlflow.log_metric(f"{prefix}_accuracy", m["accuracy"])
            mlflow.log_metric(f"{prefix}_f1_macro", m["f1_macro"])
            mlflow.log_metric(f"{prefix}_precision_macro", m["precision_macro"])
            mlflow.log_metric(f"{prefix}_recall_macro", m["recall_macro"])

        mlflow.log_dict(grouped_metrics, "artifacts/stress_grouped_metrics.json")
        mlflow.log_artifact(str(pred_path), artifact_path="artifacts")

        print("Run ID:", run.info.run_id)
        print("Métricas gerais:", overall)
        print("Por grupo:", grouped_metrics)
        print("Predições salvas em:", pred_path)


if __name__ == "__main__":
    main()
