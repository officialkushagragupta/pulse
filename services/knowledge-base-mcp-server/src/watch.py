"""K1 (event-driven): watch data/kb and keep FAISS + BM25 in sync on create/modify/delete.

A local analogue of an Azure AI Search indexer: instead of re-scanning, a filesystem
watcher reports changed files and the IngestKnowledgeBase use case re-indexes only the
affected document. On startup it runs one full reconcile (to catch changes made while the
watcher was down), then watches until interrupted.

    uv run python src/watch.py
"""
import logging
import threading
import time
from pathlib import Path

from application.ingest_knowledge_base import IngestKnowledgeBase
from infrastructure.bm25_lexical_index import Bm25LexicalIndex
from infrastructure.config import get_settings
from infrastructure.document_source import load_document, load_documents
from infrastructure.faiss_vector_index import FaissVectorIndex
from infrastructure.logging import configure_logging
from infrastructure.ollama_embedder import OllamaEmbedder
from infrastructure.stores import JsonChunkStore, JsonManifest
from infrastructure.watcher import KnowledgeBaseWatcher

logger = logging.getLogger("kb.watch")


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    kb_dir = Path(settings.kb_dir).resolve()
    index_dir = Path(settings.index_dir)
    kb_dir.mkdir(parents=True, exist_ok=True)
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
    use_case = IngestKnowledgeBase(
        embedder, vector, lexical, chunks, manifest,
        settings.chunk_tokens, settings.chunk_overlap,
    )

    lock = threading.Lock()

    def persist() -> None:
        vector.save(vectors_path)
        lexical.save(bm25_path)
        chunks.save(chunks_path)
        manifest.save(manifest_path)

    with lock:
        report = use_case.execute(load_documents(kb_dir))
        persist()
    logger.info(
        "startup_reconcile",
        extra={"added": report.added, "updated": report.updated,
               "deleted": report.deleted, "unchanged": report.unchanged},
    )

    def on_upsert(path: Path) -> None:
        with lock:
            try:
                doc = load_document(kb_dir, path)
            except FileNotFoundError:
                return  # file vanished between event and read
            action = use_case.apply_upsert(doc)
            persist()
        logger.info("kb_upsert", extra={"doc_id": doc.doc_id, "action": action})

    def on_delete(path: Path) -> None:
        doc_id = path.relative_to(kb_dir).as_posix()
        with lock:
            removed = use_case.apply_delete(doc_id)
            persist()
        logger.info("kb_delete", extra={"doc_id": doc_id, "removed": removed})

    watcher = KnowledgeBaseWatcher(kb_dir, on_upsert, on_delete)
    watcher.start()
    logger.info("watching", extra={"kb_dir": str(kb_dir)})
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        watcher.stop()
        with lock:
            persist()
        logger.info("stopped")


if __name__ == "__main__":
    main()
