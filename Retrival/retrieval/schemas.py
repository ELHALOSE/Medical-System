"""
schemas.py
----------
The `Chunk` shape here is the integration contract with the chunking stage
(a teammate's branch): it must match the fields written to `chunks.jsonl`
by the cleaning/chunking pipeline exactly. If that schema changes, this is
the one place to update on the retrieval side.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Chunk:
    chunk_id: str
    text: str
    contextualized_text: str  # heading breadcrumb + text — what gets embedded
    headings: list[str] = field(default_factory=list)
    page_numbers: list[int] = field(default_factory=list)
    doc_name: str = ""
    char_count: int = 0
    token_count: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "Chunk":
        return cls(**{f: data[f] for f in cls.__dataclass_fields__ if f in data})

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "contextualized_text": self.contextualized_text,
            "headings": self.headings,
            "page_numbers": self.page_numbers,
            "doc_name": self.doc_name,
            "char_count": self.char_count,
            "token_count": self.token_count,
        }


def load_chunks_jsonl(path: str | Path) -> list[Chunk]:
    """Load the chunking stage's output. Raises a clear error on schema drift
    rather than silently dropping fields."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found - run the chunking pipeline first, or check "
            "you've pulled the latest chunks.jsonl from that branch."
        )

    chunks = []
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                chunks.append(Chunk.from_dict(json.loads(line)))
            except (KeyError, TypeError, json.JSONDecodeError) as e:
                raise ValueError(f"{path}:{line_no} does not match the Chunk schema: {e}") from e

    if not chunks:
        raise ValueError(f"{path} contained no chunks")

    return chunks
