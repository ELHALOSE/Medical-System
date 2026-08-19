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