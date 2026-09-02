import uuid
import hashlib
from typing import Optional, Any
from .schemas import AgentCheckoutRequest, CheckoutExecutionResult

class RazorpayExecutionEngine:
    @staticmethod
    def _generate_audit_digest(request: AgentCheckoutRequest, decision: Any) -> str:
        calc_total = getattr(decision, "calculated_total", request.claimed_total)
        raw_payload = f"{request.mandate_id}|{request.merchant_id}|{calc_total}|{request.reasoning_trace}"
        return hashlib.sha256(raw_payload.encode()).hexdigest()

    @classmethod
    def execute_autonomous_order(
        cls, 
        request: AgentCheckoutRequest, 
        decision: Any
    ) -> CheckoutExecutionResult:
        """Autonomous execution: direct machine-to-merchant settlement."""
        calc_total = getattr(decision, "calculated_total", request.claimed_total)
        mock_order_id = f"order_{uuid.uuid4().hex[:14]}"
        digest = cls._generate_audit_digest(request, decision)
        
        return CheckoutExecutionResult(
            success=True,
            mode="AUTONOMOUS_SETTLEMENT",
            transaction_id=f"TX-AUTO-{uuid.uuid4().hex[:8].upper()}",
            razorpay_order_id=mock_order_id,
            razorpay_payment_link=None,
            amount_inr=calc_total,
            status="SETTLED_AUTONOMOUSLY",
            message=f"Spend gate passed. Order settled autonomously under mandate {request.mandate_id}.",
            audit_digest=digest
        )

    @classmethod
    def generate_fallback_payment_link(
        cls, 
        request: AgentCheckoutRequest, 
        decision: Any
    ) -> CheckoutExecutionResult:
        """Fallback execution: Human-in-the-Loop escalation."""
        calc_total = getattr(decision, "calculated_total", request.claimed_total)
        reason_msg = getattr(decision, "reason", "Policy limit exceeded")
        mock_link_id = f"plink_{uuid.uuid4().hex[:12]}"
        digest = cls._generate_audit_digest(request, decision)
        
        return CheckoutExecutionResult(
            success=False,
            mode="HUMAN_FALLBACK_LINK",
            transaction_id=f"TX-LINK-{uuid.uuid4().hex[:8].upper()}",
            razorpay_order_id=None,
            razorpay_payment_link=f"https://rzp.io/i/{mock_link_id}",
            amount_inr=calc_total,
            status="ESCALATED_TO_HUMAN",
            message=f"Spend gate stopped automated checkout ({reason_msg}). Fallback link issued.",
            audit_digest=digest
        )