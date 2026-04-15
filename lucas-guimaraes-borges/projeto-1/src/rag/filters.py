from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from typing import Any


def parse_dt(value: str | None) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    s = value.strip()
    if len(s) >= 19 and s[10:11] == " ":
        try:
            return datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass
    if len(s) >= 10:
        try:
            return datetime.strptime(s[:10], "%Y-%m-%d")
        except ValueError:
            pass
    return None


def event_date_span(ev: dict[str, Any]) -> tuple[date | None, date | None]:
    end = parse_dt(ev.get("end_date"))
    start = parse_dt(ev.get("start_date"))
    if start is not None and end is not None:
        a, b = start.date(), end.date()
        return (a, b) if a <= b else (b, a)
    if start is not None:
        s = start.date()
        return s, s
    if end is not None:
        e = end.date()
        return e, e
    ad = ev.get("agenda_date")
    if isinstance(ad, str) and len(ad) >= 10:
        try:
            d = date.fromisoformat(ad[:10])
            return d, d
        except ValueError:
            pass
    return None, None


def event_in_forward_window(ev: dict[str, Any], today: date, forward_days: int) -> bool:
    span_start, span_end = event_date_span(ev)
    if span_start is None or span_end is None:
        return False
    window_end = today + timedelta(days=forward_days)
    return span_end >= today and span_start <= window_end


def dedupe_by_id(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for ev in rows:
        eid = ev.get("id")
        if eid is None:
            continue
        key = str(eid)
        cur = best.get(key)
        if cur is None or len(json.dumps(ev, ensure_ascii=False)) > len(json.dumps(cur, ensure_ascii=False)):
            best[key] = ev
    return list(best.values())
