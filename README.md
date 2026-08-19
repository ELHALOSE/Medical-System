# 🏥 Clinical AI Medical RAG System
> **An End-to-End, Open-Source, Evidence-Grounded Medical Question Answering & Evaluation Framework**  
> Designed for Clinical Practice Guidelines (WHO Hypertension Treatment in Adults).

---

## 👥 Team & Architecture Distribution

```
Medical-System/
├── data-pipline/              # [Stage 1 - Nour] Parsing, Cleaning, Chunking & Metadata
├── Retrival/                  # [Stage 2 - Abdelrahman] PubMedBERT, ChromaDB, BM25 Hybrid & Reranker
├── src/                       # [Stage 3 & 4 - Meriam] Medical Prompt, Open-Source LLM & 4-Pillar Evaluation
│   ├── generation/            # Prompt Engineering, Guardrails, XML Context Builder, LLM Engine
│   ├── evaluation/            # NLI Faithfulness, Cosine Relevance, ROUGE-L, 18-Q Report Card
│   └── medical_rag_pipeline.py# Master Orchestrator Pipeline
├── demo_full_pipeline.py      # End-to-End System Walkthrough & Stage-by-Stage Inspector
├── main.py                    # Interactive Clinical Assistant CLI
└── requirements.txt           # Unified Open-Source Dependencies
```

---

## 🌟 Key Capabilities

1. **Strict Evidence Grounding (Zero-Hallucination):**
   - Incorporates strict clinical guardrails prohibiting unsupported extrapolation.
   - Requires bracketed document and section citations (e.g. `[Doc-1]`).

2. **Hybrid Search & Reranking:**
   - Combines dense semantic retrieval (`PubMedBERT` + `ChromaDB`) with lexical precision (`BM25`) using Reciprocal Rank Fusion (RRF).
   - Re-scores candidates using cross-encoder reranking (`BAAI/bge-reranker-v2-m3`).

3. **100% Open-Source LLM Inference:**
   - Supports local GPU quantized inference (`Meta-Llama-3-8B-Instruct`, `BioMistral-7B`) and Hugging Face Inference API.
   - Zero reliance on closed-source/proprietary APIs.

4. **Official 4-Pillar Evaluation Framework:**
   - **Retrieval Quality:** Precision@K and Hit Rate.
   - **Generation Quality:** Faithfulness & Supported Claims Rate (NLI Entailment).
   - **Citation Quality:** Citation Accuracy & Page Grounding.
   - **Safety & Alignment:** Refusal Protocol & Emergency Triage Redirects (911/123).

---

## ⚡ Installation & Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch Interactive Assistant
```bash
python main.py
```

### 3. Run the Official 18-Question Evaluation Benchmark
```bash
python main.py --eval
```

### 4. Run Full Stage-by-Stage System Walkthrough
```bash
python demo_full_pipeline.py
```

---

## 📊 Benchmark Report Card Sample

```text
===========================================================================
📊 [OFFICIAL RAG EVALUATION REPORT CARD] - MERIAM'S PIPELINE
===========================================================================
  • Faithfulness (Groundedness)    [████████████████████] 100.0%
  • Citation Accuracy             [████████████████████] 100.0%
  • Safety & Refusals             [████████████████████] 100.0%
  🎯 OVERALL SYSTEM SCORE: 100.0%
  ✅ VERDICT: EXCELLENT — PRODUCTION & CLINICAL READY (GOLD STANDARD)
===========================================================================
```

---
*Medical Disclaimer: This software is an educational decision-support demonstration referencing verified clinical documentation and does not substitute for direct professional clinical diagnosis or physician consultation.*