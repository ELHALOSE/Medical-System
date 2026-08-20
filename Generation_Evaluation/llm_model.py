
import time
from typing import Any

from huggingface_hub import InferenceClient


class OpenSourceLLM:

    def __init__(
        self,
        model_id: str,
        hf_token: str | None = None,
    ):
        if not hf_token:
            raise ValueError(
                "HF_TOKEN is required for Hugging Face Inference API."
            )

        self.model_id = model_id

        self.client = InferenceClient(
            token=hf_token,
            provider="novita",
        
        )

    def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 512,
    ) -> dict[str, Any]:

        start_time = time.time()

        response = self.client.chat_completion(
            model=self.model_id,
            messages=messages,
            max_tokens=max_tokens,
            temperature=max(temperature, 0.01),
            top_p=0.9,
        )

        answer = response.choices[0].message.content

        latency = round(time.time() - start_time, 3)

        return {
            "answer": answer.strip(),
            "model_id": self.model_id,
            "latency_seconds": latency,
            "sources": [],
        }