"""Knowledge-base domain entities."""
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Document:
    doc_id: str        # stable id = path relative to the kb root
    domain: str        # HR | ENGINEERING | IT | ANALYTICS (top-level source folder)
    title: str         # file name
    content: str
    content_hash: str  # sha256 of content — drives add / update / delete


@dataclass(frozen=True, slots=True)
class Chunk:
    chunk_id: int      # globally unique int id (FAISS-friendly, never reused)
    doc_id: str
    domain: str
    title: str
    text: str          # a header-aware section (or size-bounded sub-split); embedded + BM25-indexed


@dataclass(frozen=True, slots=True)
class DocRecord:
    """Manifest entry: what a document currently contributes to the index."""

    content_hash: str
    chunk_ids: tuple[int, ...]
