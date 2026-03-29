import requests
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

# GOOGLE_BOOKS_BASE_URL = "https://www.googleapis.com/books/v1/volumes"
OPENLIBRARY_SEARCH_URL = "https://openlibrary.org/search.json"
# API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")


@dataclass
class Book:
    title: str
    authors: list[str]
    categories: list[str]
    description: str
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

    # info = data["items"][0]["volumeInfo"]
    doc = data["docs"][0]
    description = ""
    fs = doc.get("first_sentence")
    if isinstance(fs, dict):
        description = fs.get("value", "")
    elif isinstance(fs, str):
        description = fs

    book = Book(
        doc.get("title", author_title),
        doc.get("author_name", []),
        doc.get("subject", [])[:5],
        description,
        doc.get("isbn", [""])[0] if doc.get("isbn") else "",
    )

    return book
