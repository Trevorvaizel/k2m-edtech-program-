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


async def _load_context_engine_data(student_context: Any) -> Dict[str, Any]:
    """
    Fetch task 6.2 context payloads before prompt construction.
    Returns a normalized dict with profile/examples/intervention data.
    """
    context_data: Dict[str, Any] = {
        "profile": {},
        "examples": [],
        "intervention_text": "",
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

    profession = str(
        profile.get("profession")
        or _context_get_value(student_context, "profession", "")
        or ""
    ).strip()
    barrier_type = str(
        profile.get("barrier_type")
        or _context_get_value(student_context, "barrier_type", "")
        or ""
    ).strip()

    pending_calls: List[Tuple[str, Awaitable[Dict[str, Any]]]] = []
    if profession and week is not None:
        pending_calls.append(
            (
                "examples",
                _call_context_engine_webhook(
                    "getExamplesByProfession",
                    {"profession": profession, "week": week},
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


def get_active_model(provider: str) -> str:
    """Return model name based on active provider."""
    if provider == "anthropic":
        return os.getenv("CLAUDE_MODEL", CLAUDE_MODEL)
    if provider == "openai":
        return os.getenv("OPENAI_MODEL", os.getenv("LLM_MODEL", "gpt-4o-mini"))
    return os.getenv("GLM_MODEL", os.getenv("LLM_MODEL", "glm-4.7"))


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


def _build_student_context_block(
    student_context,
    agent: str,
    context_engine_data: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Build a compact personalization block from StudentContext.

    This keeps Framer grounded in zone/week/emotional context without
    hardcoding separate example libraries in this layer.
    """
    if student_context is None:
        return ""

    context_engine_data = context_engine_data or {}
    profile = context_engine_data.get("profile")
    if not isinstance(profile, dict):
        profile = {}
    context_examples = context_engine_data.get("examples")
    if not isinstance(context_examples, list):
        context_examples = []

    altitude = ""
    try:
        if hasattr(student_context, "get_altitude"):
            altitude = student_context.get_altitude() or ""
    except Exception:
        altitude = ""

    example = ""
    try:
        if hasattr(student_context, "get_relevant_example"):
            example = student_context.get_relevant_example(agent) or ""
    except Exception:
        example = ""

    profession = _truncate_text(
        profile.get("profession")
        or _context_get_value(student_context, "profession", ""),
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

    if not example and context_examples:
        example = context_examples[0]

    lines = [
        "StudentContext:",
        f"- week: {_context_get_value(student_context, 'current_week', 'unknown')}",
        f"- zone: {_context_get_value(student_context, 'zone', 'unknown')}",
        f"- emotional_state: {_context_get_value(student_context, 'emotional_state', 'unknown')}",
        f"- jtbd_primary_concern: {_context_get_value(student_context, 'jtbd_primary_concern', 'unknown')}",
    ]
    if profession:
        lines.append(f"- profession: {profession}")
    if situation:
        lines.append(f"- situation: {situation}")
    if goals:
        lines.append(f"- goals: {goals}")
    if altitude:
        lines.append(f"- altitude: {altitude}")
    if example:
        lines.append(f"- relevant_example: {example}")
    if len(context_examples) > 1:
        lines.append(f"- extra_examples: {' | '.join(context_examples[1:3])}")

    lines.append("")
    lines.append("Use this context to tailor language and scaffolding.")
    return "\n".join(lines)


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
    system_prompt = _ensure_system_prompt_loaded(agent)
    provider = get_active_provider()
    model = get_active_model(provider)

    context_engine_data = await _load_context_engine_data(student_context)
    context_block = _build_student_context_block(
        student_context,
        agent,
        context_engine_data=context_engine_data,
    )
    final_user_message = user_message
    if context_block:
        final_user_message = (
            f"{context_block}\n\n"
            f"Student message:\n{user_message}"
        )

    messages = conversation_history[-10:] + [
        {"role": "user", "content": final_user_message}
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
