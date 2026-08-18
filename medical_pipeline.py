import json
from pathlib import Path

from medical_system import (
    build_chunk_details,
    build_metadata,
    chunk_text,
    clean_full_text,
    clean_page_text,
    clean_text,
    extract_pdf_text,
    extract_title,
    parse_medical_document,
)

__all__ = [
    "build_chunk_details",
    "build_metadata",
    "chunk_text",
    "clean_full_text",
    "clean_page_text",
    "clean_text",
    "extract_pdf_text",
    "extract_title",
    "parse_medical_document",
]


if __name__ == "__main__":
    sample_pdf = "9789240033986-eng.pdf"
    if Path(sample_pdf).exists():
        json_output = json.dumps(parse_medical_document(sample_pdf), ensure_ascii=False, indent=2)
    else:
        json_output = json.dumps(
            {
                "status": "missing_pdf",
                "message": "Place the medical PDF in the project root and run again.",
                "expected_file": sample_pdf,
            },
            ensure_ascii=False,
            indent=2,
        )
    print(json_output)
    Path("output.json").write_text(json_output + "\n", encoding="utf-8")