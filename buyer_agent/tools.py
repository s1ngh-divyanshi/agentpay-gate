import httpx
from typing import Optional, List, Dict, Any

BACKEND_BASE_URL = "http://localhost:8000"

def search_merchant_catalog(max_price: Optional[float] = None, category: Optional[str] = None) -> Dict[str, Any]:
    """
    Query the merchant's live agent-readable catalog for available inventory, specifications, and prices.
    """
    params = {}
    if max_price:
        params["max_price"] = max_price
    if category:
        params["category"] = category
        
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{BACKEND_BASE_URL}/api/catalog/semantic-feed", params=params)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": f"Failed to query catalog: {str(e)}"}

def dispatch_checkout_intent(
    mandate_id: str,
    merchant_id: str,
    items: List[Dict[str, Any]],
    claimed_total: float,
    reasoning_trace: str
) -> Dict[str, Any]:
    """
    Submit a purchase request to the AgentPay Gate checkout engine.
    items should be a list of dicts with keys: sku (str), quantity (int), unit_price (float).
    """
    payload = {
        "mandate_id": mandate_id,
        "merchant_id": merchant_id,
        "items": items,
        "claimed_total": claimed_total,
        "reasoning_trace": reasoning_trace,
        "currency": "INR"
    }
    
    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.post(f"{BACKEND_BASE_URL}/api/checkout/execute", json=payload)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": f"Checkout dispatch failed: {str(e)}"}