"""Testes para filtros e datas da agenda."""

from __future__ import annotations

from datetime import date

from rag.filters import (
    dedupe_by_id,
    event_date_span,
    event_in_forward_window,
    parse_dt,
)


def test_parse_dt_datetime() -> None:
    d = parse_dt("2026-03-28 18:30:00")
    assert d is not None
    assert d.year == 2026 and d.month == 3 and d.day == 28


def test_parse_dt_date_only() -> None:
    d = parse_dt("2026-03-28")
    assert d is not None
    assert d.date() == date(2026, 3, 28)


def test_parse_dt_none_and_invalid() -> None:
    assert parse_dt(None) is None
    assert parse_dt("") is None
    assert parse_dt("invalid") is None


def test_event_date_span_start_end() -> None:
    a, b = event_date_span(
        {"start_date": "2026-03-01 10:00:00", "end_date": "2026-03-05 22:00:00"},
    )
    assert a == date(2026, 3, 1)
    assert b == date(2026, 3, 5)


def test_event_date_span_reversed_normalized() -> None:
    a, b = event_date_span(
        {"start_date": "2026-03-10 10:00:00", "end_date": "2026-03-01 22:00:00"},
    )
    assert a == date(2026, 3, 1)
    assert b == date(2026, 3, 10)


def test_event_date_span_agenda_date() -> None:
    a, b = event_date_span({"agenda_date": "2026-04-15"})
    assert a == b == date(2026, 4, 15)


def test_event_date_span_empty() -> None:
    assert event_date_span({}) == (None, None)


def test_event_in_forward_window() -> None:
    today = date(2026, 3, 28)
    ev = {"start_date": "2026-03-30 20:00:00", "end_date": "2026-03-30 23:00:00"}
    assert event_in_forward_window(ev, today, forward_days=14) is True


def test_event_in_forward_window_past() -> None:
    today = date(2026, 3, 28)
    ev = {"start_date": "2026-03-01 20:00:00", "end_date": "2026-03-01 23:00:00"}
    assert event_in_forward_window(ev, today, forward_days=14) is False


def test_event_in_forward_window_too_far() -> None:
    today = date(2026, 3, 28)
    ev = {"start_date": "2026-05-01 20:00:00", "end_date": "2026-05-01 23:00:00"}
    assert event_in_forward_window(ev, today, forward_days=14) is False


def test_dedupe_by_id_keeps_richer_row() -> None:
    rows = [
        {"id": 1, "title": "A"},
        {"id": 1, "title": "A", "extra": "more fields"},
    ]
    out = dedupe_by_id(rows)
    assert len(out) == 1
    assert "extra" in out[0]


def test_dedupe_by_id_skips_without_id() -> None:
    rows = [{"title": "x"}, {"id": 2, "title": "y"}]
    out = dedupe_by_id(rows)
    assert len(out) == 1
    assert out[0]["id"] == 2
