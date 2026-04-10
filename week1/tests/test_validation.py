"""Tests for input validation — no LLM calls needed."""

import httpx
import pytest

from app.main import app


@pytest.fixture
async def client():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


async def test_summarize_empty_text_returns_422(client):
    response = await client.post("/summarize", json={"text": "", "max_length": 50})
    assert response.status_code == 422


async def test_summarize_missing_max_length_returns_422(client):
    response = await client.post("/summarize", json={"text": "Some text."})
    assert response.status_code == 422


async def test_summarize_text_too_long_returns_422(client):
    response = await client.post(
        "/summarize", json={"text": "x" * 10_001, "max_length": 50}
    )
    assert response.status_code == 422


async def test_summarize_max_length_zero_returns_422(client):
    response = await client.post(
        "/summarize", json={"text": "Some text.", "max_length": 0}
    )
    assert response.status_code == 422


async def test_summarize_max_length_too_high_returns_422(client):
    response = await client.post(
        "/summarize", json={"text": "Some text.", "max_length": 501}
    )
    assert response.status_code == 422


async def test_sentiment_empty_text_returns_422(client):
    response = await client.post("/analyze-sentiment", json={"text": ""})
    assert response.status_code == 422


async def test_sentiment_text_too_long_returns_422(client):
    response = await client.post("/analyze-sentiment", json={"text": "x" * 10_001})
    assert response.status_code == 422


async def test_sentiment_missing_text_returns_422(client):
    response = await client.post("/analyze-sentiment", json={})
    assert response.status_code == 422
