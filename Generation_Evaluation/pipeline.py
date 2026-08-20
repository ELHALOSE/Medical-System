from typing import Any

from .llm_model import OpenSourceLLM
from .prompt import build_prompt


class GenerationPipeline:

    def __init__(
        self,
        model_id: str,
        hf_token: str | None = None,
    ):
        self.llm = OpenSourceLLM(
            model_id=model_id,
            hf_token=hf_token,
        )

    def generate_answer(
        self,
        query: str,
        retrieved_chunks: list[dict[str, Any]],
        chat_history: list[dict[str, str]] | None = None,
        temperature: float = 0.1,
    ) -> dict[str, Any]:

        messages = build_prompt(
            query=query,
            retrieved_chunks=retrieved_chunks,
            chat_history=chat_history,
        )

        result = self.llm.generate(
            messages=messages,
            temperature=temperature,
        )

        return {
            "answer": result["answer"],
            "sources": result.get("sources", []),
            "evaluation": {},
            "model_id": result["model_id"],
            "latency_seconds": result["latency_seconds"],
        }