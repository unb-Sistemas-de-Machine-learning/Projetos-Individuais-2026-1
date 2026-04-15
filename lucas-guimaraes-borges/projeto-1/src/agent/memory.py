"""Persistência simples do histórico (usuário ↔ assistente) em JSON."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from utils.paths import chat_memory_path

SCHEMA_VERSION = 1


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def memory_enabled() -> bool:
    return not _truthy("CHAT_MEMORY_DISABLE")


def memory_file_path() -> Path:
    raw = os.environ.get("CHAT_MEMORY_PATH", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return chat_memory_path()


def load_turns(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(raw, dict):
        return []
    turns = raw.get("turns")
    if not isinstance(turns, list):
        return []
    out: list[dict[str, str]] = []
    for item in turns:
        if not isinstance(item, dict):
            continue
        u = item.get("user")
        a = item.get("assistant")
        if isinstance(u, str) and isinstance(a, str):
            out.append({"user": u, "assistant": a})
    return out


def turns_to_messages(turns: list[dict[str, str]]) -> list[BaseMessage]:
    msgs: list[BaseMessage] = []
    for t in turns:
        msgs.append(HumanMessage(content=t["user"]))
        msgs.append(AIMessage(content=t["assistant"]))
    return msgs


def save_turns(path: Path, turns: list[dict[str, str]]) -> None:
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "turns": turns,
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        dir=path.parent,
        prefix=".chat_memory_",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def append_turn_and_save(path: Path, turns: list[dict[str, str]], user: str, assistant: str) -> None:
    turns.append({"user": user, "assistant": assistant})
    save_turns(path, turns)
