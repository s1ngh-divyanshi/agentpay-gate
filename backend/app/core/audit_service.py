import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

LEDGER_FILE = Path(__file__).parent.parent / "data" / "audit_ledger.json"

class AuditRecord(BaseModel):
    record_id: str
    timestamp: str
    mandate_id: str
    merchant_id: str
    decision_status: str
    mode: str
    claimed_total: float
    calculated_total: float
    razorpay_order_id: Optional[str]
    razorpay_payment_link: Optional[str]
    reasoning_trace: str
    items: List[Dict[str, Any]]
    previous_block_hash: str
    digest_hash: str

class AuditLedgerService:
    @staticmethod
    def _init_storage():
        if not LEDGER_FILE.exists():
            LEDGER_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(LEDGER_FILE, "w") as f:
                json.dump([], f)

    @classmethod
    def get_all_records(cls) -> List[Dict[str, Any]]:
        cls._init_storage()
        try:
            with open(LEDGER_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []

    @classmethod
    def log_entry(
        cls,
        mandate_id: str,
        merchant_id: str,
        decision_status: str,
        mode: str,
        claimed_total: float,
        calculated_total: float,
        razorpay_order_id: Optional[str],
        razorpay_payment_link: Optional[str],
        reasoning_trace: str,
        items: List[Dict[str, Any]]
    ) -> AuditRecord:
        cls._init_storage()
        records = cls.get_all_records()
        
        prev_hash = records[-1]["digest_hash"] if records else "0000000000000000000000000000000000000000000000000000000000000000"
        timestamp = datetime.now(timezone.utc).isoformat()
        record_id = f"AUDIT-TX-{len(records) + 1:04d}"

        # Cryptographic block linkage
        payload_to_sign = f"{prev_hash}|{record_id}|{timestamp}|{mandate_id}|{calculated_total}|{decision_status}|{reasoning_trace}"
        digest_hash = hashlib.sha256(payload_to_sign.encode()).hexdigest()

        entry = AuditRecord(
            record_id=record_id,
            timestamp=timestamp,
            mandate_id=mandate_id,
            merchant_id=merchant_id,
            decision_status=decision_status,
            mode=mode,
            claimed_total=claimed_total,
            calculated_total=calculated_total,
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_link=razorpay_payment_link,
            reasoning_trace=reasoning_trace,
            items=items,
            previous_block_hash=prev_hash,
            digest_hash=digest_hash
        )

        records.append(entry.model_dump())
        with open(LEDGER_FILE, "w") as f:
            json.dump(records, f, indent=2)

        return entry