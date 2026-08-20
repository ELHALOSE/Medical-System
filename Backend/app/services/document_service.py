import importlib
import importlib.util
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.repositories.chunk import ChunkRepository
from app.repositories.document import DocumentRepository
from app.services.rag_index_service import RAGIndexService


REPO_ROOT = Path(__file__).resolve().parents[3]
UPLOAD_DIR = Path(os.getenv("DOCUMENT_UPLOAD_DIR", str(REPO_ROOT / "Backend" / "uploads")))
DATA_PIPELINE_ROOT = REPO_ROOT / "data-pipline"
DOCUMENT_PARSER_DEVICE = os.getenv("DOCUMENT_PARSER_DEVICE", "cpu").lower()


class DocumentService:
    def __init__(self, db: Session):
        self.document_repository = DocumentRepository(db)
        self.chunk_repository = ChunkRepository(db)
        self.rag_index_service = RAGIndexService()

    def upload_document(self, file: UploadFile, user_id: UUID):
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file must have a filename",
            )
        if Path(file.filename).suffix.lower() != ".pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF uploads are supported",
            )

        document = self.document_repository.create_document(
            file_name=file.filename,
            uploaded_by=user_id,
        )
        target_path = self._document_path(document.id, file.filename)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with target_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return document

    def process_document(self, document_id: UUID, user_id: UUID) -> dict[str, Any]:
        document = self.document_repository.get_by_id(document_id)
        if not document or document.uploaded_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        path = self._find_document_file(document.id)
        parsed = _parse_document(path)
        chunk_details = parsed["content"]["chunk_details"]
        old_chunk_ids = [str(chunk.id) for chunk in self.chunk_repository.list_by_document(document.id)]
        chunks = self.chunk_repository.replace_document_chunks(document.id, chunk_details)
        self.rag_index_service.delete_chunks(old_chunk_ids)
        self.rag_index_service.upsert_chunks(chunks)

        return {
            "document": document,
            "chunk_count": len(chunks),
            "page_count": parsed["metadata"].get("page_count", 0),
            "table_count": parsed["metadata"].get("table_count", 0),
        }

    def _document_path(self, document_id: UUID, filename: str) -> Path:
        safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", Path(filename).name)
        return UPLOAD_DIR / f"{document_id}_{safe_name}"

    def _find_document_file(self, document_id: UUID) -> Path:
        matches = list(UPLOAD_DIR.glob(f"{document_id}_*"))
        if not matches:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Uploaded document file not found",
            )
        return matches[0]


def _parse_document(path: Path) -> dict[str, Any]:
    _force_cpu_document_parser()
    _ensure_data_pipeline_package()
    pipeline = importlib.import_module("data_pipeline.pipeline")

    try:
        return pipeline.parse_medical_document(str(path))
    except Exception as exc:
        return _parse_document_with_pypdf(path, exc)


def _force_cpu_document_parser() -> None:
    if DOCUMENT_PARSER_DEVICE == "cpu":
        os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
        os.environ.setdefault("DOCLING_DEVICE", "cpu")


def _parse_document_with_pypdf(path: Path, original_error: Exception) -> dict[str, Any]:
    from pypdf import PdfReader

    chunking = importlib.import_module("data_pipeline.chunking")
    metadata_module = importlib.import_module("data_pipeline.metadata")

    try:
        reader = PdfReader(str(path))
        pages_data = []
        text_parts = []
        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            pages_data.append(
                {
                    "page_number": page_number,
                    "title": "",
                    "text": page_text,
                    "tables": [],
                }
            )
            text_parts.append(f"--- PAGE {page_number} ---\n{page_text}")

        text = "\n\n".join(text_parts)
        chunks = chunking.chunk_text(text)
        chunk_details = chunking.build_chunk_details(chunks, pages_data, text)
        return {
            "source": {
                "file_name": path.name,
                "path": str(path.resolve()),
                "source_type": "pdf",
                "page_count": len(pages_data),
            },
            "content": {
                "raw_text": text,
                "pages": pages_data,
                "chunks": chunks,
                "chunk_details": chunk_details,
                "tables": [],
            },
            "metadata": metadata_module.build_metadata(
                path.name,
                len(pages_data),
                len(chunks),
                0,
                "pdf",
            ),
        }
    except Exception as fallback_error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Document parsing failed with Docling and pypdf fallback. "
                f"Docling error: {original_error}. Fallback error: {fallback_error}"
            ),
        ) from fallback_error


def _ensure_data_pipeline_package() -> None:
    if "data_pipeline" in sys.modules:
        return

    init_path = DATA_PIPELINE_ROOT / "__init__.py"
    spec = importlib.util.spec_from_file_location(
        "data_pipeline",
        init_path,
        submodule_search_locations=[str(DATA_PIPELINE_ROOT)],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["data_pipeline"] = module
    spec.loader.exec_module(module)