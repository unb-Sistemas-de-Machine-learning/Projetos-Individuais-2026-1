"""RAG leve: recuperação por TF-IDF sobre trechos da base local em Markdown."""

from __future__ import annotations

import re
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _chunk_markdown(text: str, min_len: int = 40) -> list[str]:
    parts = re.split(r"\n\s*\n", text.strip())
    return [p.strip() for p in parts if len(p.strip()) >= min_len]


def load_kb_chunks(kb_dir: Path) -> list[str]:
    chunks: list[str] = []
    if not kb_dir.is_dir():
        return chunks
    for path in sorted(kb_dir.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        chunks.extend(_chunk_markdown(raw))
    return chunks


class TfIdfRetriever:
    def __init__(self, chunks: list[str]) -> None:
        self._chunks = chunks
        if not chunks:
            self._vectorizer = None
            self._matrix = None
            return
        self._vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            max_features=8000,
        )
        self._matrix = self._vectorizer.fit_transform(chunks)

    def top_k(self, query: str, k: int = 4) -> list[str]:
        if not self._chunks or self._vectorizer is None or self._matrix is None:
            return []
        q = self._vectorizer.transform([query])
        scores = cosine_similarity(q, self._matrix).ravel()
        ranked = sorted(
            range(len(self._chunks)),
            key=lambda i: scores[i],
            reverse=True,
        )[:k]
        return [self._chunks[i] for i in ranked if scores[i] > 0.01]
