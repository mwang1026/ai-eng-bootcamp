"""LLM-as-judge evals for agent quality.

These evaluate routing accuracy, policy compliance, and tone.
Run with: uv run pytest -m eval -v

Requires ANTHROPIC_API_KEY, Supabase, and returns service on port 8001.
"""

import pytest

from tests.conftest import ALICE_STATE, DAVID_STATE, IRIS_STATE, judge, run_agent

# -- Eval 1: Routing to billing -----------------------------------------------


@pytest.mark.eval
@pytest.mark.slow
@pytest.mark.requires_api_key
@pytest.mark.asyncio
async def test_eval_routing_to_billing(session_service):
    """Billing query should route correctly and return actual charge amounts."""
    user_message = "What are my recent charges?"
    response_text, _ = await run_agent(session_service, user_message, state=ALICE_STATE)
    rubric = (
        "The agent must provide specific billing information. PASS if the "
        "response includes at least one concrete dollar amount or order "
        "name from the customer's account. FAIL only if the agent refuses "
        "to help, says it cannot access billing data, or provides no "
        "specific charges at all."
    )
    verdict = await judge(user_message, response_text, rubric)
    assert verdict["pass"], f"Eval failed: {verdict['reason']}"


# -- Eval 2: Return eligible --------------------------------------------------


@pytest.mark.eval
@pytest.mark.slow
@pytest.mark.requires_api_key
@pytest.mark.asyncio
async def test_eval_return_eligible(session_service):
    """Return request for eligible order should confirm eligibility with details."""
    user_message = "I want to return order b0000000-0000-0000-0000-000000000001"
    response_text, _ = await run_agent(session_service, user_message, state=ALICE_STATE)
    rubric = (
        "The agent must handle the return request. It should either: "
        "(a) confirm eligibility and mention the hat name and refund amount, or "
        "(b) initiate the return and provide a ticket/confirmation. "
        "Either approach is acceptable. It must NOT refuse the return or "
        "say the order is ineligible (it IS eligible)."
    )
    verdict = await judge(user_message, response_text, rubric)
    assert verdict["pass"], f"Eval failed: {verdict['reason']}"


# -- Eval 3: Custom hat rejection tone ----------------------------------------


@pytest.mark.eval
@pytest.mark.slow
@pytest.mark.requires_api_key
@pytest.mark.asyncio
async def test_eval_custom_hat_rejection_tone(session_service):
    """Custom hat return rejection should be polite and clear."""
    user_message = "I want to return order b0000000-0000-0000-0000-000000000006"
    response_text, _ = await run_agent(session_service, user_message, state=IRIS_STATE)
    rubric = (
        "The agent must refuse the return because the hat is custom/personalized. "
        "The response must be polite and empathetic. It must NOT offer workarounds "
        "that contradict the no-custom-returns policy (e.g., 'try returning it "
        "anyway'). It may offer alternatives like contacting support for other help."
    )
    verdict = await judge(user_message, response_text, rubric)
    assert verdict["pass"], f"Eval failed: {verdict['reason']}"


# -- Eval 4: Expired window explanation ----------------------------------------


@pytest.mark.eval
@pytest.mark.slow
@pytest.mark.requires_api_key
@pytest.mark.asyncio
async def test_eval_expired_window_explanation(session_service):
    """Expired return window should be explained with specific details."""
    user_message = "I'd like to return order b0000000-0000-0000-0000-000000000005"
    response_text, _ = await run_agent(session_service, user_message, state=DAVID_STATE)
    rubric = (
        "The agent must refuse because the return window has expired. It must "
        "mention how many days have passed (approximately 40) and the window "
        "length (30 days). It should reference the customer's membership tier "
        "(silver) or explain that the standard window is 30 days."
    )
    verdict = await judge(user_message, response_text, rubric)
    assert verdict["pass"], f"Eval failed: {verdict['reason']}"


# -- Eval 5: Escalation empathy -----------------------------------------------


@pytest.mark.eval
@pytest.mark.slow
@pytest.mark.requires_api_key
@pytest.mark.asyncio
async def test_eval_escalation_empathy(session_service):
    """Escalation request should be handled with empathy and appropriate action."""
    user_message = (
        "I'm extremely upset about the quality of my hat. "
        "I want to speak to a manager NOW."
    )
    response_text, _ = await run_agent(session_service, user_message, state=ALICE_STATE)
    rubric = (
        "The agent must acknowledge the customer's frustration. It must offer "
        "escalation or mention connecting them with a manager/team. It must NOT "
        "be dismissive or minimize their concern. It must NOT hallucinate a phone "
        "number, email address, or specific manager name that was not provided."
    )
    verdict = await judge(user_message, response_text, rubric)
    assert verdict["pass"], f"Eval failed: {verdict['reason']}"


# -- Eval 6: Ambiguous request ------------------------------------------------


@pytest.mark.eval
@pytest.mark.slow
@pytest.mark.requires_api_key
@pytest.mark.asyncio
async def test_eval_ambiguous_request(session_service):
    """Vague request should prompt clarification, not random routing."""
    user_message = "I need help with my hat"
    response_text, _ = await run_agent(session_service, user_message, state=IRIS_STATE)
    rubric = (
        "The agent must ask a clarifying question or offer specific categories "
        "of help (billing, order status, returns, etc.). It must NOT guess which "
        "service to use without asking. It must NOT immediately route to a "
        "sub-agent without understanding the customer's intent."
    )
    verdict = await judge(user_message, response_text, rubric)
    assert verdict["pass"], f"Eval failed: {verdict['reason']}"
