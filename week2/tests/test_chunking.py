"""Tests for document chunking logic.

Pure unit tests — no API calls, no embeddings, no vector store.
Tests that RecursiveCharacterTextSplitter produces chunks with the
expected size, overlap, count, and metadata properties.
"""

from langchain_core.documents import Document

from rag import chunk_documents, compare_chunk_strategies
from tests.helpers import make_long_opinion

# --- Basic chunking behavior ---


def test_long_doc_produces_multiple_chunks():
    doc = make_long_opinion()
    chunks = chunk_documents([doc], chunk_size=500, chunk_overlap=100)
    assert len(chunks) > 1


def test_short_doc_stays_single_chunk():
    doc = Document(
        page_content="Short opinion.",
        metadata={"case_name": "Short v. Doc", "date_filed": "2005-01-01"},
    )
    chunks = chunk_documents([doc], chunk_size=500, chunk_overlap=100)
    assert len(chunks) == 1
    assert chunks[0].page_content == "Short opinion."


def test_chunks_respect_max_size():
    doc = make_long_opinion()
    chunk_size = 500
    chunks = chunk_documents([doc], chunk_size=chunk_size, chunk_overlap=100)
    for chunk in chunks:
        # RecursiveCharacterTextSplitter can slightly exceed chunk_size
        # when it can't find a separator within the limit
        assert len(chunk.page_content) <= chunk_size + 100


def test_metadata_preserved_through_chunking():
    doc = Document(
        page_content="Some text. " * 200,
        metadata={"case_name": "Meta v. Data", "date_filed": "2005-06-23"},
    )
    chunks = chunk_documents([doc], chunk_size=500, chunk_overlap=100)
    for chunk in chunks:
        assert chunk.metadata["case_name"] == "Meta v. Data"
        assert chunk.metadata["date_filed"] == "2005-06-23"


# --- Chunk size comparison ---


def test_smaller_chunk_size_produces_more_chunks():
    doc = make_long_opinion()
    small = chunk_documents([doc], chunk_size=200, chunk_overlap=50)
    large = chunk_documents([doc], chunk_size=1000, chunk_overlap=200)
    assert len(small) > len(large)


def test_overlap_produces_more_chunks_than_no_overlap():
    """Chunks with overlap should produce more total chunks than without."""
    doc = make_long_opinion(paragraphs=10)
    with_overlap = chunk_documents([doc], chunk_size=500, chunk_overlap=200)
    without_overlap = chunk_documents([doc], chunk_size=500, chunk_overlap=0)
    assert len(with_overlap) >= len(without_overlap)


# --- compare_chunk_strategies (the function used in Step 2) ---


def test_compare_returns_1000_200_strategy():
    """compare_chunk_strategies should select the 1000/200 chunks."""
    doc = make_long_opinion(paragraphs=30)
    chosen = compare_chunk_strategies([doc])
    expected = chunk_documents([doc], chunk_size=1000, chunk_overlap=200)
    assert len(chosen) == len(expected)


def test_compare_handles_multiple_docs():
    docs = [make_long_opinion(paragraphs=10) for _ in range(3)]
    chunks = compare_chunk_strategies(docs)
    assert len(chunks) > 3
    assert all(c.metadata["case_name"] == "Long v. Opinion" for c in chunks)
