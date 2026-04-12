"""Testes para persistência de conversa em JSON."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from agent import memory as mem


def test_load_turns_missing_file(tmp_path: Path) -> None:
    assert mem.load_turns(tmp_path / "nope.json") == []


def test_load_turns_invalid_json(tmp_path: Path) -> None:
    p = tmp_path / "bad.json"
    p.write_text("not json {{{", encoding="utf-8")
    assert mem.load_turns(p) == []


def test_save_load_roundtrip(tmp_path: Path) -> None:
    p = tmp_path / "m.json"
    turns = [{"user": "olá", "assistant": "oi"}]
    mem.save_turns(p, turns)
    assert mem.load_turns(p) == turns
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["schema_version"] == mem.SCHEMA_VERSION
    assert "updated_at" in data
    assert isinstance(data["turns"], list)


def test_load_turns_skips_bad_items(tmp_path: Path) -> None:
    p = tmp_path / "m.json"
    p.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "turns": [
                    {"user": "a", "assistant": "b"},
                    {"user": 1, "assistant": "x"},
                    "não é dict",
                    {"user": "c", "assistant": "d"},
                ],
            },
        ),
        encoding="utf-8",
    )
    assert mem.load_turns(p) == [
        {"user": "a", "assistant": "b"},
        {"user": "c", "assistant": "d"},
    ]


def test_turns_to_messages() -> None:
    msgs = mem.turns_to_messages([{"user": "q", "assistant": "a"}])
    assert len(msgs) == 2
    assert isinstance(msgs[0], HumanMessage)
    assert msgs[0].content == "q"
    assert isinstance(msgs[1], AIMessage)
    assert msgs[1].content == "a"


def test_append_turn_and_save(tmp_path: Path) -> None:
    p = tmp_path / "m.json"
    turns: list[dict[str, str]] = []
    mem.append_turn_and_save(p, turns, "u1", "a1")
    assert turns == [{"user": "u1", "assistant": "a1"}]
    mem.append_turn_and_save(p, turns, "u2", "a2")
    assert mem.load_turns(p) == [
        {"user": "u1", "assistant": "a1"},
        {"user": "u2", "assistant": "a2"},
    ]


def test_memory_enabled_respects_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CHAT_MEMORY_DISABLE", raising=False)
    assert mem.memory_enabled() is True
    monkeypatch.setenv("CHAT_MEMORY_DISABLE", "1")
    assert mem.memory_enabled() is False
    monkeypatch.setenv("CHAT_MEMORY_DISABLE", "true")
    assert mem.memory_enabled() is False


def test_memory_file_path_custom(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    custom = tmp_path / "custom.json"
    monkeypatch.setenv("CHAT_MEMORY_PATH", str(custom))
    assert mem.memory_file_path() == custom.resolve()
