import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from book_fetcher import Book

EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


class RAGCatalog:
    def __init__(self, db_path: str = "data/chroma_db"):
        self._client = chromadb.PersistentClient(path=db_path)
        self._ef = SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
        self._collection = self._client.get_or_create_collection(
            name="books",
            embedding_function=self._ef
        )

    def add_book(self, book: Book) -> None:
        doc_id = book.isbn or book.title.replace(" ", "_")
        text = _book_to_text(book)
        self._collection.upsert(
            ids=[doc_id],
            documents=[text],
            metadatas=[{
                "title": book.title,
                "authors": ", ".join(book.authors),
                "categories": ", ".join(book.categories),
                "work_key": book.work_key
            }],
        )

    def add_books(self, books: list[Book]) -> None:
        for book in books:
            self.add_book(book)

    def search_similar(
            self,
            query: str,
            k: int = 5,
            titles_to_remove: list[str] = []
    ) -> dict:
        n_results = k + (len(titles_to_remove) if titles_to_remove else 0) + 5
        result = self._collection.query(
            query_texts=[query],
            n_results=min(n_results, self._collection.count() or 1),
        )
        books = []
        for i, metadata in enumerate(result["metadatas"][0]):
            title = metadata["title"]
            if titles_to_remove and title in titles_to_remove:
                continue
            books.append({
                "title": title,
                "authors": metadata["authors"],
                "categories": metadata["categories"],
                "distance": result["distances"][0][i],
            })
            if len(books) >= k:
                break
        return books


def _book_to_text(book: Book) -> str:
    parts = [
        book.title,
        "from " + ", ".join(book.authors),
        "Genders: " + ", ".join(book.categories),
        book.description,
    ]
    return " | ".join(part for part in parts if part)
