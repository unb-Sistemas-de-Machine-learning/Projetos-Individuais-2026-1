"""FastAPI app for guarded IMDb sentiment inference."""

from __future__ import annotations

import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import mlflow.pyfunc
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from transformers import AutoTokenizer

from src.data.preprocess import clean_text
from src.guardrails import GuardrailViolation, validate_review
from src.model.loader import MODEL_NAME

DEFAULT_MODEL_URI = "models:/sentiment-imdb/1"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_URI = os.getenv("SENTIMENT_MODEL_URI", DEFAULT_MODEL_URI)
TOKENIZER_NAME = os.getenv("SENTIMENT_TOKENIZER_NAME", "")
TOKENIZER_LOCAL_ONLY = os.getenv("SENTIMENT_TOKENIZER_LOCAL_ONLY", "1") != "0"
MODEL_LOAD_RETRIES = int(os.getenv("SENTIMENT_MODEL_LOAD_RETRIES", "10"))
MODEL_LOAD_RETRY_SECONDS = float(os.getenv("SENTIMENT_MODEL_LOAD_RETRY_SECONDS", "3"))
DISCLAIMER = (
    "This prediction is for English movie-review sentiment only. "
    "The model supports only positive and negative labels."
)


class PredictRequest(BaseModel):
    text: str = Field(...)


class PredictResponse(BaseModel):
    label: str
    confidence: float
    disclaimer: str


class HealthResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    status: str
    model_uri: str
    tokenizer_name: str
    model_loaded: bool
    model_load_error: str | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model_uri = MODEL_URI
    app.state.tokenizer_name = _resolve_tokenizer_name()
    app.state.model = None
    app.state.model_load_error = None
    app.state.tokenizer = AutoTokenizer.from_pretrained(
        app.state.tokenizer_name,
        local_files_only=TOKENIZER_LOCAL_ONLY,
    )
    yield


app = FastAPI(
    title="IMDb Sentiment API",
    description="Guarded FastAPI endpoint for the MLflow IMDb sentiment model.",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    return HealthResponse(
        status="ok",
        model_uri=request.app.state.model_uri,
        tokenizer_name=request.app.state.tokenizer_name,
        model_loaded=request.app.state.model is not None,
        model_load_error=request.app.state.model_load_error,
    )


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest, request: Request) -> PredictResponse:
    text = clean_text(payload.text)

    try:
        validate_review(text, tokenizer=request.app.state.tokenizer)
    except GuardrailViolation as exc:
        raise HTTPException(
            status_code=422,
            detail={"code": exc.code, "message": exc.message},
        ) from exc

    model = _get_or_load_model(request)
    raw_prediction = model.predict([text])
    prediction = _first_prediction(raw_prediction)

    return PredictResponse(
        label=str(prediction["label"]),
        confidence=float(prediction["score"]),
        disclaimer=DISCLAIMER,
    )


def _get_or_load_model(request: Request):
    if request.app.state.model is not None:
        return request.app.state.model

    try:
        request.app.state.model = _load_model(request.app.state.model_uri)
        request.app.state.model_load_error = None
        return request.app.state.model
    except RuntimeError as exc:
        request.app.state.model_load_error = str(exc)
        raise HTTPException(
            status_code=503,
            detail={
                "code": "model_unavailable",
                "message": (
                    "The sentiment model is not available. Register "
                    "'sentiment-imdb' in MLflow or set SENTIMENT_MODEL_URI."
                ),
            },
        ) from exc


def _load_model(model_uri: str):
    last_error: Exception | None = None

    for attempt in range(1, MODEL_LOAD_RETRIES + 1):
        try:
            return mlflow.pyfunc.load_model(model_uri)
        except Exception as exc:
            last_error = exc
            if attempt < MODEL_LOAD_RETRIES:
                time.sleep(MODEL_LOAD_RETRY_SECONDS)

    raise RuntimeError(
        "Could not load the MLflow sentiment model. "
        f"Tried model URI '{model_uri}'. Set SENTIMENT_MODEL_URI or "
        "MLFLOW_TRACKING_URI if the registered model is stored elsewhere."
    ) from last_error


def _resolve_tokenizer_name() -> str:
    if TOKENIZER_NAME:
        return TOKENIZER_NAME

    tokenizer_dirs = sorted(
        path.parent
        for path in (PROJECT_ROOT / "mlruns").glob(
            "*/models/*/artifacts/components/tokenizer/tokenizer.json"
        )
    )

    if tokenizer_dirs:
        return str(tokenizer_dirs[0])

    return MODEL_NAME


def _first_prediction(raw_prediction: Any) -> dict[str, Any]:
    """Normalize common MLflow pyfunc output shapes to one prediction dict."""
    if isinstance(raw_prediction, pd.DataFrame):
        return raw_prediction.iloc[0].to_dict()

    if isinstance(raw_prediction, pd.Series):
        first = raw_prediction.iloc[0]
        return _coerce_prediction(first)

    if isinstance(raw_prediction, list):
        return _coerce_prediction(raw_prediction[0])

    if hasattr(raw_prediction, "tolist"):
        values = raw_prediction.tolist()
        if values:
            return _coerce_prediction(values[0])

    return _coerce_prediction(raw_prediction)


def _coerce_prediction(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    if isinstance(value, pd.Series):
        return value.to_dict()

    raise TypeError(f"Unexpected model prediction shape: {type(value).__name__}")
