/**
 * K2M Enrollment Form — Step Engine
 * One question at a time. Progress-tracked. Brand-native.
 */

const ENROLL_API_URL =
  import.meta.env.VITE_ENROLL_API_URL ||
  "https://kira-bot-production.up.railway.app/api/enroll";

// ── State ──────────────────────────────────────────────────────────────────
const state = {
  email: "",
  zone: "",
  zone_verification: "",
  emotional_baseline: [],   // multi-select array
  anxiety_level: 5,
  situation: "",
  goals: "",
  habits_baseline: [],      // multi-select array
  parent_email: "",
  submitUrl: "",
};

const TOTAL_STEPS = 8;
let currentStep = 0;
let transitioning = false;

// ── DOM helpers ────────────────────────────────────────────────────────────
const $ = (id) => document.getElementById(id);
const progressFill = $("progress-fill");
const stepCounter  = $("step-counter");
const backBtn      = $("back-btn");

function updateProgress(step) {
  const pct = typeof step === "number" && step > 0
    ? Math.round((step / TOTAL_STEPS) * 100)
    : step === "confirm" ? 100 : 0;

  progressFill.style.width = `${pct}%`;

  if (step === 0 || step === "success") {
    stepCounter.style.opacity = "0";
    backBtn.style.display = "none";
  } else if (step === "confirm") {
    stepCounter.innerHTML = `<span>${TOTAL_STEPS}</span> / ${TOTAL_STEPS}`;
    stepCounter.style.opacity = "1";
    backBtn.style.display = "block";
  } else {
    stepCounter.innerHTML = `<span>${step}</span> / ${TOTAL_STEPS}`;
    stepCounter.style.opacity = "1";
    backBtn.style.display = step > 1 ? "block" : "none";
  }
}

// ── Panel transitions ──────────────────────────────────────────────────────
function showPanel(stepId) {
  if (transitioning) return;
  transitioning = true;

  const getPanel = (s) =>
    typeof s === "number" ? $(`step-${s}`) : $(`${s}-panel`);

  const target = getPanel(stepId);
  if (!target) { transitioning = false; return; }

  const current = document.querySelector(".step-panel.active");
  if (current && current !== target) {
    current.classList.add("exit-up");
    current.classList.remove("active");
    setTimeout(() => {
      current.classList.remove("exit-up");
      current.style.display = "none";
    }, 380);
  }

  setTimeout(() => {
    target.style.display = "block";
    requestAnimationFrame(() => {
      target.classList.add("active");
      transitioning = false;
      const focusable = target.querySelector("input, textarea");
      if (focusable) focusable.focus();
    });
  }, current && current !== target ? 200 : 0);
}

function goTo(step) {
  currentStep = step;
  updateProgress(step);
  showPanel(step);
}

function goNext() {
  if (typeof currentStep === "number" && currentStep < TOTAL_STEPS) {
    goTo(currentStep + 1);
  } else if (currentStep === TOTAL_STEPS || currentStep === 8) {
    buildConfirmScreen();
    goTo("confirm");
  }
}

// ── Card selection (single) ────────────────────────────────────────────────
function initCards(containerId) {
  const container = $(containerId);
  if (!container) return;
  container.querySelectorAll(".zone-card").forEach(card => {
    card.addEventListener("click", () => {
      container.querySelectorAll(".zone-card").forEach(c => c.classList.remove("selected"));
      card.classList.add("selected");
    });
  });
}

function getSelectedCard(containerId) {
  const sel = document.querySelector(`#${containerId} .zone-card.selected`);
  return sel ? sel.dataset.value : "";
}

// ── Pill (multi-select) toggle ─────────────────────────────────────────────
function initPills(containerId, noneId = null) {
  const container = $(containerId);
  if (!container) return;
  container.querySelectorAll(".pill").forEach(pill => {
    pill.addEventListener("click", () => {
      const isNone = pill.id === noneId;
      if (isNone) {
        container.querySelectorAll(".pill").forEach(p => p.classList.remove("selected"));
        pill.classList.toggle("selected");
      } else {
        if (noneId) {
          const nonePill = $(noneId);
          if (nonePill) nonePill.classList.remove("selected");
        }
        pill.classList.toggle("selected");
      }
    });
  });
}

function getSelectedPills(containerId) {
  return [...document.querySelectorAll(`#${containerId} .pill.selected`)]
    .map(p => p.dataset.value);
}

// ── Anxiety slider ─────────────────────────────────────────────────────────
const ANXIETY_ANCHORS = {
  1: "😌 Calm — not worried at all",
  2: "🙂 Mostly calm",
  3: "😐 Slightly unsure",
  4: "😕 A little nervous",
  5: "😬 Nervous but manageable",
  6: "😟 Fairly anxious",
  7: "😰 Quite anxious",
  8: "😱 Very anxious",
  9: "😨 Panicking a bit",
  10: "🚫 Avoiding AI entirely",
};

function initSlider() {
  const slider = $("anxiety-slider");
  const display = $("anxiety-value");
  const anchor  = $("anxiety-anchor");
  if (!slider) return;

  const update = () => {
    const v = parseInt(slider.value, 10);
    display.textContent = v;
    anchor.textContent = ANXIETY_ANCHORS[v] || "";
    state.anxiety_level = v;
    const pct = ((v - 1) / 9) * 100;
    slider.style.background =
      `linear-gradient(to right, #13d7d0 ${pct}%, #1f2937 ${pct}%)`;
  };

  slider.addEventListener("input", update);
  update();
}

// ── Validation helpers ─────────────────────────────────────────────────────
function showError(id, visible) {
  const el = $(id);
  if (el) el.classList.toggle("visible", visible);
}

function isValidEmail(v) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
}

// ── Confirm screen ─────────────────────────────────────────────────────────
function buildConfirmScreen() {
  const rows = [
    { label: "Email",            value: state.email },
    { label: "AI starting point", value: state.zone },
    { label: "Scenario match",   value: state.zone_verification || "—" },
    { label: "Feeling",          value: state.emotional_baseline.join(", ") || "—" },
    { label: "Anxiety",          value: `${state.anxiety_level} / 10` },
    { label: "Context",          value: state.situation },
    { label: "Goal",             value: state.goals },
    { label: "Habits",           value: state.habits_baseline.length
        ? state.habits_baseline.join(", ") : "None yet" },
    { label: "Parent email",     value: state.parent_email || "Not provided" },
  ];

  $("confirm-rows").innerHTML = rows.map(r => `
    <div class="confirm-row">
      <span class="confirm-label">${r.label}</span>
      <span class="confirm-value">${r.value}</span>
    </div>
  `).join("");
}

// ── Error banner ───────────────────────────────────────────────────────────
function showBanner(msg) {
  const b = $("error-banner");
  b.textContent = msg;
  b.classList.add("show");
  setTimeout(() => b.classList.remove("show"), 5000);
}

// ── Submit ─────────────────────────────────────────────────────────────────
async function submit() {
  const btn   = $("submit-btn");
  const errEl = $("submit-error");
  btn.classList.add("loading");
  btn.textContent = "Submitting...";
  errEl.classList.remove("visible");

  const payload = {
    email:             state.email,
    zone:              state.zone,
    situation:         state.situation,
    goals:             state.goals,
    emotional_baseline: state.emotional_baseline.join(","),
    anxiety_level:     state.anxiety_level,
  };

  // Optional fields — only include if populated
  if (state.zone_verification) payload.zone_verification = state.zone_verification;
  if (state.habits_baseline.length) payload.habits_baseline = state.habits_baseline.join(",");
  if (state.parent_email) payload.parent_email = state.parent_email;

  try {
    const res  = await fetch(ENROLL_API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await res.json();

    if (!res.ok || !body.success) {
      const msg = body.error || "Enrollment failed. Please try again.";
      errEl.textContent = msg;
      errEl.classList.add("visible");
      showBanner(msg);
      return;
    }

    // Success
    state.submitUrl = body.submit_url || "";
    progressFill.style.width = "100%";
    stepCounter.style.opacity = "0";
    backBtn.style.display = "none";
    goTo("success");

    const link = $("payment-link");
    if (link && state.submitUrl) {
      link.href = state.submitUrl;
      link.style.display = "inline-block";
    }
  } catch (err) {
    console.error("Enroll request failed", err);
    const msg = "Network error — check your connection and try again.";
    errEl.textContent = msg;
    errEl.classList.add("visible");
    showBanner(msg);
  } finally {
    btn.classList.remove("loading");
    btn.textContent = "Complete Enrollment ↵";
  }
}

// ── Keyboard: Enter to advance ─────────────────────────────────────────────
document.addEventListener("keydown", (e) => {
  if (e.key !== "Enter") return;
  if (document.activeElement?.tagName === "TEXTAREA") return;
  const okBtn = document.querySelector(".step-panel.active .ok-btn:not(.loading)");
  if (okBtn) okBtn.click();
});

// ── Back button ────────────────────────────────────────────────────────────
backBtn?.addEventListener("click", () => {
  if (currentStep === "confirm") {
    goTo(TOTAL_STEPS);
  } else if (typeof currentStep === "number" && currentStep > 1) {
    goTo(currentStep - 1);
  }
});

// ── Step initialisers ──────────────────────────────────────────────────────
function initEmailStep() {
  const input = $("email-input");
  const params = new URLSearchParams(window.location.search);
  const pre = params.get("email") || "";
  if (pre && input) input.value = pre;

  $("email-ok")?.addEventListener("click", () => {
    const val = input?.value.trim().toLowerCase() || "";
    if (!isValidEmail(val)) { showError("email-error", true); input?.focus(); return; }
    showError("email-error", false);
    state.email = val;
    goTo(1);
  });

  input?.addEventListener("input", () => showError("email-error", false));
}

function initZoneStep() {
  initCards("zone-cards");
  $("zone-ok")?.addEventListener("click", () => {
    const val = getSelectedCard("zone-cards");
    if (!val) { showError("zone-error", true); return; }
    showError("zone-error", false);
    state.zone = val;
    goNext();
  });
}

function initScenarioStep() {
  initCards("scenario-cards");
  $("scenario-ok")?.addEventListener("click", () => {
    const val = getSelectedCard("scenario-cards");
    if (!val) { showError("scenario-error", true); return; }
    showError("scenario-error", false);
    state.zone_verification = val;
    goNext();
  });
}

function initEmotionStep() {
  initPills("emotion-pills");
  $("emotion-ok")?.addEventListener("click", () => {
    const vals = getSelectedPills("emotion-pills");
    if (!vals.length) { showError("emotion-error", true); return; }
    showError("emotion-error", false);
    state.emotional_baseline = vals;
    goNext();
  });
}

function initAnxietyStep() {
  initSlider();
  $("anxiety-ok")?.addEventListener("click", () => {
    state.anxiety_level = parseInt($("anxiety-slider")?.value || "5", 10);
    goNext();
  });
}

function initSituationStep() {
  $("situation-ok")?.addEventListener("click", () => {
    const val = $("situation-input")?.value.trim() || "";
    if (val.length < 5) { showError("situation-error", true); return; }
    showError("situation-error", false);
    state.situation = val;
    goNext();
  });
}

function initGoalsStep() {
  $("goals-ok")?.addEventListener("click", () => {
    const val = $("goals-input")?.value.trim() || "";
    if (val.length < 5) { showError("goals-error", true); return; }
    showError("goals-error", false);
    state.goals = val;
    goNext();
  });
}

function initHabitsStep() {
  initPills("habit-pills", "habit-none");
  $("habit-ok")?.addEventListener("click", () => {
    const vals = getSelectedPills("habit-pills");
    state.habits_baseline = vals.includes("none") ? [] : vals;
    goNext();
  });
  $("habit-skip")?.addEventListener("click", () => {
    state.habits_baseline = [];
    goNext();
  });
}

function initParentStep() {
  $("parent-ok")?.addEventListener("click", () => {
    const val = $("parent-email-input")?.value.trim().toLowerCase() || "";
    if (val && !isValidEmail(val)) { showBanner("That doesn't look like a valid email."); return; }
    state.parent_email = val;
    goNext();
  });
  $("parent-skip")?.addEventListener("click", () => {
    state.parent_email = "";
    goNext();
  });
}

function initConfirmStep() {
  $("submit-btn")?.addEventListener("click", submit);
}

// ── Boot ───────────────────────────────────────────────────────────────────
window.addEventListener("DOMContentLoaded", () => {
  updateProgress(0);
  initEmailStep();
  initZoneStep();
  initScenarioStep();
  initEmotionStep();
  initAnxietyStep();
  initSituationStep();
  initGoalsStep();
  initHabitsStep();
  initParentStep();
  initConfirmStep();
});
