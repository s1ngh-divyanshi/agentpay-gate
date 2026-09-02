from fastapi import APIRouter, HTTPException
from app.core.schemas import AgentCheckoutRequest, AgentIntentMandate, GateDecision
from app.core.guardrails import SpendGateEngine
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/api/gate", tags=["Spend Gate"])

# Mock active mandate repository for testing
MOCK_MANDATE = AgentIntentMandate(
    mandate_id="MANDATE-DEMO-001",
    buyer_agent_id="AGENT-PROCURE-BOT",
    user_id="USER-9876",
    max_budget_inr=10000.0,
    authorized_categories=["Office Furniture", "Electronics"],
    expires_at=datetime.now(timezone.utc) + timedelta(hours=2)
)

@router.post("/evaluate", response_model=GateDecision)
async def evaluate_agent_request(request: AgentCheckoutRequest):
    """
    Evaluates an agent checkout payload against the authorized mandate rules.
    """
    if request.mandate_id != MOCK_MANDATE.mandate_id:
        raise HTTPException(status_code=404, detail="Mandate ID not found or unauthorized.")
        
    decision = SpendGateEngine.evaluate_transaction(MOCK_MANDATE, request)
    return decision