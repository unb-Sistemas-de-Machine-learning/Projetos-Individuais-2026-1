"""
Endpoint de inferência com guardrails e limitações explícitas.

Executar:
  uvicorn src.serve.app:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from transformers import pipeline

from src.guardrails.policy import GuardrailConfig, apply_confidence_guardrail, validate_inference_request

ROOT = Path(__file__).resolve().parents[2]


def _load_cfg() -> dict:
    with (ROOT / "config" / "config.yaml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)


cfg = _load_cfg()
model_cfg = cfg["model"]
gr_cfg_dict = cfg.get("guardrails", {})
guard = GuardrailConfig(
    min_chars=int(gr_cfg_dict.get("min_chars", 3)),
    max_chars=int(gr_cfg_dict.get("max_chars", 8000)),
    min_confidence=float(gr_cfg_dict.get("min_confidence", 0.55)),
)

_clf: Any = None


def get_classifier() -> Any:
    global _clf
    if _clf is None:
        model_id = os.environ.get("HF_MODEL_ID", model_cfg["hf_id"])
        _clf = pipeline(model_cfg["task"], model=model_id, tokenizer=model_id)
    return _clf


app = FastAPI(
    title="Inferência — sentimento (SST-2 / DistilBERT)",
    version="1.0.0",
    description=(
        "Classificação de sentimento em **inglês** com modelo pré-treinado. "
        "Não é sistema de saúde nem aconselhamento profissional. "
        "Resultados são probabilísticas e podem falhar fora do domínio do dataset."
    ),
)


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Texto de entrada em inglês.")


class PredictResponse(BaseModel):
    label: str | None = None
    score: float | None = None
    status: str
    disclaimer: str
    guardrail: dict[str, Any] | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(body: PredictRequest) -> PredictResponse:
    ok, code, meta = validate_inference_request(body.text, guard)
    disclaimer = (
        "Este serviço classifica sentimento positivo/negativo em textos curtos em inglês (estilo revisões). "
        "Não use para diagnóstico, jurídico ou decisões críticas. "
        "Confiança baixa é sinal de incerteza — não interprete como certeza absoluta."
    )

    if not ok:
        raise HTTPException(
            status_code=422,
            detail={
                "error": code,
                "meta": meta,
                "disclaimer": disclaimer,
            },
        )

    clf = get_classifier()
    out = clf(body.text.strip())
    if isinstance(out, list):
        out = out[0]
    score = float(out.get("score", 0.0))
    label = str(out.get("label", ""))

    conf_status, conf_meta = apply_confidence_guardrail(score, guard)
    if conf_status == "uncertain":
        return PredictResponse(
            label=None,
            score=score,
            status="uncertain",
            disclaimer=disclaimer,
            guardrail=conf_meta,
        )

    return PredictResponse(
        label=label,
        score=score,
        status="ok",
        disclaimer=disclaimer,
        guardrail=None,
    )


@app.get("/limitations")
def limitations() -> dict[str, Any]:
    return {
        "escopo": "Classificação binária de sentimento (positivo/negativo) em inglês.",
        "nao_faz": [
            "Diagnóstico médico ou triagem de saúde",
            "Detecção de toxicidade ou moderação em produção sem camadas adicionais",
            "Garantia de imparcialidade entre domínios (notícias, redes sociais, etc.)",
        ],
        "metricas_referencia": "Avaliadas em split de validação SST-2; performance pode cair fora desse domínio.",
    }
