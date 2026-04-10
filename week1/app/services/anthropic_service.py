import logging
from pathlib import Path

import httpx
from anthropic import Anthropic, APIError, APITimeoutError
from fastapi import HTTPException
from pydantic import BaseModel

from app.config import Settings

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"


class AnthropicService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.client = Anthropic(
            api_key=self.settings.anthropic_api_key,
            timeout=httpx.Timeout(self.settings.anthropic_timeout, connect=5.0),
        )
        self.model = self.settings.default_model

    def _load_prompt(self, filename: str) -> str:
        return (PROMPTS_DIR / filename).read_text()

    def _call_llm[T: BaseModel](
        self,
        *,
        system: str,
        user_message: str,
        output_format: type[T],
        max_tokens: int = 1024,
    ) -> T:
        try:
            response = self.client.messages.parse(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user_message}],
                output_format=output_format,
            )
            logger.info(
                "Anthropic API call: input_tokens=%d output_tokens=%d",
                response.usage.input_tokens,
                response.usage.output_tokens,
            )
            result = response.parsed_output
            if result is None:
                logger.error("Anthropic returned no parsed output")
                raise HTTPException(
                    status_code=502, detail="LLM returned empty response"
                )
            return result
        except APITimeoutError:
            logger.exception("Anthropic API timeout")
            raise HTTPException(
                status_code=502, detail="LLM service timed out"
            ) from None
        except APIError:
            logger.exception("Anthropic API error")
            raise HTTPException(status_code=502, detail="LLM service error") from None

    def summarize(self, text: str, max_length: int) -> str:
        from app.models import SummarizeResponse

        system = self._load_prompt("summarize.txt")
        user_msg = (
            f"Summarize the following text in approximately "
            f"{max_length} words:\n\n{text}"
        )
        result = self._call_llm(
            system=system,
            user_message=user_msg,
            output_format=SummarizeResponse,
            max_tokens=max_length * 3,
        )
        return result.summary

    def analyze_sentiment(self, text: str) -> dict:
        from app.models import SentimentResponse

        system = self._load_prompt("analyze_sentiment.txt")
        result = self._call_llm(
            system=system,
            user_message=text,
            output_format=SentimentResponse,
            max_tokens=512,
        )
        return {"sentiment": result.sentiment, "explanation": result.explanation}
