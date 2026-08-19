from pathlib import Path
import re
from typing import Any, Dict, List, Tuple

from docling.document_converter import DocumentConverter
from .text_cleaning import clean_full_text, clean_page_text


def extract_title(page_text: str) -> str:
    lines = [line.strip() for line in (page_text or "").splitlines() if line.strip()]
    for line in lines[:10]:
        if re.fullmatch(r"--- PAGE \d+ ---", line) or re.match(r"^\d+(?:\.\d+)*\s+", line):
            continue
        if len(line) <= 220:
            return line
    return ""


def _extract_with_docling(document: Any) -> Tuple[str, List[Dict[str, Any]]]:
    text = clean_full_text(document.export_to_markdown())
    tables: List[Dict[str, Any]] = []

    for table_index, table in enumerate(getattr(document, "tables", []), start=1):
        try:
            dataframe = table.export_to_dataframe(doc=document)
            rows = [
                ["" if value is None else clean_page_text(str(value)) for value in row]
                for row in dataframe.fillna("").values.tolist()
            ]
        except Exception:
            rows = []

        if rows:
            provenance = getattr(table, "prov", [])
            page_number = getattr(provenance[0], "page_no", None) if provenance else None
            tables.append({"page": page_number, "table_index": table_index, "rows": rows})

    return text, tables


def _extract_page_data(document: Any, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    page_texts: Dict[int, List[str]] = {}

    for item, _ in document.iterate_items():
        item_text = getattr(item, "text", "")
        if not item_text:
            continue
        provenance = getattr(item, "prov", [])
        page_numbers = {getattr(origin, "page_no", 1) for origin in provenance}
        for page_number in page_numbers or {1}:
            page_texts.setdefault(page_number, []).append(item_text)

    page_count = len(getattr(document, "pages", {}))
    page_count = max(page_count, max(page_texts, default=1))
    pages_data = []
    for page_number in range(1, page_count + 1):
        page_text = clean_page_text("\n".join(page_texts.get(page_number, [])))
        page_tables = [table for table in tables if table["page"] == page_number]
        pages_data.append({"page_number": page_number, "title": extract_title(page_text), "text": page_text, "tables": page_tables})
    return pages_data


def _build_page_aware_text(pages_data: List[Dict[str, Any]]) -> str:
    parts = []
    for page in pages_data:
        parts.append(f"--- PAGE {page['page_number']} ---\n{page.get('text', '')}")
    return "\n\n".join(parts)


def extract_pdf_text(pdf_path: str) -> Tuple[str, List[Dict[str, Any]], int, List[Dict[str, Any]]]:
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    converter = DocumentConverter()
    document = converter.convert(str(pdf_file)).document
    _, tables = _extract_with_docling(document)
    pages_data = _extract_page_data(document, tables)
    text = _build_page_aware_text(pages_data)
    return text, tables, len(pages_data), pages_data