from datetime import datetime, timezone
from typing import Dict, Any, Tuple
from app.core.schemas import AgentIntentMandate, AgentCheckoutRequest, GateDecision
from app.core.config import SPEND_LIMIT_MAX_PER_TX_INR
import json
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "products.json"

def get_product_lookup() -> Dict[str, Any]:
    with open(DATA_PATH, "r") as f:
        products = json.load(f)
    return {p["sku"]: p for p in products}

class SpendGateEngine:
    @staticmethod
    def evaluate_transaction(
        mandate: AgentIntentMandate, 
        request: AgentCheckoutRequest
    ) -> GateDecision:
        product_db = get_product_lookup()
        
        # Check 1: Mandate Expiry
        current_time = datetime.now(timezone.utc)
        if mandate.expires_at < current_time:
            return GateDecision(
                is_approved=False,
                status_code="EXPIRED_MANDATE",
                calculated_total=0.0,
                message="The user-authorized mandate has expired.",
                requires_human_fallback=True
            )

        # Check 2: Catalog Truth & Server-Side Price Calculation
        calculated_total = 0.0
        for item in request.items:
            product = product_db.get(item.sku)
            if not product:
                return GateDecision(
                    is_approved=False,
                    status_code="INVALID_SKU",
                    calculated_total=0.0,
                    message=f"Product SKU {item.sku} does not exist.",
                    requires_human_fallback=True
                )
            
            # Stock Check
            available_stock = product["offers"]["inventoryLevel"]
            if item.quantity > available_stock:
                return GateDecision(
                    is_approved=False,
                    status_code="OUT_OF_STOCK",
                    calculated_total=0.0,
                    message=f"Insufficient inventory for {item.sku}. Requested: {item.quantity}, Available: {available_stock}.",
                    requires_human_fallback=True
                )

            # High-value item human verification flag
            if product.get("metadata", {}).get("requiresHumanVerification", False):
                return GateDecision(
                    is_approved=False,
                    status_code="REQUIRES_HUMAN_APPROVAL",
                    calculated_total=0.0,
                    message=f"Product {product['name']} strictly requires manual human sign-off.",
                    requires_human_fallback=True
                )

            # Calculate price using server database (ignoring any modified price from the LLM)
            catalog_price = float(product["offers"]["price"])
            
            # Check for bulk discount
            discounts = product["offers"].get("bulkDiscounts", [])
            applied_discount = 0.0
            for d in discounts:
                if item.quantity >= d["minQuantity"]:
                    applied_discount = max(applied_discount, d["discountPercent"])
            
            effective_price = catalog_price * (1 - applied_discount / 100)
            calculated_total += effective_price * item.quantity

        # Check 3: Check claimed total vs verified calculation (Anti-Tampering)
        if abs(calculated_total - request.claimed_total) > 0.01:
            return GateDecision(
                is_approved=False,
                status_code="PRICE_MISMATCH",
                calculated_total=calculated_total,
                message=f"Claimed total (₹{request.claimed_total}) does not match server-calculated total (₹{calculated_total}).",
                requires_human_fallback=True
            )

        # Check 4: Hard Platform Spend Limit
        if calculated_total > SPEND_LIMIT_MAX_PER_TX_INR:
            return GateDecision(
                is_approved=False,
                status_code="EXCEEDED_GLOBAL_LIMIT",
                calculated_total=calculated_total,
                message=f"Transaction total ₹{calculated_total} exceeds the global per-tx limit of ₹{SPEND_LIMIT_MAX_PER_TX_INR}.",
                requires_human_fallback=True
            )

        # Check 5: Mandate-Specific Budget Limit
        if calculated_total > mandate.max_budget_inr:
            return GateDecision(
                is_approved=False,
                status_code="EXCEEDED_MANDATE_BUDGET",
                calculated_total=calculated_total,
                message=f"Total ₹{calculated_total} exceeds authorized mandate budget of ₹{mandate.max_budget_inr}.",
                requires_human_fallback=True
            )

        # Passed all deterministic checks
        return GateDecision(
            is_approved=True,
            status_code="APPROVED",
            calculated_total=calculated_total,
            message="Deterministic checks passed. Transaction approved for gateway dispatch.",
            requires_human_fallback=False
        )