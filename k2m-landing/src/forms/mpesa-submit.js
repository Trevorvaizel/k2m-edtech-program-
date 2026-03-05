import "./forms.css";

const MPESA_API_URL =
  import.meta.env.VITE_MPESA_SUBMIT_API_URL ||
  "https://kira-bot-production.up.railway.app/api/mpesa-submit";

function byId(id) {
  return document.getElementById(id);
}

function setStatus(kind, message) {
  const status = byId("mpesaStatus");
  if (!status) {
    return;
  }
  status.className = `k2m-status ${kind}`;
  status.textContent = message;
  status.hidden = false;
}

function readTokenFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return (params.get("token") || "").trim();
}

async function checkToken(token) {
  if (!token) {
    setStatus("error", "Missing token. Open the exact payment link from your email.");
    return false;
  }

  try {
    const response = await fetch(`${MPESA_API_URL}?token=${encodeURIComponent(token)}`);
    const body = await response.json();
    if (!response.ok || !body.valid) {
      setStatus("error", body.error || "Invalid or expired payment link.");
      return false;
    }
    if (body.email_hint) {
      byId("tokenHint").textContent = `Link validated for ${body.email_hint}`;
    }
    return true;
  } catch (error) {
    console.error("Token validation failed", error);
    setStatus("error", "Could not validate token. Please retry.");
    return false;
  }
}

async function onSubmit(event) {
  event.preventDefault();
  const submit = byId("submitMpesa");
  const token = byId("token").value.trim();
  const mpesaCode = byId("mpesaCode").value.trim().toUpperCase();

  if (!token || !mpesaCode) {
    setStatus("error", "Token and M-Pesa code are required.");
    return;
  }

  submit.disabled = true;
  submit.textContent = "Submitting...";

  try {
    const response = await fetch(MPESA_API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        token,
        mpesa_code: mpesaCode,
      }),
    });
    const body = await response.json();
    if (!response.ok || !body.success) {
      setStatus("error", body.error || "Could not submit M-Pesa code.");
      return;
    }
    setStatus("success", body.message || "M-Pesa code submitted successfully.");
    byId("mpesaForm").reset();
    byId("token").value = token;
  } catch (error) {
    console.error("M-Pesa submit failed", error);
    setStatus("error", "Network error. Please retry.");
  } finally {
    submit.disabled = false;
    submit.textContent = "Submit M-Pesa Code";
  }
}

window.addEventListener("DOMContentLoaded", async () => {
  const form = byId("mpesaForm");
  if (!form) {
    return;
  }
  const token = readTokenFromUrl();
  byId("token").value = token;
  const valid = await checkToken(token);
  if (!valid) {
    byId("submitMpesa").disabled = true;
    return;
  }
  form.addEventListener("submit", onSubmit);
});
