import os
import unicodedata
from google import genai
import requests
from catalog_builder import RAGCatalog
from book_fetcher import search_book_metadata, Book
from dotenv import load_dotenv
from price_checker import verify_price

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")
DB_PATH = "data/chroma_db"
WORKS_URL = "https://openlibrary.org{work_key}.json"


class Agent:
    def __init__(self, db_path: str = DB_PATH):
        self._catalog = RAGCatalog(db_path=db_path)

    def recommend(self, read_books: list[str], k: int = 5) -> list[Book]:
        read_context: list[Book] = []
        for title in read_books:
            try:
                meta = search_book_metadata(title)
                read_context.append(meta)
            except Exception:
                book = Book(
                    title=title,
                    authors=[],
                    categories=[],
                    description="",
                    isbn="",
                    work_key=""
                )
                read_context.append(book)

        query = _build_rag_query(read_context)

        normalized_read = [_normalize_title(t) for t in read_books]
        candidates = self._catalog.search_similar(query, k=k * 3, titles_to_remove=read_books)
        candidates = [c for c in candidates if _normalize_title(c["title"]) not in normalized_read]
        # candidates = _enrich_candidates(candidates)

        candidates_with_price = []
        for book in candidates:
            offers = verify_price(book["title"])
            minimum_price = min((o.price for o in offers), default=None)
            candidates_with_price.append({
                **book,
                "offers": offers,
                "minimum_price": minimum_price
            })

        return self._rank(
            read_books=read_books,
            read_context=read_context,
            candidates=candidates_with_price,
            k=k,
        )

    def _rank(self, read_books, read_context, candidates, k) -> list[dict]:
        read_books_text = "\n".join(
            f"- {m.title} ({', '.join(m.authors)}) — {', '.join(m.categories)}"
            for m in read_context
        )

        diverse = []
        seen_authors = set()
        for c in candidates:
            author_key = c["authors"][0].lower() if c.get("authors") else ""
            if author_key not in seen_authors:
                seen_authors.add(author_key)
                diverse.append(c)
            if len(diverse) == k:
                break

        justifications = self._justify_all(diverse, read_books_text)

        result = []
        for candidate, justification in zip(diverse, justifications):
            result.append({
                "title": candidate["title"],
                "justification": justification,
                "minimum_price": candidate.get("minimum_price"),
                "cheapest_store": min(candidate["offers"], key=lambda o: o.price).store if candidate.get("offers") else "",
                "offers": candidate.get("offers", []),
            })
        return result

    def _justify_all(self, candidates: list[dict], read_books_text: str) -> list[str]:
        books_list = "\n".join(
            f"{i+1}. \"{c['title']}\" de {c['authors']} (gêneros: {c['categories']})"
            for i, c in enumerate(candidates)
        )
        prompt = f"""Você é um agente de recomendação literária. Responda SOMENTE em português do Brasil (pt-BR).

O usuário leu os seguintes livros:
{read_books_text}

Para cada livro recomendado abaixo, escreva 1 a 2 frases em português do Brasil explicando por que é uma boa recomendação para este usuário.

Livros recomendados:
{books_list}

Responda APENAS com as justificativas numeradas no formato:
1. <justificativa>
2. <justificativa>
...

Não inclua nenhum outro texto."""

        client = genai.Client()
        response = client.models.generate_content(model=MODEL, contents=prompt)
        lines = [l.strip() for l in response.text.strip().splitlines() if l.strip()]

        justifications = []
        for line in lines:
            if line and line[0].isdigit() and ". " in line:
                justifications.append(line.split(". ", 1)[1])

        while len(justifications) < len(candidates):
            justifications.append("")
        return justifications[:len(candidates)]


def _normalize_title(title: str) -> str:
    normalized = unicodedata.normalize("NFD", title.lower())
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")


def _build_rag_query(read_context: list[Book]) -> str:
    categories = set()
    descriptions = []
    for book in read_context:
        categories.update(book.categories)
        if book.description:
            descriptions.append(book.description[:200])
    return " ".join(list(categories)) + " " + " ".join(descriptions[:3])


def _enrich_candidates(candidates: list[Book]) -> list[Book]:
    enriched = []
    for book in candidates:
        work_key = book.get("work_key", "")
        if not work_key:
            enriched.append(book)
            continue
        try:
            resp = requests.get(WORKS_URL.format(work_key=work_key), timeout=8)
            data = resp.json()

            description = data.get("description", "")
            if isinstance(description, dict):
                description = description.get("value", "")

            categories = data.get("subjects", [])

            enriched.append({
                **book,
                "description": description,
                "categories": ", ".join(categories[:8]) if categories else book["categories"]
            })
        except Exception:
            enriched.append(book)

    return enriched
