import pytest

from retrieval.schemas import Chunk


@pytest.fixture
def sample_chunks() -> list[Chunk]:
    return [
        Chunk(
            chunk_id="doc::0000",
            text="Initiate pharmacological treatment for adults with confirmed BP >=140/90 mmHg.",
            contextualized_text="Recommendations > BP threshold\nInitiate pharmacological treatment for adults with confirmed BP >=140/90 mmHg.",
            headings=["Recommendations", "BP threshold"],
            page_numbers=[12],
            doc_name="guideline",
            char_count=80,
            token_count=20,
        ),
        Chunk(
            chunk_id="doc::0001",
            text="First-line agents include thiazide diuretics, ACE inhibitors, ARBs, and CCBs.",
            contextualized_text="Recommendations > First-line agents\nFirst-line agents include thiazide diuretics, ACE inhibitors, ARBs, and CCBs.",
            headings=["Recommendations", "First-line agents"],
            page_numbers=[18],
            doc_name="guideline",
            char_count=79,
            token_count=18,
        ),
        Chunk(
            chunk_id="doc::0002",
            text="Reassess blood pressure monthly until control is achieved.",
            contextualized_text="Recommendations > Follow-up\nReassess blood pressure monthly until control is achieved.",
            headings=["Recommendations", "Follow-up"],
            page_numbers=[22],
            doc_name="guideline",
            char_count=60,
            token_count=13,
        ),
    ]
