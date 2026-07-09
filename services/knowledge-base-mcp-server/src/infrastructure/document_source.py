"""Filesystem document source: load .md files from the kb directory."""
import hashlib
from pathlib import Path

from domain.entities import Document


def load_document(kb_dir: Path, path: Path) -> Document:
    content = path.read_text(encoding="utf-8")
    rel = path.relative_to(kb_dir).as_posix()
    domain = rel.split("/", 1)[0]
    return Document(
        doc_id=rel,
        domain=domain,
        title=path.name,
        content=content,
        content_hash=hashlib.sha256(content.encode("utf-8")).hexdigest(),
    )


def load_documents(kb_dir: Path) -> list[Document]:
    return [load_document(kb_dir, path) for path in sorted(kb_dir.rglob("*.md"))]
