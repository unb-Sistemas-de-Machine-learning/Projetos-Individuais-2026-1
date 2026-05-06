"""Loop de conversação (LangChain) + consulta Pinecone."""

from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from openai import OpenAI
from pinecone import Pinecone
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from zoneinfo import ZoneInfo

from agent.chat_models import build_chat_llm, chat_llm_label
from agent.memory import (
    append_turn_and_save,
    load_turns,
    memory_enabled,
    memory_file_path,
    turns_to_messages,
)
from utils.paths import agent_system_prompt_path, env_file

EMBED_MODEL = "text-embedding-3-small"
EMBED_DIMS = 512
TOP_K = 15

_MES = (
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
)
_DIAS = (
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
)


def load_system_prompt(tz_name: str, prompt_path: Any = None) -> str:
    path = prompt_path or agent_system_prompt_path()
    raw = path.read_text(encoding="utf-8")
    tz = ZoneInfo(tz_name)
    now = datetime.now(tz)
    d = now.date()
    human = f"{_DIAS[d.weekday()]}, {d.day} de {_MES[d.month - 1]} de {d.year}"
    current = (
        f"{d.isoformat()} — {human} ({tz_name}); "
        f"horário local {now.strftime('%H:%M')}"
    )
    return raw.replace("{{CURRENT_DATE}}", current)


def embed_query(client: OpenAI, text: str) -> list[float]:
    r = client.embeddings.create(
        model=EMBED_MODEL,
        input=text[:8000],
        dimensions=EMBED_DIMS,
    )
    return r.data[0].embedding


def _meta_line(label: str, value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    return f"{label}: {value}"


def _hit_parts(hit: Any) -> tuple[dict[str, Any], float]:
    if isinstance(hit, dict):
        return dict(hit.get("metadata") or {}), float(hit.get("score") or 0.0)
    md = getattr(hit, "metadata", None) or {}
    if not isinstance(md, dict):
        md = dict(md)
    return md, float(getattr(hit, "score", 0.0))


def format_match(rank: int, hit: Any) -> str:
    m, score = _hit_parts(hit)
    lines = [
        f"### Trecho {rank} (relevância ~ {score:.4f})",
    ]
    for label, key in (
        ("ID", "event_id"),
        ("Título", "title"),
        ("Tipo", "type"),
        ("Local", "location"),
        ("Endereço", "address"),
        ("Classificação etária", "age_range"),
        ("Gratuito (metadado)", "gratuito"),
        ("Início", "start_date"),
        ("Fim", "end_date"),
        ("Data na agenda", "agenda_date"),
        ("Link de compra", "purchase_link"),
    ):
        s = _meta_line(label, m.get(key))
        if s:
            lines.append(f"- {s}")
    return "\n".join(lines)


def retrieve_context(openai_client: OpenAI, index: Any, query: str) -> str:
    vec = embed_query(openai_client, query)
    res = index.query(vector=vec, top_k=TOP_K, include_metadata=True)
    if isinstance(res, dict):
        matches = res.get("matches") or []
    else:
        matches = list(getattr(res, "matches", None) or [])
    if not matches:
        return (
            "(Nenhum trecho foi encontrado na base para esta consulta. "
            "Informe o usuário com clareza e sugira reformular ou ampliar o pedido.)"
        )
    parts = [format_match(i + 1, m) for i, m in enumerate(matches)]
    return "\n\n".join(parts)


def _message_text(msg: BaseMessage) -> str:
    c = msg.content
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        parts: list[str] = []
        for block in c:
            if isinstance(block, dict) and "text" in block:
                parts.append(str(block["text"]))
            else:
                parts.append(str(block))
        return "".join(parts)
    return str(c)


def run() -> None:
    load_dotenv(env_file())
    console = Console(highlight=True)

    openai_key = os.environ.get("OPENAI_API_KEY")
    pinecone_key = os.environ.get("PINECONE_API_KEY")
    index_name = os.environ.get("PINECONE_INDEX", "events")
    tz_name = os.environ.get("EVENTS_TZ", "America/Sao_Paulo")

    if not openai_key:
        sys.exit("Defina OPENAI_API_KEY no .env (embeddings para o Pinecone).")
    if not pinecone_key:
        sys.exit("Defina PINECONE_API_KEY no .env")

    prompt_path = agent_system_prompt_path()
    if not prompt_path.is_file():
        sys.exit(f"Falta o ficheiro de system prompt: {prompt_path}")

    system_instruction = load_system_prompt(tz_name, prompt_path)
    llm = build_chat_llm()
    llm_desc = chat_llm_label(llm)

    oai = OpenAI(api_key=openai_key)
    pc = Pinecone(api_key=pinecone_key)
    index = pc.Index(index_name)

    mem_on = memory_enabled()
    mem_path = memory_file_path() if mem_on else None
    turns: list[dict[str, str]] = load_turns(mem_path) if mem_path else []
    messages: list[BaseMessage] = [SystemMessage(content=system_instruction)]
    messages.extend(turns_to_messages(turns))

    mem_hint = ""
    if mem_on and mem_path is not None:
        mem_hint = (
            f"\n[dim]Memória em JSON:[/] [cyan]{mem_path.name}[/]"
            f" ({len(turns)} turno(s); [bold]CHAT_MEMORY_DISABLE=1[/] para desligar)"
        )
        if turns:
            mem_hint += f"\n[dim]Histórico anterior restaurado:[/] {len(turns)} pergunta(s)."

    console.print()
    console.print(
        Panel.fit(
            "[bold green]Agente de eventos culturais — Distrito Federal (DF)[/]\n"
            f"[dim]LLM:[/] [cyan]{llm_desc}[/]\n"
            "[dim]Somente agenda no DF; dados vindos do Pinecone.[/]\n"
            "Comandos: [bold]sair[/], [bold]exit[/], [bold]fim[/] ou Ctrl+C."
            f"{mem_hint}",
            title="Agenda Cultural DF",
            border_style="green",
        ),
    )
    console.print()

    while True:
        try:
            user = console.input("[bold yellow]Você ▸ [/bold yellow]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Encerrando. Até logo.[/]")
            break

        if not user:
            continue
        if user.lower() in {"sair", "exit", "quit", "fim"}:
            console.print("[dim]Até logo.[/]")
            break

        try:
            context = retrieve_context(oai, index, user)
            prompt = (
                "Trechos recuperados da agenda cultural do Distrito Federal (DF) "
                "(use somente estes dados para fatos sobre eventos):\n\n"
                f"{context}\n\n"
                "---\n"
                f"Pergunta do usuário:\n{user}"
            )
            messages.append(HumanMessage(content=prompt))
            with console.status("[bold cyan]Digitando a resposta…[/]"):
                reply = llm.invoke(messages)
            text = _message_text(reply) if isinstance(reply, BaseMessage) else str(reply)
            if not text.strip():
                text = "(Resposta vazia.)"
            messages.append(AIMessage(content=text))
            if mem_on and mem_path is not None:
                append_turn_and_save(mem_path, turns, user, text)
        except Exception as e:
            console.print(f"[bold red]Erro:[/] {e}")
            if messages and isinstance(messages[-1], HumanMessage):
                messages.pop()
            continue

        console.print()
        console.rule("[bold cyan]Assistente[/]", style="cyan")
        console.print(Markdown(text))
        console.rule(style="dim")
        console.print()
