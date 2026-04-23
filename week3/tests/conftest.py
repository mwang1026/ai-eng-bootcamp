"""Shared fixtures, helpers, and hooks for the test suite."""

import os

import pytest
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Load .env so API keys are available at collection time
load_dotenv()

# -- Marker hooks -------------------------------------------------------------


def pytest_collection_modifyitems(config, items):
    """Auto-skip tests marked requires_api_key when credentials are missing."""
    skip_no_key = pytest.mark.skip(reason="ANTHROPIC_API_KEY not set")
    for item in items:
        if "requires_api_key" in item.keywords and not os.getenv("ANTHROPIC_API_KEY"):
            item.add_marker(skip_no_key)


# -- Customer state dicts -----------------------------------------------------

ALICE_STATE = {
    "user_name": "Alice Chen",
    "user_email": "alice.chen@email.com",
    "membership_tier": "gold",
    "customer_id": "a0000000-0000-0000-0000-000000000001",
}

IRIS_STATE = {
    "user_name": "Iris Thompson",
    "user_email": "iris.thompson@email.com",
    "membership_tier": "bronze",
    "customer_id": "a0000000-0000-0000-0000-000000000009",
}

BOB_STATE = {
    "user_name": "Bob Martinez",
    "user_email": "bob.martinez@email.com",
    "membership_tier": "gold",
    "customer_id": "a0000000-0000-0000-0000-000000000002",
}

DAVID_STATE = {
    "user_name": "David Kim",
    "user_email": "david.kim@email.com",
    "membership_tier": "silver",
    "customer_id": "a0000000-0000-0000-0000-000000000004",
}

# -- Fixtures -----------------------------------------------------------------


@pytest.fixture
def session_service():
    return InMemorySessionService()


# -- Agent runner helper ------------------------------------------------------


async def run_agent(session_service, user_message: str, state: dict | None = None):
    """Send a message to the root agent and collect response text.

    Lazily imports root_agent to avoid import-time failures when
    environment variables or MCP services are not available.
    """
    from hat_store_agent.agent import root_agent

    runner = Runner(
        app_name="hat_store_test",
        agent=root_agent,
        session_service=session_service,
    )
    session = await session_service.create_session(
        app_name="hat_store_test",
        user_id="test_user",
        state=state or {},
    )
    message = types.Content(
        role="user",
        parts=[types.Part(text=user_message)],
    )
    events = []
    async for event in runner.run_async(
        session_id=session.id,
        user_id="test_user",
        new_message=message,
    ):
        events.append(event)

    response_text = ""
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text
    return response_text, events


# -- LLM-as-judge helper ------------------------------------------------------


async def judge(user_message: str, agent_response: str, rubric: str) -> dict:
    """Ask Claude to grade an agent response against a rubric.

    Returns {"pass": bool, "reason": str}.
    """
    import litellm

    prompt = (
        "You are grading an AI customer support agent's response.\n\n"
        f"USER MESSAGE: {user_message}\n\n"
        f"AGENT RESPONSE: {agent_response}\n\n"
        f"RUBRIC:\n{rubric}\n\n"
        "Respond with exactly one line: PASS or FAIL, followed by a brief reason.\n"
        "Example: PASS - correctly identified order as eligible for return\n"
        "Example: FAIL - did not mention the 60-day gold member window"
    )

    response = await litellm.acompletion(
        model="anthropic/claude-haiku-4-5-20251001",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
    )
    text = response.choices[0].message.content.strip()
    passed = text.upper().startswith("PASS")
    return {"pass": passed, "reason": text}
