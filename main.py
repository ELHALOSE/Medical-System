
import json
import importlib.util
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
PACKAGE_DIR = PROJECT_ROOT / "data-pipline"
PACKAGE_NAME = "data_pipeline"

package_spec = importlib.util.spec_from_file_location(
    PACKAGE_NAME,
    PACKAGE_DIR / "__init__.py",
    submodule_search_locations=[str(PACKAGE_DIR)],
)
if package_spec is None or package_spec.loader is None:
    raise ImportError(f"Could not load package from {PACKAGE_DIR}")
package = importlib.util.module_from_spec(package_spec)
sys.modules[PACKAGE_NAME] = package
package_spec.loader.exec_module(package)

build_chunk_details = package.build_chunk_details
build_metadata = package.build_metadata
chunk_text = package.chunk_text
clean_full_text = package.clean_full_text
clean_page_text = package.clean_page_text
clean_text = package.clean_text
extract_pdf_text = package.extract_pdf_text
extract_title = package.extract_title
parse_medical_document = package.parse_medical_document

__all__ = [
    "build_chunk_details",
    "build_metadata",
    "chunk_text",
    "clean_full_text",
    "clean_page_text",
    "clean_text",
    "extract_pdf_text",
    "extract_title",
    "parse_medical_document",
]


if __name__ == "__main__":
    sample_pdf = PROJECT_ROOT / "source" / "9789240033986-eng.pdf"
    if Path(sample_pdf).exists():
        json_output = json.dumps(parse_medical_document(sample_pdf), ensure_ascii=False, indent=2)
    else:
        json_output = json.dumps(
            {
                "status": "missing_pdf",
                "message": "Place the medical PDF in the project root and run again.",
                "expected_file": str(sample_pdf),
            },
            ensure_ascii=False,
            indent=2,
        )
    print(json_output)
    (PROJECT_ROOT / "output.json").write_text(json_output + "\n", encoding="utf-8")

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
