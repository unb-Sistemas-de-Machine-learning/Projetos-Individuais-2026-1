"""Fábrica de modelos de chat (LangChain) — troca de provedor via ambiente."""

from __future__ import annotations

import os
import sys

from langchain_core.language_models.chat_models import BaseChatModel


def _float_env(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, str(default)))
    except ValueError:
        return default


DEFAULT_OPENAI_AGENT_MODEL = "gpt-5-nano"


def build_chat_llm() -> BaseChatModel:
    """
    Provedor em AGENT_LLM_PROVIDER:
      - openai (default): OPENAI_API_KEY; OPENAI_AGENT_MODEL (default: gpt-5-nano)
    """
    provider = os.environ.get("AGENT_LLM_PROVIDER", "openai").strip().lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        if not os.environ.get("OPENAI_API_KEY"):
            sys.exit("AGENT_LLM_PROVIDER=openai requer OPENAI_API_KEY no .env")
        model_name = os.environ.get("OPENAI_AGENT_MODEL", DEFAULT_OPENAI_AGENT_MODEL)
        # GPT-5: API costuma fixar temperature=1; outros modelos usam 0.3 por omissão.
        if os.environ.get("OPENAI_AGENT_TEMPERATURE", "").strip() != "":
            temperature = _float_env("OPENAI_AGENT_TEMPERATURE", 1.0)
        elif model_name.lower().startswith("gpt-5"):
            temperature = 1.0
        else:
            temperature = 0.3
        return ChatOpenAI(model=model_name, temperature=temperature)

    sys.exit(
        f"AGENT_LLM_PROVIDER desconhecido: {provider!r}. Use: openai",
    )


def chat_llm_label(llm: BaseChatModel) -> str:
    """Nome curto para exibir no terminal."""
    model = getattr(llm, "model_name", None) or getattr(llm, "model", None)
    provider = os.environ.get("AGENT_LLM_PROVIDER", "openai").strip().lower()
    return f"{provider} / {model or type(llm).__name__}"
