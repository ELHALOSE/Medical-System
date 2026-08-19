import json

import pytest

from retrieval.schemas import Chunk, load_chunks_jsonl


def test_chunk_roundtrips_through_dict(sample_chunks):
    chunk = sample_chunks[0]
    assert Chunk.from_dict(chunk.to_dict()) == chunk


def test_load_chunks_jsonl_reads_valid_file(sample_chunks, tmp_path):
    path = tmp_path / "chunks.jsonl"
    with path.open("w") as f:
        for c in sample_chunks:
            f.write(json.dumps(c.to_dict()) + "\n")

    loaded = load_chunks_jsonl(path)
    assert len(loaded) == len(sample_chunks)
    assert loaded[0].chunk_id == sample_chunks[0].chunk_id


def test_load_chunks_jsonl_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_chunks_jsonl(tmp_path / "does_not_exist.jsonl")


def test_load_chunks_jsonl_bad_schema_raises(tmp_path):
    path = tmp_path / "bad.jsonl"
    path.write_text('{"unexpected_field": "oops"}\n')
    with pytest.raises(ValueError):
        load_chunks_jsonl(path)
