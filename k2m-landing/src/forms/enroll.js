import "./forms.css";

const ENROLL_API_URL =
  import.meta.env.VITE_ENROLL_API_URL ||
  "https://kira-bot-production.up.railway.app/api/enroll";

function byId(id) {
  return document.getElementById(id);
}

function setStatus(kind, message, linkHref = "") {
  const status = byId("enrollStatus");
  if (!status) {
    return;
  }
  status.className = `k2m-status ${kind}`;
  if (linkHref) {
    status.innerHTML = `${message} <a class="k2m-inline-link" href="${linkHref}">Open payment form</a>`;
  } else {
    status.textContent = message;
  }
  status.hidden = false;
}

function loadQueryDefaults() {
  const params = new URLSearchParams(window.location.search);
  const email = params.get("email") || "";
  if (email) {
    byId("email").value = email;
  }
}

async function onSubmit(event) {
  event.preventDefault();

  const form = event.currentTarget;
  const submit = byId("submitEnroll");
  const payload = {
    email: byId("email").value.trim().toLowerCase(),
    zone: byId("zone").value.trim(),
    situation: byId("situation").value.trim(),
    goals: byId("goals").value.trim(),
    emotional_baseline: byId("emotional").value.trim(),
    parent_email: byId("parentEmail").value.trim().toLowerCase(),
  };

  if (!payload.email || !payload.zone || !payload.situation || !payload.goals || !payload.emotional_baseline) {
    setStatus("error", "Please complete all required fields.");
    return;
  }

  submit.disabled = true;
  submit.textContent = "Submitting...";

  try {
    const response = await fetch(ENROLL_API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await response.json();

    if (!response.ok || !body.success) {
      setStatus("error", body.error || "Enrollment submission failed.");
      return;
    }

    form.reset();
    byId("email").value = payload.email;
    setStatus(
      "success",
      "Enrollment recorded. Step 3 of 4: complete your payment using this secure link.",
      body.submit_url || ""
    );
  } catch (error) {
    console.error("Enroll request failed", error);
    setStatus("error", "Network error. Please retry.");
  } finally {
    submit.disabled = false;
    submit.textContent = "Save And Continue";
  }
}

window.addEventListener("DOMContentLoaded", () => {
  const form = byId("enrollForm");
  if (!form) {
    return;
  }
  loadQueryDefaults();
  form.addEventListener("submit", onSubmit);
});
