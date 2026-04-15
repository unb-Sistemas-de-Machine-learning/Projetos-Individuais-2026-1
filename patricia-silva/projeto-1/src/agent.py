"""Chamadas ao LLM com saída JSON validada (explicabilidade estruturada)."""

from __future__ import annotations

import json
import re
from typing import Any

import httpx
from google import genai
from google.genai import types
from google.genai.errors import ClientError

from . import config
from .schemas import AgenteSaida

# Ordem: preferência do .env, depois IDs comuns na API Gemini (v1beta).
_GEMINI_FALLBACK_MODELS = (
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-1.5-flash-8b",
)


def _gemini_model_candidates() -> list[str]:
    preferred = config.GEMINI_MODEL.strip()
    out: list[str] = []
    seen: set[str] = set()
    for m in (preferred, *_GEMINI_FALLBACK_MODELS):
        if m and m not in seen:
            seen.add(m)
            out.append(m)
    return out


SYSTEM_PROMPT = """Você é um agente educacional. Sua função é RECOMENDAR trilhas e ações de estudo
com base no perfil do aluno. Restrição obrigatória: EXPLICABILIDADE — cada recomendação deve ter
justificativa clara ligada ao objetivo, nível e tempo informados.

Use o contexto recuperado da base de conhecimento quando relevante; você pode complementar com
conhecimento geral, mas deixe explícito quando uma ideia vem só do senso comum.

Responda APENAS com um objeto JSON válido no schema:
{
  "resumo_perfil": string,
  "recomendacoes": [
    {
      "titulo": string,
      "tipo": string,
      "descricao": string,
      "justificativa": string (obrigatória, >= 20 caracteres),
      "passos": [string, ...]
    }
  ],
  "avisos_ou_limitacoes": [string]
}

Entre 2 e 6 recomendações. Cada justificativa deve mencionar pelo menos um elemento do pedido do usuário
(objetivo, nível, tempo ou restrição)."""


def _parse_json_loose(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        return json.loads(m.group())
    raise ValueError("Resposta do modelo não é JSON válido")


def _gemini_complete(user_prompt: str) -> str:
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    cfg = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.35,
        response_mime_type="application/json",
    )
    last_err: Exception | None = None
    for model_id in _gemini_model_candidates():
        try:
            response = client.models.generate_content(
                model=model_id,
                contents=user_prompt,
                config=cfg,
            )
            text = response.text
            if not text:
                raise RuntimeError("Gemini: texto de resposta vazio.")
            return text
        except ClientError as e:
            last_err = e
            # 404 = nome de modelo inválido; tenta o próximo. 429 = quota: não insistir.
            if e.code == 404:
                continue
            raise
    raise RuntimeError(
        "Nenhum modelo Gemini da lista funcionou. Último erro: "
        f"{last_err!s}. Ajuste GEMINI_MODEL ou use o AI Studio → ListModels."
    ) from last_err


def _ollama_complete(user_prompt: str) -> str:
    url = f"{config.OLLAMA_HOST}/api/chat"
    body = {
        "model": config.OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "options": {"temperature": 0.35},
    }
    with httpx.Client(timeout=120.0) as client:
        r = client.post(url, json=body)
        r.raise_for_status()
        data = r.json()
    return (data.get("message") or {}).get("content") or ""


def gerar_plano(user_prompt: str, max_retries: int = 2) -> AgenteSaida:
    last_err: Exception | None = None
    attempt_prompt = user_prompt
    for _ in range(max_retries):
        try:
            if config.GEMINI_API_KEY:
                raw = _gemini_complete(attempt_prompt)
            else:
                raw = _ollama_complete(attempt_prompt)
            data = _parse_json_loose(raw)
            return AgenteSaida.model_validate(data)
        except Exception as e:
            last_err = e
            attempt_prompt = (
                user_prompt
                + "\n\nCorrija a saída anterior. Erro de validação: "
                + str(e)[:500]
            )
    raise RuntimeError(f"Falha ao obter JSON válido do LLM: {last_err}") from last_err
