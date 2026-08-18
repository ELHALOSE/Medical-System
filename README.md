# Medical-System

This project implements a non-AI document parsing pipeline for medical PDFs.

## What it does
- Parses PDF text and tables
- Removes noisy formatting and whitespace issues
- Splits long text into overlapping chunks
- Builds JSON-ready metadata
- Exports a clean structure for downstream medical systems

## Structure
- medical_pipeline.py: compatibility facade and command-line entry point
- medical_system/text_cleaning.py: page and document text cleaning
- medical_system/extraction.py: PDF text, title, and table extraction
- medical_system/chunking.py: text chunking and page metadata mapping
- medical_system/metadata.py: output metadata construction
- medical_system/pipeline.py: main document parsing workflow
- medical_system/__init__.py: public package exports
- tests/test_medical_pipeline.py: validation tests

## Install
```bash
pip install -r requirements.txt
```

## Run
```bash
python medical_pipeline.py
```

## Output shape
The script returns a JSON-like Python dictionary with:
- source
- content.raw_text
- content.chunks
- content.tables
- metadata

This pipeline intentionally ignores scanned images/diagrams because they are not machine-readable text without OCR. For image-heavy PDFs, add OCR later as a separate stage.