"""Testes para funções puras do runner (prompt e formatação RAG)."""

from __future__ import annotations

from pathlib import Path

from agent.runner import format_match, load_system_prompt


def test_load_system_prompt_substitutes_date(tmp_path: Path) -> None:
    p = tmp_path / "sys.md"
    p.write_text("Data: {{CURRENT_DATE}}", encoding="utf-8")
    out = load_system_prompt("UTC", prompt_path=p)
    assert "{{CURRENT_DATE}}" not in out
    assert "Data:" in out
    assert "UTC" in out


def test_format_match_dict_hit() -> None:
    hit = {
        "score": 0.9123,
        "metadata": {
            "event_id": "42",
            "title": "Show",
            "type": "Música",
            "location": "Brasília",
        },
    }
    text = format_match(1, hit)
    assert "Trecho 1" in text
    assert "0.9123" in text
    assert "Show" in text
    assert "Música" in text
    assert "Brasília" in text
