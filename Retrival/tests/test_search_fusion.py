from retrieval.search import BM25Index, reciprocal_rank_fusion


def test_rrf_agreement_boosts_rank():
    """An id ranked highly in both lists should beat one that only appears in one."""
    dense = ["a", "b", "c"]
    lexical = ["a", "c", "d"]

    fused = reciprocal_rank_fusion([dense, lexical], top_k=4)

    assert fused[0] == "a"  # top of both rankings
    assert "b" in fused and "d" in fused  # single-ranking hits still surface


def test_rrf_respects_top_k():
    dense = ["a", "b", "c", "d", "e"]
    fused = reciprocal_rank_fusion([dense], top_k=2)
    assert fused == ["a", "b"]


def test_rrf_handles_disjoint_rankings():
    dense = ["a", "b"]
    lexical = ["c", "d"]
    fused = reciprocal_rank_fusion([dense, lexical], top_k=4)
    assert set(fused) == {"a", "b", "c", "d"}


def test_bm25_finds_exact_acronym_match(sample_chunks):
    """The scenario hybrid search exists for: BM25 should surface the chunk
    containing an exact drug-class acronym even without semantic overlap."""
    index = BM25Index.build(sample_chunks)
    results = index.search("ARB", top_k=3)
    assert results[0] == "doc::0001"


def test_bm25_index_save_and_load_roundtrip(sample_chunks, tmp_path):
    index = BM25Index.build(sample_chunks)
    path = tmp_path / "bm25.pkl"
    index.save(path)

    loaded = BM25Index.load(path)
    assert loaded.search("ARB", top_k=1) == index.search("ARB", top_k=1)
