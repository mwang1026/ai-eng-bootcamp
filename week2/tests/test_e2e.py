"""End-to-end tests for the full RAG chain.

These make real Claude API calls (costs ~$0.001 per test with Haiku).
Skipped automatically when ANTHROPIC_API_KEY is not set.

Tests the complete pipeline: retrieval → prompt → Claude → answer,
verifying that answers are grounded in context and that the model
refuses out-of-scope questions.
"""

import pytest
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_chroma import Chroma
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

from rag import EMBEDDING_MODEL, LLM_MODEL, RAG_PROMPT_TEMPLATE
from tests.conftest import requires_api_key

load_dotenv()

# All tests in this module are slow and need an API key
pytestmark = [pytest.mark.slow, requires_api_key]


@pytest.fixture(scope="module")
def e2e_vectorstore(embeddings, tmp_path_factory):
    """A small vectorstore with known content for predictable answers."""
    from langchain_core.documents import Document

    chunks = [
        Document(
            page_content=(
                "In Kelo v. City of New London (2005), the Supreme Court held "
                "that the general benefits a community enjoyed from economic "
                "growth qualified as a permissible 'public use' under the "
                "Takings Clause of the Fifth Amendment. The city's taking of "
                "private property to sell for private development qualified as "
                "a permissible public use. Justice Stevens delivered the opinion."
            ),
            metadata={
                "case_name": "Kelo v. City of New London",
                "date_filed": "2005-06-23",
            },
        ),
        Document(
            page_content=(
                "In Roper v. Simmons (2005), the Court held that the Eighth "
                "and Fourteenth Amendments forbid imposition of the death "
                "penalty on offenders who were under the age of 18 when their "
                "crimes were committed. The Court overruled Stanford v. Kentucky. "
                "Justice Kennedy wrote the majority opinion."
            ),
            metadata={
                "case_name": "Roper v. Simmons",
                "date_filed": "2005-03-01",
            },
        ),
    ]

    tmp = tmp_path_factory.mktemp("e2e_chroma")
    from langchain_huggingface import HuggingFaceEmbeddings

    emb = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return Chroma.from_documents(
        documents=chunks,
        embedding=emb,
        persist_directory=str(tmp),
        collection_name="e2e_test",
    )


@pytest.fixture(scope="module")
def rag_chain(e2e_vectorstore):
    """Build a RetrievalQA chain with real Claude."""
    llm = ChatAnthropic(model=LLM_MODEL, temperature=0, max_tokens=512)
    prompt = PromptTemplate(
        template=RAG_PROMPT_TEMPLATE,
        input_variables=["context", "question"],
    )
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=e2e_vectorstore.as_retriever(search_kwargs={"k": 2}),
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True,
    )


def test_answers_grounded_in_context(rag_chain):
    """Answer about Kelo should cite the case and reference takings/public use."""
    result = rag_chain.invoke(
        {"query": "Can cities take private property for economic development?"}
    )
    answer = result["result"].lower()
    assert "kelo" in answer
    assert "public use" in answer or "fifth amendment" in answer or "takings" in answer


def test_returns_source_documents(rag_chain):
    """Chain should return the source documents it retrieved."""
    result = rag_chain.invoke({"query": "Is the death penalty allowed for minors?"})
    source_names = [d.metadata["case_name"] for d in result["source_documents"]]
    assert any("Roper" in name for name in source_names)


def test_refuses_out_of_scope_question(rag_chain):
    """When asked about a case not in the corpus, should refuse or caveat.

    This is the most important test — it proves the grounding prompt works.
    Obergefell v. Hodges (2015) is not in our 2000-2009 corpus, so the model
    should say it doesn't have enough context rather than answering from
    its training knowledge.
    """
    result = rag_chain.invoke(
        {
            "query": (
                "What did the Supreme Court rule about same-sex marriage "
                "in Obergefell v. Hodges?"
            )
        }
    )
    answer = result["result"].lower()
    refusal_phrases = [
        "does not contain",
        "not contain sufficient",
        "no information",
        "insufficient",
        "not addressed",
        "cannot find",
        "not able to",
    ]
    assert any(phrase in answer for phrase in refusal_phrases), (
        f"Expected refusal for out-of-scope query, got: {result['result'][:300]}"
    )
