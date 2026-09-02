from fastapi import APIRouter, Query
from typing import Optional, List
import json
from pathlib import Path

router = APIRouter(prefix="/api/catalog", tags=["Catalog"])

DATA_PATH = Path(__file__).parent.parent / "data" / "products.json"

def load_products():
    with open(DATA_PATH, "r") as f:
        return json.load(f)

@router.get("/semantic-feed")
async def get_agent_readable_catalog(
    max_price: Optional[float] = Query(None, description="Filter by max budget in INR"),
    category: Optional[str] = Query(None, description="Filter by product category")
):
    """
    Agent-facing endpoint adhering to JSON-LD semantic structure for LLM tool-calling.
    """
    products = load_products()
    filtered = []
    for item in products:
        price = item["offers"]["price"]
        cat = item["category"].lower()
        
        if max_price and price > max_price:
            continue
        if category and category.lower() not in cat:
            continue
        filtered.append(item)
        
    return {
        "protocol": "AP2/JSON-LD",
        "currency": "INR",
        "total_results": len(filtered),
        "items": filtered
    }