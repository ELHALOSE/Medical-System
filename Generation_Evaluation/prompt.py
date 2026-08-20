from typing import Any


SYSTEM_PROMPT = """
You are a medical question-answering assistant.

Answer the question using ONLY the provided medical documents.

Rules:
1. Use only information supported by the retrieved documents.
2. Do not invent medical facts.
3. If the answer is not found in the documents, say:
   "The answer was not found in the provided documents."
4. Cite the supporting document using [Doc-1], [Doc-2], etc.
5. Keep the answer concise and clinically precise.
6. Do not provide unsupported diagnoses or treatment recommendations.
"""


def build_prompt(
    query: str,
    retrieved_chunks: list[dict[str, Any]],
    chat_history: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:

    context_parts = []

    for i, chunk in enumerate(retrieved_chunks, start=1):

        metadata = chunk.get("metadata") or {}

        source = (
            metadata.get("source_doc")
            or metadata.get("title")
            or "Unknown document"
        )

        page_start = metadata.get("page_start")
        page_end = metadata.get("page_end")

        if page_start and page_end:
            page_info = f"Pages: {page_start}-{page_end}"
        elif page_start:
            page_info = f"Page: {page_start}"
        else:
            page_info = ""

        context_parts.append(
            f"[Doc-{i}]\n"
            f"Source: {source}\n"
            f"{page_info}\n"
            f"Content:\n{chunk.get('text', '')}"
        )

    context = "\n\n".join(context_parts)

    user_prompt = f"""
Medical Documents:

{context}
"""

    if chat_history:
        history = "\n".join(
            f"{message.get('role', 'user')}: "
            f"{message.get('content', '')}"
            for message in chat_history
        )

        user_prompt += f"""

Conversation History:

{history}
"""

    user_prompt += f"""

Question:

{query}

Answer:
"""

    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT.strip(),
        },
        {
            "role": "user",
            "content": user_prompt.strip(),
        },
    ]