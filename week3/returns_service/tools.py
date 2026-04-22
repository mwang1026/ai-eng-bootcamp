"""Return eligibility and initiation tools for Hats R Us.

Calls Supabase REST API directly via httpx. Only requires order_id —
the customer is resolved from the order's customer_id foreign key.
"""

import os
from datetime import UTC, datetime

import httpx

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

RETURN_WINDOW_DAYS = 30
GOLD_RETURN_WINDOW_DAYS = 60


def _supabase_headers() -> dict[str, str]:
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def _get(table: str, params: dict) -> list[dict]:
    resp = httpx.get(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=_supabase_headers(),
        params=params,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def _post(table: str, data: dict) -> list[dict]:
    resp = httpx.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=_supabase_headers(),
        json=data,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def check_return_eligibility(order_id: str) -> dict:
    """Check if an order is eligible for return.

    Args:
        order_id: The UUID of the order to check.

    Returns:
        A dict with eligible (bool), reason (str), and order details.
    """
    orders = _get("orders", {"id": f"eq.{order_id}", "select": "*"})
    if not orders:
        return {"eligible": False, "reason": "Order not found."}
    order = orders[0]

    customers = _get("customers", {"id": f"eq.{order['customer_id']}", "select": "*"})
    customer = customers[0]

    if order["status"] != "delivered":
        return {
            "eligible": False,
            "reason": (
                f"Order status is '{order['status']}'. "
                "Only delivered orders can be returned."
            ),
        }

    if order["hat_style"] == "custom":
        return {
            "eligible": False,
            "reason": "Custom/personalized hats cannot be returned.",
        }

    ordered_at = datetime.fromisoformat(order["ordered_at"])
    days_since_order = (datetime.now(UTC) - ordered_at).days
    tier = customer["membership_tier"]
    window = GOLD_RETURN_WINDOW_DAYS if tier == "gold" else RETURN_WINDOW_DAYS

    if days_since_order > window:
        return {
            "eligible": False,
            "reason": (
                f"Return window expired. Order was placed "
                f"{days_since_order} days ago. Your {tier} "
                f"membership has a {window}-day return window."
            ),
        }

    return {
        "eligible": True,
        "days_remaining": window - days_since_order,
        "order": {
            "hat_name": order["hat_name"],
            "hat_style": order["hat_style"],
            "total": str(order["total"]),
        },
        "customer_name": customer["name"],
        "membership_tier": tier,
    }


def initiate_return(order_id: str) -> dict:
    """Initiate a return for an order. Call check_return_eligibility first.

    Args:
        order_id: The UUID of the order to return.

    Returns:
        A dict with success (bool), ticket_id (str), and details.
    """
    eligibility = check_return_eligibility(order_id)
    if not eligibility["eligible"]:
        return {"success": False, "reason": eligibility["reason"]}

    orders = _get("orders", {"id": f"eq.{order_id}", "select": "customer_id"})
    customer_id = orders[0]["customer_id"]

    tickets = _post(
        "support_tickets",
        {
            "customer_id": customer_id,
            "order_id": order_id,
            "subject": f"Return: {eligibility['order']['hat_name']}",
            "description": (
                f"Return initiated for {eligibility['order']['hat_name']}. "
                f"Refund amount: ${eligibility['order']['total']}."
            ),
            "category": "return",
            "status": "open",
            "priority": "medium",
        },
    )

    return {
        "success": True,
        "ticket_id": tickets[0]["id"],
        "hat_name": eligibility["order"]["hat_name"],
        "refund_amount": eligibility["order"]["total"],
    }
