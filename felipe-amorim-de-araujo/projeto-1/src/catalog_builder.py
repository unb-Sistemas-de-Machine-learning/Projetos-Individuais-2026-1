import requests
import argparse
from rag import RAGCatalog
from book_fetcher import Book
import time

OPENLIBRARY_SUBJECTS_URL = "https://openlibrary.org/subjects/{subject}.json"

SUBJECTS = [
    "fiction", "classic_literature", "literary_fiction", "short_stories",
    "mystery", "thriller", "horror", "crime_fiction",
    "science_fiction", "fantasy", "dystopian_fiction", "adventure",
    "romance", "historical_fiction",
    "biography", "autobiography", "history", "philosophy",
    "psychology", "self_help", "science", "essays",
    "brazilian_literature", "latin_american_literature",
    "spanish_literature", "french_literature",
    "japanese_literature", "american_literature", "british_literature",
    "coming_of_age", "political_fiction", "war_stories",
    "magical_realism", "graphic_novels", "poetry",
    "19th_century_fiction", "20th_century_fiction",
]
DEFAULT_LIMIT = 500


def search_books_per_subject(subject: str, limit: int = DEFAULT_LIMIT) -> list[Book]:
    url = OPENLIBRARY_SUBJECTS_URL.format(subject=subject)
    response = requests.get(url, params={"limit": limit}, timeout=30)
    response.raise_for_status()
    data = response.json()

    books = []
    for work in data.get("works", []):
        title = work.get("title", "").strip()
        if not title:
            continue
        if _is_low_quality_title(title):
            continue

        subjects = [s for s in work.get("subject", []) if isinstance(s, str)]
        if len(subjects) < 2:
            continue

        work_key = work.get("key").split("/")[2]

        book = Book(
            title=title,
            authors=[a["name"] for a in work.get("authors", [])],
            categories=[subject.replace("_", " ")] + subjects[:4],
            description="",
            isbn="",
            work_key=work_key
        )

        books.append(book)

    return books


def _is_low_quality_title(title: str) -> bool:
    if len(title) > 90:
        return True
    if title.count(":") >= 2:
        return True
    ascii_ratio = sum(1 for c in title if ord(c) < 128) / max(len(title), 1)
    if ascii_ratio < 0.8:
        return True
    lower = title.lower()
    academic_markers = [
        "an introduction to", "a history of", "a guide to",
        "proceedings of", "journal of", "transactions of",
        "vol.", "volume ", "edition", "handbook of",
    ]
    return any(marker in lower for marker in academic_markers)


def main():
    parser = argparse.ArgumentParser(
        description="Builds the RAG catalog using the Open Library API."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"Books per subject (default: {DEFAULT_LIMIT}).",
    )
    args = parser.parse_args()

    catalog = RAGCatalog()
    total = 0
    print(
        f"Building catalog: {len(SUBJECTS)} subject x {args.limit} books = up to {len(SUBJECTS) * args.limit} books\n"
    )
    for subject in SUBJECTS:
        print(f"Loading: {subject}...")
        try:
            books = search_books_per_subject(subject, limit=args.limit)
            catalog.add_books(books)
            total += len(books)
            print(f"  ✓ {len(books)} books added")
            time.sleep(0.5)  # rate limit
        except Exception as e:
            print(f"  ✗ Error for subject'{subject}': {e}")
    print(f"\nCatalog built with {total} books in total.")


if __name__ == "__main__":
    main()
