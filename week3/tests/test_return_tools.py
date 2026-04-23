"""Unit tests for returns_service/tools.py.

All tests mock _get and _post — no network calls, no API keys required.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import call, patch

from returns_service.tools import check_return_eligibility, initiate_return

# -- Helpers -------------------------------------------------------------------


def _order(
    *,
    days_ago: int = 10,
    status: str = "delivered",
    hat_style: str = "fedora",
    hat_name: str = "Classic Wool Fedora",
    customer_id: str = "cust-001",
    total: float = 89.99,
):
    """Build a mock order dict with sensible defaults."""
    ordered_at = (datetime.now(UTC) - timedelta(days=days_ago)).isoformat()
    return {
        "id": "order-001",
        "customer_id": customer_id,
        "hat_name": hat_name,
        "hat_style": hat_style,
        "color": "black",
        "size": "M",
        "quantity": 1,
        "unit_price": float(total),
        "total": float(total),
        "status": status,
        "ordered_at": ordered_at,
    }


def _customer(*, tier: str = "bronze", name: str = "Test User"):
    return {
        "id": "cust-001",
        "name": name,
        "email": "test@example.com",
        "membership_tier": tier,
    }


def _mock_get(order_rows, customer_rows=None):
    """Return a side_effect function for _get that dispatches by table name."""

    def side_effect(table, params):
        if table == "orders":
            return order_rows
        if table == "customers":
            return customer_rows or []
        return []

    return side_effect


# -- check_return_eligibility tests -------------------------------------------


@patch("returns_service.tools._get")
class TestCheckReturnEligibility:
    """Tests for check_return_eligibility covering every branch."""

    def test_order_not_found(self, mock_get):
        mock_get.side_effect = _mock_get(order_rows=[])
        result = check_return_eligibility("nonexistent-id")
        assert result["eligible"] is False
        assert "not found" in result["reason"].lower()

    def test_order_pending(self, mock_get):
        mock_get.side_effect = _mock_get(
            order_rows=[_order(status="pending")],
            customer_rows=[_customer()],
        )
        result = check_return_eligibility("order-001")
        assert result["eligible"] is False
        assert "pending" in result["reason"].lower()

    def test_order_shipped(self, mock_get):
        mock_get.side_effect = _mock_get(
            order_rows=[_order(status="shipped")],
            customer_rows=[_customer()],
        )
        result = check_return_eligibility("order-001")
        assert result["eligible"] is False
        assert "shipped" in result["reason"].lower()

    def test_order_cancelled(self, mock_get):
        mock_get.side_effect = _mock_get(
            order_rows=[_order(status="cancelled")],
            customer_rows=[_customer()],
        )
        result = check_return_eligibility("order-001")
        assert result["eligible"] is False
        assert "cancelled" in result["reason"].lower()

    def test_custom_hat_rejected(self, mock_get):
        mock_get.side_effect = _mock_get(
            order_rows=[_order(hat_style="custom")],
            customer_rows=[_customer()],
        )
        result = check_return_eligibility("order-001")
        assert result["eligible"] is False
        assert "custom" in result["reason"].lower()

    def test_bronze_within_window(self, mock_get):
        mock_get.side_effect = _mock_get(
            order_rows=[_order(days_ago=15)],
            customer_rows=[_customer(tier="bronze")],
        )
        result = check_return_eligibility("order-001")
        assert result["eligible"] is True
        assert result["days_remaining"] == 15
        assert result["membership_tier"] == "bronze"

    def test_bronze_expired(self, mock_get):
        mock_get.side_effect = _mock_get(
            order_rows=[_order(days_ago=35)],
            customer_rows=[_customer(tier="bronze")],
        )
        result = check_return_eligibility("order-001")
        assert result["eligible"] is False
        assert "30" in result["reason"]
        assert "expired" in result["reason"].lower()

    def test_gold_within_extended_window(self, mock_get):
        mock_get.side_effect = _mock_get(
            order_rows=[_order(days_ago=45)],
            customer_rows=[_customer(tier="gold")],
        )
        result = check_return_eligibility("order-001")
        assert result["eligible"] is True
        assert result["days_remaining"] == 15
        assert result["membership_tier"] == "gold"

    def test_gold_expired(self, mock_get):
        mock_get.side_effect = _mock_get(
            order_rows=[_order(days_ago=65)],
            customer_rows=[_customer(tier="gold")],
        )
        result = check_return_eligibility("order-001")
        assert result["eligible"] is False
        assert "60" in result["reason"]
        assert "expired" in result["reason"].lower()

    def test_silver_gets_standard_window(self, mock_get):
        """Silver members get the 30-day window, not the 60-day gold window."""
        mock_get.side_effect = _mock_get(
            order_rows=[_order(days_ago=35)],
            customer_rows=[_customer(tier="silver")],
        )
        result = check_return_eligibility("order-001")
        assert result["eligible"] is False
        assert "30" in result["reason"]

    def test_boundary_day_30_bronze(self, mock_get):
        """Exactly 30 days ago should still be eligible (code uses >, not >=)."""
        mock_get.side_effect = _mock_get(
            order_rows=[_order(days_ago=30)],
            customer_rows=[_customer(tier="bronze")],
        )
        result = check_return_eligibility("order-001")
        assert result["eligible"] is True
        assert result["days_remaining"] == 0

    def test_boundary_day_zero(self, mock_get):
        """Order placed today should be eligible with full window remaining."""
        mock_get.side_effect = _mock_get(
            order_rows=[_order(days_ago=0)],
            customer_rows=[_customer(tier="bronze")],
        )
        result = check_return_eligibility("order-001")
        assert result["eligible"] is True
        assert result["days_remaining"] == 30

    def test_eligible_response_includes_order_details(self, mock_get):
        """Eligible result includes order details and customer_name."""
        mock_get.side_effect = _mock_get(
            order_rows=[_order(hat_name="Summer Panama", total=75.00)],
            customer_rows=[_customer(tier="bronze", name="Alice Chen")],
        )
        result = check_return_eligibility("order-001")
        assert result["eligible"] is True
        assert result["order"]["hat_name"] == "Summer Panama"
        assert result["order"]["total"] == "75.0"
        assert result["customer_name"] == "Alice Chen"


# -- initiate_return tests ----------------------------------------------------


@patch("returns_service.tools._post")
@patch("returns_service.tools._get")
class TestInitiateReturn:
    """Tests for initiate_return."""

    def test_ineligible_order(self, mock_get, mock_post):
        """Ineligible order should return success=False without creating a ticket."""
        mock_get.side_effect = _mock_get(order_rows=[])
        result = initiate_return("nonexistent-id")
        assert result["success"] is False
        assert "not found" in result["reason"].lower()
        mock_post.assert_not_called()

    def test_success(self, mock_get, mock_post):
        """Eligible order should create a ticket and return success=True."""
        order = _order(days_ago=10, hat_name="Classic Fedora", total=89.99)
        customer = _customer(tier="bronze", name="Test User")

        # _get called 3x: eligibility (orders, customers), then orders
        mock_get.side_effect = [
            [order],  # check_return_eligibility → orders
            [customer],  # check_return_eligibility → customers
            [order],  # initiate_return → orders (for customer_id)
        ]
        mock_post.return_value = [{"id": "ticket-abc-123"}]

        result = initiate_return("order-001")
        assert result["success"] is True
        assert result["ticket_id"] == "ticket-abc-123"
        assert result["hat_name"] == "Classic Fedora"
        assert result["refund_amount"] == "89.99"

    def test_post_payload(self, mock_get, mock_post):
        """Verify the support ticket POST payload is correctly constructed."""
        order = _order(days_ago=5, hat_name="Bucket Hat", total=39.99)
        customer = _customer(tier="bronze")

        mock_get.side_effect = [
            [order],
            [customer],
            [order],
        ]
        mock_post.return_value = [{"id": "ticket-xyz"}]

        initiate_return("order-001")

        mock_post.assert_called_once()
        args = mock_post.call_args
        assert args == call(
            "support_tickets",
            {
                "customer_id": "cust-001",
                "order_id": "order-001",
                "subject": "Return: Bucket Hat",
                "description": (
                    "Return initiated for Bucket Hat. Refund amount: $39.99."
                ),
                "category": "return",
                "status": "open",
                "priority": "medium",
            },
        )
