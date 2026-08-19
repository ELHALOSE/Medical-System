"""
query_cli.py
------------
Manual test harness - lets you sanity-check retrieval quality without
waiting on the prompting/generation side to be wired up.

Usage:
    python -m cli.query_cli --chunks-path output.json --query "some question"
"""

from __future__ import annotations

import argparse
import sys

from retrieval.config import RetrievalConfig
from retrieval.pipeline import Retriever
from retrieval.schemas import load_chunks


def print_results(results: list) -> None:
    if not results:
        print("  (no results)")
        return
    for rank, (chunk, score) in enumerate(results, start=1):
        title = chunk.title or "(no title)"
        preview = chunk.text.replace("\n", " ")[:140]
        print(f"  {rank}. score={score:.3f}  pages={chunk.page_start}-{chunk.page_end}  [{title}]")
        print(f"     {preview}...")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunks-path", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--output", default=None, help="Path to write results JSON (default: config.output_path)")
    parser.add_argument(
        "--query", default=None, help="Run one query and exit instead of an interactive loop"
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args(sys.argv[1:])

    config = RetrievalConfig()
    chunks = load_chunks(args.chunks_path)
    retriever = Retriever.load(config, chunks)
    output_path = args.output or config.output_path

    if args.query:
        results = retriever.retrieve(args.query, top_k=args.top_k)
        print_results(results)
        Retriever.export_results(args.query, results, output_path)
        print(f"\nResults saved to {output_path}")
        sys.exit(0)

    print("Retrieval CLI ready. Type a question (Ctrl+D / Ctrl+C to quit).")
    while True:
        try:
            query = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not query:
            continue
        results = retriever.retrieve(query, top_k=args.top_k)
        print_results(results)
        Retriever.export_results(query, results, output_path)
        print(f"  -> saved to {output_path}")
