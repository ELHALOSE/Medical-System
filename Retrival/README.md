# retrieval

Owns exactly four pieces of the RAG pipeline: **Embedding, VectorDB, Search,
Reranker**. Cleaning/chunking and prompting/generation are other branches -
this package's only contract with them is:

- **Input**: `output.json`, the JSON file produced by the chunking pipeline,
  with chunks at `content.chunk_details`.
- **Output**: `Retriever.retrieve(query, top_k)` → `list[(Chunk, score)]`,
  the single call the generation branch needs.

If the schema changes, `schemas.py` is the one place to update.

## Structure

```
retrieval/              # Python package (pip install -e .)
  __init__.py            # exports Retriever, RetrievalConfig, Chunk, load_chunks
  config.py              # all tunables, env-var overridable
  schemas.py             # Chunk dataclass - the integration contract
  embedding.py           # Embedder (sentence-transformers wrapper)
  vectorstore.py         # VectorStore (Chroma wrapper)
  search.py              # BM25Index + HybridSearcher (dense + lexical, RRF fusion)
  reranker.py            # Reranker (cross-encoder wrapper)
  pipeline.py            # Retriever - orchestrates the above, the public API
cli/
  build_index.py         # run once per output.json to embed + index
  query_cli.py           # manual retrieval testing, no generation stage needed
```

## Usage

```bash
pip install -e .

# 1. Build the index once (or whenever output.json changes)
python -m cli.build_index --chunks-path output.json

# 2. Test retrieval directly
python -m cli.query_cli --chunks-path output.json --query "target blood pressure for adults"
```

From code (what the generation branch will do):

```python
from retrieval import Retriever, RetrievalConfig, load_chunks

chunks = load_chunks("output.json")
retriever = Retriever.load(RetrievalConfig(), chunks)

results = retriever.retrieve("what is the target blood pressure for adults?")
for chunk, score in results:
    print(score, f"pages {chunk.page_start}-{chunk.page_end}", chunk.text[:100])
```

## Config

All tunables are environment-variable overridable (`config.py`), e.g.:

```bash
export RERANKER_MODEL_ID="BAAI/bge-reranker-base"  # lighter/faster, CPU-friendly
export CANDIDATE_POOL=30
export TOP_K=8
```
