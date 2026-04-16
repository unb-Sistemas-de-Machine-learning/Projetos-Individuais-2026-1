import requests
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

# GOOGLE_BOOKS_BASE_URL = "https://www.googleapis.com/books/v1/volumes"
OPENLIBRARY_SEARCH_URL = "https://openlibrary.org/search.json"
OPENLIBRARY_WORKS_URL = "https://openlibrary.org{work_key}.json"
# API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")


@dataclass
class Book:
    title: str
    authors: list[str]
    categories: list[str]
    description: str
    work_key: str
    isbn: str


def search_book_metadata(author_title: str) -> Book:
    params = {
        "q": author_title,
        "maxResults": 1,
        "langRestrict": "pt",
        # "key": API_KEY
    }
    response = requests.get(OPENLIBRARY_SEARCH_URL, params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if not data.get("docs"):
        raise Exception(f"Book not found: {author_title}")

    doc = data["docs"][0]
    work_key = doc.get("key", "")

    book = Book(
        title=doc.get("title", author_title),
        authors=doc.get("author_name", []),
        categories=doc.get("subject", [])[:5],
        description="",
        isbn=doc.get("isbn", [""])[0] if doc.get("isbn") else "",
        work_key=work_key
    )

    if work_key:
        try:
            work = _search_work_data(work_key)
            book.description = work.get("description", "")
            book.categories = work.get("categories", "")
        except Exception:
            pass

    return book


def _search_work_data(work_key: str) -> dict:
    url = OPENLIBRARY_WORKS_URL.format(work_key=work_key)
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    description = data.get("description", "")
    if isinstance(description, dict):
        description = description.get("value", "")

    subjects = data.get("subjects", [])[:8]

    return {
        "description": description,
        "categories": subjects,
    }
