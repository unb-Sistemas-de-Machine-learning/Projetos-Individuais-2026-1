#!/usr/bin/env python3
"""
Pipeline principal: ingestão → qualidade → manifesto → avaliação → MLflow (métricas, artefatos, modelo).

Uso:
  cd projeto-2/sistema-ml-nlp-sentimento
  python scripts/pipeline_run.py
  MLFLOW_TRACKING_URI=sqlite:///mlflow.db mlflow ui
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import mlflow
import mlflow.transformers
import numpy as np
import yaml
from sklearn.metrics import confusion_matrix

# Raiz do projeto (pai de scripts/)
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.ingest import dataset_metadata, load_glue_sst2  # noqa: E402
from src.data.preprocess import save_split_manifest  # noqa: E402
from src.data.quality import dataset_quality_report  # noqa: E402
from src.model.hf_predictor import build_pipeline, evaluate_on_split  # noqa: E402


def load_config() -> dict:
    cfg_path = ROOT / "config" / "config.yaml"
    with cfg_path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def _resolve_seed(default_seed: int) -> int:
    env_seed = os.environ.get("PIPELINE_SEED")
    return int(env_seed) if env_seed else int(default_seed)


def _resolve_model_hf_id(default_hf_id: str) -> str:
    return os.environ.get("PIPELINE_MODEL_HF_ID", default_hf_id)


def main() -> None:
    cfg = load_config()
    seed = _resolve_seed(int(cfg["seed"]))
    mlflow_cfg = cfg["mlflow"]
    dataset_cfg = cfg["dataset"]
    model_cfg = cfg["model"]
    model_hf_id = _resolve_model_hf_id(model_cfg["hf_id"])

    os.environ.setdefault("MLFLOW_TRACKING_URI", mlflow_cfg["tracking_uri"])
    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    mlflow.set_experiment(mlflow_cfg["experiment_name"])

    data_dir = ROOT / "data" / "processed"
    raw_dir = ROOT / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    max_train = os.environ.get("MAX_TRAIN_SAMPLES")
    max_train_i = int(max_train) if max_train else None

    ds = load_glue_sst2(cache_dir=raw_dir, max_train_samples=max_train_i, seed=seed)
    meta = dataset_metadata(ds)
    manifest_path = save_split_manifest(ds, data_dir, seed=seed, extra={"dataset": "glue/sst2"})

    q_train = dataset_quality_report(
        ds["train"],
        text_column=dataset_cfg["text_column"],
        label_column=dataset_cfg["label_column"],
    )
    q_val = dataset_quality_report(
        ds["validation"],
        text_column=dataset_cfg["text_column"],
        label_column=dataset_cfg["label_column"],
    )

    clf = build_pipeline(model_hf_id, task=model_cfg["task"])

    run_name = os.environ.get("PIPELINE_RUN_NAME", "eval-and-register")
    with mlflow.start_run(run_name=run_name) as run:
        mlflow.log_param("seed", seed)
        mlflow.log_param("model_hf_id", model_hf_id)
        mlflow.log_param("dataset", "glue/sst2")
        mlflow.log_param("task", model_cfg["task"])
        if max_train_i:
            mlflow.log_param("max_train_samples", max_train_i)

        # Artefatos de dados / qualidade
        mlflow.log_dict(meta, "artifacts/dataset_metadata.json")
        mlflow.log_dict(q_train, "artifacts/quality_train.json")
        mlflow.log_dict(q_val, "artifacts/quality_validation.json")
        mlflow.log_artifact(str(manifest_path), artifact_path="data")

        # Avaliação em validação (subconjunto opcional para demo rápida)
        eval_env = os.environ.get("EVAL_VALIDATION_MAX")
        val_split = ds["validation"]
        if eval_env:
            n = min(int(eval_env), val_split.num_rows)
            val_split = val_split.select(range(n))
            mlflow.log_param("eval_validation_max", n)

        metrics = evaluate_on_split(
            clf,
            val_split,
            text_column=dataset_cfg["text_column"],
            label_column=dataset_cfg["label_column"],
        )
        for k, v in metrics.items():
            mlflow.log_metric(k, v)

        # Matriz de confusão como artefato
        texts = [str(t) for t in val_split[dataset_cfg["text_column"]]]
        y_true = np.array(val_split[dataset_cfg["label_column"]])
        preds = []
        bs = 16
        for i in range(0, len(texts), bs):
            batch = texts[i : i + bs]
            out = clf(batch)
            if not isinstance(out, list):
                out = [out]
            from src.model.hf_predictor import _labels_from_outputs  # noqa: E402

            preds.extend(_labels_from_outputs(out))
        y_pred = np.array(preds[: len(y_true)])
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        cm_path = data_dir / "confusion_matrix.json"
        cm_path.write_text(json.dumps(cm.tolist()), encoding="utf-8")
        mlflow.log_artifact(str(cm_path), artifact_path="metrics")

        # Registro do modelo (flavor transformers)
        try:
            mlflow.transformers.log_model(
                transformers_model=clf,
                artifact_path="hf-model",
                task=model_cfg["task"],
            )
            model_uri = f"runs:/{run.info.run_id}/hf-model"
            reg_name = mlflow_cfg["registered_model_name"]
            mlflow.register_model(model_uri=model_uri, name=reg_name)
            print(f"Modelo registrado: {reg_name} @ {model_uri}")
        except Exception as e:
            print(f"Aviso: registro via transformers falhou ({e}); logando pipeline como artefato.")
            # Fallback: salvar ids no param
            mlflow.log_param("register_fallback", str(e))

        print("Run ID:", run.info.run_id)
        print("Métricas:", metrics)


if __name__ == "__main__":
    main()
