<div align="center">

# AgentPay Gate ⚡

### Deterministic Governance & Cryptographic Audit Middleware for Agentic Commerce

[![Razorpay AI Builder 2026](https://img.shields.io/badge/Razorpay-AI%20Builder%20Internship%202026-0c2340?style=for-the-badge&logo=razorpay&logoColor=3395FF)](https://razorpay.com/buildathon)
[![Track 01](https://img.shields.io/badge/Track%2001-AI%20Growth%20%26%20Agentic%20Commerce-blue?style=for-the-badge)](#)
[![Security Architecture](https://img.shields.io/badge/Ledger-SHA--256%20Block--Linked-10b981?style=for-the-badge)](#)

<p align="center">
  A deterministic proxy enforcing organizational spend constraints, automated human fallback escalations, and tamper-evident cryptographic provenance for autonomous AI buyer agents.
</p>

</div>

---

## 🎯 Context

Developed for the **Razorpay AI Builder Internship 2026** under **Track 01: AI Growth & Agentic Commerce**.

Autonomous AI agents are fundamentally probabilistic. Exposing raw payment credentials to LLMs risks prompt injection, price hallucinations, and runaway spend loops. **AgentPay Gate** serves as a deterministic proxy between AI agents and Razorpay rails—validating catalog prices out-of-band, enforcing strict transaction limits, and logging every action to an immutable SHA-256 audit ledger.

---

## 🏛️ System Architecture

```text
               ┌──────────────────────────────┐
               │   Autonomous AI Buyer Agent  │
               └──────────────┬───────────────┘
                              │ Dispatches Intent
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    AGENTPAY GATE MIDDLEWARE                 │
│                                                             │
│  [1] Catalog Verification  ──►  Re-checks live SKU pricing  │
│  [2] Price Arithmetic      ──►  Detects hallucinated fees   │
│  [3] Policy Boundary Engine──►  Enforces Limit (≤ ₹5,000)   │
└──────────────┬──────────────────────────────┬───────────────┘
               │ Passed Gate                  │ Breached Limit
               ▼                              ▼
  ┌─────────────────────────┐    ┌─────────────────────────┐
  │  Razorpay Orders API    │    │  Razorpay Payment Links │
  │  (Autonomous Auto-Pay)  │    │  (Human-in-the-Loop)    │
  └────────────┬────────────┘    └────────────┬────────────┘
               │                              │
               └──────────────┬───────────────┘
                              ▼
  ┌─────────────────────────────────────────────────────────┐
  │         SHA-256 BLOCK-LINKED AUDIT LEDGER               │
  │     [Block N-1] ◄── [Block N] ◄── [Block N+1]           │
  │  (Timestamp, Mandate, Items, Reasoning, Hash Signature) │
  └─────────────────────────────────────────────────────────┘

```

---

## ⚡ Core Features

- **Deterministic Spend-Gate:** Recalculates cart arithmetic out-of-band against merchant feeds; strictly enforces hard monetary caps (e.g., ₹5,000/tx).
- **Graceful Degradation:** Diverts high-value or restricted orders into secure Razorpay Payment Links for human supervisor review.
- **Block-Linked Audit Trail:** Cryptographically seals every decision, cart payload, and reasoning trace in a backward-linked SHA-256 chain ($H_n = \text{SHA-256}(H_{n-1} \parallel \text{Data}_n)$).
- **Governance Dashboard:** Real-time financial telemetry, slide-out transaction proof inspectors, and an interactive simulation sandbox.

---

## 📂 Repository Structure

```text
agentpay-core/
├── backend/
│   ├── app/
│   │   ├── api/          # Catalog, gate, checkout, and audit endpoints
│   │   ├── core/         # Spend-gate engine, Razorpay handler, and Merkle ledger
│   │   └── data/         # Catalog data and persistent JSON ledger
│   └── requirements.txt
├── buyer_agent/          # Autonomous AI buyer implementation & tool definitions
├── frontend/
│   ├── css/styles.css    # UI styling tokens
│   ├── js/app.js         # Client-side state, sandbox triggers, & chain verifier
│   └── index.html        # Telemetry & governance dashboard
└── README.md

```

---

## 🚀 Quickstart

### 1. Installation

```bash
git clone [https://github.com/s1ngh-divyanshi/agentpay-gate.git](https://github.com/s1ngh-divyanshi/agentpay-gate.git)
cd agentpay-gate
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

### 2. Environment Setup

Create a `.env` file in the root or `backend/` directory:

```env
GEMINI_API_KEY=your_gemini_api_key
RAZORPAY_KEY_ID=rzp_test_placeholder
RAZORPAY_KEY_SECRET=rzp_secret_placeholder
```

### 3. Launch

```bash
uvicorn backend.app.main:app --reload --port 8000
```

- **Dashboard:** [http://localhost:8000/](http://localhost:8000/)
- **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Demonstration Matrix

| Action                      | Gate Evaluation          | System Outcome                                                           |
| --------------------------- | ------------------------ | ------------------------------------------------------------------------ |
| **Valid Order (< ₹5,000)**  | Within policy limits     | Settles automatically via Razorpay Orders API (`AUTONOMOUS`).            |
| **Limit Breach (> ₹5,000)** | Hard cap exceeded        | Escalates to human sign-off via Payment Link (`HUMAN_FALLBACK`).         |
| **Review & Pay ↗**          | Supervisor authorization | Settles order, binds payment ID, and updates status to `HUMAN_APPROVED`. |
| **Verify Chain**            | Full cryptographic check | Recalculates all SHA-256 pointers to verify audit trail integrity.       |

---

## 🛡️ Security Guarantees

- **Credential Isolation:** AI agents never receive raw API keys or settlement permissions.
- **Tamper-Evident Ledger:** Modifying any historical block in storage breaks downstream hash pointers, immediately failing cryptographic checks.
- **Explainable Auditing:** Every entry stores the agent's explicit reasoning trace alongside the cryptographic signature.
