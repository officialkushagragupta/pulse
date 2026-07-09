"""Normalize the Text-to-SQL batch files into one canonical JSONL.

The batch files under data/text-to-sql-jsonl/ are pretty-printed JSON *arrays*. This
script concatenates them and re-emits every object verbatim as one compact JSON line
(proper JSONL) — format only: no schema/SQL validation, no dedup, no field remapping.
Re-run it whenever you add batches.

Usage:
    python scripts/normalize_dataset.py [input_dir] [output_file]
    # defaults: data/text-to-sql-jsonl/  ->  data/text-to-sql-jsonl/dataset.jsonl
"""
from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path

logger = logging.getLogger("normalize_dataset")

DEFAULT_DIR = Path("data/text-to-sql-jsonl")
_FENCE = re.compile(r"```(?:json)?")
_DECODER = json.JSONDecoder()


def load_objects(path: Path) -> list[dict]:
    """Read one batch file that may hold several concatenated JSON arrays/objects."""
    text = _FENCE.sub("", path.read_text(encoding="utf-8"))
    objects: list[dict] = []
    i, n = 0, len(text)
    while i < n:
        while i < n and text[i] in " \t\r\n,":  # skip whitespace / stray separators
            i += 1
        if i >= n:
            break
        value, i = _DECODER.raw_decode(text, i)
        if isinstance(value, list):
            objects.extend(value)
        elif isinstance(value, dict):
            objects.append(value)
        else:
            raise ValueError(f"{path.name}: unexpected top-level {type(value).__name__}")
    return objects


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    in_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DIR
    out_file = Path(sys.argv[2]) if len(sys.argv) > 2 else in_dir / "dataset.jsonl"

    batches = sorted(in_dir.glob("*-batch.jsonl"))
    if not batches:
        logger.warning("no *-batch.jsonl files found in %s", in_dir)
        return

    rows: list[dict] = []
    seen_ids: set[object] = set()
    duplicate_ids = 0
    for batch in batches:
        objects = load_objects(batch)
        for obj in objects:
            rows.append(obj)
            key = obj.get("id")
            if key in seen_ids:
                duplicate_ids += 1
            seen_ids.add(key)
        logger.info("%s: %d examples", batch.name, len(objects))

    with out_file.open("w", encoding="utf-8") as handle:
        for obj in rows:
            handle.write(json.dumps(obj, ensure_ascii=False) + "\n")

    logger.info("wrote %d examples -> %s", len(rows), out_file)
    if duplicate_ids:
        logger.warning(
            "%d duplicate 'id' values across batches (ids reset per batch); "
            "format-only run left them untouched",
            duplicate_ids,
        )


if __name__ == "__main__":
    main()
