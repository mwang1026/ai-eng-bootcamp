"""Tests for embedding + vector store retrieval.

Integration tests that use real sentence-transformers embeddings and
a temporary ChromaDB. No external API calls — embeddings run locally.

Marked @slow because loading the embedding model takes a few seconds.
"""

import pytest
from langchain_chroma import Chroma

# All tests in this module need the real embedding model
pytestmark = pytest.mark.slow


@pytest.fixture
def vectorstore(sample_chunks, embeddings, tmp_path):
    """Create a temporary ChromaDB populated with sample chunks."""
    return Chroma.from_documents(
        documents=sample_chunks,
        embedding=embeddings,
        persist_directory=str(tmp_path / "test_chroma"),
        collection_name="test_collection",
    )


# --- Vector store basics ---


def test_stores_all_chunks(vectorstore, sample_chunks):
    assert vectorstore._collection.count() == len(sample_chunks)


def test_similarity_search_returns_k_results(vectorstore):
    results = vectorstore.similarity_search("gun rights", k=2)
    assert len(results) == 2


def test_results_contain_page_content(vectorstore):
    results = vectorstore.similarity_search("habeas corpus", k=1)
    assert len(results[0].page_content) > 0


def test_results_preserve_metadata(vectorstore):
    results = vectorstore.similarity_search("property rights", k=1)
    assert "case_name" in results[0].metadata
    assert "date_filed" in results[0].metadata


# --- Retrieval relevance ---
# Each query should surface the most topically relevant case as the top result.
# This tests that the embedding model + chunking produce meaningful vectors.


def test_gun_rights_retrieves_heller(vectorstore):
    results = vectorstore.similarity_search("individual right to bear arms", k=1)
    assert "Heller" in results[0].metadata["case_name"]


def test_eminent_domain_retrieves_kelo(vectorstore):
    results = vectorstore.similarity_search(
        "government taking private property for development", k=1
    )
    assert "Kelo" in results[0].metadata["case_name"]


def test_guantanamo_retrieves_boumediene(vectorstore):
    results = vectorstore.similarity_search(
        "habeas corpus rights of Guantanamo detainees", k=1
    )
    assert "Boumediene" in results[0].metadata["case_name"]


def test_juvenile_death_penalty_retrieves_roper(vectorstore):
    results = vectorstore.similarity_search("death penalty for minors under 18", k=1)
    assert "Roper" in results[0].metadata["case_name"]
