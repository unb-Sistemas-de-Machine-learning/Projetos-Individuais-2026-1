from __future__ import annotations

from pathlib import Path

_PKG = Path(__file__).resolve().parent.parent


def package_root() -> Path:
    return _PKG


def project_root() -> Path:
    return _PKG.parent


def env_file() -> Path:
    return project_root() / ".env"


def default_events_json() -> Path:
    return project_root() / "events.json"


def agent_system_prompt_path() -> Path:
    return _PKG / "agent" / "prompts" / "event_agent_system.md"


def chat_memory_path() -> Path:
    return project_root() / "chat_memory.json"
