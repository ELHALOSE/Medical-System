"""
schemas.py
----------
The `Chunk` shape here is the integration contract with the chunking stage.
It matches the `chunk_details` entries in the output.json produced by the
cleaning/chunking pipeline. If that schema changes, this is the one place
to update on the retrieval side.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Chunk:
    chunk_id: str
    text: str
    title: str = ""
    page_start: int = 0
    page_end: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "Chunk":
        return cls(
            chunk_id=str(data["chunk_id"]),
            text=data["text"],
            title=data.get("title", ""),
            page_start=data.get("page_start", 0),
            page_end=data.get("page_end", 0),
        )

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "title": self.title,
            "page_start": self.page_start,
            "page_end": self.page_end,
        }


def load_chunks(path: str | Path) -> list[Chunk]:
    """Load chunks from the chunking pipeline's output.json.

    Expects a JSON file with structure:
        { "content": { "chunk_details": [ {...}, ... ] } }
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found - run the chunking pipeline first."
        )

    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    try:
        chunk_details = data["content"]["chunk_details"]
    except (KeyError, TypeError) as e:
        raise ValueError(
            f"{path} does not have the expected structure "
            "(content.chunk_details): {e}"
        ) from e

    chunks = []
    for i, item in enumerate(chunk_details):
        try:
            chunks.append(Chunk.from_dict(item))
        except (KeyError, TypeError) as e:
            raise ValueError(
                f"{path}: chunk_details[{i}] does not match the Chunk schema: {e}"
            ) from e

    if not chunks:
        raise ValueError(f"{path} contained no chunks")

    return chunks
