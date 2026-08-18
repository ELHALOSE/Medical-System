from typing import Any, Dict, List
import re


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
    if not text or not text.strip():
        return []
    text = text.strip()
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    if len(text) <= chunk_size:
        return [text]
    chunks: List[str] = []
    current: List[str] = []
    current_word_count = 0
    for sentence in sentences:
        count = len(sentence)
        if count > chunk_size:
            if current:
                chunks.append(" ".join(current))
                current, current_word_count = [], 0
            words = sentence.split()
            part: List[str] = []
            part_length = 0
            for word in words:
                if part and part_length + len(word) + 1 > chunk_size:
                    chunks.append(" ".join(part))
                    part, part_length = [], 0
                part.append(word)
                part_length += len(word) + (1 if part_length else 0)
            if part:
                chunks.append(" ".join(part))
            continue
        if current and current_word_count + count + 1 > chunk_size:
            chunks.append(" ".join(current))
            overlap_sentences: List[str] = []
            overlap_length = 0
            for previous in reversed(current):
                previous_count = len(previous)
                if overlap_length + previous_count + 1 <= overlap:
                    overlap_sentences.insert(0, previous)
                    overlap_length += previous_count + 1
                else:
                    break
            current, current_word_count = overlap_sentences, overlap_length
        current.append(sentence)
        current_word_count += count + (1 if current_word_count else 0)
    if current:
        chunks.append(" ".join(current))
    return chunks


def build_chunk_details(chunks: List[str], pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    page_ranges = []
    cursor = 0
    for page in pages_data:
        count = len((page.get("text") or "").split())
        page_ranges.append({"page_number": page["page_number"], "title": page.get("title", ""), "start": cursor, "end": cursor + count})
        cursor += count
    details = []
    chunk_cursor = 0
    for chunk_id, chunk in enumerate(chunks, start=1):
        count = len(chunk.split())
        matching = [page for page in page_ranges if page["start"] < chunk_cursor + count and page["end"] > chunk_cursor]
        details.append({"chunk_id": chunk_id, "page_start": matching[0]["page_number"] if matching else None, "page_end": matching[-1]["page_number"] if matching else None, "title": matching[0]["title"] if matching else "", "text": chunk})
        chunk_cursor += count
    return details