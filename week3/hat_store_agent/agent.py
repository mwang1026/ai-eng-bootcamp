"""Hats R Us multi-agent customer support system.

Root agent routes to:
- billing_agent (MCP/Supabase) — billing inquiries, charges, refunds
- order_status_agent (MCP/Supabase) — order tracking, delivery status
- returns_agent (A2A remote) — return eligibility and processing
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

load_dotenv()

_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load_prompt(name: str) -> str:
    return (_PROMPTS_DIR / f"{name}.txt").read_text()


MODEL = LiteLlm(model=os.getenv("MODEL", "anthropic/claude-haiku-4-5-20251001"))

# -- MCP Toolset: Supabase (stdio approach) ----------------------------------
# The Supabase MCP server exposes many tools (apply_migration, deploy_edge_function,
# create_branch, etc.). We use ADK tool_filter to restrict each agent to only the
# tools it needs — read-only database access via list_tables + execute_sql.
# This is safer than relying on --read-only at the server level because the
# filtering happens in ADK before the LLM ever sees the tool definitions.

_supabase_connection = StdioConnectionParams(
    server_params=StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "@supabase/mcp-server-supabase@latest",
            "--access-token",
            os.getenv("SUPABASE_ACCESS_TOKEN", ""),
            "--project-ref",
            os.getenv("SUPABASE_PROJECT_REF", ""),
        ],
    ),
)

# Read-only toolset: agents can list tables and run SELECT queries
supabase_read_only = McpToolset(
    connection_params=_supabase_connection,
    tool_filter=["list_tables", "execute_sql"],
)

# -- Sub-agent: Billing -------------------------------------------------------
billing_agent = LlmAgent(
    model=MODEL,
    name="billing_agent",
    description=(
        "Handles billing inquiries: invoices, payment status, charges, "
        "refunds, and account balance questions."
    ),
    instruction=_load_prompt("billing_agent"),
    tools=[supabase_read_only],
)

# -- Sub-agent: Order Status ---------------------------------------------------
order_status_agent = LlmAgent(
    model=MODEL,
    name="order_status_agent",
    description=(
        "Handles order tracking and status inquiries: where is my order, "
        "delivery estimates, order history."
    ),
    instruction=_load_prompt("order_status_agent"),
    tools=[supabase_read_only],
)

# -- Sub-agent: Returns (A2A Remote) ------------------------------------------
returns_agent_url = os.getenv("RETURNS_AGENT_URL", "http://localhost:8001")
returns_agent = RemoteA2aAgent(
    name="returns_agent",
    description=(
        "Handles return requests: checks return eligibility based on the "
        "30-day return window (60 days for gold members), and initiates "
        "returns for eligible orders. Cannot return custom hats."
    ),
    agent_card=f"{returns_agent_url}/.well-known/agent-card.json",
)

# -- Root Agent (Router) -------------------------------------------------------
root_agent = LlmAgent(
    model=MODEL,
    name="hat_store_support",
    description="Main customer support router for Hats R Us hat store.",
    instruction=_load_prompt("root_agent"),
    sub_agents=[billing_agent, order_status_agent, returns_agent],
)
