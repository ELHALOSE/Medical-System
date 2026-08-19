from typing import Any, Dict


def build_metadata(file_name: str, page_count: int, chunk_count: int, table_count: int, source_type: str = "pdf") -> Dict[str, Any]:
    if isinstance(source_type, int):
        source_type = "pdf" if source_type == 1 else str(source_type)
    elif source_type is None:
        source_type = "pdf"
    else:
        source_type = str(source_type)
    return {"file_name": file_name, "page_count": page_count, "chunk_count": chunk_count, "table_count": table_count, "source_type": source_type, "parser": "pypdf + pdfplumber", "output_format": "json"}