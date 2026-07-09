"""Filesystem watcher adapter (watchdog).

Reports *what changed* under the kb directory as create/modify/delete of `.md` files and
nothing more — it does no chunking, embedding, or indexing. The composition root wires its
callbacks to the IngestKnowledgeBase use case, which decides *how* to update the indices.

Editor "atomic saves" (write temp then rename) surface as on_moved; those are translated
into a delete of the old path plus an upsert of the new one.
"""
from collections.abc import Callable
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

PathCallback = Callable[[Path], None]


def _is_markdown(path: str) -> bool:
    return path.lower().endswith(".md")


class _MarkdownEventHandler(FileSystemEventHandler):
    def __init__(self, on_upsert: PathCallback, on_delete: PathCallback) -> None:
        self._on_upsert = on_upsert
        self._on_delete = on_delete

    def on_created(self, event: FileSystemEvent) -> None:
        if not event.is_directory and _is_markdown(event.src_path):
            self._on_upsert(Path(event.src_path))

    def on_modified(self, event: FileSystemEvent) -> None:
        if not event.is_directory and _is_markdown(event.src_path):
            self._on_upsert(Path(event.src_path))

    def on_deleted(self, event: FileSystemEvent) -> None:
        if not event.is_directory and _is_markdown(event.src_path):
            self._on_delete(Path(event.src_path))

    def on_moved(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        if _is_markdown(event.src_path):
            self._on_delete(Path(event.src_path))
        if _is_markdown(event.dest_path):
            self._on_upsert(Path(event.dest_path))


class KnowledgeBaseWatcher:
    def __init__(self, kb_dir: Path, on_upsert: PathCallback, on_delete: PathCallback) -> None:
        self._kb_dir = kb_dir
        self._handler = _MarkdownEventHandler(on_upsert, on_delete)
        self._observer = Observer()

    def start(self) -> None:
        self._observer.schedule(self._handler, str(self._kb_dir), recursive=True)
        self._observer.start()

    def stop(self) -> None:
        self._observer.stop()
        self._observer.join()
