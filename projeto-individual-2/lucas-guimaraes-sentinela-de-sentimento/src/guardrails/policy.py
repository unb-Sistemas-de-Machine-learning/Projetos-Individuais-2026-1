"""
Guardrails: evitar uso fora de escopo, baixa confiança sem aviso e respostas enganosas.

Escopo declarado: texto em inglês, análise de sentimento de frases curtas (estilo SST-2).
Não é diagnóstico médico nem sistema de saúde — limitações explícitas na API.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class GuardrailConfig:
    min_chars: int = 3
    max_chars: int = 8000
    min_confidence: float = 0.55


def _mostly_latin_ascii(text: str) -> bool:
    """Heurística leve: SST-2 é inglês; recusa texto claramente fora (ex.: só símbolos)."""
    letters = sum(1 for c in text if c.isalpha())
    return letters >= max(2, len(text) // 12)


def validate_inference_request(text: str, cfg: GuardrailConfig) -> tuple[bool, str | None, dict[str, Any]]:
    """
    Retorna (ok, código_erro, meta). Se não ok, a inferência não deve prosseguir sem aviso.
    """
    t = text.strip()
    if not t:
        return False, "empty_text", {}
    if len(t) < cfg.min_chars:
        return False, "text_too_short", {"min_chars": cfg.min_chars}
    if len(t) > cfg.max_chars:
        return False, "text_too_long", {"max_chars": cfg.max_chars}
    if not _mostly_latin_ascii(t):
        return False, "likely_out_of_scope_language_or_noise", {}
    # Recusa padrões óbvios de prompt injection / tarefa fora do escopo
    if re.search(r"\bignore (all|previous) instructions\b", t, re.I):
        return False, "policy_blocked_pattern", {}
    return True, None, {}


def apply_confidence_guardrail(
    score: float,
    cfg: GuardrailConfig,
) -> tuple[str, dict[str, Any]]:
    """
    Evita falsa confiança: abaixo do limiar, retorna resposta 'uncertain' com disclaimer.
    """
    if score < cfg.min_confidence:
        return "uncertain", {
            "reason": "low_confidence",
            "min_confidence": cfg.min_confidence,
            "score": score,
        }
    return "ok", {}
