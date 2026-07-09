"""K1: incremental ingest of the knowledge base (add / update / delete).

Two entry paths share the same per-document core:
- execute(documents): full reconcile — diff every on-disk doc against the manifest
  (used by the one-shot ingest and by the watcher's startup reconcile).
- apply_upsert(doc) / apply_delete(doc_id): single-document operations driven by
  filesystem events (the event-driven watcher).

Diff is by content hash:
- doc in manifest but gone from disk  -> DELETE (purge its chunks from every index)
- doc on disk but not in manifest      -> ADD
- doc on disk with a changed hash       -> UPDATE (purge old chunks, then re-index)
- doc on disk with an unchanged hash    -> skip
"""
from dataclasses import dataclass

from domain.chunking import chunk_markdown
from domain.entities import Chunk, DocRecord, Document
from domain.ports import ChunkStore, Embedder, LexicalIndex, Manifest, VectorIndex


@dataclass(frozen=True, slots=True)
class IngestReport:
    added: int
    updated: int
    deleted: int
    unchanged: int


class IngestKnowledgeBase:
    def __init__(
        self,
        embedder: Embedder,
        vector_index: VectorIndex,
        lexical_index: LexicalIndex,
        chunk_store: ChunkStore,
        manifest: Manifest,
        chunk_tokens: int,
        chunk_overlap: int,
    ) -> None:
        self._embedder = embedder
        self._vector = vector_index
        self._lexical = lexical_index
        self._chunks = chunk_store
        self._manifest = manifest
        self._chunk_tokens = chunk_tokens
        self._chunk_overlap = chunk_overlap

    def execute(self, documents: list[Document]) -> IngestReport:
        on_disk = {doc.doc_id: doc for doc in documents}
        deleted = 0
        for doc_id in self._manifest.doc_ids():
            if doc_id not in on_disk and self.apply_delete(doc_id):
                deleted += 1

        counts = {"added": 0, "updated": 0, "unchanged": 0}
        for doc in documents:
            counts[self.apply_upsert(doc)] += 1
        return IngestReport(counts["added"], counts["updated"], deleted, counts["unchanged"])

    def apply_upsert(self, doc: Document) -> str:
        """Add or update a single document. Returns 'added' | 'updated' | 'unchanged'."""
        record = self._manifest.get(doc.doc_id)
        if record is None:
            self._index(doc)
            return "added"
        if record.content_hash != doc.content_hash:
            self._purge(doc.doc_id)
            self._index(doc)
            return "updated"
        return "unchanged"

    def apply_delete(self, doc_id: str) -> bool:
        """Remove a single document from every index. Returns True if it was present."""
        if self._manifest.get(doc_id) is None:
            return False
        self._purge(doc_id)
        return True

    def _purge(self, doc_id: str) -> None:
        record = self._manifest.get(doc_id)
        if record is not None:
            ids = list(record.chunk_ids)
            self._vector.remove(ids)
            self._lexical.remove(ids)
            self._chunks.remove(ids)
        self._manifest.delete(doc_id)

    def _index(self, doc: Document) -> None:
        texts = chunk_markdown(doc.content, self._chunk_tokens, self._chunk_overlap)
        if not texts:
            self._manifest.set(doc.doc_id, DocRecord(doc.content_hash, ()))
            return
        ids = self._manifest.allocate_ids(len(texts))
        vectors = self._embedder.embed(texts)
        chunks = [
            Chunk(chunk_id=i, doc_id=doc.doc_id, domain=doc.domain, title=doc.title, text=t)
            for i, t in zip(ids, texts)
        ]
        self._vector.add(ids, vectors)
        self._lexical.add(ids, texts)
        self._chunks.add(chunks)
        self._manifest.set(doc.doc_id, DocRecord(doc.content_hash, tuple(ids)))
