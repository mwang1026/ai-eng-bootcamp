from fastapi import APIRouter, Depends, Request

from app.dependencies import get_anthropic_service
from app.limiter import limiter
from app.models import SummarizeRequest, SummarizeResponse
from app.services.anthropic_service import AnthropicService

router = APIRouter()


@router.post("/summarize", response_model=SummarizeResponse)
@limiter.limit("1/second")
async def summarize(
    request: Request,
    body: SummarizeRequest,
    service: AnthropicService = Depends(get_anthropic_service),
):
    summary = service.summarize(body.text, body.max_length)
    return SummarizeResponse(summary=summary)
