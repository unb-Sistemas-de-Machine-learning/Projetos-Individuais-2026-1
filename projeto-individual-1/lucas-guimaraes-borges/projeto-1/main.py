#!/usr/bin/env python3
"""
Ponto de entrada: scrape | sync | chat.

Execute na raiz do projeto (onde está o `.env` e `events.json`):

    python main.py scrape
    python main.py sync
    python main.py sync --dry-run --skip-scrape
    python main.py chat
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


def _cmd_scrape(_: argparse.Namespace) -> None:
    from scraper import agenda_scraper

    agenda_scraper.run()


def _cmd_sync(args: argparse.Namespace) -> None:
    from rag.sync import run as sync_run

    sync_run(
        skip_scrape=args.skip_scrape,
        events_path=args.events_json,
        dry_run=args.dry_run,
    )


def _cmd_chat(_: argparse.Namespace) -> None:
    from agent import run_chat

    run_chat()


def main() -> None:
    p = argparse.ArgumentParser(
        description="Agenda cultural DF — scrape, RAG Pinecone, agente OpenAI",
    )
    sub = p.add_subparsers(dest="command", required=True)

    p_scrape = sub.add_parser("scrape", help="Baixa a agenda Metrópoles → events.json")
    p_scrape.set_defaults(handler=_cmd_scrape)

    p_sync = sub.add_parser("sync", help="Scrape + embeddings + Pinecone (janela configurável)")
    p_sync.add_argument("--skip-scrape", action="store_true", help="Só lê events.json")
    p_sync.add_argument(
        "--events-json",
        type=Path,
        default=_ROOT / "events.json",
        help="Caminho do JSON (default: ./events.json)",
    )
    p_sync.add_argument("--dry-run", action="store_true")
    p_sync.set_defaults(handler=_cmd_sync)

    p_chat = sub.add_parser("chat", help="Agente de conversação no terminal")
    p_chat.set_defaults(handler=_cmd_chat)

    args = p.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
