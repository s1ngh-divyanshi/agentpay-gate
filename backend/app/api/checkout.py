from fastapi import APIRouter, HTTPException
from ..core.schemas import AgentCheckoutRequest, CheckoutExecutionResult
from ..core.guardrails import SpendGateEngine
from ..core.razorpay_service import RazorpayExecutionEngine
from ..core.audit_service import AuditLedgerService
from .gate import MOCK_MANDATE

router = APIRouter(prefix="/api/checkout", tags=["Autonomous Checkout"])

@router.post("/execute", response_model=CheckoutExecutionResult)
async def process_agent_checkout(request: AgentCheckoutRequest):
    # 1. Evaluate Spend Gate
    decision = SpendGateEngine.evaluate_transaction(MOCK_MANDATE, request)

    # 2. Route execution based on decision
    if decision.is_approved:
        result = RazorpayExecutionEngine.execute_autonomous_order(request, decision)
    else:
        result = RazorpayExecutionEngine.generate_fallback_payment_link(request, decision)

    # 3. Commit to immutable audit ledger
    AuditLedgerService.log_entry(
        mandate_id=request.mandate_id,
        merchant_id=request.merchant_id,
        decision_status=decision.status_code,
        mode=result.mode,
        claimed_total=request.claimed_total,
        calculated_total=decision.calculated_total,
        razorpay_order_id=result.razorpay_order_id,
        razorpay_payment_link=result.razorpay_payment_link,
        reasoning_trace=request.reasoning_trace,
        items=[item.model_dump() for item in request.items]
    )

    return result