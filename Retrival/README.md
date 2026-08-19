# retrieval

Owns exactly four pieces of the RAG pipeline: **Embedding, VectorDB, Search,
Reranker**. Cleaning/chunking and prompting/generation are other branches -
this package's only contract with them is:

- **Input**: `chunks.jsonl`, one JSON object per line matching `Chunk` in
  `src/retrieval/schemas.py` (produced by the chunking branch).
- **Output**: `Retriever.retrieve(query, top_k)` → `list[(Chunk, score)]`,
  the single call the generation branch needs.

If either schema changes, `schemas.py` is the one place to update.

## Structure

```
retrieval/              # Python package (pip install -e .)
  __init__.py            # exports Retriever, RetrievalConfig, Chunk
  config.py              # all tunables, env-var overridable
  schemas.py             # Chunk dataclass - the integration contract
  embedding.py           # Embedder (sentence-transformers wrapper)
  vectorstore.py         # VectorStore (Chroma wrapper)
  search.py              # BM25Index + HybridSearcher (dense + lexical, RRF fusion)
  reranker.py            # Reranker (cross-encoder wrapper)
  pipeline.py            # Retriever - orchestrates the above, the public API
cli/
  build_index.py         # run once per chunks.jsonl to embed + index
  query_cli.py           # manual retrieval testing, no generation stage needed
tests/
  conftest.py            # shared pytest fixtures
  test_search_fusion.py  # RRF + BM25 logic, fast, no models
  test_schemas.py        # Chunk (de)serialization, fast, no models
  test_pipeline_integration.py  # real models end-to-end, slow, opt-in
```

## Design notes

- **Embedding**: `NeuML/pubmedbert-base-embeddings` - domain-tuned PubMedBERT,
  drop-in `sentence-transformers` model, no custom encoding logic needed.
- **VectorDB**: `ChromaDB`, embedded/persistent - no server to run, stores
  scalar metadata (headings/pages/doc_name) alongside vectors.
- **Search**: hybrid dense + BM25 fused with **Reciprocal Rank Fusion**.
  Pure dense embeddings miss exact drug-class acronyms (ACEi, ARB, BB, CCB);
  BM25 catches those reliably. `reciprocal_rank_fusion()` is a standalone
  pure function specifically so it's testable without loading any model.
- **Reranker**: `BAAI/bge-reranker-v2-m3` cross-encoder, run only on the
  hybrid-search shortlist (`candidate_pool`, default 20) - too slow to run
  over the full corpus, but far more precise than bi-encoder similarity on
  the candidates it does see.

## Usage

```bash
pip install -e ".[dev]"

# 1. Build the index once (or whenever chunks.jsonl changes)
python -m cli.build_index --chunks-path path/to/chunks.jsonl

# 2. Test retrieval directly
python -m cli.query_cli --chunks-path path/to/chunks.jsonl --query "target blood pressure for adults"
```

From code (what the generation branch will do):

```python
from retrieval.config import RetrievalConfig
from retrieval.pipeline import Retriever
from retrieval.schemas import load_chunks_jsonl

chunks = load_chunks_jsonl("path/to/chunks.jsonl")
retriever = Retriever.load(RetrievalConfig(), chunks)

results = retriever.retrieve("what is the target blood pressure for adults?")
for chunk, score in results:
    print(score, chunk.page_numbers, chunk.text[:100])
```

## Testing

```bash
pytest                              # fast tests only (default, no models)
pytest -m integration               # + real end-to-end test (downloads models)
```

## Config

All tunables are environment-variable overridable (`config.py`), e.g.:

```bash
export RERANKER_MODEL_ID="BAAI/bge-reranker-base"  # lighter/faster, CPU-friendly
export CANDIDATE_POOL=30
export TOP_K=8
```
