# 🩺 Generation & Evaluation Module (Meriam's Deliverables)

This package implements the **Generation and Evaluation layers** for the Medical RAG System from scratch using open-source models.

---

## 📁 File Structure & Responsibilities

| File | Task | Key Functionality |
| :--- | :--- | :--- |
| **`prompt.py`** | **1) Prompt Engineering** | Medical System Prompt, Strict Groundedness, Citations `[Doc-X]`, Refusals & Emergency Redirection. |
| **`context.py`** | **2) Context Construction** | Dynamic XML formatting (`<context>`), Metadata extraction (Pages/Sections), Token budgeting. |
| **`llm_model.py`** | **3) Open-Source LLM Model** | `Meta-Llama-3-8B-Instruct` / `BioMistral-7B`, 4-bit Quantization (bitsandbytes), HF Inference API. |
| **`evaluation.py`** | **4) Evaluation From Scratch** | NLI DeBERTa (Faithfulness), Cosine Math (Relevance), Citation Accuracy & Official 18-Q Report Card. |
| **`pipeline.py`** | **Master Orchestrator** | Coordinates the 4 modules into a unified, clean interface. |

---

## ⚡ Quick Test

```python
from Generation_Evaluation import GenerationPipeline

# Initialize
pipeline = GenerationPipeline(backend="mock")

# Ask
result = pipeline.generate_answer("What is the first-line treatment for hypertension?")

print(result["answer"])
print(result["evaluation"])
```
