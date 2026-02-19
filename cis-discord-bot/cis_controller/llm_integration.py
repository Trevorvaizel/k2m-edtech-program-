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
from typing import Any, Dict, List, Optional, Tuple

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

# Cached system prompts - loaded once at startup, reused for all calls
CACHED_SYSTEM_PROMPTS: Dict[str, Optional[str]] = {
    "frame": None,
    "diverge": None,
    "challenge": None,
    "synthesize": None,
}

# Global Anthropic client (initialized on first use)
_anthropic_client: Optional[Any] = None


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


def _build_student_context_block(student_context, agent: str) -> str:
    """
    Build a compact personalization block from StudentContext.

    This keeps Framer grounded in zone/week/emotional context without
    hardcoding separate example libraries in this layer.
    """
    if student_context is None:
        return ""

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

    lines = [
        "StudentContext:",
        f"- week: {getattr(student_context, 'current_week', 'unknown')}",
        f"- zone: {getattr(student_context, 'zone', 'unknown')}",
        f"- emotional_state: {getattr(student_context, 'emotional_state', 'unknown')}",
        f"- jtbd_primary_concern: {getattr(student_context, 'jtbd_primary_concern', 'unknown')}",
    ]
    if altitude:
        lines.append(f"- altitude: {altitude}")
    if example:
        lines.append(f"- relevant_example: {example}")

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

    context_block = _build_student_context_block(student_context, agent)
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
            return await _call_anthropic(agent, model, system_prompt, messages)

        if provider in {"zhipu", "openai", "openai-compatible"}:
            return await _call_openai_compatible(
                provider=provider,
                agent=agent,
                model=model,
                system_prompt=system_prompt,
                messages=messages,
            )

        raise ValueError(f"Unsupported AI_PROVIDER: {provider}")

    except Exception as exc:
        # LLM Provider Failure Handling (Task 4.5)
        # Return fallback message encouraging Habit 1 practice independently
        logger.error("LLM provider failure (%s/%s): %s", provider, agent, exc)

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
