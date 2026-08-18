from pathlib import Path
from typing import Any, Dict
from .chunking import build_chunk_details, chunk_text
from .extraction import extract_pdf_text
from .metadata import build_metadata


def parse_medical_document(pdf_path: str, chunk_size: int = 800, overlap: int = 120) -> Dict[str, Any]:
    text, tables, page_count, pages_data = extract_pdf_text(pdf_path)
    chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
    return {"source": {"file_name": Path(pdf_path).name, "path": str(Path(pdf_path).resolve()), "source_type": "pdf", "page_count": page_count}, "content": {"raw_text": text, "pages": pages_data, "chunks": chunks, "chunk_details": build_chunk_details(chunks, pages_data), "tables": tables}, "metadata": build_metadata(Path(pdf_path).name, page_count, len(chunks), len(tables), "pdf")}