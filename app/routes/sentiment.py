from fastapi import APIRouter, Depends, Request

from app.dependencies import get_anthropic_service
from app.limiter import limiter
from app.models import SentimentRequest, SentimentResponse
from app.services.anthropic_service import AnthropicService

router = APIRouter()


@router.post("/analyze-sentiment", response_model=SentimentResponse)
@limiter.limit("1/second")
async def analyze_sentiment(
    request: Request,
    body: SentimentRequest,
    service: AnthropicService = Depends(get_anthropic_service),
):
    result = service.analyze_sentiment(body.text)
    return SentimentResponse(**result)
