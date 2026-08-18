from medical_pipeline import build_metadata, chunk_text, clean_full_text, clean_text, parse_medical_document


def test_clean_text_removes_noise_and_normalizes_whitespace():
    raw = "  H e a l t h   \n\n  report  2024   \t with   extra   spaces  "
    cleaned = clean_text(raw)
    assert "Health report 2024 with extra spaces" in cleaned
    assert "\n\n" not in cleaned


def test_chunk_text_creates_multiple_chunks_with_overlap():
    text = " ".join([f"Sentence {i} " for i in range(1, 21)])
    chunks = chunk_text(text, chunk_size=80, overlap=20)
    assert len(chunks) >= 2
    assert all(len(chunk) <= 120 for chunk in chunks)


def test_build_metadata_contains_key_fields():
    metadata = build_metadata("sample.pdf", 3, 14, 2, 1)
    assert metadata["file_name"] == "sample.pdf"
    assert metadata["page_count"] == 3
    assert metadata["chunk_count"] == 14
    assert metadata["table_count"] == 2
    assert metadata["source_type"] == "pdf"


def test_clean_full_text_removes_page_markers():
    raw = "--- PAGE 1 ---\nFirst paragraph.\n--- PAGE 2 ---\nSecond paragraph."
    cleaned = clean_full_text(raw)
    assert "--- PAGE" not in cleaned
    assert "First paragraph." in cleaned
    assert "Second paragraph." in cleaned


def test_parse_medical_document_keeps_page_number_title_and_table_structure():
    result = parse_medical_document("9789240033986-eng.pdf")
    assert "pages" in result["content"]
    assert result["content"]["pages"][0]["page_number"] == 1
    assert "title" in result["content"]["pages"][0]
    assert "tables" in result["content"]["pages"][0]
