from typing import Any, Dict, List

from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
    if not text or not text.strip():
        return []
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
        strip_whitespace=True,
    )
    return splitter.split_text(text.strip())


def build_chunk_details(
    chunks: List[str],
    pages_data: List[Dict[str, Any]],
    source_text: str = "",
) -> List[Dict[str, Any]]:
    page_ranges = []
    for page in pages_data:
        marker = f"--- PAGE {page['page_number']} ---\n"
        start = source_text.find(marker) if source_text else -1
        if start < 0:
            start = page_ranges[-1]["end"] + 2 if page_ranges else 0
        content_start = start + len(marker)
        page_ranges.append({"page_number": page["page_number"], "title": page.get("title", ""), "start": content_start, "end": content_start + len(page.get("text") or "")})
    details = []
    search_start = 0
    for chunk_id, chunk in enumerate(chunks, start=1):
        chunk_start = source_text.find(chunk, search_start) if source_text else search_start
        if chunk_start < 0:
            chunk_start = search_start
        chunk_end = chunk_start + len(chunk)
        matching = [page for page in page_ranges if page["start"] < chunk_end and page["end"] > chunk_start]
        details.append({"chunk_id": chunk_id, "page_start": matching[0]["page_number"] if matching else None, "page_end": matching[-1]["page_number"] if matching else None, "title": matching[0]["title"] if matching else "", "text": chunk})
        search_start = max(chunk_start + 1, chunk_end - 120)
    return details