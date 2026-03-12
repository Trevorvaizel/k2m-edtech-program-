"""
CIS Controller - LLM Integration
Story 4.7 Implementation: provider-swappable LLM calls.

Supports:
- openai (GPT) as active runtime provider via Chat Completions
- anthropic (Claude Sonnet) via env swap
- zhipu (GLM) via OpenAI-compatible Chat Completions
"""

import asyncio
import json
import logging
import os
import re
import urllib.error
import urllib.request
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

try:
    import anthropic
except ImportError:
    anthropic = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model configuration
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250514")
MAX_TOKENS = 1000
TEMPERATURE = 1.0
ENABLE_PROMPT_CACHING = os.getenv("ENABLE_PROMPT_CACHING", "true").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
LLM_MAX_RETRIES = max(int(os.getenv("LLM_MAX_RETRIES", "3")), 1)
LLM_RETRY_BASE_DELAY_SECONDS = max(float(os.getenv("LLM_RETRY_BASE_DELAY_SECONDS", "0.25")), 0.0)

# Cached system prompts - loaded once at startup, reused for all calls
CACHED_SYSTEM_PROMPTS: Dict[str, Optional[str]] = {
    "frame": None,
    "diverge": None,
    "challenge": None,
    "synthesize": None,
}

# Global Anthropic client (initialized on first use)
_anthropic_client: Optional[Any] = None

# Runtime notifier for instant Trevor alerts on provider failures.
_runtime_failure_notifier: Optional[Callable[[str, str, str], Awaitable[None]]] = None

# Task 6.5: fast-tier model routing for high-volume commands.
FAST_TIER_AGENTS = {
    "frame",
    "diverge",
    "dashboard_summary",
    "dashboard-summary",
    "trevor-summary",
    "profession_inference",
}

# Task 6.5: deep-tier model routing for higher-reasoning commands.
DEEP_TIER_AGENTS = {
    "challenge",
    "synthesize",
    "create-artifact",
    "create_artifact",
    "artifact",
}

ALLOWED_PROFESSIONS = {
    "teacher",
    "entrepreneur",
    "university_student",
    "working_professional",
    "gap_year_student",
    "other",
}
INFERRED_PROFESSIONS = {
    "teacher",
    "entrepreneur",
    "university_student",
    "working_professional",
}


def _get_context_engine_webhook_url() -> str:
    """Resolve Apps Script context webhook URL from env."""
    return os.getenv("CONTEXT_ENGINE_WEBHOOK_URL", "").strip()


def _get_context_engine_webhook_token() -> str:
    """Resolve shared secret token used by Apps Script context webhook."""
    return os.getenv("CONTEXT_ENGINE_WEBHOOK_TOKEN", "").strip()


def _get_context_engine_timeout_seconds() -> float:
    """Resolve context webhook timeout with sane lower bound."""
    raw = os.getenv("CONTEXT_ENGINE_TIMEOUT_SECONDS", "2.5").strip()
    try:
        parsed = float(raw)
    except ValueError:
        parsed = 2.5
    return max(parsed, 0.5)


def _context_get_value(student_context: Any, key: str, default: Any = "") -> Any:
    """Read field from dict-like or object-like student context."""
    if student_context is None:
        return default
    if isinstance(student_context, dict):
        return student_context.get(key, default)
    return getattr(student_context, key, default)


def _normalize_week_number(value: Any) -> Optional[int]:
    """Normalize week to positive integer when possible."""
    try:
        week = int(value)
    except (TypeError, ValueError):
        return None
    if week <= 0:
        return None
    return week


def _truncate_text(value: Any, max_len: int = 220) -> str:
    """Return compact single-line context strings."""
    text = str(value or "").strip().replace("\n", " ")
    if len(text) <= max_len:
        return text
    return f"{text[:max_len - 3].rstrip()}..."


def _normalize_agent_key(agent: Optional[str]) -> str:
    """Normalize command/agent names to one routing key."""
    if not agent:
        return ""
    return str(agent).strip().lower().replace(" ", "_")


def _resolve_model_tier(agent: Optional[str]) -> str:
    """Map agent names to model tier. Defaults to deep tier."""
    key = _normalize_agent_key(agent)
    if key in FAST_TIER_AGENTS:
        return "fast"
    if key in DEEP_TIER_AGENTS:
        return "deep"
    return "deep"


def _normalize_profession(value: Any) -> str:
    """Normalize profession labels from profile/form/webhook sources."""
    token = str(value or "").strip().lower()
    if not token:
        return ""
    token = token.replace("-", "_").replace(" ", "_")
    aliases = {
        "university": "university_student",
        "student": "university_student",
        "working": "working_professional",
        "professional": "working_professional",
        "gap_year": "gap_year_student",
    }
    token = aliases.get(token, token)
    return token if token in ALLOWED_PROFESSIONS else ""


def _normalize_inferred_profession(value: Any) -> str:
    """Normalize inferred profession label to one supported example bucket."""
    token = _normalize_profession(value)
    if token in INFERRED_PROFESSIONS:
        return token

    raw = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    if not raw:
        return ""

    aliases = {
        "uni": "university_student",
        "university": "university_student",
        "student": "university_student",
        "working": "working_professional",
        "professional": "working_professional",
    }
    mapped = aliases.get(raw, raw)
    return mapped if mapped in INFERRED_PROFESSIONS else ""


def _resolve_effective_profession(raw_profession: Any, raw_inferred: Any) -> str:
    """
    Resolve profession bucket used for examples/prompt grounding.

    Task 6.7 contract:
    - If profession != other -> use profession as-is.
    - If profession == other -> use profession_inferred if available.
    - If inference missing/invalid -> fallback to working_professional.
    """
    profession = _normalize_profession(raw_profession)
    inferred = _normalize_inferred_profession(raw_inferred)

    if profession == "other":
        return inferred or "working_professional"
    if profession:
        return profession
    return inferred


def _persist_profession_inferred(discord_id: str, profession_inferred: str) -> None:
    """Persist inferred profession to runtime DB when a shared store is available."""
    if not discord_id or not profession_inferred:
        return
    try:
        from database import get_runtime_store

        store = get_runtime_store()
        if store is None:
            return
        setter = getattr(store, "set_profession_inferred", None)
        if callable(setter):
            setter(discord_id, profession_inferred)
    except Exception as exc:
        logger.warning("Could not persist profession_inferred for %s: %s", discord_id, exc)


def _extract_examples(raw_examples: Any) -> List[str]:
    """Extract up to 3 example_text strings from webhook payload."""
    if not isinstance(raw_examples, list):
        return []

    examples: List[str] = []
    for item in raw_examples:
        if isinstance(item, dict):
            text = item.get("example_text") or item.get("text") or ""
        else:
            text = item
        cleaned = _truncate_text(text, max_len=180)
        if cleaned:
            examples.append(cleaned)
        if len(examples) >= 3:
            break
    return examples


def _extract_intervention_text(payload: Dict[str, Any]) -> str:
    """
    Read intervention text from flexible response shapes.
    This data is fetched in task 6.2 plumbing and consumed by later task 6.4 logic.
    """
    intervention = payload.get("intervention")
    if isinstance(intervention, dict):
        return _truncate_text(intervention.get("intervention_text", ""), max_len=240)
    if isinstance(intervention, str):
        return _truncate_text(intervention, max_len=240)
    return _truncate_text(payload.get("intervention_text", ""), max_len=240)


def _normalize_barrier_type(value: Any) -> str:
    """Normalize barrier type to one of the supported intervention tracks."""
    raw = str(value or "").strip().lower()
    allowed = {"identity", "time", "relevance", "technical"}
    return raw if raw in allowed else ""


def _format_example_lines(examples: List[str]) -> List[str]:
    """Render up to 3 context examples as numbered lines."""
    rendered: List[str] = []
    for idx, example in enumerate(examples[:3], start=1):
        if not example:
            continue
        rendered.append(f"{idx}. {example}")
    return rendered


def _agent_personalization_guidance(agent: str, profession: str) -> List[str]:
    """Return agent-specific personalization directives for task 6.3."""
    role = profession or "student"
    if agent == "frame":
        return [
            f"- Use a personalized framing seed grounded in {role} realities.",
            "- Ask exactly one clarifying question and keep it concrete.",
            "- Ground follow-up prompts in the provided profession examples.",
        ]
    if agent == "diverge":
        return [
            f"- Generate profession-specific alternatives a {role} can test this week.",
            "- Offer 5-7 distinct perspectives before converging.",
            "- Keep divergence practical; avoid abstract thought experiments.",
        ]
    if agent == "challenge":
        return [
            f"- Stress-test assumptions with examples from similar {role} contexts.",
            "- Challenge the idea, never the person's identity or capacity.",
            "- End with one revision question that strengthens decision quality.",
        ]
    if agent == "synthesize":
        return [
            "- Reference the student's journey arc (zone movement + explored topics).",
            "- Help them articulate conclusions in their own words.",
            f"- Bridge toward how another {role} could apply the same insight.",
        ]
    return []


async def _call_context_engine_webhook(action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call Apps Script context webhook with shared secret token auth.

    Contract:
      POST CONTEXT_ENGINE_WEBHOOK_URL
      JSON body includes:
        - action: getStudentContext | getExamplesByProfession | getIntervention
        - token: CONTEXT_ENGINE_WEBHOOK_TOKEN (if configured)
        - action-specific params
    """
    url = _get_context_engine_webhook_url()
    if not url:
        return {"success": False, "error": "CONTEXT_ENGINE_WEBHOOK_URL not configured"}

    body_payload: Dict[str, Any] = {"action": action}
    body_payload.update(payload or {})

    token = _get_context_engine_webhook_token()
    if token:
        body_payload["token"] = token

    body = json.dumps(body_payload).encode("utf-8")
    timeout_seconds = _get_context_engine_timeout_seconds()

    def _send_request() -> Dict[str, Any]:
        request = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=timeout_seconds) as resp:
            raw_text = resp.read().decode("utf-8")
        parsed = json.loads(raw_text or "{}")
        if isinstance(parsed, dict):
            return parsed
        return {"success": False, "error": "Context webhook returned non-object JSON"}

    try:
        return await asyncio.to_thread(_send_request)
    except urllib.error.HTTPError as exc:
        details = ""
        try:
            details = exc.read().decode("utf-8")
        except Exception:
            details = str(exc)
        logger.warning("Context webhook %s failed: HTTP %s %s", action, exc.code, details)
        return {"success": False, "error": f"HTTP {exc.code}: {details}"}
    except urllib.error.URLError as exc:
        logger.warning("Context webhook %s connection error: %s", action, exc)
        return {"success": False, "error": f"connection error: {exc}"}
    except Exception as exc:
        logger.warning("Context webhook %s unexpected failure: %s", action, exc)
        return {"success": False, "error": str(exc)}


async def _infer_profession_for_other(
    *,
    provider: str,
    situation: str,
    goals: str,
) -> Tuple[str, Dict[str, Any]]:
    """
    Task 6.7: infer closest profession bucket for students who selected "other".

    Returns:
      (profession_inferred, cost_data)
    """
    compact_situation = _truncate_text(situation, max_len=220)
    compact_goals = _truncate_text(goals, max_len=220)
    if not compact_situation and not compact_goals:
        return "working_professional", {
            "provider": provider,
            "model": get_active_model(provider, agent="profession_inference"),
            "fallback": "missing_context",
        }

    model = get_active_model(provider, agent="profession_inference")
    system_prompt = (
        "Classify the student into one profession bucket for coaching examples.\n"
        "Allowed labels only: teacher, entrepreneur, university_student, working_professional.\n"
        "Return exactly one label and nothing else."
    )
    user_prompt = (
        f"Situation: {compact_situation or 'unknown'}\n"
        f"Goals: {compact_goals or 'unknown'}"
    )
    messages = [{"role": "user", "content": user_prompt}]

    try:
        if provider == "anthropic":
            response_text, cost_data = await _call_anthropic(
                "profession_inference",
                model,
                system_prompt,
                messages,
            )
        elif provider in {"zhipu", "openai", "openai-compatible"}:
            response_text, cost_data = await _call_openai_compatible(
                provider=provider,
                agent="profession_inference",
                model=model,
                system_prompt=system_prompt,
                messages=messages,
            )
        else:
            raise ValueError(f"Unsupported AI_PROVIDER for profession inference: {provider}")
    except Exception as exc:
        logger.warning("Profession inference failed for provider %s: %s", provider, exc)
        return "working_professional", {
            "provider": provider,
            "model": model,
            "fallback": "provider_error",
        }

    raw_text = str(response_text or "").strip().lower()
    inferred = _normalize_inferred_profession(raw_text)
    if not inferred:
        # Allow minor formatting drift like "Answer: teacher".
        for token in re.findall(r"[a-z_]+", raw_text):
            candidate = _normalize_inferred_profession(token)
            if candidate:
                inferred = candidate
                break

    if not inferred:
        inferred = "working_professional"
        cost_data = dict(cost_data or {})
        cost_data["fallback"] = "invalid_label"

    return inferred, cost_data or {"provider": provider, "model": model}


async def _load_context_engine_data(
    student_context: Any,
    *,
    agent: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Fetch task 6.2 context payloads before prompt construction.
    Returns a normalized dict with profile/examples/intervention data.
    """
    context_data: Dict[str, Any] = {
        "profile": {},
        "examples": [],
        "intervention_text": "",
        "profession_effective": "",
        "profession_inferred": "",
    }
    if student_context is None:
        return context_data
    if not _get_context_engine_webhook_url():
        return context_data

    discord_id = str(_context_get_value(student_context, "discord_id", "") or "").strip()
    week = _normalize_week_number(_context_get_value(student_context, "current_week", None))

    profile: Dict[str, Any] = {}
    if discord_id:
        profile_response = await _call_context_engine_webhook(
            "getStudentContext",
            {"discord_id": discord_id},
        )
        raw_profile = profile_response.get("profile")
        if profile_response.get("success") and isinstance(raw_profile, dict):
            profile = raw_profile
    context_data["profile"] = profile

    raw_profession = (
        profile.get("profession")
        or _context_get_value(student_context, "profession", "")
        or ""
    )
    raw_profession_inferred = (
        profile.get("profession_inferred")
        or _context_get_value(student_context, "profession_inferred", "")
        or ""
    )
    situation = str(
        profile.get("situation")
        or _context_get_value(student_context, "situation", "")
        or ""
    ).strip()
    goals = str(
        profile.get("goals")
        or _context_get_value(student_context, "goals", "")
        or ""
    ).strip()

    profession = _normalize_profession(raw_profession)
    profession_inferred = _normalize_inferred_profession(raw_profession_inferred)

    # Task 6.7: infer once on first /frame for profession="other".
    if profession == "other" and not profession_inferred and _normalize_agent_key(agent) == "frame":
        provider = get_active_provider()
        profession_inferred, inference_cost = await _infer_profession_for_other(
            provider=provider,
            situation=situation,
            goals=goals,
        )
        profile["profession_inferred"] = profession_inferred
        if discord_id and profession_inferred:
            _persist_profession_inferred(discord_id, profession_inferred)
        logger.info(
            "Task 6.7 profession inference: discord_id=%s inferred=%s model=%s",
            discord_id or "unknown",
            profession_inferred,
            inference_cost.get("model", "unknown"),
        )

    effective_profession = _resolve_effective_profession(profession, profession_inferred)
    context_data["profession_effective"] = effective_profession
    context_data["profession_inferred"] = profession_inferred

    barrier_type = _normalize_barrier_type(
        profile.get("barrier_type")
        or _context_get_value(student_context, "barrier_type", "")
    )

    pending_calls: List[Tuple[str, Awaitable[Dict[str, Any]]]] = []
    if effective_profession and week is not None:
        pending_calls.append(
            (
                "examples",
                _call_context_engine_webhook(
                    "getExamplesByProfession",
                    {"profession": effective_profession, "week": week},
                ),
            )
        )
    if barrier_type and week is not None:
        pending_calls.append(
            (
                "intervention",
                _call_context_engine_webhook(
                    "getIntervention",
                    {"barrier_type": barrier_type, "week": week},
                ),
            )
        )

    if not pending_calls:
        return context_data

    labels = [item[0] for item in pending_calls]
    responses = await asyncio.gather(
        *[item[1] for item in pending_calls],
        return_exceptions=True,
    )

    for label, response in zip(labels, responses):
        if isinstance(response, Exception):
            logger.warning("Context webhook %s raised error: %s", label, response)
            continue
        if not isinstance(response, dict) or not response.get("success"):
            continue
        if label == "examples":
            context_data["examples"] = _extract_examples(response.get("examples"))
        elif label == "intervention":
            context_data["intervention_text"] = _extract_intervention_text(response)

    return context_data


async def get_context_engine_intervention(
    discord_id: str,
    current_week: Any,
    fallback_context: Any = None,
) -> Dict[str, Any]:
    """
    Resolve barrier-aware intervention copy for escalation routing (task 6.4).

    Returns:
      {
        "success": bool,
        "profile": dict,
        "profession": str,
        "barrier_type": str,
        "week": Optional[int],
        "intervention_text": str,
      }
    """
    result: Dict[str, Any] = {
        "success": False,
        "profile": {},
        "profession": "",
        "barrier_type": "",
        "week": _normalize_week_number(current_week),
        "intervention_text": "",
    }

    cleaned_discord_id = str(discord_id or "").strip()
    if not cleaned_discord_id or not _get_context_engine_webhook_url():
        return result

    profile_response = await _call_context_engine_webhook(
        "getStudentContext",
        {"discord_id": cleaned_discord_id},
    )
    profile = profile_response.get("profile")
    if isinstance(profile, dict) and profile_response.get("success"):
        result["profile"] = profile

    result["profession"] = _truncate_text(
        result["profile"].get("profession")
        or _context_get_value(fallback_context, "profession", ""),
        max_len=80,
    )
    result["barrier_type"] = _normalize_barrier_type(
        result["profile"].get("barrier_type")
        or _context_get_value(fallback_context, "barrier_type", ""),
    )

    week = result["week"]
    barrier_type = result["barrier_type"]
    if barrier_type and week is not None:
        intervention_response = await _call_context_engine_webhook(
            "getIntervention",
            {"barrier_type": barrier_type, "week": week},
        )
        if isinstance(intervention_response, dict) and intervention_response.get("success"):
            result["intervention_text"] = _extract_intervention_text(intervention_response)

    result["success"] = bool(result["profile"] or result["intervention_text"])
    return result


def get_active_provider() -> str:
    """
    Resolve provider from env aliases.

    Supported aliases:
    - anthropic, claude
    - zhipu, glm, glm-4.7
    - openai, gpt
    """
    provider = os.getenv("AI_PROVIDER", "openai").strip().lower()
    aliases = {
        "anthropic": "anthropic",
        "claude": "anthropic",
        "zhipu": "zhipu",
        "glm": "zhipu",
        "glm-4.7": "zhipu",
        "openai": "openai",
        "gpt": "openai",
    }
    return aliases.get(provider, provider)


def get_active_model(provider: str, agent: Optional[str] = None) -> str:
    """
    Return model name based on provider + task tier.

    Task 6.5 routing:
    - fast tier: /frame, /diverge, dashboard summaries
    - deep tier: /challenge, /synthesize, /create-artifact
    """
    tier = _resolve_model_tier(agent)

    if provider == "anthropic":
        fast_model = os.getenv(
            "CLAUDE_HAIKU_MODEL",
            os.getenv("CLAUDE_FAST_MODEL", "claude-3-5-haiku-latest"),
        )
        deep_model = os.getenv(
            "CLAUDE_SONNET_MODEL",
            os.getenv("CLAUDE_MODEL", CLAUDE_MODEL),
        )
        return fast_model if tier == "fast" else deep_model

    if provider == "openai":
        fast_model = os.getenv(
            "OPENAI_FAST_MODEL",
            os.getenv("OPENAI_MODEL", os.getenv("LLM_MODEL", "gpt-4o-mini")),
        )
        deep_model = os.getenv(
            "OPENAI_REASONING_MODEL",
            os.getenv("OPENAI_MODEL", os.getenv("LLM_MODEL", "gpt-4o-mini")),
        )
        return fast_model if tier == "fast" else deep_model

    fast_model = os.getenv(
        "GLM_FAST_MODEL",
        os.getenv("GLM_MODEL", os.getenv("LLM_MODEL", "glm-4.7")),
    )
    deep_model = os.getenv(
        "GLM_REASONING_MODEL",
        os.getenv("GLM_MODEL", os.getenv("LLM_MODEL", "glm-4.7")),
    )
    return fast_model if tier == "fast" else deep_model


def _get_openai_compatible_key(provider: str) -> str:
    """Return key for OpenAI-compatible providers."""
    if provider == "zhipu":
        key = os.getenv("ZHIPU_API_KEY") or os.getenv("OPENAI_API_KEY")
    else:
        key = os.getenv("OPENAI_API_KEY")

    if not key:
        if provider == "zhipu":
            raise ValueError(
                "zhipu API key is not configured. "
                "Set ZHIPU_API_KEY (or OPENAI_API_KEY)."
            )
        raise ValueError(
            f"{provider} API key is not configured. Set OPENAI_API_KEY."
        )
    return key


def _get_openai_compatible_base_url(provider: str) -> str:
    """Return base URL for OpenAI-compatible providers."""
    if provider == "zhipu":
        # Default works for GLM OpenAI-compatible endpoint shape.
        base_url = (
            os.getenv("ZHIPU_BASE_URL")
            or os.getenv("OPENAI_BASE_URL")
            or "https://open.bigmodel.cn/api/paas/v4"
        )
    elif provider == "openai":
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    else:
        base_url = os.getenv("OPENAI_BASE_URL", "")

    if not base_url:
        raise ValueError("OPENAI_BASE_URL is required for non-Anthropic providers.")
    return base_url.rstrip("/")


def validate_provider_configuration() -> Tuple[bool, str]:
    """
    Validate required env config for the active provider.

    Returns:
        (is_valid, detail_message)
    """
    provider = get_active_provider()
    if provider == "anthropic":
        if anthropic is None:
            return False, "anthropic package is not installed"
        if not os.getenv("ANTHROPIC_API_KEY"):
            return False, "ANTHROPIC_API_KEY is not set"
        return True, f"provider={provider}, model={get_active_model(provider)}"

    if provider in {"zhipu", "openai", "openai-compatible"}:
        try:
            _get_openai_compatible_key(provider)
            base_url = _get_openai_compatible_base_url(provider)
        except ValueError as exc:
            return False, str(exc)
        return True, (
            f"provider={provider}, "
            f"model={get_active_model(provider)}, base_url={base_url}"
        )

    return False, f"Unsupported AI_PROVIDER: {provider}"


async def check_provider_api_health(timeout_seconds: int = 10) -> Tuple[bool, str]:
    """
    Validate active provider configuration and perform a lightweight API probe.

    Returns:
        (is_healthy, details)
    """
    config_ok, config_details = validate_provider_configuration()
    if not config_ok:
        return False, config_details

    provider = get_active_provider()

    def _ping_openai_compatible() -> Tuple[bool, str]:
        api_key = _get_openai_compatible_key(provider)
        base_url = _get_openai_compatible_base_url(provider)
        endpoint = f"{base_url}/models"
        req = urllib.request.Request(
            endpoint,
            method="GET",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            status = getattr(resp, "status", 200)
            if status >= 400:
                return False, f"{provider} health probe HTTP {status}"
        return True, f"{provider} API reachable"

    def _ping_anthropic() -> Tuple[bool, str]:
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/models",
            method="GET",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            status = getattr(resp, "status", 200)
            if status >= 400:
                return False, f"anthropic health probe HTTP {status}"
        return True, "anthropic API reachable"

    try:
        if provider == "anthropic":
            return await asyncio.to_thread(_ping_anthropic)

        if provider in {"zhipu", "openai", "openai-compatible"}:
            return await asyncio.to_thread(_ping_openai_compatible)

        return False, f"Unsupported AI_PROVIDER: {provider}"
    except urllib.error.HTTPError as exc:
        return False, f"{provider} API HTTP {exc.code}"
    except urllib.error.URLError as exc:
        return False, f"{provider} API connection error: {exc}"
    except Exception as exc:
        return False, f"{provider} API health probe failed: {exc}"


def get_anthropic_client() -> Any:
    """Get or create Anthropic client singleton."""
    if anthropic is None:
        raise ValueError("anthropic package is not installed. Install requirements first.")

    global _anthropic_client
    if _anthropic_client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        _anthropic_client = anthropic.Anthropic(api_key=api_key)
    return _anthropic_client


def set_runtime_failure_notifier(
    notifier: Optional[Callable[[str, str, str], Awaitable[None]]]
) -> None:
    """
    Register callback used for immediate Trevor alerts on runtime LLM failures.

    Args:
        notifier: Coroutine function receiving (provider, agent, error_message),
            or None to clear notifier.
    """
    global _runtime_failure_notifier
    _runtime_failure_notifier = notifier


def load_system_prompts() -> None:
    """
    Load available agent prompts into cache.

    Called at bot startup. If not called, fallback lazy-loading still attempts
    to populate prompt cache during first request.
    """
    prompt_modules = {
        "frame": ("agents.framer_prompt", "get_system_prompt"),
        "diverge": ("agents.explorer_prompt", "get_system_prompt"),
        "challenge": ("agents.challenger_prompt", "get_system_prompt"),
        "synthesize": ("agents.synthesizer_prompt", "get_system_prompt"),
    }

    for agent_name, (module_name, func_name) in prompt_modules.items():
        try:
            module = __import__(module_name, fromlist=[func_name])
            loader = getattr(module, func_name, None)
            if callable(loader):
                CACHED_SYSTEM_PROMPTS[agent_name] = loader()
                logger.info("Loaded system prompt for %s", agent_name)
        except Exception as exc:
            logger.warning("Could not load %s prompt yet: %s", agent_name, exc)


def _ensure_system_prompt_loaded(agent: str) -> str:
    """Return cached prompt, trying lazy load once if missing."""
    if agent not in CACHED_SYSTEM_PROMPTS:
        raise ValueError(f"Unknown agent: {agent}")

    if not CACHED_SYSTEM_PROMPTS[agent]:
        load_system_prompts()

    prompt = CACHED_SYSTEM_PROMPTS.get(agent)
    if not prompt:
        raise ValueError(f"System prompt not loaded for agent: {agent}")
    return prompt


def _build_personalized_system_prompt(
    base_system_prompt: str,
    student_context: Any,
    agent: str,
    context_engine_data: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Inject task 6.3 personalization into system prompts for all CIS agents.

    Fallback contract:
    - If context is unavailable, return base system prompt unchanged.
    """
    if student_context is None:
        return base_system_prompt

    context_engine_data = context_engine_data or {}
    profile = context_engine_data.get("profile")
    if not isinstance(profile, dict):
        profile = {}
    context_examples = context_engine_data.get("examples")
    if not isinstance(context_examples, list):
        context_examples = []

    profession = _truncate_text(
        _resolve_effective_profession(
            profile.get("profession")
            or _context_get_value(student_context, "profession", ""),
            profile.get("profession_inferred")
            or context_engine_data.get("profession_inferred")
            or _context_get_value(student_context, "profession_inferred", ""),
        ),
        max_len=80,
    )
    situation = _truncate_text(
        profile.get("situation")
        or _context_get_value(student_context, "situation", ""),
        max_len=220,
    )
    goals = _truncate_text(
        profile.get("goals")
        or _context_get_value(student_context, "goals", ""),
        max_len=220,
    )
    barrier_type = _normalize_barrier_type(
        profile.get("barrier_type")
        or _context_get_value(student_context, "barrier_type", ""),
    )
    journey_summary = _truncate_text(
        profile.get("cis_journey_summary")
        or _context_get_value(student_context, "cis_journey_summary", ""),
        max_len=280,
    )
    last_frame_topic = _truncate_text(
        profile.get("last_frame_topic")
        or _context_get_value(student_context, "last_frame_topic", ""),
        max_len=180,
    )

    # Preserve legacy local example fallback if context webhook lacks examples.
    if not context_examples:
        try:
            local_example = (
                student_context.get_relevant_example(agent)
                if hasattr(student_context, "get_relevant_example")
                else ""
            )
        except Exception:
            local_example = ""
        local_example = _truncate_text(local_example, max_len=180)
        if local_example:
            context_examples = [local_example]

    has_personalization = any(
        [profession, situation, goals, barrier_type, context_examples, journey_summary, last_frame_topic]
    )
    if not has_personalization:
        return base_system_prompt

    week = _context_get_value(student_context, "current_week", "unknown")
    zone = _context_get_value(student_context, "zone", "unknown")
    agent_directives = _agent_personalization_guidance(agent, profession)
    example_lines = _format_example_lines(context_examples)

    lines = [
        "",
        "## Task 6.3 Personalization Context (INTERNAL)",
        "Use these details to ground responses in the student's world.",
        "Never expose internal labels like barrier type to the student verbatim.",
        f"- current_week: {week}",
        f"- current_zone: {zone}",
        f"- profession: {profession or 'unknown'}",
    ]
    if situation:
        lines.append(f"- situation: {situation}")
    if goals:
        lines.append(f"- goals: {goals}")
    if barrier_type:
        lines.append(f"- internal_barrier_signal: {barrier_type}")
    if last_frame_topic:
        lines.append(f"- last_frame_topic: {last_frame_topic}")
    if journey_summary:
        lines.append(f"- cis_journey_summary: {journey_summary}")

    if example_lines:
        lines.append("- profession_examples_week_relevant:")
        lines.extend([f"  {line}" for line in example_lines])

    if agent_directives:
        lines.append("- agent_specific_directives:")
        lines.extend([f"  {directive}" for directive in agent_directives])

    lines.extend(
        [
            "- fallback_rule: if context feels incomplete, keep original generic coaching behavior.",
            "- safety_rule: no ranking, no comparison, no pressure language.",
        ]
    )

    return f"{base_system_prompt}\n" + "\n".join(lines)


def _extract_openai_choice_text(response_data: Dict[str, Any]) -> str:
    """Parse assistant content from OpenAI-compatible chat completion payload."""
    choices = response_data.get("choices", [])
    if not choices:
        raise ValueError("No choices returned from provider")

    message = choices[0].get("message", {})
    content = message.get("content", "")
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
        joined = "".join(parts).strip()
        if joined:
            return joined

    raise ValueError("Provider response does not include readable text content")


async def _call_anthropic(
    agent: str,
    model: str,
    system_prompt: str,
    messages: List[Dict[str, str]],
) -> Tuple[str, Dict[str, Any]]:
    """
    Dispatch to Anthropic API using thread offload.

    Returns:
        Tuple of (response_text, cost_data) where cost_data contains:
        - input_tokens, output_tokens, cache_tokens, total_tokens
        - input_cost, cache_cost, output_cost, total_cost_usd
    """
    client = get_anthropic_client()

    kwargs: Dict[str, Any] = {
        "model": model,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "messages": messages,
        "system": [{"type": "text", "text": system_prompt}],
    }

    if ENABLE_PROMPT_CACHING:
        kwargs["system"][0]["cache_control"] = {"type": "ephemeral"}
        kwargs["betas"] = ["prompt-caching-2024-07-31"]

    response = await asyncio.to_thread(client.messages.create, **kwargs)
    response_text = response.content[0].text

    input_tokens = getattr(response.usage, "input_tokens", 0)
    output_tokens = getattr(response.usage, "output_tokens", 0)
    cache_tokens = getattr(response.usage, "cache_read_input_tokens", 0)

    input_cost = (input_tokens - cache_tokens) * 3.0 / 1_000_000 * 0.5
    cache_cost = cache_tokens * 0.30 / 1_000_000 * 0.5
    output_cost = output_tokens * 15.0 / 1_000_000 * 0.5
    total_cost = input_cost + cache_cost + output_cost

    cost_data = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_tokens": cache_tokens,
        "total_tokens": input_tokens + output_tokens + cache_tokens,
        "input_cost": input_cost,
        "cache_cost": cache_cost,
        "output_cost": output_cost,
        "total_cost_usd": total_cost,
        "provider": "anthropic",
        "model": model,
    }

    logger.info(
        "API Call (%s/%s): %s in, %s out, %s cached | $%.4f",
        agent,
        model,
        input_tokens,
        output_tokens,
        cache_tokens,
        total_cost,
    )

    return response_text, cost_data


async def _call_openai_compatible(
    provider: str,
    agent: str,
    model: str,
    system_prompt: str,
    messages: List[Dict[str, str]],
) -> Tuple[str, Dict[str, Any]]:
    """
    Dispatch to OpenAI-compatible Chat Completions endpoint.

    Returns:
        Tuple of (response_text, cost_data) where cost_data contains:
        - prompt_tokens, completion_tokens, total_tokens
        - total_cost_usd (estimated based on provider pricing)
        - provider, model
    """
    api_key = _get_openai_compatible_key(provider)
    base_url = _get_openai_compatible_base_url(provider)
    endpoint = f"{base_url}/chat/completions"

    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
    }
    body = json.dumps(payload).encode("utf-8")

    def _send_request() -> Dict[str, Any]:
        req = urllib.request.Request(
            endpoint,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))

    try:
        response_data = await asyncio.to_thread(_send_request)
    except urllib.error.HTTPError as exc:
        details = ""
        try:
            details = exc.read().decode("utf-8")
        except Exception:
            details = str(exc)
        raise Exception(f"{provider} API HTTP {exc.code}: {details}")
    except urllib.error.URLError as exc:
        raise Exception(f"{provider} API connection error: {exc}")

    usage = response_data.get("usage", {})
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

    # Estimate costs (actual pricing varies by provider)
    # These are conservative estimates for budget tracking
    if provider == "zhipu":
        # GLM-4 pricing approximation (conservative estimate)
        prompt_cost = prompt_tokens * 0.50 / 1_000_000
        completion_cost = completion_tokens * 1.00 / 1_000_000
    else:
        # GPT-4o-mini pricing approximation
        prompt_cost = prompt_tokens * 0.15 / 1_000_000
        completion_cost = completion_tokens * 0.60 / 1_000_000

    total_cost = prompt_cost + completion_cost

    cost_data = {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "prompt_cost": prompt_cost,
        "completion_cost": completion_cost,
        "total_cost_usd": total_cost,
        "provider": provider,
        "model": model,
    }

    logger.info(
        "API Call (%s/%s/%s): %s prompt, %s completion, %s total | $%.4f",
        provider,
        agent,
        model,
        prompt_tokens,
        completion_tokens,
        total_tokens,
        total_cost,
    )

    response_text = _extract_openai_choice_text(response_data)
    return response_text, cost_data


def _is_retryable_llm_error(exc: Exception) -> bool:
    """Best-effort classifier for transient provider failures."""
    message = str(exc).lower()
    retryable_markers = (
        "rate limit",
        "429",
        "timeout",
        "timed out",
        "connection error",
        "connection reset",
        "temporarily unavailable",
        "service unavailable",
        "500",
        "502",
        "503",
        "504",
        "internal server error",
    )
    return any(marker in message for marker in retryable_markers)


async def _call_with_exponential_backoff(
    provider: str,
    agent: str,
    op: Callable[[], Awaitable[Tuple[str, Dict[str, Any]]]],
) -> Tuple[str, Dict[str, Any]]:
    """
    Execute provider call with exponential backoff for transient failures.
    """
    attempt = 1
    last_exc: Optional[Exception] = None
    while attempt <= LLM_MAX_RETRIES:
        try:
            return await op()
        except Exception as exc:
            last_exc = exc
            should_retry = attempt < LLM_MAX_RETRIES and _is_retryable_llm_error(exc)
            if not should_retry:
                raise

            delay_seconds = LLM_RETRY_BASE_DELAY_SECONDS * (2 ** (attempt - 1))
            logger.warning(
                "LLM call transient failure (%s/%s) attempt %s/%s: %s. Retrying in %.2fs",
                provider,
                agent,
                attempt,
                LLM_MAX_RETRIES,
                exc,
                delay_seconds,
            )
            await asyncio.sleep(delay_seconds)
            attempt += 1

    # Defensive fallback (loop should always return/raise before here).
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("LLM retry loop ended without result")


async def call_agent_with_context(
    agent: str,
    student_context,
    user_message: str,
    conversation_history: List[Dict[str, str]],
) -> Tuple[str, Dict[str, Any]]:
    """
    Call active LLM provider with system prompt + StudentContext.

    Args:
        agent: Agent name (frame, diverge, challenge, synthesize)
        student_context: StudentContext domain model
        user_message: Student's message
        conversation_history: Last 10 messages for context window

    Returns:
        Tuple of (response_text, cost_data) where cost_data contains:
        - Token counts (varies by provider)
        - Cost breakdown (input/output/cache costs)
        - Total cost in USD
        - Provider and model information
    """
    base_system_prompt = _ensure_system_prompt_loaded(agent)
    provider = get_active_provider()
    model = get_active_model(provider, agent=agent)

    context_engine_data = await _load_context_engine_data(
        student_context,
        agent=agent,
    )
    system_prompt = _build_personalized_system_prompt(
        base_system_prompt,
        student_context,
        agent,
        context_engine_data=context_engine_data,
    )

    messages = conversation_history[-10:] + [
        {"role": "user", "content": user_message}
    ]

    try:
        if provider == "anthropic":
            return await _call_with_exponential_backoff(
                provider=provider,
                agent=agent,
                op=lambda: _call_anthropic(agent, model, system_prompt, messages),
            )

        if provider in {"zhipu", "openai", "openai-compatible"}:
            return await _call_with_exponential_backoff(
                provider=provider,
                agent=agent,
                op=lambda: _call_openai_compatible(
                    provider=provider,
                    agent=agent,
                    model=model,
                    system_prompt=system_prompt,
                    messages=messages,
                ),
            )

        raise ValueError(f"Unsupported AI_PROVIDER: {provider}")

    except Exception as exc:
        # LLM Provider Failure Handling (Task 4.5)
        # Return fallback message encouraging Habit 1 practice independently
        logger.error("LLM provider failure (%s/%s): %s", provider, agent, exc)

        if _runtime_failure_notifier is not None:
            try:
                await _runtime_failure_notifier(provider, agent, str(exc))
            except Exception as notify_exc:
                logger.error(
                    "Runtime failure notifier failed (%s/%s): %s",
                    provider,
                    agent,
                    notify_exc,
                )

        from cis_controller.health_monitor import get_llm_fallback_message

        fallback_message = get_llm_fallback_message(agent)

        # Return fallback message with zero cost data
        cost_data = {
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "provider": provider,
            "model": model,
            "fallback": True,
        }

        return fallback_message, cost_data
