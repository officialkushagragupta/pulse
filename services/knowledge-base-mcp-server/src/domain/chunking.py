"""Header-aware markdown chunking (pure domain logic).

Split on markdown headings so each chunk is a coherent, self-contained section; any
section larger than the target is sub-split into overlapping windows. Docs without
headings fall back to plain size-bounded windows. Token budgets are approximated by
word count (~0.75 words per token) to stay dependency-free.
"""
_WORDS_PER_TOKEN = 0.75


def _split_by_headings(content: str) -> list[str]:
    sections: list[list[str]] = []
    current: list[str] = []
    for line in content.splitlines():
        if line.lstrip().startswith("#") and current:
            sections.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append(current)
    joined = ["\n".join(lines).strip() for lines in sections]
    return [s for s in joined if s] or ([content.strip()] if content.strip() else [])


def _window(words: list[str], max_words: int, overlap_words: int) -> list[str]:
    step = max(1, max_words - overlap_words)
    pieces: list[str] = []
    for start in range(0, len(words), step):
        pieces.append(" ".join(words[start : start + max_words]))
        if start + max_words >= len(words):
            break
    return pieces


def chunk_markdown(content: str, chunk_tokens: int, overlap_tokens: int) -> list[str]:
    max_words = max(1, int(chunk_tokens * _WORDS_PER_TOKEN))
    overlap_words = max(0, int(overlap_tokens * _WORDS_PER_TOKEN))
    chunks: list[str] = []
    for section in _split_by_headings(content):
        words = section.split()
        if len(words) <= max_words:
            chunks.append(section)
        else:
            chunks.extend(_window(words, max_words, overlap_words))
    return chunks
