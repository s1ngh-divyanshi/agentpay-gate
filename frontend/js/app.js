const API_BASE = window.location.origin;
let cachedRecords = [];
let currentRecordIdForPayment = null;

async function fetchLedger() {
  try {
    const res = await fetch(`${API_BASE}/api/audit/records`);
    if (!res.ok) return [];
    return await res.json();
  } catch (err) {
    console.error("Failed to load records:", err);
    return [];
  }
}

async function runIntegrityCheck() {
  try {
    const res = await fetch(`${API_BASE}/api/audit/verify-integrity`);
    const data = await res.json();
    
    const badge = document.getElementById("integrity-badge");
    const msg = document.getElementById("integrity-message");
    const count = document.getElementById("integrity-count");
    const pulse = document.getElementById("integrity-pulse");

    if (!badge || !msg || !count || !pulse) return;

    count.innerText = data.total_records_checked || 0;

    if (data.status === "VERIFIED_VALID") {
      badge.innerText = "VERIFIED VALID";
      badge.className = "text-[11px] font-mono font-bold text-emerald-400 px-2 py-0.5 rounded bg-emerald-950/80 border border-emerald-800 leading-normal";
      pulse.innerHTML = `
        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
        <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
      `;
      const hashStr = data.latest_block_hash ? data.latest_block_hash.slice(0, 24) : 'Genesis';
      msg.innerText = `Chain Valid • Latest Hash: ${hashStr}...`;
      msg.className = "text-xs text-slate-300 font-mono leading-normal mt-0.5";
    } else {
      badge.innerText = "TAMPER DETECTED";
      badge.className = "text-[11px] font-mono font-bold text-rose-400 px-2 py-0.5 rounded bg-rose-950/80 border border-rose-800 leading-normal";
      pulse.innerHTML = `<span class="relative inline-flex rounded-full h-3 w-3 bg-rose-500"></span>`;
      msg.innerText = `Compromised at ${data.corrupted_record_id || 'ledger'}: ${data.message}`;
      msg.className = "text-xs text-rose-400 font-mono font-bold leading-normal mt-0.5";
    }
  } catch (err) {
    console.error("Integrity check failed:", err);
  }
}

async function triggerDemoTx(scenario) {
  let items = [];
  let reasoning = "";

  if (scenario === 'autonomous') {
    // 1 item strictly under ₹5,000 global per-tx limit
    items = [{ sku: "PROD-OFFICE-CHAIR-01", quantity: 1, unit_price: 3499.0 }];
    reasoning = "Procuring single ergonomic chair. Verified sum ₹3,499 is within ₹5,000 threshold.";

  } else if (scenario === 'limit_breach') {
    // Randomize quantities so total is dynamic (> ₹5,000)
    const chairQty = Math.floor(Math.random() * 2) + 1; // 1 or 2
    const kbQty = Math.floor(Math.random() * 2) + 1;    // 1 or 2
    
    items = [
      { sku: "PROD-OFFICE-CHAIR-01", quantity: chairQty, unit_price: 3499.0 },
      { sku: "PROD-MECH-KB-02", quantity: kbQty, unit_price: 4200.0 }
    ];
    const total = (chairQty * 3499.0) + (kbQty * 4200.0);
    reasoning = `Basket (${chairQty}x chair, ${kbQty}x keyboard) total ₹${total.toLocaleString()} exceeds per-transaction cap of ₹5,000.`;

  } else if (scenario === 'high_value') {
    // Enterprise equipment requisition requiring human verification
    const qty = Math.floor(Math.random() * 2) + 1;
    const price = 85000.0;
    items = [{ sku: "PROD-SERVER-BLADE-99", quantity: qty, unit_price: price }];
    reasoning = `Enterprise server blade requisition (Qty: ${qty}, Total: ₹${(qty * price).toLocaleString()}) escalated to human sign-off.`;
  }

  const calculatedTotal = items.reduce((acc, curr) => acc + (curr.unit_price * curr.quantity), 0);

  const payload = {
    mandate_id: "MANDATE-DEMO-001",
    merchant_id: "MERCHANT-01",
    items: items,
    claimed_total: calculatedTotal,
    reasoning_trace: reasoning,
    currency: "INR"
  };

  try {
    const res = await fetch(`${API_BASE}/api/checkout/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const errText = await res.text();
      console.error("Execution failed:", errText);
      alert("Spend-Gate Rejected Request: " + errText);
      return;
    }

    await refreshData();
  } catch (err) {
    console.error("Execution Error:", err);
    alert("Execution error: " + err.message);
  }
}

function openDetail(recordId) {
  const rec = cachedRecords.find(r => r.record_id === recordId);
  if (!rec) return;

  document.getElementById("modal-record-id").innerText = rec.record_id;
  document.getElementById("modal-reasoning").innerText = rec.reasoning_trace || "No reasoning trace recorded.";
  document.getElementById("modal-mandate").innerText = rec.mandate_id;
  document.getElementById("modal-merchant").innerText = rec.merchant_id;
  document.getElementById("modal-prev-hash").innerText = rec.previous_block_hash;
  document.getElementById("modal-digest-hash").innerText = rec.digest_hash;

  const rawBtn = document.getElementById("modal-raw-json-btn");
  if (rawBtn) {
    rawBtn.onclick = () => {
      window.open(`${API_BASE}/api/audit/records`, '_blank');
    };
  }

  const itemsContainer = document.getElementById("modal-items");
  if (rec.items && rec.items.length > 0) {
    itemsContainer.innerHTML = rec.items.map(item => `
      <div class="flex items-center justify-between text-slate-200 font-mono text-xs py-0.5">
        <span>• ${item.sku} (Qty: ${item.quantity})</span>
        <span class="font-bold text-white">₹${((item.unit_price || 0) * (item.quantity || 1)).toLocaleString()}</span>
      </div>
    `).join("");
  } else {
    itemsContainer.innerHTML = `<span class="text-slate-500">No items recorded.</span>`;
  }

  document.getElementById("detail-modal").classList.remove("hidden");
}

function closeModal() {
  document.getElementById("detail-modal").classList.add("hidden");
}

function openPaymentReview(recordId) {
  const rec = cachedRecords.find(r => r.record_id === recordId);
  if (!rec) return;

  if (rec.razorpay_payment_link && !rec.razorpay_payment_link.includes("mock")) {
    window.open(rec.razorpay_payment_link, "_blank");
    return;
  }

  currentRecordIdForPayment = recordId;
  document.getElementById("pay-modal-txid").innerText = rec.record_id;
  document.getElementById("pay-modal-amount").innerText = `₹${(rec.calculated_total || rec.claimed_total || 0).toLocaleString()}`;
  document.getElementById("pay-modal-reason").innerText = rec.decision_status;
  document.getElementById("payment-modal").classList.remove("hidden");
}

function closePaymentModal() {
  document.getElementById("payment-modal").classList.add("hidden");
}

async function simulateApproval() {
  if (!currentRecordIdForPayment) return;

  try {
    const res = await fetch(`${API_BASE}/api/audit/approve-human`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ record_id: currentRecordIdForPayment })
    });

    const data = await res.json();
    if (data.status === "SUCCESS") {
      closePaymentModal();
      await refreshData();
    } else {
      alert("Error: " + data.message);
    }
  } catch (err) {
    alert("Approval request failed: " + err.message);
  }
}

async function resetLedger() {
  if (!confirm("Reset audit ledger back to baseline demo records?")) return;
  try {
    const res = await fetch(`${API_BASE}/api/audit/reset`, { method: "POST" });
    if (res.ok) {
      await refreshData();
    }
  } catch (err) {
    alert("Reset failed: " + err.message);
  }
}

async function refreshData() {
  const tbody = document.getElementById("ledger-body");
  if (!tbody) {
    console.error("Element #ledger-body not found in DOM");
    return;
  }

  cachedRecords = await fetchLedger();

  let totalSpend = 0;
  let autoCount = 0;
  let fallbackCount = 0;

  if (!cachedRecords || cachedRecords.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="py-12 text-center text-slate-400 font-sans text-xs">No transactions recorded yet. Use the sandbox buttons above to simulate orders.</td></tr>`;
    const statSpend = document.getElementById("stat-spend");
    const statAuto = document.getElementById("stat-auto");
    const statFallback = document.getElementById("stat-fallback");
    if (statSpend) statSpend.innerText = "₹0";
    if (statAuto) statAuto.innerText = "0";
    if (statFallback) statFallback.innerText = "0";
    await runIntegrityCheck();
    return;
  }

  tbody.innerHTML = cachedRecords.slice().reverse().map(r => {
    const finalAmount = r.calculated_total > 0 ? r.calculated_total : (r.claimed_total || 0);
    totalSpend += finalAmount;
    
    const isAuto = r.mode === "AUTONOMOUS_SETTLEMENT";
    const isHumanApproved = r.mode === "HUMAN_APPROVED_SETTLEMENT";

    if (isAuto || isHumanApproved) {
      autoCount++;
    } else {
      fallbackCount++;
    }

    let modeBadge = "";
    if (isAuto) {
      modeBadge = `<span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-bold font-mono bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 leading-normal"><span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>AUTONOMOUS</span>`;
    } else if (isHumanApproved) {
      modeBadge = `<span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-bold font-mono bg-blue-500/15 text-blue-300 border border-blue-500/30 leading-normal"><span class="w-1.5 h-1.5 rounded-full bg-blue-400"></span>HUMAN_APPROVED</span>`;
    } else {
      modeBadge = `<span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-bold font-mono bg-amber-500/15 text-amber-300 border border-amber-500/30 leading-normal"><span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>HUMAN_FALLBACK</span>`;
    }

    let decisionBadge = `<span class="font-mono text-slate-300 text-xs font-semibold">${r.decision_status}</span>`;
    if (r.decision_status === "APPROVED") {
      decisionBadge = `<span class="text-emerald-400 font-mono font-bold text-xs">APPROVED</span>`;
    } else if (r.decision_status === "EXCEEDED_GLOBAL_LIMIT") {
      decisionBadge = `<span class="text-amber-400 font-mono font-bold text-xs">EXCEEDED_GLOBAL_LIMIT</span>`;
    } else {
      decisionBadge = `<span class="text-rose-400 font-mono font-bold text-xs">${r.decision_status}</span>`;
    }

    const actionContent = r.razorpay_order_id 
      ? `<span class="text-slate-300 font-mono text-[11px]">${r.razorpay_order_id}</span>`
      : (r.razorpay_payment_link 
          ? `<button onclick="event.stopPropagation(); openPaymentReview('${r.record_id}')" class="inline-flex items-center gap-1 text-blue-400 hover:text-blue-300 font-mono font-bold text-xs underline decoration-blue-400/50 leading-normal">Review & Pay ↗</button>`
          : `<span class="text-slate-500 font-mono text-xs">None</span>`);

    return `
      <tr onclick="openDetail('${r.record_id}')" class="hover:bg-[#191f2c] transition-colors cursor-pointer group">
        <td class="py-3 px-4 font-mono font-bold text-blue-400 group-hover:text-blue-300">${r.record_id}</td>
        <td class="py-3 px-4">${modeBadge}</td>
        <td class="py-3 px-4">${decisionBadge}</td>
        <td class="py-3 px-4 text-right font-mono text-slate-400">₹${(r.claimed_total || 0).toLocaleString()}</td>
        <td class="py-3 px-4 text-right font-mono font-bold text-white text-sm">₹${finalAmount.toLocaleString()}</td>
        <td class="py-3 px-4">${actionContent}</td>
        <td class="py-3 px-4">
          <a href="/api/audit/records" target="_blank" onclick="event.stopPropagation()" class="font-mono text-slate-400 hover:text-slate-200 text-[11px] underline decoration-slate-600" title="${r.digest_hash}">
            ${r.digest_hash ? r.digest_hash.slice(0, 16) : ''}...
          </a>
        </td>
      </tr>
    `;
  }).join("");

  const statSpend = document.getElementById("stat-spend");
  const statAuto = document.getElementById("stat-auto");
  const statFallback = document.getElementById("stat-fallback");

  if (statSpend) statSpend.innerText = `₹${totalSpend.toLocaleString()}`;
  if (statAuto) statAuto.innerText = autoCount;
  if (statFallback) statFallback.innerText = fallbackCount;

  await runIntegrityCheck();
}

document.addEventListener("DOMContentLoaded", () => {
  refreshData();
});