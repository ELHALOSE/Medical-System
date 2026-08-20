from typing import List, Dict, Any


class MedicalContextBuilder:

    def __init__(self, max_chars: int = 10000):
        self.max_chars = max_chars

    def build(
        self,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        if not retrieved_chunks:
            return {
                "context": (
                    "<context>\n"
                    "No relevant medical documents were retrieved.\n"
                    "</context>"
                ),
                "sources": []
            }

        documents = []
        sources = []
        total_chars = 0

        for index, chunk in enumerate(
            retrieved_chunks,
            start=1
        ):

            text = str(
                chunk.get("text", "")
            ).strip()

            if not text:
                continue

            metadata = chunk.get(
                "metadata",
                {}
            ) or {}

            source = (
                metadata.get("source_doc")
                or metadata.get("source")
                or "Unknown"
            )

            page = (
                metadata.get("page_number")
                or metadata.get("page")
                or "N/A"
            )

            section = (
                metadata.get("section_title")
                or metadata.get("section")
                or ""
            )

            header = (
                f"[Doc-{index} | "
                f"Source: {source} | "
                f"Page: {page}"
            )

            if section:
                header += f" | Section: {section}"

            header += "]"

            block = (
                f"{header}\n"
                f"{text}\n"
            )

            if total_chars + len(block) > self.max_chars:
                break

            documents.append(block)

            sources.append({
                "doc_id": f"Doc-{index}",
                "source": source,
                "page": page,
                "section": section,
                "chunk_id": chunk.get(
                    "chunk_id"
                )
            })

            total_chars += len(block)

        context = (
            "<context>\n"
            + "\n".join(documents)
            + "\n</context>"
        )

        return {
            "context": context,
            "sources": sources
        }