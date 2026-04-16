from __future__ import annotations
import json
import os
from dataclasses import dataclass, asdict

WISHLIST_PATH = "data/wishlist.json"


@dataclass
class WishlistItem:
    title: str
    authors: str = ""


class Wishlist:
    def __init__(self, path: str = WISHLIST_PATH):
        self._path = path
        self._items: list[WishlistItem] = self._load()

    def add(self, title: str, authors: str = "") -> bool:
        if any(i.title == title for i in self._items):
            return False
        self._items.append(WishlistItem(title=title, authors=authors))
        self._save()
        return True

    def remove(self, title: str) -> bool:
        before = len(self._items)
        self._items = [i for i in self._items if i.title != title]
        if len(self._items) < before:
            self._save()
            return True
        return False

    def list(self) -> list[WishlistItem]:
        return list(self._items)

    def _load(self) -> list[WishlistItem]:
        if os.path.exists(self._path):
            with open(self._path, "r", encoding="utf-8") as f:
                return [WishlistItem(**item) for item in json.load(f)]
        return []

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump([asdict(i) for i in self._items], f, ensure_ascii=False, indent=2)
