from datetime import datetime, timezone
import logging
import time

import mlflow
import mlflow.pyfunc
import pandas as pd
from fastapi import Body, FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.config import (
    CONTENT_COLUMN,
    MLFLOW_EXPERIMENT_SERVING,
    MLFLOW_TRACKING_URI,
    SERVING_MODEL_FALLBACK_TO_HF,
    SERVING_MODEL_URI,
    SPAM_THRESHOLD,
)
from src.model.classifier import PretrainedSpamModel
from src.preprocessing.guardrails import validate_comment

logger = logging.getLogger(__name__)


class PredictionRequest(BaseModel):
    content: str = Field(..., min_length=1, description="Comentario do YouTube")


class PredictionResponse(BaseModel):
    allowed: bool
    guardrail_reason: str
    prediction: str
    spam_probability: float


app = FastAPI(title="YouTube Spam Classifier API", version="1.0.0")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(MLFLOW_EXPERIMENT_SERVING)

class MlflowModelAdapter:
    def __init__(self, pyfunc_model):
        self.pyfunc_model = pyfunc_model

    def predict_proba(self, texts):
        model_input = pd.DataFrame({CONTENT_COLUMN: list(texts)})
        predictions = self.pyfunc_model.predict(model_input)
        return predictions["spam_probability"].astype(float).tolist()


def _load_serving_model():
    if SERVING_MODEL_URI:
        try:
            loaded_model = mlflow.pyfunc.load_model(SERVING_MODEL_URI)
            logger.info("Modelo de serving carregado do registry: %s", SERVING_MODEL_URI)
            return MlflowModelAdapter(loaded_model), "mlflow_registry", SERVING_MODEL_URI
        except Exception as exc:
            logger.warning("Falha ao carregar modelo do registry (%s): %s", SERVING_MODEL_URI, exc)
            if not SERVING_MODEL_FALLBACK_TO_HF:
                raise

    model = PretrainedSpamModel()
    logger.info("Modelo de serving carregado do Hugging Face")
    return model, "huggingface_fallback", "hf-default"


MODEL, MODEL_SOURCE, MODEL_REF = _load_serving_model()


@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/predict", response_model=PredictionResponse)
def predict(request=Body(...)):
    if isinstance(request, dict):
        content = request.get("content") or request.get("text")
    else:
        content = getattr(request, "content", None) or getattr(request, "text", None)

    if not isinstance(content, str) or not content.strip():
        raise HTTPException(status_code=422, detail="Envie JSON com 'content' ou 'text' não vazio")

    request_start = time.perf_counter()
    guardrail = validate_comment(content)
    if not guardrail.allowed:
        latency_ms = (time.perf_counter() - request_start) * 1000.0
        with mlflow.start_run(run_name="inference_guardrail"):
            mlflow.log_param("allowed", False)
            mlflow.log_param("reason", guardrail.reason)
            mlflow.log_param("model_source", MODEL_SOURCE)
            mlflow.log_param("model_ref", MODEL_REF)
            mlflow.log_metric("latency_ms", float(latency_ms))
        return PredictionResponse(
            allowed=False,
            guardrail_reason=guardrail.reason,
            prediction="rejected",
            spam_probability=0.0,
        )

    try:
        score = MODEL.predict_proba([content])[0]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Falha na inferencia: {exc}") from exc

    prediction = "spam" if score >= SPAM_THRESHOLD else "ham"
    latency_ms = (time.perf_counter() - request_start) * 1000.0

    with mlflow.start_run(run_name="inference_request"):
        mlflow.log_param("allowed", True)
        mlflow.log_param("prediction", prediction)
        mlflow.log_param("model_source", MODEL_SOURCE)
        mlflow.log_param("model_ref", MODEL_REF)
        mlflow.log_metric("spam_probability", float(score))
        mlflow.log_metric("latency_ms", float(latency_ms))

    return PredictionResponse(
        allowed=True,
        guardrail_reason="ok",
        prediction=prediction,
        spam_probability=float(score),
    )


@app.post("/predict-batch")
def predict_batch(payload=Body(...)):
    request_start = time.perf_counter()
    if not isinstance(payload, list) or not payload:
        raise HTTPException(status_code=400, detail="Lista vazia")

    rows = []
    for idx, item in enumerate(payload):
        if isinstance(item, dict):
            content = item.get("content") or item.get("text")
        else:
            content = getattr(item, "content", None) or getattr(item, "text", None)

        if not isinstance(content, str) or not content.strip():
            raise HTTPException(
                status_code=422,
                detail=f"Item {idx} inválido: envie 'content' ou 'text' não vazio",
            )

        guardrail = validate_comment(content)
        if guardrail.allowed:
            score = MODEL.predict_proba([content])[0]
            prediction = "spam" if score >= SPAM_THRESHOLD else "ham"
        else:
            score = 0.0
            prediction = "rejected"

        rows.append(
            {
                "content": content,
                "allowed": guardrail.allowed,
                "guardrail_reason": guardrail.reason,
                "spam_probability": float(score),
                "prediction": prediction,
            }
        )

    output_df = pd.DataFrame(rows)
    latency_ms = (time.perf_counter() - request_start) * 1000.0
    accepted = float(output_df["allowed"].sum())
    rejected = float((~output_df["allowed"]).sum())
    batch_size = float(len(output_df))
    with mlflow.start_run(run_name="inference_batch"):
        mlflow.log_param("model_source", MODEL_SOURCE)
        mlflow.log_param("model_ref", MODEL_REF)
        mlflow.log_metric("batch_size", batch_size)
        mlflow.log_metric("accepted", accepted)
        mlflow.log_metric("rejected", rejected)
        mlflow.log_metric("accepted_ratio", accepted / batch_size)
        mlflow.log_metric("rejected_ratio", rejected / batch_size)
        mlflow.log_metric("avg_spam_probability", float(output_df["spam_probability"].mean()))
        mlflow.log_metric("latency_ms", float(latency_ms))

    return output_df.to_dict(orient="records")

