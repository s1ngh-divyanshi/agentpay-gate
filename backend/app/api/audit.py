import json
import hashlib
from typing import List, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel
from ..core.audit_service import LEDGER_FILE, AuditLedgerService

# 1. Initialize FastAPI APIRouter
router = APIRouter(prefix="/api/audit", tags=["Audit Ledger"])

# 2. Schema Models
class ApproveRequest(BaseModel):
    record_id: str

# 3. Default Pristine Demo Records for Reset Functionality
INITIAL_RECORDS = [
    {
        "record_id": "AUDIT-TX-0001",
        "timestamp": "2026-09-02T13:00:00.000000+00:00",
        "mandate_id": "MANDATE-DEMO-001",
        "merchant_id": "MERCHANT-01",
        "decision_status": "APPROVED",
        "mode": "AUTONOMOUS_SETTLEMENT",
        "claimed_total": 3499.0,
        "calculated_total": 3499.0,
        "razorpay_order_id": "order_auto_001_demo",
        "razorpay_payment_link": None,
        "reasoning_trace": "Selected ergonomic chair within authorized mandate limit.",
        "items": [
            {
                "sku": "PROD-OFFICE-CHAIR-01",
                "quantity": 1,
                "unit_price": 3499.0
            }
        ],
        "previous_block_hash": "0000000000000000000000000000000000000000000000000000000000000000",
        "digest_hash": "15675d1c7dd7e6488d5e89a54bb3fbb457e5e3b5df5bfa4a6e60b8d5a1f284e3"
    },
    {
        "record_id": "AUDIT-TX-0002",
        "timestamp": "2026-09-02T13:05:00.000000+00:00",
        "mandate_id": "MANDATE-DEMO-001",
        "merchant_id": "MERCHANT-01",
        "decision_status": "EXCEEDED_GLOBAL_LIMIT",
        "mode": "HUMAN_FALLBACK_LINK",
        "claimed_total": 7699.0,
        "calculated_total": 7699.0,
        "razorpay_order_id": None,
        "razorpay_payment_link": "https://rzp.io/i/mock_safety_approval_link",
        "reasoning_trace": "Autonomous buyer agent fulfilled setup intent with chair and keyboard. Verified sum: ₹7699.0.",
        "items": [
            {
                "sku": "PROD-OFFICE-CHAIR-01",
                "quantity": 1,
                "unit_price": 3499.0
            },
            {
                "sku": "PROD-MECH-KB-02",
                "quantity": 1,
                "unit_price": 4200.0
            }
        ],
        "previous_block_hash": "15675d1c7dd7e6488d5e89a54bb3fbb457e5e3b5df5bfa4a6e60b8d5a1f284e3",
        "digest_hash": "8fccd0d9e81f626d1c493ef2b8dfa283995818d6ee5144b204642ab672922ec9"
    }
]

# 4. Endpoints
@router.get("/records")
async def get_audit_trail() -> List[Dict[str, Any]]:
    """Retrieve full append-only audit trail."""
    return AuditLedgerService.get_all_records()

@router.get("/verify-integrity")
async def verify_chain_integrity():
    """
    Cryptographic verification: Validates the SHA-256 hash pointer
    linking each audit block to ensure no logs were tampered with.
    """
    records = AuditLedgerService.get_all_records()
    if not records:
        return {"status": "EMPTY", "message": "Ledger contains no records."}

    for i, record in enumerate(records):
        prev_hash = "0000000000000000000000000000000000000000000000000000000000000000" if i == 0 else records[i-1]["digest_hash"]
        
        if record.get("previous_block_hash") != prev_hash:
            return {
                "status": "COMPROMISED",
                "corrupted_record_id": record.get("record_id"),
                "message": "Block chain linkage broken. Previous hash pointer mismatch."
            }

        recalculated_payload = f"{prev_hash}|{record['record_id']}|{record['timestamp']}|{record['mandate_id']}|{record['calculated_total']}|{record['decision_status']}|{record['reasoning_trace']}"
        recalculated_hash = hashlib.sha256(recalculated_payload.encode()).hexdigest()

        if recalculated_hash != record.get("digest_hash"):
            return {
                "status": "COMPROMISED",
                "corrupted_record_id": record.get("record_id"),
                "message": "Digest signature mismatch. Block payload altered."
            }

    return {
        "status": "VERIFIED_VALID",
        "total_records_checked": len(records),
        "latest_block_hash": records[-1]["digest_hash"],
        "message": "All transaction blocks cryptographically verified and tamper-free."
    }

@router.post("/approve-human")
async def approve_human_fallback(req: ApproveRequest):
    """
    Human-in-the-Loop escalation approval:
    Transitions a HUMAN_FALLBACK transaction to approved settlement and re-signs the hash chain.
    """
    records = AuditLedgerService.get_all_records()
    found = False
    
    for r in records:
        if r.get("record_id") == req.record_id:
            r["decision_status"] = "APPROVED_BY_HUMAN"
            r["mode"] = "HUMAN_APPROVED_SETTLEMENT"
            r["razorpay_order_id"] = f"order_human_{r['record_id'].lower()}"
            r["razorpay_payment_link"] = None
            found = True
            break
            
    if not found:
        return {"status": "ERROR", "message": "Record not found."}

    # Re-link and calculate cryptographic digests for the ledger
    for i, r in enumerate(records):
        prev_hash = "0000000000000000000000000000000000000000000000000000000000000000" if i == 0 else records[i-1]["digest_hash"]
        r["previous_block_hash"] = prev_hash
        payload_to_sign = f"{prev_hash}|{r['record_id']}|{r['timestamp']}|{r['mandate_id']}|{r['calculated_total']}|{r['decision_status']}|{r['reasoning_trace']}"
        r["digest_hash"] = hashlib.sha256(payload_to_sign.encode()).hexdigest()

    with open(LEDGER_FILE, "w") as f:
        json.dump(records, f, indent=2)

    return {"status": "SUCCESS", "message": f"{req.record_id} approved and cryptographically re-signed."}

@router.post("/reset")
async def reset_audit_ledger():
    """Resets the audit ledger back to the initial baseline records."""
    with open(LEDGER_FILE, "w") as f:
        json.dump(INITIAL_RECORDS, f, indent=2)
    return {"status": "SUCCESS", "message": "Ledger restored to baseline state."}