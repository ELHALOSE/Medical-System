"""
Task 1: Prompt Engineering & Clinical Guardrails
Author: Meriam
Description: Handcrafted medical prompts with strict zero-hallucination guardrails,
             mandatory citations [Doc-X], refusal protocol, and emergency triage.
"""

from typing import Dict, List, Optional


class MedicalPromptEngineer:
    """
    Constructs clinical-grade prompts for Open-Source LLMs.
    """

    DEFAULT_SYSTEM_PROMPT = (
        "You are an expert Clinical AI Medical Assistant specializing in evidence-based medicine.\n"
        "Your duty is to assist healthcare providers and patients by answering medical inquiries "
        "ACCURATELY, SAFELY, and CONCISELY based EXCLUSIVELY on the provided clinical documents.\n\n"
        "### CLINICAL OPERATING GUIDELINES ###\n"
        "1. STRICT GROUNDEDNESS:\n"
        "   - Use ONLY the facts provided in the <context> section.\n"
        "   - Do NOT assume, extrapolate, or use outside medical knowledge not verified in the context.\n"
        "   - If the context does not contain sufficient information, state: "
        "'Based on the provided medical reference documents, there is insufficient evidence to answer this question.'\n\n"
        "2. MANDATORY CITATION PROTOCOL:\n"
        "   - Every claim, dosage, or clinical threshold MUST be cited using [Doc-1], [Doc-2], etc.\n\n"
        "3. MEDICAL DISCLAIMER & EMERGENCY TRIAGE:\n"
        "   - If the query describes acute life-threatening symptoms (e.g. crushing chest pain, loss of consciousness, stroke symptoms), "
        "immediately advise seeking emergency medical attention (Call 911 / 123) BEFORE providing educational info.\n"
        "   - Always conclude responses with a concise professional medical disclaimer.\n\n"
        "4. TONE & STRUCTURE:\n"
        "   - Professional, empathetic, objective, and clinically precise."
    )

    FEW_SHOT_EXAMPLES = [
        {
            "query": "What is the systolic blood pressure threshold for starting pharmacological treatment?",
            "context": (
                "<context>\n"
                "[Doc-1 | Source: WHO_Hypertension_Guideline.pdf | Page: 14]\n"
                "WHO recommends initiating pharmacological antihypertensive treatment in individuals with a confirmed diagnosis "
                "of hypertension and systolic blood pressure >= 140 mmHg or diastolic blood pressure >= 90 mmHg.\n"
                "</context>"
            ),
            "response": (
                "According to clinical guidelines:\n\n"
                "• **Threshold:** Pharmacological treatment is recommended when **Systolic BP >= 140 mmHg** "
                "or **Diastolic BP >= 90 mmHg** in confirmed hypertension [Doc-1].\n\n"
                "*Disclaimer: This information is for clinical reference only. Consult a physician for direct medical care.*"
            )
        }
    ]

    def __init__(
        self,
        system_prompt: Optional[str] = None,
        include_few_shot: bool = True
    ):
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        self.include_few_shot = include_few_shot

    def build_user_prompt(self, query: str, formatted_context: str) -> str:
        return (
            f"Verified Medical Reference Documents:\n\n"
            f"{formatted_context}\n\n"
            f"### CLINICIAN / PATIENT QUESTION ###\n"
            f"Question: {query}\n\n"
            f"Provide a strictly grounded clinical answer citing the documents ([Doc-X]) for all claims."
        )

    def format_chat_messages(
        self,
        query: str,
        formatted_context: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        messages: List[Dict[str, str]] = [{"role": "system", "content": self.system_prompt}]

        if self.include_few_shot:
            for ex in self.FEW_SHOT_EXAMPLES:
                messages.append({"role": "user", "content": f"{ex['context']}\n\nQuestion: {ex['query']}"})
                messages.append({"role": "assistant", "content": ex['response']})

        if chat_history:
            for turn in chat_history:
                messages.append({"role": turn.get("role", "user"), "content": turn.get("content", "")})

        messages.append({"role": "user", "content": self.build_user_prompt(query, formatted_context)})
        return messages
