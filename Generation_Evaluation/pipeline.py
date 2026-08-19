"""
Generation & Evaluation Master Pipeline
Author: Meriam
Description: Integrates Prompt (Task 1), Context Builder (Task 2), LLM Model (Task 3), and Evaluator (Task 4).
"""

from typing import List, Dict, Any, Optional

from Generation_Evaluation.prompt import MedicalPromptEngineer
from Generation_Evaluation.context import MedicalContextBuilder
from Generation_Evaluation.llm_model import OpenSourceLLM
from Generation_Evaluation.evaluation import MedicalEvaluator


class GenerationPipeline:
    """
    Unified pipeline for Meriam's deliverables.
    """

    def __init__(
        self,
        model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct",
        backend: str = "mock",
        hf_token: Optional[str] = None
    ):
        self.prompt_engineer = MedicalPromptEngineer()
        self.context_builder = MedicalContextBuilder()
        self.llm = OpenSourceLLM(model_id=model_id, backend=backend, hf_token=hf_token)
        self.evaluator = MedicalEvaluator()

    def generate_answer(
        self,
        query: str,
        retrieved_chunks: Optional[List[Dict[str, Any]]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        if not retrieved_chunks:
            retrieved_chunks = [
                {
                    "text": "WHO recommends initiating pharmacological treatment in confirmed hypertension with SBP >= 140 or DBP >= 90 mmHg. First-line drugs: thiazide diuretics, ACE inhibitors/ARBs, and CCBs.",
                    "metadata": {"source_doc": "WHO_Hypertension_Guideline.pdf", "page_number": 14, "section_title": "1.4 Pharmacological Treatment"},
                    "score": 0.95
                }
            ]

        # 1. Build XML Context (Task 2)
        ctx_data = self.context_builder.build_context(retrieved_chunks)
        formatted_context = ctx_data["formatted_context"]
        sources = ctx_data["sources"]

        # 2. Format Prompt (Task 1)
        messages = self.prompt_engineer.format_chat_messages(
            query=query,
            formatted_context=formatted_context,
            chat_history=chat_history
        )

        # 3. LLM Inference (Task 3)
        gen_res = self.llm.generate(messages=messages, temperature=temperature)
        answer = gen_res["answer"]

        # 4. Self-Evaluation (Task 4)
        faith_score = self.evaluator.evaluate_faithfulness(answer, formatted_context)
        rel_score = self.evaluator.evaluate_relevance(query, answer)

        return {
            "query": query,
            "answer": answer,
            "sources": sources,
            "latency_seconds": gen_res["latency_seconds"],
            "model_id": gen_res["model_id"],
            "evaluation": {
                "faithfulness_score": faith_score,
                "relevance_score": rel_score
            }
        }
