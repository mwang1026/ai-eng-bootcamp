"""Integration tests for the 4 required scenarios.

These tests hit real APIs (Claude + Supabase) and require:
- ANTHROPIC_API_KEY set in environment
- Supabase tables created and seeded
- Returns service running on port 8001 (for test_returns_via_a2a)

Run all: uv run pytest tests/
Run fast only: uv run pytest tests/ -m "not slow"
"""

import pytest
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# -- Fixtures -----------------------------------------------------------------


@pytest.fixture
def session_service():
    return InMemorySessionService()


async def _run_agent(session_service, user_message: str, state: dict | None = None):
    """Send a message to the root agent and collect response text."""
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

    # Collect all text from agent responses
    response_text = ""
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text
    return response_text, events


# -- Test State ---------------------------------------------------------------

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


# -- Scenario 1: Billing (MCP) -----------------------------------------------


@pytest.mark.slow
@pytest.mark.requires_api_key
@pytest.mark.asyncio
async def test_billing_query_via_mcp(session_service):
    """Billing query routes to billing_agent, queries Supabase via MCP."""
    response_text, events = await _run_agent(
        session_service,
        "Can you check my recent charges?",
        state=ALICE_STATE,
    )
    response_lower = response_text.lower()
    assert any(
        keyword in response_lower
        for keyword in ["order", "charge", "total", "$", "fedora", "panama"]
    ), f"Expected billing info in response, got: {response_text[:500]}"


# -- Scenario 2: Returns with order ID (A2A) ----------------------------------


@pytest.mark.slow
@pytest.mark.requires_api_key
@pytest.mark.asyncio
async def test_returns_with_order_id_via_a2a(session_service):
    """Return request with order ID routes to returns_agent via A2A.

    Uses Iris's bucket hat order (b...007), delivered 20 days ago, eligible.
    """
    response_text, events = await _run_agent(
        session_service,
        "I want to return order b0000000-0000-0000-0000-000000000007",
        state=IRIS_STATE,
    )
    response_lower = response_text.lower()
    assert any(
        keyword in response_lower
        for keyword in ["return", "eligible", "bucket", "refund", "ticket"]
    ), f"Expected return info in response, got: {response_text[:500]}"


# -- Scenario 3: Returns without order ID (order lookup → A2A) ----------------


@pytest.mark.slow
@pytest.mark.requires_api_key
@pytest.mark.asyncio
async def test_returns_without_order_id_prompts_lookup(session_service):
    """Return request without order ID asks for ID or offers to look up orders."""
    response_text, events = await _run_agent(
        session_service,
        "I want to return an order",
        state=IRIS_STATE,
    )
    response_lower = response_text.lower()
    assert any(
        keyword in response_lower
        for keyword in ["order id", "look up", "which order", "recent orders"]
    ), f"Expected order ID prompt or lookup offer, got: {response_text[:500]}"


# -- Scenario 4: Escalation ---------------------------------------------------


@pytest.mark.slow
@pytest.mark.requires_api_key
@pytest.mark.asyncio
async def test_escalation(session_service):
    """Unrecognized request handled by root agent (escalation)."""
    response_text, events = await _run_agent(
        session_service,
        "I want to speak to a manager about hat quality.",
        state=ALICE_STATE,
    )
    response_lower = response_text.lower()
    assert any(
        keyword in response_lower
        for keyword in [
            "manager",
            "escalat",
            "team",
            "representative",
            "help",
            "concern",
            "sorry",
        ]
    ), f"Expected escalation response, got: {response_text[:500]}"
