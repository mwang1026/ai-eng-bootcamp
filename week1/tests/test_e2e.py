"""End-to-end tests that hit the real Anthropic API.

These tests require a valid ANTHROPIC_API_KEY in .env.
They make real API calls and cost real money (tiny amounts with Haiku).
"""

import asyncio

import httpx
import pytest

from app.main import app
from app.models import Sentiment


@pytest.fixture
async def client():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
        timeout=60.0,
    ) as c:
        yield c


async def test_summarize_returns_summary(client):
    text = (
        "FastAPI is a modern, fast (high-performance), web framework for "
        "building APIs with Python based on standard Python type hints. "
        "The key features are: Fast to code, fewer bugs, intuitive, easy, "
        "short, robust, standards-based. It is built on top of Starlette "
        "for the web parts and Pydantic for the data parts."
    )
    response = await client.post("/summarize", json={"text": text, "max_length": 20})
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert len(data["summary"]) > 0


async def test_analyze_sentiment_positive(client):
    await asyncio.sleep(1.1)  # respect rate limit
    response = await client.post(
        "/analyze-sentiment",
        json={"text": "I absolutely love this product! It's amazing and wonderful."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] in [s.value for s in Sentiment]
    assert len(data["explanation"]) > 0
    assert data["sentiment"] == "positive"


async def test_analyze_sentiment_negative(client):
    await asyncio.sleep(1.1)  # respect rate limit
    response = await client.post(
        "/analyze-sentiment",
        json={"text": "This is terrible. I hate it. Worst experience ever."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] == "negative"
    assert len(data["explanation"]) > 0


async def test_analyze_sentiment_neutral(client):
    await asyncio.sleep(1.1)  # respect rate limit
    response = await client.post(
        "/analyze-sentiment",
        json={"text": "The meeting is scheduled for 3pm on Tuesday in room 204."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] == "neutral"
    assert len(data["explanation"]) > 0
