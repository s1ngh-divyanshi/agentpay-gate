# AgentPay Gate ⚡

> **Track 01: AI Growth & Agentic Commerce** — Gated Transactional Middleware and Immutable Audit Ledger for Machine-to-Merchant Payments.

![AgentPay Architecture](https://img.shields.io/badge/Status-Production%20Ready-emerald) ![Python](https://img.shields.io/badge/Backend-FastAPI-blue) ![Frontend](https://img.shields.io/badge/Frontend-Tailwind%20CSS-indigo) ![Security](https://img.shields.io/badge/Audit-SHA--256%20Merkle-amber)

---

## 🚀 Overview

As autonomous AI procurement agents gain transaction capabilities, probabilistic LLMs introduce severe financial risks: prompt injection attacks, runaway API costs, and silent policy violations.

**AgentPay Gate** acts as an uncompromisable deterministic proxy layer between autonomous AI buyer agents and payment gateways (Razorpay). It intercepts purchase intents, validates SKUs against live merchant feeds, enforces hard organizational spend caps (e.g., ₹5,000/tx), signs append-only cryptographic audit ledgers, and degrades gracefully to human-in-the-loop workflows when limits are breached.

---

## 🛠️ Architecture & Core Components

```text
 [ Autonomous AI Agent ]
          │ (Intent / Basket Payload)
          ▼
   [ AgentPay Gate ] ──(Deterministic Rule Check: Limit ≤ ₹5,000?)
          ├── YES ──► [ Razorpay API ] ──► Autonomous Settlement (Order ID)
          └── NO  ──► [ Fallback Engine ] ──► Human-in-the-Loop Payment Link
          │
          ▼
   [ SHA-256 Cryptographic Audit Ledger ] (Append-only Merkle chain)
```

1. **Deterministic Spend-Gate Engine:** Evaluates multi-item baskets against strict organizational mandates and per-transaction limits.
2. **Graceful Degradation Protocol:** Automatically redirects high-value or restricted orders into secure payment links (`ESCALATED_TO_HUMAN`) rather than failing abruptly.
3. **Cryptographic Audit Ledger:** Every evaluation and settlement action is stored in an immutable, block-linked SHA-256 chain ensuring tamper-evident provenance.
4. **Interactive Governance Dashboard:** A dark-mode financial UI featuring live metric tracking, transaction inspection drawers, real-time integrity chain validation, and one-click demo triggers.

---

## 📂 Project Structure

```text
agentpay-core/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routers (catalog, gate, checkout, audit)
│   │   ├── core/         # Spend gate logic, Razorpay engine, audit ledger service
│   │   └── data/         # Mock catalog & audit_ledger.json store
│   └── .env              # Environment variables & API keys
├── frontend/
│   ├── css/
│   │   └── styles.css    # Custom design tokens and modern styling
│   ├── js/
│   │   └── app.js        # Dashboard state, API sync, and sandbox triggers
│   └── index.html        # Main governance and audit interface
└── README.md
```

---

## ⚙️ Quickstart & Local Installation

### 1. Clone the Repository

```bash
git clone [https://github.com/YOUR_USERNAME/agentpay-gate.git](https://github.com/YOUR_USERNAME/agentpay-gate.git)
cd agentpay-gate
```

### 2. Set Up Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r backend/requirements.txt  # Or install fastapi uvicorn requests python-dotenv rich
```

### 3. Configure Environment Variables

Create a `.env` file in your root or `backend/` directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
RAZORPAY_KEY_ID=rzp_test_mockkey
RAZORPAY_KEY_SECRET=mock_secret
```

### 4. Run the Backend Server

```bash
uvicorn backend.app.main:app --reload --port 8000
```

### 5. Access the Dashboard

Open your browser and navigate to:

- **Governance UI:** [http://localhost:8000/](http://localhost:8000/)
- **Interactive API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 💡 Hackathon Demonstration Guide

Use the **Agent Execution Sandbox** directly on the web dashboard to demonstrate key protocol features to judges:

1. **Valid Order (< ₹5,000):** Triggers autonomous machine-to-merchant settlement (`AUTONOMOUS` mode with a generated Razorpay order ID).
2. **Random Limit Breach (> ₹5,000):** Intercepts the basket, enforces policy constraints, issues a secure payment link, and flags the record for review (`HUMAN_FALLBACK`).
3. **High-Value SKU (> ₹45k):** Tests enterprise infrastructure requisitions requiring supervisor sign-off.
4. **Verify Chain:** Instantly computes SHA-256 pointers across all recorded blocks to prove tamper-free audit integrity.
