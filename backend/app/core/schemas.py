from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CartItem(BaseModel):
    sku: str
    quantity: int = Field(gt=0, description="Quantity must be greater than zero")
    unit_price: float = Field(gt=0, description="Agreed unit price from catalog")

class AgentIntentMandate(BaseModel):
    """
    Mandate issued by the user/system defining what the buyer agent is authorized to do.
    """
    mandate_id: str
    buyer_agent_id: str
    user_id: str
    max_budget_inr: float = Field(gt=0, description="Hard cap on expenditure")
    authorized_categories: List[str]
    expires_at: datetime

class AgentCheckoutRequest(BaseModel):
    """
    Payload submitted by the AI buyer agent to request checkout.
    """
    mandate_id: str
    merchant_id: str
    items: List[CartItem]
    claimed_total: float
    reasoning_trace: str = Field(..., description="LLM explanation for item selection")
    currency: str = "INR"

class GateDecision(BaseModel):
    is_approved: bool
    status_code: str  # "APPROVED", "EXCEEDED_BUDGET", "PRICE_MISMATCH", "OUT_OF_STOCK", "EXPIRED_MANDATE"
    calculated_total: float
    message: str
    requires_human_fallback: bool

class CheckoutExecutionResult(BaseModel):
    success: bool
    mode: str  # "AUTONOMOUS_SETTLEMENT" or "HUMAN_FALLBACK_LINK"
    transaction_id: str
    razorpay_order_id: Optional[str] = None
    razorpay_payment_link: Optional[str] = None
    amount_inr: float
    status: str
    message: str
    audit_digest: str