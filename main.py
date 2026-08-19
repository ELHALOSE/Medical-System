"""
Medical System - Interactive Clinical Assistant & Evaluation Runner
Author: Meriam

Usage:
    python main.py             # Start Interactive Live Chat CLI
    python main.py --eval      # Run Official 18-Question Evaluation Report Card
"""

import sys
import argparse
from Generation_Evaluation import GenerationPipeline, MedicalEvaluator


def start_interactive_session(pipeline: GenerationPipeline):
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("\n" + "=" * 75)
    print("🩺 MEDICAL AI ASSISTANT - GENERATION & EVALUATION (MERIAM)")
    print("=" * 75)
    print("Commands:")
    print("  • Type any clinical question and press Enter.")
    print("  • Type 'eval' to run the official 18-Question Benchmark & Report Card.")
    print("  • Type 'exit' or 'quit' to end the session.")
    print("=" * 75 + "\n")

    while True:
        try:
            user_input = input("👩‍⚕️ Ask a medical question: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSession ended.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "q"):
            print("Session terminated. Goodbye!")
            break

        if user_input.lower() in ("eval", "benchmark", "report"):
            print("\n🚀 Running Official Benchmark Evaluation...")
            evaluator = MedicalEvaluator()
            res = evaluator.run_benchmark(pipeline)
            evaluator.print_report_card(res)
            continue

        print("\n⏳ Processing clinical query & verifying medical citations...")
        res = pipeline.generate_answer(query=user_input)

        print("\n" + "─" * 70)
        print("📝 CLINICAL RESPONSE:")
        print("─" * 70)
        print(res["answer"])
        print("─" * 70)

        print("\n📚 ATTACHED EVIDENCE & CITATIONS:")
        for s in res["sources"]:
            print(f"  • [{s['doc_id']}] {s['source']} (Page: {s['page']} | Section: {s['section']})")

        print(f"\n⏱️ Latency: {res['latency_seconds']}s")
        f_score = res["evaluation"]["faithfulness_score"] * 100
        r_score = res["evaluation"]["relevance_score"] * 100
        print(f"🎯 Quality Badges: [Faithfulness: {f_score:.1f}%] | [Relevance: {r_score:.1f}%]")
        print("\n" + "=" * 75 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Medical RAG Generation & Evaluation")
    parser.add_argument("--eval", action="store_true", help="Run 18-Question Evaluation Report Card")
    parser.add_argument("--backend", default="mock", choices=["mock", "hf_api", "local_transformers"])
    args = parser.parse_args()

    pipeline = GenerationPipeline(backend=args.backend)

    if args.eval:
        evaluator = MedicalEvaluator()
        res = evaluator.run_benchmark(pipeline)
        evaluator.print_report_card(res)
    else:
        start_interactive_session(pipeline)


if __name__ == "__main__":
    main()
