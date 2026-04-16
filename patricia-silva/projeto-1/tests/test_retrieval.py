"""Testes sem LLM: base local e recuperação."""

from pathlib import Path

from src.config import ROOT
from src.retrieval import TfIdfRetriever, load_kb_chunks


def test_kb_nao_vazia():
    kb = ROOT / "data" / "kb"
    chunks = load_kb_chunks(kb)
    assert len(chunks) >= 3


def test_retriever_ranqueia_repeticao():
    kb = Path(__file__).resolve().parents[1] / "data" / "kb"
    chunks = load_kb_chunks(kb)
    r = TfIdfRetriever(chunks)
    hits = r.top_k("repetição espaçada revisão flashcards", k=2)
    assert hits
    joined = " ".join(hits).lower()
    assert "repetição" in joined or "espaçada" in joined or "revisão" in joined
