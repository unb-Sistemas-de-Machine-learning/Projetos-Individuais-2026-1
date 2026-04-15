from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
from pinecone import NotFoundException, Pinecone
from zoneinfo import ZoneInfo

from utils.paths import default_events_json, env_file
from rag.documents import (
    EMBED_DIMS,
    EMBED_MODEL,
    event_to_text,
    load_events_json,
    metadata_for_pinecone,
    truncate_for_embedding,
)
from rag.filters import dedupe_by_id, event_in_forward_window
from scraper import agenda_scraper

BATCH_UPSERT = 64


def run(
    *,
    skip_scrape: bool,
    events_path: Path,
    dry_run: bool,
) -> None:
    load_dotenv(env_file())

    openai_key = os.environ.get("OPENAI_API_KEY")
    pinecone_key = os.environ.get("PINECONE_API_KEY")
    index_name = os.environ.get("PINECONE_INDEX", "events")
    tz_name = os.environ.get("EVENTS_TZ", "America/Sao_Paulo")
    try:
        forward_days = max(1, int(os.environ.get("EVENTS_FORWARD_DAYS", "14")))
    except ValueError:
        forward_days = 14

    if not dry_run:
        if not openai_key:
            sys.exit("Defina OPENAI_API_KEY no .env")
        if not pinecone_key:
            sys.exit("Defina PINECONE_API_KEY no .env")

    tz = ZoneInfo(tz_name)
    today = datetime.now(tz).date()

    if skip_scrape:
        if not events_path.is_file():
            sys.exit(f"Arquivo não encontrado: {events_path}")
        data = load_events_json(events_path)
    else:
        data = agenda_scraper.run()

    raw = data.get("events_flat") or []
    deduped = dedupe_by_id(raw)
    window_end = today + timedelta(days=forward_days)
    current = [ev for ev in deduped if event_in_forward_window(ev, today, forward_days)]

    if dry_run:
        print(
            f"[dry-run] Janela [{today} … {window_end}] ({forward_days}d, {tz_name}): "
            f"{len(current)} / {len(deduped)} eventos",
        )
        return

    client = OpenAI(api_key=openai_key)
    pc = Pinecone(api_key=pinecone_key)
    index = pc.Index(index_name)
    try:
        index.delete(delete_all=True)
    except NotFoundException as e:
        body = getattr(e, "body", b"") or b""
        if isinstance(body, bytes):
            body = body.decode("utf-8", errors="replace")
        if "Namespace not found" not in str(body):
            raise

    if not current:
        print(f"Índice '{index_name}' limpo; nenhum evento na janela para indexar.", file=sys.stderr)
        return

    texts = [truncate_for_embedding(event_to_text(ev)) for ev in current]
    vectors: list[dict[str, Any]] = []

    for i in range(0, len(texts), BATCH_UPSERT):
        batch_texts = texts[i : i + BATCH_UPSERT]
        batch_events = current[i : i + BATCH_UPSERT]
        resp = client.embeddings.create(
            model=EMBED_MODEL,
            input=batch_texts,
            dimensions=EMBED_DIMS,
        )
        for ev, item in zip(batch_events, resp.data, strict=True):
            eid = ev.get("id")
            if eid is None:
                continue
            vectors.append(
                {
                    "id": str(eid),
                    "values": item.embedding,
                    "metadata": metadata_for_pinecone(ev),
                }
            )

        if vectors:
            index.upsert(vectors=vectors)
            vectors.clear()

    print(
        f"Pinecone '{index_name}': reindexados {len(current)} eventos "
        f"(janela {forward_days}d; scrape={'sim' if not skip_scrape else 'não'}).",
        file=sys.stderr,
    )


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Scrape + RAG Pinecone (janela de datas)")
    p.add_argument("--skip-scrape", action="store_true", help="Usa só o JSON em disco")
    p.add_argument(
        "--events-json",
        type=Path,
        default=default_events_json(),
        help="Caminho do events.json (com --skip-scrape)",
    )
    p.add_argument("--dry-run", action="store_true", help="Só contagem; sem API")
    args = p.parse_args(argv)
    run(skip_scrape=args.skip_scrape, events_path=args.events_json, dry_run=args.dry_run)
