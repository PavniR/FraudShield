/**
 * FraudShield Frontend Application JS
 */

document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("kpi-total")) {
    loadDashboardSummary();
  }
  if (document.getElementById("transactions-table-body")) {
    loadTransactions();
  }
  if (document.getElementById("tx-form")) {
    setupTesterForm();
  }
});

async function loadDashboardSummary() {
  try {
    const res = await fetch("/api/dashboard/summary/");
    const data = await res.json();
    
    document.getElementById("kpi-total").innerText = data.kpis.total_transactions;
    document.getElementById("kpi-allowed").innerText = data.kpis.allowed_count;
    document.getElementById("kpi-review").innerText = data.kpis.review_count;
    document.getElementById("kpi-blocked").innerText = data.kpis.blocked_count;
    document.getElementById("kpi-rate").innerText = `${data.kpis.fraud_rate_percent}%`;

    const tbody = document.getElementById("recent-suspicious-body");
    if (tbody) {
      tbody.innerHTML = "";
      if (data.recent_suspicious_transactions.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:#9ca3af;">No suspicious transactions recorded yet.</td></tr>`;
        return;
      }
      data.recent_suspicious_transactions.forEach(tx => {
        const tr = document.createElement("tr");
        const decisionBadge = getDecisionBadge(tx.status);
        const evalScore = tx.evaluation ? `${tx.evaluation.risk_score} pts (${(tx.evaluation.fraud_probability * 100).toFixed(1)}% ML)` : "N/A";
        
        tr.innerHTML = `
          <td><code>${tx.transaction_id.substring(0, 8)}</code></td>
          <td>₹${parseFloat(tx.amount).toLocaleString('en-IN')}</td>
          <td>${tx.merchant_detail ? tx.merchant_detail.merchant_name : 'Retail'}</td>
          <td>${new Date(tx.timestamp).toLocaleString()}</td>
          <td>${evalScore}</td>
          <td>${decisionBadge}</td>
        `;
        tbody.appendChild(tr);
      });
    }
  } catch (err) {
    console.error("Error loading dashboard summary:", err);
  }
}

async function loadTransactions(statusFilter = "") {
  try {
    let url = "/api/transactions/";
    if (statusFilter) {
      url += `?status=${statusFilter}`;
    }
    const res = await fetch(url);
    const data = await res.json();
    
    const tbody = document.getElementById("transactions-table-body");
    tbody.innerHTML = "";

    if (data.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:#9ca3af;">No transactions found.</td></tr>`;
      return;
    }

    data.forEach(tx => {
      const tr = document.createElement("tr");
      const decisionBadge = getDecisionBadge(tx.status);
      
      tr.innerHTML = `
        <td><code>${tx.transaction_id.substring(0, 8)}</code></td>
        <td><code>${tx.account_number || 'ACC-1001'}</code></td>
        <td>₹${parseFloat(tx.amount).toLocaleString('en-IN')}</td>
        <td>${tx.location}</td>
        <td>${new Date(tx.timestamp).toLocaleString()}</td>
        <td>${decisionBadge}</td>
        <td><button class="btn btn-primary" style="padding:0.35rem 0.75rem; font-size:0.8rem;" onclick="viewTxDetail(${tx.id})">Details</button></td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Error loading transactions:", err);
  }
}

async function viewTxDetail(txId) {
  try {
    const res = await fetch(`/api/transactions/${txId}/`);
    const tx = await res.json();
    
    const modalContent = document.getElementById("modal-detail-content");
    const evalData = tx.evaluation || {};
    
    let rulesHtml = "";
    if (evalData.rule_violations && evalData.rule_violations.length > 0) {
      rulesHtml = evalData.rule_violations.map(rv => `
        <li class="rule-item">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong>${rv.rule_name}</strong>
            <span class="badge badge-severity-${rv.severity.toLowerCase()}">${rv.severity}</span>
          </div>
          <p style="font-size:0.85rem; color:#9ca3af; margin-top:0.25rem;">${rv.explanation}</p>
        </li>
      `).join("");
    } else {
      rulesHtml = `<p style="color:#10b981; font-size:0.9rem;">No rule violations triggered.</p>`;
    }

    modalContent.innerHTML = `
      <h3 style="font-size:1.25rem; margin-bottom:1rem; color:#fff;">Transaction Evaluation Details</h3>
      <p style="margin-bottom:0.5rem;"><strong>ID:</strong> <code>${tx.transaction_id}</code></p>
      <p style="margin-bottom:0.5rem;"><strong>Account:</strong> ${tx.account_number || 'ACC-1001'}</p>
      <p style="margin-bottom:0.5rem;"><strong>Amount:</strong> ₹${parseFloat(tx.amount).toLocaleString('en-IN')}</p>
      <p style="margin-bottom:0.5rem;"><strong>Location:</strong> ${tx.location}</p>
      <p style="margin-bottom:0.5rem;"><strong>New Device:</strong> ${tx.is_new_device ? 'Yes ⚠️' : 'No'}</p>
      <p style="margin-bottom:1rem;"><strong>Recent Bursts:</strong> ${tx.recent_transaction_count} txns</p>
      
      <hr style="border-color:var(--panel-border); margin:1rem 0;">
      
      <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:0.5rem; text-align:center; margin-bottom:1rem;">
        <div style="background:rgba(255,255,255,0.03); padding:0.75rem; border-radius:8px;">
          <div style="font-size:0.75rem; color:#9ca3af;">ML Probability</div>
          <div style="font-size:1.2rem; font-weight:700; color:#fff;">${evalData.fraud_probability ? (evalData.fraud_probability * 100).toFixed(1) + '%' : 'N/A'}</div>
        </div>
        <div style="background:rgba(255,255,255,0.03); padding:0.75rem; border-radius:8px;">
          <div style="font-size:0.75rem; color:#9ca3af;">Risk Score</div>
          <div style="font-size:1.2rem; font-weight:700; color:#fff;">${evalData.risk_score || 0} / 100</div>
        </div>
        <div style="background:rgba(255,255,255,0.03); padding:0.75rem; border-radius:8px;">
          <div style="font-size:0.75rem; color:#9ca3af;">Decision</div>
          <div>${getDecisionBadge(tx.status)}</div>
        </div>
      </div>

      <h4 style="font-size:1rem; margin-top:1rem; color:#fff;">Triggered Fraud Rules:</h4>
      <ul class="rule-list">${rulesHtml}</ul>
    `;

    document.getElementById("modal-backdrop").classList.add("show");
  } catch (err) {
    console.error("Error fetching detail:", err);
  }
}

function closeModal() {
  document.getElementById("modal-backdrop").classList.remove("show");
}

function setupTesterForm() {
  const form = document.getElementById("tx-form");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      account_number: document.getElementById("account_number").value,
      amount: parseFloat(document.getElementById("amount").value),
      location: document.getElementById("location").value,
      is_new_device: document.getElementById("is_new_device").checked,
      recent_transaction_count: parseInt(document.getElementById("recent_transaction_count").value),
      merchant_id_str: document.getElementById("merchant_name").value
    };

    try {
      const res = await fetch("/api/transactions/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      
      const resultCard = document.getElementById("eval-result-card");
      resultCard.style.display = "block";

      const evalData = data.evaluation || {};
      
      let rulesHtml = "";
      if (evalData.rule_violations && evalData.rule_violations.length > 0) {
        rulesHtml = evalData.rule_violations.map(rv => `
          <li class="rule-item">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <strong>${rv.rule_name}</strong>
              <span class="badge badge-severity-${rv.severity.toLowerCase()}">${rv.severity}</span>
            </div>
            <p style="font-size:0.85rem; color:#9ca3af; margin-top:0.25rem;">${rv.explanation}</p>
          </li>
        `).join("");
      } else {
        rulesHtml = `<p style="color:#10b981; font-size:0.9rem;">No rule violations triggered. Transaction looks safe!</p>`;
      }

      resultCard.innerHTML = `
        <h3 style="font-size:1.25rem; color:#fff; margin-bottom:1rem;">Evaluation Result</h3>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
          <div>
            <span style="font-size:0.85rem; color:#9ca3af;">Decision:</span>
            ${getDecisionBadge(data.status)}
          </div>
          <div>
            <span style="font-size:0.85rem; color:#9ca3af;">Risk Score:</span>
            <strong style="font-size:1.2rem; color:#fff;">${evalData.risk_score} / 100</strong>
          </div>
          <div>
            <span style="font-size:0.85rem; color:#9ca3af;">ML Fraud Prob:</span>
            <strong style="font-size:1.2rem; color:#fff;">${(evalData.fraud_probability * 100).toFixed(1)}%</strong>
          </div>
        </div>
        <h4 style="font-size:0.95rem; color:#fff; margin-top:1rem;">Triggered Reasons:</h4>
        <ul class="rule-list">${rulesHtml}</ul>
      `;
    } catch (err) {
      alert("Error evaluating transaction: " + err.message);
    }
  });
}

function getDecisionBadge(status) {
  if (status === "ALLOWED") return `<span class="badge badge-allow">ALLOW</span>`;
  if (status === "REVIEW") return `<span class="badge badge-review">REVIEW</span>`;
  if (status === "BLOCKED") return `<span class="badge badge-block">BLOCK</span>`;
  return `<span class="badge" style="background:#4b5563;">PENDING</span>`;
}
