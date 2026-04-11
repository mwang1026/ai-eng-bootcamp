"""Tests for document loading from cached JSON.

Unit tests that verify the JSONLoader integration using a temporary
fixture file. No CourtListener API calls — tests the load-from-cache path.
"""

from langchain_community.document_loaders import JSONLoader
from langchain_core.documents import Document


def _load_with_json_loader(filepath) -> list[Document]:
    """Load opinions using the same JSONLoader config as rag.py."""

    def extract_metadata(record: dict, metadata: dict) -> dict:
        metadata["case_name"] = record.get("case_name", "Unknown")
        metadata["date_filed"] = record.get("date_filed", "Unknown")
        metadata["opinion_id"] = record.get("opinion_id", "Unknown")
        return metadata

    loader = JSONLoader(
        file_path=str(filepath),
        jq_schema=".[]",
        content_key="text",
        metadata_func=extract_metadata,
    )
    return loader.load()


def test_loads_correct_number_of_documents(sample_opinions_json):
    docs = _load_with_json_loader(sample_opinions_json)
    assert len(docs) == 3


def test_all_results_are_documents(sample_opinions_json):
    docs = _load_with_json_loader(sample_opinions_json)
    assert all(isinstance(d, Document) for d in docs)


def test_page_content_comes_from_text_field(sample_opinions_json):
    docs = _load_with_json_loader(sample_opinions_json)
    # page_content should be the opinion text, not the case name
    assert "city of New London" in docs[0].page_content
    assert "Kelo" not in docs[0].page_content


def test_metadata_extracted_correctly(sample_opinions_json):
    docs = _load_with_json_loader(sample_opinions_json)
    kelo = docs[0]
    assert kelo.metadata["case_name"] == "Kelo v. City of New London"
    assert kelo.metadata["date_filed"] == "2005-06-23"
    assert kelo.metadata["opinion_id"] == 1


def test_all_docs_have_required_metadata_fields(sample_opinions_json):
    docs = _load_with_json_loader(sample_opinions_json)
    for doc in docs:
        assert "case_name" in doc.metadata
        assert "date_filed" in doc.metadata
        assert "opinion_id" in doc.metadata
        assert doc.metadata["case_name"] != "Unknown"


def test_preserves_document_order(sample_opinions_json):
    docs = _load_with_json_loader(sample_opinions_json)
    names = [d.metadata["case_name"] for d in docs]
    assert names == [
        "Kelo v. City of New London",
        "Roper v. Simmons",
        "Boumediene v. Bush",
    ]
