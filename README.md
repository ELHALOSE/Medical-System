# Medical-System

This project implements a non-AI document parsing pipeline for medical PDFs.

## What it does
- Parses PDF text and tables
- Removes noisy formatting and whitespace issues
- Splits long text into overlapping chunks
- Builds JSON-ready metadata
- Exports a clean structure for downstream medical systems

## Structure
- medical_pipeline.py: main parsing and chunking logic
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