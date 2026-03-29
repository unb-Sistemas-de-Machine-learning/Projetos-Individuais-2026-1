import os
import requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_BOOKS_BASE_URL = "https://www.googleapis.com/books/v1/volumes"
API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")


def search_book_metadata(author_title: str) -> dict:
    params = {
        "q": author_title,
        "maxResults": 1,
        "langRestrict": "pt",
        # "key": API_KEY
    }
    response = requests.get(GOOGLE_BOOKS_BASE_URL, params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if "items" not in data:
        raise Exception(f"Book not found: {author_title}")

    info = data["items"][0]["volumeInfo"]
    return {
        "title": info.get("title", author_title),
        "authors": info.get("authors", []),
        "categories": info.get("categories", []),
        "description": info.get("description", ""),
        "language": info.get("language", ""),
        "isbn": _extract_isbn(info),
    }


def _extract_isbn(volume_info: dict) -> str:
    for id_item in volume_info.get("industryIdentifiers", []):
        if id_item["type"] in ("ISBN_13", "ISBN_10"):
            return id_item["identifier"]
    return ""
