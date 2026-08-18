from pathlib import Path
import re
from typing import Any, Dict, List, Tuple

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None
try:
    import pdfplumber
except ImportError:
    pdfplumber = None
from .text_cleaning import clean_full_text, clean_page_text


def extract_title(page_text: str) -> str:
    lines = [line.strip() for line in (page_text or "").splitlines() if line.strip()]
    for line in lines[:10]:
        if re.fullmatch(r"--- PAGE \d+ ---", line) or re.match(r"^\d+(?:\.\d+)*\s+", line):
            continue
        if len(line) <= 220:
            return line
    return ""


def extract_pdf_text(pdf_path: str) -> Tuple[str, List[Dict[str, Any]], int, List[Dict[str, Any]]]:
    if PdfReader is None:
        raise ImportError("pypdf is required. Install with: pip install pypdf pdfplumber")
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    pages = PdfReader(str(pdf_file)).pages
    text_parts: List[str] = []
    tables: List[Dict[str, Any]] = []
    pages_data: List[Dict[str, Any]] = []
    plumber_pdf = None
    if pdfplumber is not None:
        try:
            plumber_pdf = pdfplumber.open(str(pdf_file))
        except Exception:
            plumber_pdf = None
    try:
        for idx, page in enumerate(pages, start=1):
            page_text = clean_page_text(page.extract_text() or "")
            page_tables: List[Dict[str, Any]] = []
            if plumber_pdf is not None:
                try:
                    extracted = plumber_pdf.pages[idx - 1].extract_tables() or []
                    for table_idx, table in enumerate(extracted, start=1):
                        rows = [["" if cell is None else clean_page_text(str(cell)) for cell in (row or [])] for row in table or []]
                        rows = [row for row in rows if any(cell.strip() for cell in row)]
                        if rows:
                            entry = {"page": idx, "table_index": table_idx, "rows": rows}
                            tables.append(entry)
                            page_tables.append(entry)
                except Exception:
                    pass
            pages_data.append({"page_number": idx, "title": extract_title(page_text), "text": page_text, "tables": page_tables})
            text_parts.append(f"--- PAGE {idx} ---\n{page_text}")
    finally:
        if plumber_pdf is not None:
            plumber_pdf.close()
    return clean_full_text("\n\n".join(text_parts)), tables, len(pages), pages_data