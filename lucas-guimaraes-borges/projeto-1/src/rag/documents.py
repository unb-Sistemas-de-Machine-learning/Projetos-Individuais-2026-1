from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import tiktoken

EMBED_MODEL = "text-embedding-3-small"
EMBED_DIMS = 512
MAX_EMBED_TOKENS = 8000

_enc: tiktoken.Encoding | None = None


def has_purchase_link(ev: dict[str, Any]) -> bool:
    link = ev.get("purchase_link")
    if link is None or link is False:
        return False
    return isinstance(link, str) and bool(link.strip())


def ingressos_text(ev: dict[str, Any]) -> str:
    if not has_purchase_link(ev):
        parts = ["Ingressos: evento gratuito (sem link de compra de ingressos)."]
        ft = ev.get("free_type")
        if isinstance(ft, str) and ft.strip():
            parts.append(f"Observação: {ft.strip()}.")
        return " ".join(parts)
    return f"Ingressos: pagos. Link para compra: {ev.get('purchase_link')}"


def event_to_text(ev: dict[str, Any]) -> str:
    addr = ev.get("address")
    address_s = addr.strip() if isinstance(addr, str) else ("" if addr in (None, False) else str(addr))
    ar = ev.get("age_range")
    age_s = ar.strip() if isinstance(ar, str) else ("" if ar in (None, False) else str(ar))

    lines = [
        f"Título: {ev.get('title', '')}",
        f"Tipo: {ev.get('type', '')}",
        f"Descrição: {ev.get('description', '')}",
        f"Local: {ev.get('location', '')}",
        f"Endereço: {address_s}",
        f"Faixa etária / classificação: {age_s}",
        f"Início: {ev.get('start_date', '')}",
        f"Fim: {ev.get('end_date', '')}",
        f"Data na agenda: {ev.get('agenda_date', '')}",
        ingressos_text(ev),
    ]
    return "\n".join(lines)


def truncate_for_embedding(text: str, max_tokens: int = MAX_EMBED_TOKENS) -> str:
    global _enc
    if _enc is None:
        _enc = tiktoken.get_encoding("cl100k_base")
    tokens = _enc.encode(text)
    if len(tokens) <= max_tokens:
        return text
    return _enc.decode(tokens[:max_tokens])


def metadata_for_pinecone(ev: dict[str, Any]) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "event_id": ev.get("id"),
        "title": (ev.get("title") or "")[:2000],
        "type": (ev.get("type") or "")[:256],
        "location": (ev.get("location") or "")[:512],
        "address": (ev.get("address") or "")[:512],
        "age_range": (ev.get("age_range") or "")[:256],
        "gratuito": not has_purchase_link(ev),
        "start_date": (ev.get("start_date") or "")[:64],
        "end_date": (ev.get("end_date") or "")[:64],
        "agenda_date": (str(ev.get("agenda_date") or ""))[:32],
        "source": (ev.get("_source") or "")[:32],
    }
    if has_purchase_link(ev):
        meta["purchase_link"] = str(ev.get("purchase_link"))[:2000]
    out: dict[str, Any] = {}
    for k, v in meta.items():
        if v is None:
            continue
        if isinstance(v, str) and v == "":
            continue
        out[k] = v
    return out


def load_events_json(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)
