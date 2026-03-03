# Provider Runtime Override (Canonical)

**Effective Date:** 2026-02-18  
**Scope:** `cis-discord-bot` implementation and Discord infra sprint execution

## Active Runtime Provider

- `AI_PROVIDER=openai` is the active runtime configuration for current development/deployment.
- Provider swap architecture is still retained (`openai | anthropic | zhipu`) via environment variables.

## Why This Exists

Legacy design/playbook artifacts reference Claude/Anthropic as the originally selected implementation provider.  
Runtime has been swapped and validated on OpenAI. Without an explicit override, this creates implementation drift.

## Source-of-Truth Precedence

1. Runtime env in deployment (`AI_PROVIDER`, provider API key, model vars)
2. `cis-discord-bot/.env` and `cis-discord-bot/.env.template`
3. `cis-discord-bot/cis_controller/llm_integration.py`
4. Sprint tracker: `_bmad-output/cohort-design-artifacts/operations/sprint/discord-implementation-sprint.yaml`
5. Older playbook language that names a specific provider

## Normalization Rule for Legacy Docs

When older docs say:

- "Claude API down" -> interpret as "active LLM provider down"
- "Anthropic SDK integration" -> interpret as "provider-routed LLM integration"
- Provider-specific cost language -> treat as historical estimate, re-check against active provider pricing

## Implementation Note

No guardrails, agent behavior, or weekly design logic changed as part of this provider swap.  
Only model provider plumbing/config changed.
