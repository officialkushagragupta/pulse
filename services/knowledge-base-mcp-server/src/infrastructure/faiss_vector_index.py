"""Dense vector index adapter (FAISS) with add / remove / search + persistence.

Uses IndexIDMap2 over IndexFlatIP with L2-normalized vectors, so inner product == cosine
similarity and chunks are addressed by their own int ids (enabling incremental removal
on update/delete). The dimension is fixed by the first batch added.
"""
from pathlib import Path

import faiss
import numpy as np


class FaissVectorIndex:
    def __init__(self) -> None:
        self._index: faiss.IndexIDMap2 | None = None

    def _ensure(self, dim: int) -> None:
        if self._index is None:
            self._index = faiss.IndexIDMap2(faiss.IndexFlatIP(dim))

    def add(self, ids: list[int], vectors: list[list[float]]) -> None:
        if not ids:
            return
        arr = np.asarray(vectors, dtype="float32")
        faiss.normalize_L2(arr)
        self._ensure(arr.shape[1])
        self._index.add_with_ids(arr, np.asarray(ids, dtype="int64"))

    def remove(self, ids: list[int]) -> None:
        if self._index is None or not ids:
            return
        self._index.remove_ids(np.asarray(ids, dtype="int64"))

    def search(self, vector: list[float], k: int) -> list[tuple[int, float]]:
        if self._index is None or self._index.ntotal == 0:
            return []
        query = np.asarray([vector], dtype="float32")
        faiss.normalize_L2(query)
        scores, ids = self._index.search(query, min(k, self._index.ntotal))
        return [(int(i), float(s)) for i, s in zip(ids[0], scores[0]) if i != -1]

    def save(self, path: Path) -> None:
        if self._index is not None:
            faiss.write_index(self._index, str(path))

    def load(self, path: Path) -> None:
        if path.exists():
            self._index = faiss.read_index(str(path))
