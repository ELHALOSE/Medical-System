"""
Task 2: Context Construction & Metadata Formatting
Author: Meriam
Description: Dynamically constructs and formats structured medical context from retrieved chunks,
             organizing metadata into clean XML blocks and enforcing token limits.
"""

from typing import List, Dict, Any, Union


class MedicalContextBuilder:
    """
    Constructs indexed XML medical context blocks ([Doc-1], [Doc-2]) from retrieval results.
    """

    def __init__(self, max_context_chars: int = 10000):
        self.max_context_chars = max_context_chars

    def build_context(self, retrieved_items: List[Union[Dict[str, Any], Any]]) -> Dict[str, Any]:
        if not retrieved_items:
            return {
                "formatted_context": "<context>\nNo relevant medical reference documents found.\n</context>",
                "sources": [],
                "doc_count": 0
            }

        formatted_docs = []
        sources = []
        current_chars = 0

        for idx, item in enumerate(retrieved_items, start=1):
            if isinstance(item, dict):
                text = item.get("text", "").strip()
                meta = item.get("metadata", {})
                score = item.get("score", 1.0)
                chunk_id = item.get("chunk_id", f"chunk_{idx}")
            else:
                text = getattr(item, "text", "").strip()
                meta = getattr(item, "metadata", {})
                score = getattr(item, "score", 1.0)
                chunk_id = getattr(item, "chunk_id", f"chunk_{idx}")

            source_file = meta.get("source_doc") or meta.get("source") or "WHO_Hypertension_Guideline.pdf"
            page_num = meta.get("page_number") or meta.get("page") or "N/A"
            section = meta.get("section_title") or meta.get("section") or ""
            section_str = f" | Section: {section}" if section else ""
            score_str = f" | Score: {score:.2f}" if isinstance(score, (int, float)) else ""

            doc_header = f"[Doc-{idx} | Source: {source_file} | Page: {page_num}{section_str}{score_str}]"
            doc_block = f"{doc_header}\n{text}\n"

            if current_chars + len(doc_block) > self.max_context_chars:
                break

            formatted_docs.append(doc_block)
            current_chars += len(doc_block)

            sources.append({
                "doc_id": f"Doc-{idx}",
                "chunk_id": chunk_id,
                "source": source_file,
                "page": page_num,
                "section": section,
                "score": score
            })

        formatted_context = "<context>\n" + "\n".join(formatted_docs) + "\n</context>"

        return {
            "formatted_context": formatted_context,
            "sources": sources,
            "doc_count": len(formatted_docs)
        }
