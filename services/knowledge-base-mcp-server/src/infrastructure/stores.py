"""JSON-persisted chunk store and manifest.

- JsonChunkStore: chunk_id -> Chunk (source of truth for chunk text/metadata; feeds BM25
  rebuilds and K2 retrieval results).
- JsonManifest: doc_id -> DocRecord (content hash + owned chunk ids) plus a monotonic id
  allocator so chunk ids are never reused (safe FAISS removal on update/delete).
"""
import json
from dataclasses import asdict
from pathlib import Path

from domain.entities import Chunk, DocRecord


class JsonChunkStore:
    def __init__(self) -> None:
        self._chunks: dict[int, Chunk] = {}

    def add(self, chunks: list[Chunk]) -> None:
        for chunk in chunks:
            self._chunks[chunk.chunk_id] = chunk

    def remove(self, ids: list[int]) -> None:
        for chunk_id in ids:
            self._chunks.pop(chunk_id, None)

    def get(self, chunk_id: int) -> Chunk | None:
        return self._chunks.get(chunk_id)

    def all(self) -> list[Chunk]:
        return list(self._chunks.values())

    def save(self, path: Path) -> None:
        path.write_text(
            json.dumps([asdict(c) for c in self._chunks.values()]), encoding="utf-8"
        )

    def load(self, path: Path) -> None:
        if path.exists():
            rows = json.loads(path.read_text(encoding="utf-8"))
            self._chunks = {row["chunk_id"]: Chunk(**row) for row in rows}


class JsonManifest:
    def __init__(self) -> None:
        self._docs: dict[str, DocRecord] = {}
        self._next_id: int = 0

    def get(self, doc_id: str) -> DocRecord | None:
        return self._docs.get(doc_id)

    def doc_ids(self) -> list[str]:
        return list(self._docs)

    def set(self, doc_id: str, record: DocRecord) -> None:
        self._docs[doc_id] = record

    def delete(self, doc_id: str) -> None:
        self._docs.pop(doc_id, None)

    def allocate_ids(self, count: int) -> list[int]:
        start = self._next_id
        self._next_id += count
        return list(range(start, start + count))

    def save(self, path: Path) -> None:
        payload = {
            "next_id": self._next_id,
            "docs": {
                doc_id: {"content_hash": rec.content_hash, "chunk_ids": list(rec.chunk_ids)}
                for doc_id, rec in self._docs.items()
            },
        }
        path.write_text(json.dumps(payload), encoding="utf-8")

    def load(self, path: Path) -> None:
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            self._next_id = payload.get("next_id", 0)
            self._docs = {
                doc_id: DocRecord(
                    content_hash=rec["content_hash"], chunk_ids=tuple(rec["chunk_ids"])
                )
                for doc_id, rec in payload.get("docs", {}).items()
            }
