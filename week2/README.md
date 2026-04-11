# Week 2: Supreme Court Precedent Finder (RAG)

A retrieval-augmented generation pipeline that answers questions about Supreme Court precedent from 2000-2009, using ChromaDB for vector search and Claude for generation.

## Architecture

```
CourtListener REST API
        │
        ▼
   JSON Cache (data/opinions.json)
        │
        ▼
   LangChain JSONLoader → Documents
        │
        ▼
   RecursiveCharacterTextSplitter → Chunks
        │
        ▼
   HuggingFace all-MiniLM-L6-v2 → Embeddings
        │
        ▼
   ChromaDB (chroma_db/) → Vector Store
        │
        ▼
   RetrievalQA Chain (retriever + Claude) → Grounded Answers
```

## Setup

```bash
cd week2
uv sync

# Copy .env.example to .env and fill in:
#   ANTHROPIC_API_KEY — your Anthropic API key
#   COURTLISTENER_API_TOKEN — free token from courtlistener.com/profile/
cp .env.example .env

# Run the full pipeline
uv run python rag.py
```

### Getting a CourtListener API Token

1. Register at [courtlistener.com](https://www.courtlistener.com/register/)
2. Go to your [profile page](https://www.courtlistener.com/profile/)
3. Copy the API token and add it to your `.env` file

## The 6 Steps

### Step 1: Load
Fetches ~50-100 SCOTUS opinions (2000-2009) from the CourtListener REST API v4. Responses are cached to `data/opinions.json` so subsequent runs skip the API call. Uses LangChain's `JSONLoader` to parse the cached data into `Document` objects.

### Step 2: Chunk
Splits opinions using `RecursiveCharacterTextSplitter` with two strategies:
- **500 / 100 overlap** — More chunks, finer granularity, but fragments legal arguments
- **1000 / 200 overlap** — Fewer chunks, preserves multi-paragraph reasoning

Selected **1000/200** because legal opinions contain arguments that span multiple paragraphs. Cutting mid-argument loses context the LLM needs.

### Step 3: Embed + Store
Embeds chunks locally using `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional vectors) and stores in ChromaDB. The vector store persists to `chroma_db/` — re-runs load from disk instead of re-embedding.

### Step 4: Test Retrieval
Runs 3 test queries against the vector store (without the LLM) to verify that retrieval returns relevant chunks. This isolates retrieval quality from generation quality.

### Step 5: Build RAG Chain
Wires up `RetrievalQA` with Claude (`claude-haiku-4-5-20251001`) and a strict grounding prompt that instructs the model to answer ONLY from the provided context and refuse if the context is insufficient.

### Step 6: Evaluate
Runs 5 questions through the full pipeline and scores each on:
- **Retrieval accuracy** — Did the vector store return chunks from the correct case?
- **Faithfulness** — Is the answer grounded in the context (not hallucinated)?
- **Correctness** — Is the answer factually right?

Question 5 is a **negative test**: it asks about Obergefell v. Hodges (2015), which is outside our 2000-2009 corpus. If the grounding prompt works, the model should refuse rather than answering from its training knowledge.

## Key Design Decisions

- **Local embeddings** over an embedding API: No extra account, zero cost, adequate quality for ~100 documents. The chunking strategy matters more than embedding model choice at this scale.
- **Strict grounding prompt**: The biggest lever for preventing hallucination. Combined with negative test cases, this lets us measure whether answers actually come from RAG.
- **Cached API responses**: Avoids hammering CourtListener on re-runs and makes the script idempotent.
- **chunk_size=1000**: Legal reasoning spans paragraphs. Smaller chunks fragment arguments and hurt retrieval quality.

## Cost

- Embeddings: Free (runs locally)
- CourtListener API: Free (with token)
- Claude Haiku: ~$0.01-0.02 for the full eval suite (8 queries × ~5K input tokens each)
