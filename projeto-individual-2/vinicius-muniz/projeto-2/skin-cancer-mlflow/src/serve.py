"""Endpoint FastAPI para inferência com guardrails."""
from __future__ import annotations
import base64
import io
import logging
import os
from pathlib import Path
from typing import Optional
import mlflow
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image
from .config import load_config, project_root
from .guardrails import validate_file

logger = logging.getLogger("skin-cancer-serve")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def _load_model(cfg: dict):
    mlflow.set_tracking_uri(cfg["mlflow"]["tracking_uri"])
    name = cfg["mlflow"]["registered_model_name"]
    stage = os.environ.get("MODEL_STAGE", "None")
    version = os.environ.get("MODEL_VERSION")
    if version:
        uri = f"models:/{name}/{version}"
    elif stage and stage != "None":
        uri = f"models:/{name}/{stage}"
    else:
        uri = f"models:/{name}/latest"
    logger.info("Loading model from %s", uri)
    return mlflow.pyfunc.load_model(uri)


cfg = load_config()
app = FastAPI(title="Skin Cancer Detection", version="0.1.0")
model = None


@app.on_event("startup")
def startup():
    global model
    try:
        model = _load_model(cfg)
    except Exception as e:
        logger.warning("Registry load failed (%s); fallback to local pyfunc.", e)
        from .model import SkinCancerPyfunc
        m = SkinCancerPyfunc()
        class _Ctx:
            artifacts = {
                "model_dir": str(project_root() / cfg["model"]["local_dir"]),
                "config": str(project_root() / "configs" / "config.yaml"),
            }
        m.load_context(_Ctx())
        model = m


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.get("/meta")
def meta():
    return {
        "model_id": cfg["model"]["hf_model_id"],
        "labels": cfg["model"]["labels"],
        "guardrails": cfg["guardrails"],
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(503, "Modelo indisponível.")
    content = await file.read()
    if len(content) > cfg["guardrails"]["max_image_mb"] * 1024 * 1024:
        raise HTTPException(413, "Arquivo excede limite.")
    ext = Path(file.filename).suffix.lower().lstrip(".")
    if ext not in cfg["guardrails"]["allowed_formats"]:
        raise HTTPException(415, f"Formato {ext} não suportado.")
    try:
        Image.open(io.BytesIO(content)).verify()
    except Exception:
        raise HTTPException(400, "Imagem inválida.")
    b64 = base64.b64encode(content).decode()
    df = pd.DataFrame([{"path": "", "image_b64": b64}])
    try:
        result = model.predict(df)
    except Exception as e:
        logger.exception("Inference error")
        raise HTTPException(500, f"Erro: {e}")
    logger.info("predict result=%s", result[0].get("decision"))
    return result[0]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=cfg["inference"]["host"], port=cfg["inference"]["port"])
