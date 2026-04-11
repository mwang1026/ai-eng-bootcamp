"""Shared fixtures for week2 RAG tests.

Fixture hierarchy (cheapest → most expensive):
- sample_opinion / sample_chunks: plain Python objects, instant
- embeddings: loads sentence-transformers model (~80MB, cached after first run)
- vectorstore: creates a temp ChromaDB from sample chunks + real embeddings
- rag_chain: builds full RetrievalQA chain with real Claude (needs API key)
"""

import json
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from langchain_core.documents import Document

# Load .env at import time so skipif markers can see API keys
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# ---------------------------------------------------------------------------
# Lightweight fixtures — no external deps, used by unit tests
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_opinions_json(tmp_path: Path) -> Path:
    """Write a small cached opinions JSON file and return its path."""
    opinions = [
        {
            "opinion_id": 1,
            "case_name": "Kelo v. City of New London",
            "date_filed": "2005-06-23",
            "text": (
                "The city of New London approved a development plan that was "
                "projected to create in excess of 1,000 jobs, to increase tax "
                "and other revenues, and to revitalize an economically "
                "distressed city. The petitioners are owners of real property "
                "that the city condemned for the development project. "
                "The question presented is whether the city's proposed "
                "disposition of this property qualifies as a public use "
                "within the meaning of the Takings Clause of the Fifth "
                "Amendment to the Constitution."
            ),
        },
        {
            "opinion_id": 2,
            "case_name": "Roper v. Simmons",
            "date_filed": "2005-03-01",
            "text": (
                "At age 17, respondent Simmons planned and committed a capital "
                "murder. The Court now holds that the Eighth Amendment prohibits "
                "imposition of the death penalty on offenders who were under "
                "the age of 18 when their crimes were committed. The Eighth "
                "Amendment's prohibition against cruel and unusual punishments "
                "must be interpreted according to its text, by considering "
                "history, tradition, and precedent, and with due regard for "
                "its purpose and function in the constitutional design."
            ),
        },
        {
            "opinion_id": 3,
            "case_name": "Boumediene v. Bush",
            "date_filed": "2008-06-12",
            "text": (
                "Petitioners are aliens designated as enemy combatants and "
                "detained at the United States Naval Station at Guantanamo Bay. "
                "The question is whether they have the constitutional privilege "
                "of habeas corpus. The Court holds that the detainees have the "
                "constitutional privilege of habeas corpus and that the "
                "procedures for review of their status are not an adequate "
                "substitute for habeas corpus."
            ),
        },
    ]
    filepath = tmp_path / "opinions.json"
    filepath.write_text(json.dumps(opinions, indent=2))
    return filepath


@pytest.fixture
def sample_chunks() -> list[Document]:
    """Pre-chunked documents about distinct legal topics.

    Each chunk is short and topically focused so retrieval tests
    can assert which case a query should match.
    """
    return [
        Document(
            page_content=(
                "The Court holds that the Second Amendment protects an "
                "individual's right to possess a firearm unconnected with "
                "service in a militia, and to use that arm for traditionally "
                "lawful purposes, such as self-defense within the home."
            ),
            metadata={
                "case_name": "District of Columbia v. Heller",
                "date_filed": "2008-06-26",
            },
        ),
        Document(
            page_content=(
                "The city's taking of private property for economic development "
                "satisfies the public use requirement of the Fifth Amendment's "
                "Takings Clause. The government may transfer property from one "
                "private party to another if the purpose is economic development."
            ),
            metadata={
                "case_name": "Kelo v. City of New London",
                "date_filed": "2005-06-23",
            },
        ),
        Document(
            page_content=(
                "Foreign nationals detained at Guantanamo Bay have the "
                "constitutional privilege of habeas corpus. The procedures "
                "for reviewing detainee status were not an adequate substitute "
                "for habeas corpus."
            ),
            metadata={
                "case_name": "Boumediene v. Bush",
                "date_filed": "2008-06-12",
            },
        ),
        Document(
            page_content=(
                "The Eighth Amendment prohibits the imposition of the death "
                "penalty on offenders who were under the age of 18 when their "
                "crimes were committed. National consensus against the juvenile "
                "death penalty has developed."
            ),
            metadata={
                "case_name": "Roper v. Simmons",
                "date_filed": "2005-03-01",
            },
        ),
    ]


# ---------------------------------------------------------------------------
# Expensive fixtures — marked slow, scoped to module for reuse
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def embeddings():
    """Load the real embedding model. Scoped to module so it loads once.

    First run downloads ~80MB to ~/.cache/huggingface/. Subsequent runs
    use the cache. Still takes a few seconds to initialize.
    """
    from langchain_huggingface import HuggingFaceEmbeddings

    from rag import EMBEDDING_MODEL

    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


# ---------------------------------------------------------------------------
# Helpers for conditional skipping
# ---------------------------------------------------------------------------


requires_api_key = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set — skipping LLM tests",
)
