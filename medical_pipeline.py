import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover
    PdfReader = None

try:
    import pdfplumber
except ImportError:  # pragma: no cover
    pdfplumber = None


def clean_page_text(text: str) -> str:
    """
    Clean extracted text from ONE PDF page
    while preserving meaningful content and line structure.
    """

    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"(?i)\s*---\s*PAGE\s*\d+\s*---\s*", "\n", text)
    text = re.sub(r"[\u200b-\u200d\ufeff]", "", text)
    text = "".join(ch for ch in text if ch == "\n" or ch == "\t" or ch.isprintable())
    text = text.replace("\t", " ")

    broken_words = {
        "str ength": "strength",
        "r ecommendations": "recommendations",
        "Car diovascular": "Cardiovascular",
        "Fr equency": "Frequency",
        "tr eatment": "treatment",
        "Pr egnancy": "Pregnancy",
        "pr otocols": "protocols",
        "r esearch": "research",
        "Futur e": "Future",
        "Gr oup": "Group",
        "inter nal": "internal",
        "Exter nal": "External",
        "meth odologist": "methodologist",
        "anal ysis": "analysis",
        "med ications": "medications",
        "pr essure": "pressure",
        "befor e": "before",
        "T arget": "Target",
        "Resear ch": "Research",
        "appr oach": "approach",
        "r eplaced": "replaced",
        "alr eady": "already",
        "ther e": "there",
        "P atient": "Patient",
        "labor atory": "laboratory",
        "diur etics": "diuretics",
        "thr eshold": "threshold",
        "r ecommendation": "recommendation",
    }

    for broken, fixed in broken_words.items():
        text = re.sub(rf"\b{re.escape(broken)}\b", fixed, text, flags=re.IGNORECASE)

    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"[ \t]+([,.!?;:])", r"\1", text)
    text = re.sub(r"([\(\[]) +", r"\1", text)
    text = re.sub(r" +([\)\]])", r"\1", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def clean_full_text(text: str) -> str:
    """
    Clean the complete document while preserving PAGE markers.
    """

    if not text:
        return ""

    pages = re.split(r"(\n--- PAGE \d+ ---\n)", text)
    cleaned_parts = []

    for part in pages:
        if re.fullmatch(r"\n--- PAGE \d+ ---\n", part or ""):
            continue
        cleaned_parts.append(clean_page_text(part))

    text = "\n\n".join(part.strip() for part in cleaned_parts if part.strip())
    return text


def clean_text(text: str) -> str:
    """Normalize text extracted from PDF and remove noisy formatting."""
    if not text:
        return ""

    text = text.replace("\r", "\n")
    text = text.replace("\t", " ")
    text = re.sub(r"[\u200b-\u200d\ufeff]", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Fix common PDF extraction bug where single letters are split by spaces: "H e a l t h"
    text = re.sub(
        r"(?i)\b(?:[a-z]\s+){2,}[a-z]\b",
        lambda match: re.sub(r"\s+", "", match.group(0)),
        text,
    )
    text = re.sub(r"(?i)\s*---\s*PAGE\s*\d+\s*---\s*", " ", text)
    text = re.sub(r"\s*---\s*---\s*", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    text = re.sub(r"([\(\[])\s+", r"\1", text)
    text = re.sub(r"\s+([\)\]])", r"\1", text)
    text = text.strip()
    return text


def extract_title(page_text: str) -> str:
    """Try to infer a document title from the first meaningful lines on a page."""
    lines = [line.strip() for line in (page_text or "").splitlines() if line.strip()]
    for line in lines[:10]:
        if re.fullmatch(r"--- PAGE \d+ ---", line):
            continue
        if re.match(r"^\d+(?:\.\d+)*\s+", line):
            continue
        if len(line) <= 220:
            return line
    return ""


def extract_pdf_text(pdf_path: str) -> Tuple[str, List[Dict[str, Any]], int, List[Dict[str, Any]]]:
    """Extract PDF text and tables while preserving page-level metadata."""
    if PdfReader is None:
        raise ImportError("pypdf is required. Install with: pip install pypdf pdfplumber")

    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    reader = PdfReader(str(pdf_file))
    pages = reader.pages
    page_count = len(pages)
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
            title = extract_title(page_text)
            page_tables: List[Dict[str, Any]] = []

            if plumber_pdf is not None:
                try:
                    extracted_tables = plumber_pdf.pages[idx - 1].extract_tables() or []
                    for table_idx, table in enumerate(extracted_tables, start=1):
                        cleaned_rows = []
                        for row in table or []:
                            cleaned_row = [
                                "" if cell is None else clean_page_text(str(cell))
                                for cell in (row or [])
                            ]
                            if any(cell.strip() for cell in cleaned_row):
                                cleaned_rows.append(cleaned_row)

                        if cleaned_rows:
                            table_entry = {
                                "page": idx,
                                "table_index": table_idx,
                                "rows": cleaned_rows,
                            }
                            tables.append(table_entry)
                            page_tables.append(table_entry)
                except Exception:
                    pass

            pages_data.append({
                "page_number": idx,
                "title": title,
                "text": page_text,
                "tables": page_tables,
            })
            text_parts.append(f"--- PAGE {idx} ---\n{page_text}")
    finally:
        if plumber_pdf is not None:
            plumber_pdf.close()

    full_text = "\n\n".join(text_parts)
    return clean_full_text(full_text), tables, page_count, pages_data


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
    """Split text into overlapping chunks while preserving sentence boundaries when possible."""
    if not text:
        return []

    text = text.strip()
    if not text:
        return []

    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    if not sentences:
        return [text]

    if len(text.split()) <= chunk_size:
        return [text]

    chunks: List[str] = []
    current: List[str] = []
    current_word_count = 0

    for sentence in sentences:
        sentence_word_count = len(sentence.split())

        if sentence_word_count > chunk_size:
            if current:
                chunks.append(" ".join(current))
                current = []
                current_word_count = 0

            parts = sentence.split()
            for i in range(0, len(parts), chunk_size):
                part = " ".join(parts[i:i + chunk_size])
                if part:
                    chunks.append(part)
            continue

        if not current:
            current = [sentence]
            current_word_count = sentence_word_count
            continue

        if current_word_count + sentence_word_count <= chunk_size:
            current.append(sentence)
            current_word_count += sentence_word_count
            continue

        chunks.append(" ".join(current))

        overlap_sentences: List[str] = []
        overlap_word_count = 0
        for prev_sentence in reversed(current):
            prev_word_count = len(prev_sentence.split())
            if overlap_word_count + prev_word_count <= overlap:
                overlap_sentences.insert(0, prev_sentence)
                overlap_word_count += prev_word_count
            else:
                break

        current = overlap_sentences if overlap_sentences else []
        current_word_count = overlap_word_count

        if not current:
            current = [sentence]
            current_word_count = sentence_word_count
        else:
            current.append(sentence)
            current_word_count += sentence_word_count

    if current:
        chunks.append(" ".join(current))

    return chunks


def build_chunk_details(
    chunks: List[str],
    pages_data: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Attach source page and title metadata to each chunk."""
    page_ranges = []
    word_cursor = 0

    for page in pages_data:
        page_word_count = len((page.get("text") or "").split())
        page_ranges.append({
            "page_number": page["page_number"],
            "title": page.get("title", ""),
            "start": word_cursor,
            "end": word_cursor + page_word_count,
        })
        word_cursor += page_word_count

    details = []
    chunk_cursor = 0
    for chunk_id, chunk in enumerate(chunks, start=1):
        chunk_word_count = len(chunk.split())
        chunk_start = chunk_cursor
        chunk_end = chunk_cursor + chunk_word_count
        matching_pages = [
            page for page in page_ranges
            if page["start"] < chunk_end and page["end"] > chunk_start
        ]

        details.append({
            "chunk_id": chunk_id,
            "page_start": matching_pages[0]["page_number"] if matching_pages else None,
            "page_end": matching_pages[-1]["page_number"] if matching_pages else None,
            "title": matching_pages[0]["title"] if matching_pages else "",
            "text": chunk,
        })
        chunk_cursor = chunk_end

    return details


def build_metadata(file_name: str, page_count: int, chunk_count: int, table_count: int, source_type: str = "pdf") -> Dict[str, Any]:
    if isinstance(source_type, int):
        source_type = "pdf" if source_type == 1 else str(source_type)
    elif source_type is None:
        source_type = "pdf"
    else:
        source_type = str(source_type)

    return {
        "file_name": file_name,
        "page_count": page_count,
        "chunk_count": chunk_count,
        "table_count": table_count,
        "source_type": source_type,
        "parser": "pypdf + pdfplumber",
        "output_format": "json",
    }


def parse_medical_document(pdf_path: str, chunk_size: int = 800, overlap: int = 120) -> Dict[str, Any]:
    """Main parsing pipeline for medical PDF documents without AI."""
    text, tables, page_count, pages_data = extract_pdf_text(pdf_path)
    chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
    chunk_details = build_chunk_details(chunks, pages_data)

    doc = {
        "source": {
            "file_name": Path(pdf_path).name,
            "path": str(Path(pdf_path).resolve()),
            "source_type": "pdf",
            "page_count": page_count,
        },
        "content": {
            "raw_text": text,
            "pages": pages_data,
            "chunks": chunks,
            "chunk_details": chunk_details,
            "tables": tables,
        },
        "metadata": build_metadata(
            file_name=Path(pdf_path).name,
            page_count=page_count,
            chunk_count=len(chunks),
            table_count=len(tables),
            source_type="pdf",
        ),
    }
    return doc


if __name__ == "__main__":
    sample_pdf = "9789240033986-eng.pdf"
    if Path(sample_pdf).exists():
        output = parse_medical_document(sample_pdf)
        json_output = json.dumps(output, ensure_ascii=False, indent=2)
        print(json_output)

        with open("output.json", "w", encoding="utf-8") as f:
            f.write(json_output)
            f.write("\n")
    else:
        error_payload = {
            "status": "missing_pdf",
            "message": "Place the medical PDF in the project root and run again.",
            "expected_file": sample_pdf,
        }
        json_output = json.dumps(error_payload, ensure_ascii=False, indent=2)
        print(json_output)

        with open("output.json", "w", encoding="utf-8") as f:
            f.write(json_output)
            f.write("\n")
