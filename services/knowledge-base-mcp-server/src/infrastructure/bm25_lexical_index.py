"""Sparse lexical index adapter (BM25) with add / remove / search + persistence.

BM25Okapi is built from the whole corpus, so incremental add/remove mutate a per-id token
store and the BM25 model is rebuilt lazily on the next search. The token store is what gets
persisted (the model is cheap to rebuild on load).
"""
import json
from pathlib import Path

from rank_bm25 import BM25Okapi


def _tokenize(text: str) -> list[str]:
    return text.lower().split()


class Bm25LexicalIndex:
    def __init__(self) -> None:
        self._tokens: dict[int, list[str]] = {}
        self._bm25: BM25Okapi | None = None
        self._ids: list[int] = []

    def add(self, ids: list[int], texts: list[str]) -> None:
        for chunk_id, text in zip(ids, texts):
            self._tokens[chunk_id] = _tokenize(text)
        self._bm25 = None  # mark dirty

    def remove(self, ids: list[int]) -> None:
        for chunk_id in ids:
            self._tokens.pop(chunk_id, None)
        self._bm25 = None

    def _rebuild(self) -> None:
        self._ids = list(self._tokens)
        corpus = [self._tokens[i] for i in self._ids]
        self._bm25 = BM25Okapi(corpus) if corpus else None

    def search(self, query: str, k: int) -> list[tuple[int, float]]:
        if self._bm25 is None:
            self._rebuild()
        if self._bm25 is None:
            return []
        scores = self._bm25.get_scores(_tokenize(query))
        ranked = sorted(zip(self._ids, scores), key=lambda pair: pair[1], reverse=True)
        return [(int(i), float(s)) for i, s in ranked[:k]]

    def save(self, path: Path) -> None:
        path.write_text(
            json.dumps({str(i): toks for i, toks in self._tokens.items()}),
            encoding="utf-8",
        )

    def load(self, path: Path) -> None:
        if path.exists():
            raw = json.loads(path.read_text(encoding="utf-8"))
            self._tokens = {int(i): toks for i, toks in raw.items()}
            self._bm25 = None
