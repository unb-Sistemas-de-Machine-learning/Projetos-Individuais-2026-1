import json
import os
import ollama
import requests
from catalog_builder import RAGCatalog
from book_fetcher import search_book_metadata, Book
from dotenv import load_dotenv
from price_checker import verify_price

load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
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

        candidates = self._catalog.search_similar(query, k=k * 3, titles_to_remove=read_books)
        candidates = _enrich_candidates(candidates)

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
        candidates_text = "\n".join(
            f"- {c['title']} ({c['authors']}) — {c['categories']} "
            f"[Minimum price: R$ {c['minimum_price']:.2f} in {c['offers'][0].store}]"
            if c["minimum_price"] else
            f"- {c['title']} ({c['authors']}) — {c['categories']} [Price not found]"
            for c in candidates
        )

        prompt = f"""You are a literary recommendation agent.
Based on the books the user has already read,
select and rank the {k} best books from the candidate list to recommend.
Write the justification field in Brazilian Portuguese (pt-BR).

**Books already read by the user:**
{read_books_text}

**Available candidates:**
{candidates_text}

Return ONLY a valid JSON array (no markdown, no extra explanation) with exactly {k} items in this format:
[
  {{
    "title": "exact candidate title",
    "justification": "1-2 sentences explaining why this book is recommended"
  }}
]
Every item in the array must have a justification. Do not leave any item without one."""

        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.message.content.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]

        ranked = json.loads(text)

        candidates_map = {c["title"]: c for c in candidates}
        result = []
        for rec in ranked:
            candidate = candidates_map.get(rec["title"], {})
            result.append({
                "title": rec["title"],
                "justification": rec.get("justification", ""),
                "minimum_price": candidate.get("minimum_price"),
                "cheapest_store": candidate["offers"][0].store if candidate.get("offers") else "",
                "offers": candidate.get("offers", []),
            })
        return result


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
