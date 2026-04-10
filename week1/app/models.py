from enum import StrEnum

from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10_000)
    max_length: int = Field(
        ..., gt=0, le=500, description="Target word count for the summary"
    )


class SummarizeResponse(BaseModel):
    summary: str


class Sentiment(StrEnum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10_000)


class SentimentResponse(BaseModel):
    sentiment: Sentiment
    explanation: str
