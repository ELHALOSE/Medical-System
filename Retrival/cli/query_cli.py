"""
query_cli.py
------------
Manual test harness for this branch's scope only - lets you sanity-check
retrieval quality without waiting on the prompting/generation side to be
wired up.

Usage:
    python -m cli.query_cli --chunks-path ../chunking/output/chunks.jsonl
"""

from __future__ import annotations

import argparse
import sys

from retrieval.config import RetrievalConfig
from retrieval.pipeline import Retriever
from retrieval.schemas import load_chunks_jsonl


def print_results(results: list) -> None:
    if not results:
        print("  (no results)")
        return
    for rank, (chunk, score) in enumerate(results, start=1):
        heading = " > ".join(chunk.headings) or "(no heading)"
        preview = chunk.text.replace("\n", " ")[:140]
        print(f"  {rank}. score={score:.3f}  page={chunk.page_numbers}  [{heading}]")
        print(f"     {preview}...")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunks-path", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--query", default=None, help="Run one query and exit instead of an interactive loop"
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args(sys.argv[1:])

    config = RetrievalConfig()
    chunks = load_chunks_jsonl(args.chunks_path)
    retriever = Retriever.load(config, chunks)

    if args.query:
        print_results(retriever.retrieve(args.query, top_k=args.top_k))
        sys.exit(0)

    print("Retrieval CLI ready. Type a question (Ctrl+D / Ctrl+C to quit).")
    while True:
        try:
            query = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not query:
            continue
        print_results(retriever.retrieve(query, top_k=args.top_k))
