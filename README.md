# Medical-System

This project implements a non-AI document parsing pipeline for medical PDFs.

## What it does
- Parses PDF text and tables
- Removes noisy formatting and whitespace issues
- Splits long text into overlapping chunks
- Builds JSON-ready metadata
- Exports a clean structure for downstream medical systems

## Structure
- main.py: command-line entry point
- data-pipline/text_cleaning.py: page and document text cleaning
- data-pipline/extraction.py: PDF text, title, and table extraction
- data-pipline/chunking.py: text chunking and page metadata mapping
- data-pipline/metadata.py: output metadata construction
- data-pipline/pipeline.py: main document parsing workflow
- data-pipline/__init__.py: public package exports
- source/: input medical PDF files

## Install
```bash
pip install -r requirements.txt
```

## Run
```bash
python main.py
```

## Output shape
The script returns a JSON-like Python dictionary with:
- source
- content.raw_text
- content.chunks
- content.tables
- metadata

This pipeline intentionally ignores scanned images/diagrams because they are not machine-readable text without OCR. For image-heavy PDFs, add OCR later as a separate stage.