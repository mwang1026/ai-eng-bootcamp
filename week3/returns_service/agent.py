"""Returns Agent — exposed as an A2A service on port 8001.

Run with:
    uv run uvicorn returns_service.agent:a2a_app --port 8001
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env BEFORE importing tools (they read env vars at import time)
# Check week3/.env first, then hat_store_agent/.env (ADK convention)
_week3_dir = Path(__file__).parent.parent
for _env_candidate in [_week3_dir / ".env", _week3_dir / "hat_store_agent" / ".env"]:
    if _env_candidate.exists():
        load_dotenv(_env_candidate)
        break

from google.adk.a2a.utils.agent_to_a2a import to_a2a  # noqa: E402
from google.adk.agents import LlmAgent  # noqa: E402
from google.adk.models.lite_llm import LiteLlm  # noqa: E402

from .tools import check_return_eligibility, initiate_return  # noqa: E402

MODEL = LiteLlm(model=os.getenv("MODEL", "anthropic/claude-haiku-4-5-20251001"))

_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

root_agent = LlmAgent(
    model=MODEL,
    name="returns_agent",
    description=(
        "Handles return eligibility checks and return "
        "initiation for Hats R Us hat store."
    ),
    instruction=(_PROMPTS_DIR / "returns_agent.txt").read_text(),
    tools=[check_return_eligibility, initiate_return],
)

_returns_url = os.getenv("RETURNS_AGENT_URL", "http://localhost:8001")
_returns_port = int(_returns_url.rsplit(":", 1)[-1])

a2a_app = to_a2a(root_agent, port=_returns_port)
