"""K1 entry point: incremental ingest of data/kb into FAISS + BM25 (add / update / delete).

Run from the service directory:

    uv run python src/ingest.py
"""
import logging
from pathlib import Path

from application.ingest_knowledge_base import IngestKnowledgeBase
from infrastructure.bm25_lexical_index import Bm25LexicalIndex
from infrastructure.config import get_settings
from infrastructure.document_source import load_documents
from infrastructure.faiss_vector_index import FaissVectorIndex
from infrastructure.logging import configure_logging
from infrastructure.ollama_embedder import OllamaEmbedder
from infrastructure.stores import JsonChunkStore, JsonManifest

logger = logging.getLogger("kb.ingest")


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    kb_dir = Path(settings.kb_dir)
    index_dir = Path(settings.index_dir)

    documents = load_documents(kb_dir)
    if not documents:
        logger.warning("kb_ingest_blocked", extra={"reason": "data/kb empty"})
        return

    index_dir.mkdir(parents=True, exist_ok=True)
    vectors_path = index_dir / "vectors.faiss"
    bm25_path = index_dir / "bm25.json"
    chunks_path = index_dir / "chunks.json"
    manifest_path = index_dir / "manifest.json"

    vector = FaissVectorIndex()
    vector.load(vectors_path)
    lexical = Bm25LexicalIndex()
    lexical.load(bm25_path)
    chunks = JsonChunkStore()
    chunks.load(chunks_path)
    manifest = JsonManifest()
    manifest.load(manifest_path)

    embedder = OllamaEmbedder(settings.ollama_base_url, settings.embedding_model)
    ingest = IngestKnowledgeBase(
        embedder, vector, lexical, chunks, manifest,
        settings.chunk_tokens, settings.chunk_overlap,
    )
    report = ingest.execute(documents)

    vector.save(vectors_path)
    lexical.save(bm25_path)
    chunks.save(chunks_path)
    manifest.save(manifest_path)

    logger.info(
        "kb_ingest_complete",
        extra={
            "added": report.added,
            "updated": report.updated,
            "deleted": report.deleted,
            "unchanged": report.unchanged,
            "index_dir": str(index_dir),
        },
    )


if __name__ == "__main__":
    main()
