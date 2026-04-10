from functools import lru_cache

from app.config import Settings
from app.services.anthropic_service import AnthropicService


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_anthropic_service() -> AnthropicService:
    return AnthropicService(settings=get_settings())
