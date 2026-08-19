# 🏥 Clinical AI Medical RAG System

> **An End-to-End, Open-Source, Evidence-Grounded Medical Question Answering & Evaluation Framework**

A modular **Medical Retrieval-Augmented Generation (RAG)** system designed for answering clinical questions using trusted medical documents and clinical practice guidelines.

The system combines:

- Medical document parsing and preprocessing
- Semantic and lexical retrieval
- Vector database search
- Reranking
- Evidence-grounded prompt construction
- Open-source LLM generation
- Citation and safety guardrails
- Evaluation of retrieval and generation quality
- FastAPI backend and PostgreSQL persistence

---

# 🎯 Project Goal

The goal of this project is to build a medical question-answering system that provides **evidence-grounded answers** based on trusted medical documents rather than relying solely on the language model's internal knowledge.

The system follows the principle:

> **Retrieve → Rerank → Construct Context → Generate → Evaluate**

The generated answer should be supported by the retrieved medical evidence and include references to the source material whenever applicable.

---
