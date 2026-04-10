"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from app.models import (
    Sentiment,
    SentimentRequest,
    SentimentResponse,
    SummarizeRequest,
    SummarizeResponse,
)


def test_summarize_request_valid():
    req = SummarizeRequest(text="Hello world", max_length=50)
    assert req.text == "Hello world"
    assert req.max_length == 50


def test_summarize_request_rejects_empty_text():
    with pytest.raises(ValidationError):
        SummarizeRequest(text="", max_length=50)


def test_summarize_request_rejects_oversized_text():
    with pytest.raises(ValidationError):
        SummarizeRequest(text="x" * 10_001, max_length=50)


def test_summarize_response():
    resp = SummarizeResponse(summary="A summary.")
    assert resp.summary == "A summary."


def test_sentiment_request_valid():
    req = SentimentRequest(text="I love this")
    assert req.text == "I love this"


def test_sentiment_response_valid():
    resp = SentimentResponse(sentiment=Sentiment.positive, explanation="Good vibes")
    assert resp.sentiment == Sentiment.positive
    assert resp.explanation == "Good vibes"


def test_sentiment_response_rejects_invalid_sentiment():
    with pytest.raises(ValidationError):
        SentimentResponse(sentiment="angry", explanation="Bad vibes")


def test_sentiment_enum_values():
    assert set(Sentiment) == {Sentiment.positive, Sentiment.neutral, Sentiment.negative}
