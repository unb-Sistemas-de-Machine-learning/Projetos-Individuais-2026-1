"""Registro do modelo no MLflow Model Registry."""
from __future__ import annotations
import shutil
from pathlib import Path
from typing import Optional
import mlflow
from mlflow.models.signature import ModelSignature
from mlflow.types.schema import Schema, ColSpec
from .config import load_config, project_root
from .model import SkinCancerPyfunc, download_model


def _signature() -> ModelSignature:
    input_schema = Schema([
        ColSpec("string", "path"),
        ColSpec("string", "image_b64"),
    ])
    return ModelSignature(inputs=input_schema)


def run(config: Optional[dict] = None) -> str:
    cfg = config or load_config()
    mlflow.set_tracking_uri(cfg["mlflow"]["tracking_uri"])
    mlflow.set_experiment(cfg["mlflow"]["experiment_name"])

    model_dir = project_root() / cfg["model"]["local_dir"]
    if not any(model_dir.iterdir()) if model_dir.exists() else True:
        download_model(cfg)

    cfg_artifact = project_root() / "configs" / "config.yaml"
    artifacts = {
        "model_dir": str(model_dir),
        "config": str(cfg_artifact),
    }

    with mlflow.start_run(run_name="register-skin-cancer") as run:
        mlflow.log_params({
            "hf_model_id": cfg["model"]["hf_model_id"],
            "min_confidence": cfg["guardrails"]["min_confidence"],
            "skin_tone_ita_min": cfg["guardrails"]["skin_tone_ita_min"],
        })
        mlflow.pyfunc.log_model(
            artifact_path="model",
            python_model=SkinCancerPyfunc(),
            artifacts=artifacts,
            pip_requirements=str(project_root() / "requirements.txt"),
            signature=_signature(),
            registered_model_name=cfg["mlflow"]["registered_model_name"],
        )
        uri = f"runs:/{run.info.run_id}/model"
        print(f"Model logged at {uri}")
        return uri


if __name__ == "__main__":
    run()
