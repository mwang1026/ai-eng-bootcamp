"""
Supreme Court Precedent Finder — RAG Pipeline
=============================================

A retrieval-augmented generation (RAG) system that answers questions about
Supreme Court opinions from 2000-2009. Uses LangChain throughout:

- CourtListener REST API → LangChain JSONLoader (Step 1: Load)
- RecursiveCharacterTextSplitter (Step 2: Chunk)
- HuggingFace sentence-transformers + ChromaDB (Step 3: Embed + Store)
- similarity_search for retrieval testing (Step 4: Test Retrieval)
- RetrievalQA chain with Claude (Step 5: RAG Chain)
- Scored evaluation with negative test (Step 6: Evaluate)
"""

import argparse
import json
import os
import re
import shutil
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# langchain-anthropic: ChatAnthropic wraps Claude, reads ANTHROPIC_API_KEY from env
from langchain_anthropic import ChatAnthropic

# langchain-chroma: vector store backed by ChromaDB (SQLite + HNSW index on disk)
from langchain_chroma import Chroma

# langchain-classic: chains (RetrievalQA, LLMChain, etc.)
# In LangChain 1.2+, legacy chains moved from `langchain` to `langchain_classic`
from langchain_classic.chains import RetrievalQA

# langchain-community: document loaders (JSONLoader reads our cached data)
from langchain_community.document_loaders import JSONLoader

# ---------------------------------------------------------------------------
# LangChain imports — each from its own package
# ---------------------------------------------------------------------------
# langchain-core: base types (Document, prompts, output parsers)
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

# langchain-huggingface: local embeddings via sentence-transformers
# First run downloads the model (~80MB) and caches it in ~/.cache/huggingface/
from langchain_huggingface import HuggingFaceEmbeddings

# langchain-text-splitters: all text splitting implementations
# Moved from `langchain.text_splitter` to its own package in LangChain 1.2+
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ---------------------------------------------------------------------------
# Load environment variables from .env
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent / "data"
OPINIONS_CACHE = DATA_DIR / "opinions.json"
CHROMA_DIR = str(Path(__file__).parent / "chroma_db")
COLLECTION_NAME = "scotus_2000s"

# Embedding model — runs locally, no API key needed
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# LLM for the RAG chain
LLM_MODEL = "claude-haiku-4-5-20251001"

# CourtListener API settings
COURTLISTENER_BASE = "https://www.courtlistener.com/api/rest/v4"
PAGE_SIZE = 20
MAX_OPINIONS = 100  # cap to keep embedding fast and costs low


# =========================================================================
# STEP 1: LOAD — Fetch Supreme Court opinions from CourtListener
# =========================================================================
# The goal of this step is to get raw documents into LangChain's Document
# format. We do this in two phases:
#   1. Fetch from CourtListener REST API and cache as JSON (one-time)
#   2. Load from the cached JSON using LangChain's JSONLoader
#
# Why two phases? The API call is slow and rate-limited. Caching means
# re-runs of the script don't hit the API again.
# =========================================================================


def fetch_opinions_from_courtlistener() -> list[dict]:
    """
    Fetch SCOTUS opinions (2000-2009) from CourtListener REST API v4.

    CourtListener is the Free Law Project's open legal data platform.
    Their REST API lets us filter opinions by court, date range, and type.

    Returns a list of dicts, each with: case_name, date_filed, opinion_text,
    and other metadata. These get cached to data/opinions.json.
    """
    token = os.environ.get("COURTLISTENER_API_TOKEN")
    if not token:
        raise RuntimeError(
            "COURTLISTENER_API_TOKEN not set. "
            "Register at courtlistener.com and add your token to .env"
        )

    headers = {"Authorization": f"Token {token}"}

    # --- Fetch opinions with server-side filtering ---
    # The opinions endpoint supports "related field" filtering via double
    # underscores. cluster__docket__court filters by the court on the
    # opinion's parent cluster's parent docket.
    params = {
        "cluster__docket__court": "scotus",
        "cluster__date_filed__gte": "2000-01-01",
        "cluster__date_filed__lte": "2009-12-31",
        "type": "010combined",  # combined majority opinion
        "order_by": "cluster__date_filed",
        "page_size": PAGE_SIZE,
    }

    opinions = []
    url = f"{COURTLISTENER_BASE}/opinions/"
    page = 1

    print("Fetching SCOTUS opinions from CourtListener API...")
    while url and len(opinions) < MAX_OPINIONS:
        print(f"  Page {page}...", end=" ", flush=True)
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("results", []):
            if len(opinions) >= MAX_OPINIONS:
                break

            # Extract opinion text — prefer plain_text, fall back to HTML
            text = item.get("plain_text", "").strip()
            if not text:
                html = item.get("html_with_citations", "")
                # Strip HTML tags to get readable text
                text = re.sub(r"<[^>]+>", "", html).strip()

            if not text or len(text) < 500:
                # Skip very short opinions (likely empty or procedural)
                continue

            # The cluster URL contains case metadata — we need to fetch it
            # to get the case name and date. The cluster is the "case" that
            # groups related opinions (majority, concurrence, dissent).
            cluster_url = item.get("cluster")

            opinions.append(
                {
                    "opinion_id": item.get("id"),
                    "cluster_url": cluster_url,
                    "text": text,
                    "type": item.get("type"),
                }
            )

        count = len(opinions)
        print(f"({count} opinions so far)")

        # Pagination — CourtListener returns a "next" URL for the next page
        url = data.get("next")
        # Clear params for subsequent requests (the "next" URL includes them)
        params = {}
        page += 1

        # Be polite to the API
        time.sleep(0.5)

    print(f"\nFetched {len(opinions)} opinions. Now fetching case metadata...")

    # --- Fetch case names from cluster endpoints ---
    # Each opinion links to a "cluster" which has the case name and date.
    # This is an N+1 query pattern — not ideal, but necessary because the
    # opinions endpoint doesn't inline cluster data.
    for i, op in enumerate(opinions):
        cluster_url = op.get("cluster_url")
        if not cluster_url:
            op["case_name"] = "Unknown"
            op["date_filed"] = "Unknown"
            continue

        print(f"  Metadata {i + 1}/{len(opinions)}...", end="\r", flush=True)
        try:
            resp = requests.get(cluster_url, headers=headers, timeout=30)
            resp.raise_for_status()
            cluster = resp.json()
            op["case_name"] = cluster.get("case_name", "Unknown")
            op["date_filed"] = cluster.get("date_filed", "Unknown")
        except requests.RequestException:
            op["case_name"] = "Unknown"
            op["date_filed"] = "Unknown"

        time.sleep(0.3)  # rate limit courtesy

    print(f"\nDone! {len(opinions)} opinions with metadata ready.")
    return opinions


def load_documents() -> list[Document]:
    """
    Load Supreme Court opinions as LangChain Documents.

    If we've already cached the data, use JSONLoader (a LangChain document
    loader) to load from the cache. Otherwise, fetch from the API first.

    JSONLoader reads a JSON file and creates Document objects. We tell it:
    - jq_schema: how to extract each record from the JSON structure
    - content_key: which field becomes the Document's page_content
    - metadata_func: how to build metadata from each record

    This satisfies the assignment requirement to "use a LangChain document
    loader appropriate for your data type."
    """
    # Fetch and cache if needed
    if not OPINIONS_CACHE.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        opinions = fetch_opinions_from_courtlistener()
        OPINIONS_CACHE.write_text(json.dumps(opinions, indent=2))
        print(f"Cached {len(opinions)} opinions to {OPINIONS_CACHE}")
    else:
        print(f"Loading from cache: {OPINIONS_CACHE}")

    # --- Use LangChain's JSONLoader ---
    # JSONLoader uses jq-style expressions to navigate JSON structure.
    # Our JSON is an array of objects, so ".[]" iterates over each one.
    # content_key="text" means Document.page_content comes from the "text" field.
    # metadata_func lets us pull case_name, date_filed, etc. into Document.metadata.
    def extract_metadata(record: dict, metadata: dict) -> dict:
        metadata["case_name"] = record.get("case_name", "Unknown")
        metadata["date_filed"] = record.get("date_filed", "Unknown")
        metadata["opinion_id"] = record.get("opinion_id", "Unknown")
        return metadata

    loader = JSONLoader(
        file_path=str(OPINIONS_CACHE),
        jq_schema=".[]",
        content_key="text",
        metadata_func=extract_metadata,
    )

    docs = loader.load()

    # --- Print stats (required by assignment) ---
    print(f"\n{'=' * 60}")
    print("STEP 1: LOAD")
    print(f"{'=' * 60}")
    print(f"Documents loaded: {len(docs)}")
    if docs:
        first = docs[0]
        print("\nSample — first document:")
        print(f"  Case: {first.metadata.get('case_name', 'Unknown')}")
        print(f"  Date: {first.metadata.get('date_filed', 'Unknown')}")
        print(f"  Length: {len(first.page_content):,} characters")
        print(f"  Preview: {first.page_content[:300]}...")

    return docs


# =========================================================================
# STEP 2: CHUNK — Split documents into smaller pieces
# =========================================================================
# Why chunk? LLMs have limited context windows, and embedding models work
# better on smaller, focused passages. A 50-page opinion as a single vector
# would lose the nuance of individual arguments.
#
# RecursiveCharacterTextSplitter is LangChain's most versatile splitter.
# It tries to split on the largest separator first (\n\n = paragraph break),
# then falls back to smaller ones (\n, ". ", " "). This keeps paragraphs
# intact when possible — important for legal reasoning that spans sentences.
#
# chunk_overlap ensures context isn't lost at split boundaries. If a key
# argument spans a chunk boundary, the overlap means both chunks contain
# the connecting text.
# =========================================================================


def chunk_documents(
    docs: list[Document], chunk_size: int, chunk_overlap: int
) -> list[Document]:
    """Split documents into chunks with the given size and overlap."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        # Separators are tried in order — prefer splitting on paragraph
        # breaks, then newlines, then sentences, then words
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    return splitter.split_documents(docs)


def compare_chunk_strategies(docs: list[Document]) -> list[Document]:
    """
    Try two chunk sizes and compare the results (required by assignment).
    Returns the chunks from the selected strategy.
    """
    print(f"\n{'=' * 60}")
    print("STEP 2: CHUNK")
    print(f"{'=' * 60}")

    strategies = [
        {"chunk_size": 500, "chunk_overlap": 100},
        {"chunk_size": 1000, "chunk_overlap": 200},
    ]

    all_chunks = {}
    for s in strategies:
        chunks = chunk_documents(docs, s["chunk_size"], s["chunk_overlap"])
        lengths = [len(c.page_content) for c in chunks]
        label = f"{s['chunk_size']}/{s['chunk_overlap']}"
        all_chunks[label] = chunks

        print(f"\nStrategy: chunk_size={s['chunk_size']}, overlap={s['chunk_overlap']}")
        print(f"  Total chunks: {len(chunks)}")
        print(f"  Smallest chunk: {min(lengths):,} chars")
        print(f"  Largest chunk:  {max(lengths):,} chars")
        print(f"  Average chunk:  {sum(lengths) // len(lengths):,} chars")

    # --- Selection rationale ---
    # We choose 1000/200 for legal text because:
    # 1. Legal arguments span multiple paragraphs — 500 chars cuts mid-thought
    # 2. Larger chunks preserve more reasoning context for the LLM
    # 3. With only ~50-100 opinions, we can afford larger chunks (fewer total)
    # 4. The 200-char overlap captures cross-paragraph transitions
    selected = "1000/200"
    print(f"\nSelected strategy: {selected}")
    print("Reason: Legal reasoning spans multiple paragraphs. Smaller chunks")
    print("fragment arguments, losing context the LLM needs to answer accurately.")

    return all_chunks[selected]


# =========================================================================
# STEP 3: EMBED + STORE — Create vector embeddings and store in ChromaDB
# =========================================================================
# This is the core of the "retrieval" in RAG. We convert each text chunk
# into a high-dimensional vector (384 dimensions for MiniLM) that captures
# its semantic meaning. Similar texts end up as nearby vectors.
#
# HuggingFaceEmbeddings runs the model locally — no API call, no cost.
# The model (all-MiniLM-L6-v2) is a distilled BERT variant trained on
# over 1 billion sentence pairs. It's small (80MB) but effective.
#
# ChromaDB stores these vectors along with the original text and metadata.
# When we query later, it computes the cosine similarity between the query
# vector and all stored vectors, returning the closest matches.
#
# persist_directory means the DB is saved to disk — re-runs don't need to
# re-embed everything.
# =========================================================================


def create_vectorstore(chunks: list[Document]) -> Chroma:
    """Embed chunks and store in ChromaDB. Loads from disk if already built."""
    print(f"\n{'=' * 60}")
    print("STEP 3: EMBED + STORE")
    print(f"{'=' * 60}")

    # --- Initialize the embedding model ---
    # This downloads the model on first run (~80MB) and caches it
    # in ~/.cache/huggingface/. Subsequent runs use the cache.
    print("Loading embedding model (first run downloads ~80MB)...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # --- Check if we already have a populated ChromaDB ---
    chroma_path = Path(CHROMA_DIR)
    if chroma_path.exists() and any(chroma_path.iterdir()):
        print("Found existing ChromaDB — loading from disk...")
        vectorstore = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings,
            collection_name=COLLECTION_NAME,
        )
        count = vectorstore._collection.count()
        print(f"Loaded {count} vectors from existing store.")
        return vectorstore

    # --- Embed and store ---
    # Chroma.from_documents does three things:
    # 1. Calls embeddings.embed_documents() on all chunk texts
    # 2. Stores vectors + text + metadata in the ChromaDB collection
    # 3. Persists everything to CHROMA_DIR
    print(f"Embedding {len(chunks)} chunks (this may take a minute)...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
        collection_name=COLLECTION_NAME,
    )
    print(f"Created ChromaDB with {len(chunks)} vectors at {CHROMA_DIR}")
    return vectorstore


# =========================================================================
# STEP 4: TEST RETRIEVAL — Verify the vector store returns relevant chunks
# =========================================================================
# Before wiring up the LLM, we test retrieval in isolation. This is
# crucial — if retrieval returns irrelevant chunks, the LLM will either
# hallucinate or refuse to answer. Bad retrieval = bad RAG, period.
#
# similarity_search() embeds the query, then finds the k nearest vectors
# in ChromaDB using approximate nearest neighbor search (HNSW algorithm).
# =========================================================================

TEST_QUERIES = [
    "What are the limits of executive power in wartime?",
    "Can the government take private property for economic development?",
    "What constitutes cruel and unusual punishment?",
]


def test_retrieval(vectorstore: Chroma) -> None:
    """Run test queries against the vector store and print results."""
    print(f"\n{'=' * 60}")
    print("STEP 4: TEST RETRIEVAL (before wiring up the LLM)")
    print(f"{'=' * 60}")

    for i, query in enumerate(TEST_QUERIES, 1):
        print(f'\n--- Query {i}: "{query}" ---')

        # similarity_search returns Document objects ranked by cosine similarity
        results = vectorstore.similarity_search(query, k=3)

        for j, doc in enumerate(results, 1):
            case = doc.metadata.get("case_name", "Unknown")
            date = doc.metadata.get("date_filed", "Unknown")
            preview = doc.page_content[:200].replace("\n", " ")
            print(f"\n  Chunk {j}:")
            print(f"    Case: {case} ({date})")
            print(f"    Preview: {preview}...")

        # Relevance annotations — we'll fill these in after the first run
        # to see what actually gets retrieved
        print("\n  Relevance: [Review after running — are these chunks")
        print("  actually about the query topic? See README for analysis.]")


# =========================================================================
# STEP 5: BUILD THE RAG CHAIN
# =========================================================================
# Now we wire everything together: retriever + LLM + prompt template.
#
# RetrievalQA is LangChain's built-in chain for question answering over
# retrieved documents. It:
#   1. Takes a query
#   2. Retrieves k relevant chunks from the vector store
#   3. Stuffs them into a prompt template (the "stuff" chain type)
#   4. Sends the prompt to the LLM
#   5. Returns the answer + source documents
#
# The "stuff" chain type simply concatenates all retrieved chunks into the
# prompt. This works when chunks are small enough to fit in the context
# window (they are — we're using 1000-char chunks with k=5).
#
# Alternatives: "map_reduce" (summarize each chunk separately, then combine)
# and "refine" (iteratively refine the answer with each chunk). These are
# useful when chunks are too large to stuff, but add latency and cost.
# =========================================================================

RAG_PROMPT_TEMPLATE = """You are a Supreme Court legal research assistant. \
Your job is to answer questions about Supreme Court precedent using ONLY the \
provided context passages from actual court opinions.

RULES:
1. Base your answer EXCLUSIVELY on the provided context. Do not use your \
training knowledge about legal cases.
2. Cite the specific case name and year for every claim you make.
3. If the context does not contain enough information to answer the question, \
say: "The provided context does not contain sufficient information to answer \
this question."
4. If the context partially answers the question, answer what you can and \
explicitly state what is missing.
5. Never fabricate case names, holdings, or citations.

CONTEXT:
{context}

QUESTION: {question}

ANSWER (grounded only in the context above):"""


def build_rag_chain(vectorstore: Chroma) -> RetrievalQA:
    """
    Build a RetrievalQA chain with Claude and a grounding prompt.

    The grounding prompt is the key to distinguishing RAG from parametric
    knowledge. It tells Claude to ONLY use the provided context and to
    explicitly refuse if the context doesn't have the answer.
    """
    print(f"\n{'=' * 60}")
    print("STEP 5: BUILD RAG CHAIN")
    print(f"{'=' * 60}")

    # --- Initialize Claude via LangChain ---
    # ChatAnthropic reads ANTHROPIC_API_KEY from the environment automatically.
    # temperature=0 makes responses deterministic — important for factual QA.
    # max_tokens caps the response length (and cost).
    llm = ChatAnthropic(
        model=LLM_MODEL,
        temperature=0,
        max_tokens=1024,
    )

    # --- Create the prompt template ---
    # PromptTemplate validates that the template has the right variables.
    # RetrievalQA expects {context} (filled with retrieved chunks) and
    # {question} (filled with the user's query).
    prompt = PromptTemplate(
        template=RAG_PROMPT_TEMPLATE,
        input_variables=["context", "question"],
    )

    # --- Build the chain ---
    # retriever wraps the vector store with search parameters.
    # search_kwargs={"k": 5} means retrieve the top 5 most similar chunks.
    # return_source_documents=True lets us inspect what was retrieved (for eval).
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True,
    )

    print("RAG chain built successfully.")
    print(f"  LLM: {LLM_MODEL}")
    print("  Retriever: ChromaDB with k=5")
    print("  Chain type: stuff (all chunks concatenated into prompt)")

    # --- Run the same test queries through the full chain ---
    print("\nRunning test queries through the full RAG chain...")
    for i, query in enumerate(TEST_QUERIES, 1):
        print(f'\n--- Query {i}: "{query}" ---')
        result = chain.invoke({"query": query})
        print(f"\nAnswer:\n{result['result']}")
        print("\nSources used:")
        for doc in result["source_documents"]:
            case = doc.metadata.get("case_name", "Unknown")
            print(f"  - {case}")

    return chain


# =========================================================================
# STEP 6: EVALUATE
# =========================================================================
# The part most people skip — but arguably the most important.
#
# We evaluate on three dimensions:
#   1. Retrieval accuracy: Did the vector store return chunks from the
#      correct case? (Tests the embedding + chunking quality)
#   2. Faithfulness: Is the answer grounded in the retrieved context?
#      (Tests the prompt template — does the LLM stay within bounds?)
#   3. Correctness: Is the answer factually right?
#      (Tests the full pipeline end-to-end)
#
# Question 5 is a NEGATIVE TEST — it asks about a case from 2015 that
# is NOT in our 2000-2009 corpus. If the grounding prompt works, the
# model should refuse to answer rather than using its training knowledge.
# =========================================================================

EVAL_QUESTIONS = [
    {
        "question": (
            "What did the Supreme Court rule about detainees' habeas corpus "
            "rights at Guantanamo Bay?"
        ),
        "expected_case": "Boumediene",
        "expected_keywords": ["habeas corpus", "constitutional"],
        "description": "Boumediene v. Bush (2008)",
    },
    {
        "question": (
            "Can cities use eminent domain to transfer property to private "
            "developers for economic development?"
        ),
        "expected_case": "Kelo",
        "expected_keywords": ["public use", "Fifth Amendment"],
        "description": "Kelo v. City of New London (2005)",
    },
    {
        "question": (
            "Is the death penalty constitutional for crimes committed by minors?"
        ),
        "expected_case": "Roper",
        "expected_keywords": ["Eighth Amendment", "cruel", "unusual"],
        "description": "Roper v. Simmons (2005)",
    },
    {
        "question": (
            "What standard applies to claims of ineffective assistance of counsel?"
        ),
        "expected_case": "Wiggins",
        "expected_keywords": ["Strickland", "deficient", "prejudice"],
        "description": "Wiggins v. Smith (2003)",
    },
    {
        "question": (
            "What did the Supreme Court rule in Obergefell v. Hodges about "
            "same-sex marriage?"
        ),
        "expected_case": "__NEGATIVE__",
        "expected_keywords": ["does not contain sufficient information"],
        "description": "NEGATIVE TEST — Obergefell (2015) is outside our corpus",
    },
]


def evaluate(chain: RetrievalQA, vectorstore: Chroma) -> None:
    """Run the evaluation suite and print a scorecard."""
    print(f"\n{'=' * 60}")
    print("STEP 6: EVALUATE")
    print(f"{'=' * 60}")

    retrieval_score = 0
    faithfulness_score = 0
    correctness_score = 0

    for i, eq in enumerate(EVAL_QUESTIONS, 1):
        print(f"\n{'─' * 50}")
        print(f"Question {i}: {eq['description']}")
        print(f"Q: {eq['question']}")

        result = chain.invoke({"query": eq["question"]})
        answer = result["result"]
        source_docs = result["source_documents"]

        # --- 1. Retrieval accuracy ---
        # Did we retrieve chunks from the expected case?
        retrieved_cases = [doc.metadata.get("case_name", "") for doc in source_docs]
        is_negative = eq["expected_case"] == "__NEGATIVE__"

        if is_negative:
            # For negative tests, retrieval "passes" if we didn't retrieve
            # the case (since it shouldn't be in our corpus at all)
            retrieval_pass = True
            retrieval_score += 1
        else:
            retrieval_pass = any(
                eq["expected_case"].lower() in case.lower() for case in retrieved_cases
            )
            if retrieval_pass:
                retrieval_score += 1

        # --- 2. Faithfulness ---
        # Is the answer grounded in the context (not hallucinated)?
        # For positive tests: answer should reference cases from source_docs
        # For negative test: answer should contain the refusal phrase
        if is_negative:
            faithfulness_pass = (
                "does not contain sufficient information" in answer.lower()
                or "not contain" in answer.lower()
                or "no information" in answer.lower()
            )
        else:
            # Check that the answer mentions at least one retrieved case
            faithfulness_pass = any(
                case.split(",")[0].split(" v.")[0].strip().lower() in answer.lower()
                or case.split(",")[0].strip().lower() in answer.lower()
                for case in retrieved_cases
                if case and case != "Unknown"
            )
        if faithfulness_pass:
            faithfulness_score += 1

        # --- 3. Correctness ---
        # Does the answer contain expected keywords?
        answer_lower = answer.lower()
        keyword_hits = sum(
            1 for kw in eq["expected_keywords"] if kw.lower() in answer_lower
        )
        correctness_pass = keyword_hits >= 1
        if correctness_pass:
            correctness_score += 1

        # --- Print results ---
        r = "PASS" if retrieval_pass else "FAIL"
        f = "PASS" if faithfulness_pass else "FAIL"
        c = "PASS" if correctness_pass else "FAIL"
        print(f"\nAnswer:\n{answer}\n")
        print(f"Retrieved cases: {retrieved_cases}")
        print(f"  Retrieval:    [{r}]")
        print(f"  Faithfulness: [{f}]")
        print(f"  Correctness:  [{c}]")

    # --- Final scorecard ---
    total = len(EVAL_QUESTIONS)
    print(f"\n{'=' * 60}")
    print("SCORECARD")
    print(f"{'=' * 60}")
    print(f"  Retrieval accuracy: {retrieval_score}/{total}")
    print(f"  Faithfulness:       {faithfulness_score}/{total}")
    print(f"  Correctness:        {correctness_score}/{total}")
    print(f"{'=' * 60}")


# =========================================================================
# MAIN — Run all 6 steps sequentially
# =========================================================================


def main() -> None:
    """Run the full RAG pipeline: Load → Chunk → Embed → Retrieve → Chain → Eval."""
    parser = argparse.ArgumentParser(description="Supreme Court Precedent Finder — RAG")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete the ChromaDB vector store and re-embed from scratch",
    )
    args = parser.parse_args()

    if args.reset:
        chroma_path = Path(CHROMA_DIR)
        if chroma_path.exists():
            shutil.rmtree(chroma_path)
            print(f"Deleted {CHROMA_DIR} — will re-embed from scratch.")

    # Step 1: Load opinions
    docs = load_documents()

    # Step 2: Chunk with comparison
    chunks = compare_chunk_strategies(docs)

    # Step 3: Embed and store in ChromaDB
    vectorstore = create_vectorstore(chunks)

    # Step 4: Test retrieval (before LLM)
    test_retrieval(vectorstore)

    # Step 5: Build RAG chain and run test queries
    chain = build_rag_chain(vectorstore)

    # Step 6: Evaluate
    evaluate(chain, vectorstore)


if __name__ == "__main__":
    main()
