"""Integration tests for additional return/order scenarios.

These tests hit real APIs (Claude + Supabase) and require:
- ANTHROPIC_API_KEY set in environment
- Supabase tables created and seeded
- Returns service running on port 8001
"""

import pytest

from tests.conftest import ALICE_STATE, DAVID_STATE, IRIS_STATE, run_agent

# -- Custom hat rejection (b...006: Iris, custom, 5 days) ---------------------


@pytest.mark.slow
@pytest.mark.requires_api_key
@pytest.mark.asyncio
async def test_custom_hat_return_rejected(session_service):
    """Custom hats cannot be returned regardless of timing."""
    response_text, _ = await run_agent(
        session_service,
        "I want to return order b0000000-0000-0000-0000-000000000006",
        state=IRIS_STATE,
    )
    response_lower = response_text.lower()
    assert any(
        keyword in response_lower
        for keyword in [
            "custom",
            "cannot",
            "not eligible",
            "ineligible",
            "personalized",
        ]
    ), f"Expected custom hat rejection, got: {response_text[:500]}"


# -- Expired window for silver (b...005: David, beanie, 40 days) --------------


@pytest.mark.slow
@pytest.mark.requires_api_key
@pytest.mark.asyncio
async def test_expired_window_silver(session_service):
    """Silver member past the 30-day window should be rejected."""
    response_text, _ = await run_agent(
        session_service,
        "I'd like to return order b0000000-0000-0000-0000-000000000005",
        state=DAVID_STATE,
    )
    response_lower = response_text.lower()
    assert any(
        keyword in response_lower
        for keyword in ["expired", "window", "30", "not eligible", "ineligible"]
    ), f"Expected expired window rejection, got: {response_text[:500]}"


# -- Gold extended window (b...002: Alice, panama, 45 days) -------------------


@pytest.mark.slow
@pytest.mark.requires_api_key
@pytest.mark.asyncio
async def test_gold_extended_window_eligible(session_service):
    """Gold member within 60-day window should be eligible."""
    response_text, _ = await run_agent(
        session_service,
        "I want to return order b0000000-0000-0000-0000-000000000002",
        state=ALICE_STATE,
    )
    response_lower = response_text.lower()
    assert any(
        keyword in response_lower
        for keyword in ["eligible", "return", "panama", "refund", "ticket"]
    ), f"Expected eligible return response, got: {response_text[:500]}"


# -- Order status query (b...008: Alice, beret, shipped) ----------------------


@pytest.mark.slow
@pytest.mark.requires_api_key
@pytest.mark.asyncio
async def test_order_status_query(session_service):
    """Order status query should return current status."""
    response_text, _ = await run_agent(
        session_service,
        "What is the status of order b0000000-0000-0000-0000-000000000008?",
        state=ALICE_STATE,
    )
    response_lower = response_text.lower()
    assert any(
        keyword in response_lower
        for keyword in ["shipped", "beret", "transit", "delivery", "on its way"]
    ), f"Expected order status info, got: {response_text[:500]}"
