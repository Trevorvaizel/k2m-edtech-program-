"""
Tests for LLM Integration Module.

Focus:
- Provider/model routing via env-friendly helpers
- Stable call signature
- No network required (provider calls mocked)
"""

import inspect
import json
import os
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import set_runtime_store  # noqa: E402
from database.store import StudentStateStore  # noqa: E402
from agents.explorer_prompt import get_system_prompt as get_explorer_system_prompt  # noqa: E402
from cis_controller.llm_integration import (  # noqa: E402
    CACHED_SYSTEM_PROMPTS,
    CLAUDE_MODEL,
    MAX_TOKENS,
    TEMPERATURE,
    check_provider_api_health,
    call_agent_with_context,
    get_context_engine_intervention,
    get_active_model,
    get_active_provider,
    set_runtime_failure_notifier,
)


class TestModelConfiguration:
    def test_claude_model_contains_sonnet(self):
        assert "sonnet" in CLAUDE_MODEL.lower()

    def test_max_tokens_is_1000(self):
        assert MAX_TOKENS == 1000

    def test_temperature_is_1_point_0(self):
        assert TEMPERATURE == 1.0


class TestProviderHelpers:
    def test_provider_alias_glm_maps_to_zhipu(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "glm")
        assert get_active_provider() == "zhipu"

    def test_provider_alias_claude_maps_to_anthropic(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "claude")
        assert get_active_provider() == "anthropic"

    def test_provider_alias_gpt_maps_to_openai(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "gpt")
        assert get_active_provider() == "openai"

    def test_anthropic_model_resolution(self, monkeypatch):
        monkeypatch.setenv("CLAUDE_MODEL", "claude-sonnet-test")
        assert get_active_model("anthropic") == "claude-sonnet-test"

    def test_openai_model_resolution(self, monkeypatch):
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1-mini")
        monkeypatch.setenv("LLM_MODEL", "glm-4.7")
        assert get_active_model("openai") == "gpt-4.1-mini"

    def test_zhipu_model_resolution(self, monkeypatch):
        monkeypatch.setenv("LLM_MODEL", "glm-4.7")
        assert get_active_model("zhipu") == "glm-4.7"

    def test_anthropic_fast_tier_model_resolution(self, monkeypatch):
        monkeypatch.setenv("CLAUDE_HAIKU_MODEL", "claude-haiku-fast")
        monkeypatch.setenv("CLAUDE_SONNET_MODEL", "claude-sonnet-deep")
        assert get_active_model("anthropic", agent="frame") == "claude-haiku-fast"
        assert get_active_model("anthropic", agent="diverge") == "claude-haiku-fast"

    def test_anthropic_deep_tier_model_resolution(self, monkeypatch):
        monkeypatch.setenv("CLAUDE_HAIKU_MODEL", "claude-haiku-fast")
        monkeypatch.setenv("CLAUDE_SONNET_MODEL", "claude-sonnet-deep")
        assert get_active_model("anthropic", agent="challenge") == "claude-sonnet-deep"
        assert get_active_model("anthropic", agent="synthesize") == "claude-sonnet-deep"
        assert get_active_model("anthropic", agent="create-artifact") == "claude-sonnet-deep"


class TestPromptCacheShape:
    def test_frame_slot_exists(self):
        assert "frame" in CACHED_SYSTEM_PROMPTS

    def test_diverge_slot_exists(self):
        assert "diverge" in CACHED_SYSTEM_PROMPTS

    def test_challenge_slot_exists(self):
        assert "challenge" in CACHED_SYSTEM_PROMPTS

    def test_synthesize_slot_exists(self):
        assert "synthesize" in CACHED_SYSTEM_PROMPTS


class TestExplorerPromptGrounding:
    def test_emotional_context_patterns_are_explicit(self):
        prompt = get_explorer_system_prompt().lower()

        for emotional_state in (
            "overwhelmed",
            "rushing",
            "resistant",
            "confident",
            "in_circles",
        ):
            assert emotional_state in prompt


class TestCallAgentSignature:
    def test_expected_parameters_exist(self):
        sig = inspect.signature(call_agent_with_context)
        assert "agent" in sig.parameters
        assert "student_context" in sig.parameters
        assert "user_message" in sig.parameters
        assert "conversation_history" in sig.parameters

    def test_function_is_coroutine(self):
        assert inspect.iscoroutinefunction(call_agent_with_context)


class TestCallRouting:
    @pytest.mark.asyncio
    async def test_unknown_agent_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown agent"):
            await call_agent_with_context("unknown-agent", None, "test", [])

    @pytest.mark.asyncio
    async def test_routes_to_zhipu_provider(self):
        with patch(
            "cis_controller.llm_integration._ensure_system_prompt_loaded",
            return_value="SYSTEM PROMPT",
        ), patch(
            "cis_controller.llm_integration.get_active_provider",
            return_value="zhipu",
        ), patch(
            "cis_controller.llm_integration.get_active_model",
            return_value="glm-4.7",
        ), patch(
            "cis_controller.llm_integration._call_openai_compatible",
            new_callable=AsyncMock,
            return_value=("zhipu-ok", {"total_cost_usd": 0.0}),
        ) as mock_provider:
            result = await call_agent_with_context("frame", None, "hello", [])
            assert result[0] == "zhipu-ok"
            mock_provider.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_routes_to_anthropic_provider(self):
        with patch(
            "cis_controller.llm_integration._ensure_system_prompt_loaded",
            return_value="SYSTEM PROMPT",
        ), patch(
            "cis_controller.llm_integration.get_active_provider",
            return_value="anthropic",
        ), patch(
            "cis_controller.llm_integration.get_active_model",
            return_value="claude-sonnet-4-5-20250514",
        ), patch(
            "cis_controller.llm_integration._call_anthropic",
            new_callable=AsyncMock,
            return_value=("anthropic-ok", {"total_cost_usd": 0.0}),
        ) as mock_provider:
            result = await call_agent_with_context("frame", None, "hello", [])
            assert result[0] == "anthropic-ok"
            mock_provider.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_routes_to_openai_provider(self):
        with patch(
            "cis_controller.llm_integration._ensure_system_prompt_loaded",
            return_value="SYSTEM PROMPT",
        ), patch(
            "cis_controller.llm_integration.get_active_provider",
            return_value="openai",
        ), patch(
            "cis_controller.llm_integration.get_active_model",
            return_value="gpt-4o-mini",
        ), patch(
            "cis_controller.llm_integration._call_openai_compatible",
            new_callable=AsyncMock,
            return_value=("openai-ok", {"total_cost_usd": 0.0}),
        ) as mock_provider:
            result = await call_agent_with_context("frame", None, "hello", [])
            assert result[0] == "openai-ok"
            mock_provider.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_student_context_is_injected_into_system_prompt(self):
        context = SimpleNamespace(
            current_week=2,
            zone="zone_1",
            emotional_state="curious",
            jtbd_primary_concern="career_direction",
            get_altitude=lambda: "Level 2 - Pattern",
            get_relevant_example=lambda agent: "career decision example",
        )

        with patch(
            "cis_controller.llm_integration._ensure_system_prompt_loaded",
            return_value="SYSTEM PROMPT",
        ), patch(
            "cis_controller.llm_integration.get_active_provider",
            return_value="zhipu",
        ), patch(
            "cis_controller.llm_integration.get_active_model",
            return_value="glm-4.7",
        ), patch(
            "cis_controller.llm_integration._call_openai_compatible",
            new_callable=AsyncMock,
            return_value=("ok", {"total_cost_usd": 0.0}),
        ) as mock_provider:
            await call_agent_with_context("frame", context, "I need help", [])

            kwargs = mock_provider.await_args.kwargs
            messages = kwargs["messages"]
            assert messages[-1]["role"] == "user"
            assert messages[-1]["content"] == "I need help"
            assert "Task 6.3 Personalization Context" in kwargs["system_prompt"]
            assert "current_week: 2" in kwargs["system_prompt"]

    @pytest.mark.asyncio
    async def test_retries_transient_errors_before_success(self):
        with patch(
            "cis_controller.llm_integration._ensure_system_prompt_loaded",
            return_value="SYSTEM PROMPT",
        ), patch(
            "cis_controller.llm_integration.get_active_provider",
            return_value="openai",
        ), patch(
            "cis_controller.llm_integration.get_active_model",
            return_value="gpt-4o-mini",
        ), patch(
            "cis_controller.llm_integration._call_openai_compatible",
            new_callable=AsyncMock,
            side_effect=[
                Exception("openai API HTTP 503"),
                ("openai-ok", {"total_cost_usd": 0.0}),
            ],
        ) as mock_provider, patch(
            "cis_controller.llm_integration.asyncio.sleep",
            new_callable=AsyncMock,
        ):
            result = await call_agent_with_context("frame", None, "hello", [])
            assert result[0] == "openai-ok"
            assert mock_provider.await_count == 2

    @pytest.mark.asyncio
    async def test_context_engine_webhooks_called_before_prompt_assembly(self, monkeypatch):
        monkeypatch.setenv("CONTEXT_ENGINE_WEBHOOK_URL", "https://example.test/context")
        monkeypatch.setenv("CONTEXT_ENGINE_WEBHOOK_TOKEN", "ctx-secret")

        context = SimpleNamespace(
            discord_id="1234567890",
            current_week=4,
            zone="zone_2",
            emotional_state="curious",
            jtbd_primary_concern="career_direction",
        )

        with patch(
            "cis_controller.llm_integration._ensure_system_prompt_loaded",
            return_value="SYSTEM PROMPT",
        ), patch(
            "cis_controller.llm_integration.get_active_provider",
            return_value="openai",
        ), patch(
            "cis_controller.llm_integration.get_active_model",
            return_value="gpt-4o-mini",
        ), patch(
            "cis_controller.llm_integration._call_context_engine_webhook",
            new_callable=AsyncMock,
            side_effect=[
                {
                    "success": True,
                    "profile": {
                        "profession": "teacher",
                        "situation": "I teach Form 3 chemistry.",
                        "goals": "Build stronger critical-thinking sessions.",
                        "barrier_type": "time",
                    },
                },
                {
                    "success": True,
                    "examples": [
                        {"example_text": "A class planning example."},
                        {"example_text": "A CBC competency example."},
                        {"example_text": "A student feedback example."},
                    ],
                },
                {
                    "success": True,
                    "intervention": {"intervention_text": "Use one 5-minute framing sprint."},
                },
            ],
        ) as mock_context_hook, patch(
            "cis_controller.llm_integration._call_openai_compatible",
            new_callable=AsyncMock,
            return_value=("ok", {"total_cost_usd": 0.0}),
        ) as mock_provider:
            await call_agent_with_context("frame", context, "I need help", [])

        actions = [call.args[0] for call in mock_context_hook.await_args_list]
        assert actions == [
            "getStudentContext",
            "getExamplesByProfession",
            "getIntervention",
        ]

        provider_system_prompt = mock_provider.await_args.kwargs["system_prompt"]
        assert "profession: teacher" in provider_system_prompt
        assert "profession_examples_week_relevant" in provider_system_prompt
        assert "1. A class planning example." in provider_system_prompt
        assert "2. A CBC competency example." in provider_system_prompt

    @pytest.mark.asyncio
    async def test_context_webhook_payload_includes_token(self, monkeypatch):
        monkeypatch.setenv("CONTEXT_ENGINE_WEBHOOK_URL", "https://example.test/context")
        monkeypatch.setenv("CONTEXT_ENGINE_WEBHOOK_TOKEN", "ctx-secret")
        monkeypatch.setenv("CONTEXT_ENGINE_TIMEOUT_SECONDS", "3")

        from cis_controller import llm_integration as li

        captured = {}

        class _FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return b'{"success": true, "profile": {"profession": "teacher"}}'

        def _fake_urlopen(request, timeout=0):
            captured["url"] = request.full_url
            captured["timeout"] = timeout
            captured["payload"] = json.loads(request.data.decode("utf-8"))
            return _FakeResponse()

        with patch(
            "cis_controller.llm_integration.urllib.request.urlopen",
            side_effect=_fake_urlopen,
        ):
            result = await li._call_context_engine_webhook(
                "getStudentContext",
                {"discord_id": "1234567890"},
            )

        assert result["success"] is True
        assert captured["url"] == "https://example.test/context"
        assert captured["timeout"] == 3
        assert captured["payload"]["action"] == "getStudentContext"
        assert captured["payload"]["discord_id"] == "1234567890"
        assert captured["payload"]["token"] == "ctx-secret"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "agent,marker",
        [
            ("frame", "personalized framing seed"),
            ("diverge", "profession-specific alternatives"),
            ("challenge", "similar"),
            ("synthesize", "journey arc"),
        ],
    )
    async def test_agent_specific_personalization_directives(self, agent, marker, monkeypatch):
        monkeypatch.setenv("CONTEXT_ENGINE_WEBHOOK_URL", "https://example.test/context")
        context = SimpleNamespace(
            discord_id="1234567890",
            current_week=6,
            zone="zone_3",
            emotional_state="curious",
            jtbd_primary_concern="career_direction",
        )

        with patch(
            "cis_controller.llm_integration._ensure_system_prompt_loaded",
            return_value="SYSTEM PROMPT",
        ), patch(
            "cis_controller.llm_integration.get_active_provider",
            return_value="openai",
        ), patch(
            "cis_controller.llm_integration.get_active_model",
            return_value="gpt-4o-mini",
        ), patch(
            "cis_controller.llm_integration._call_context_engine_webhook",
            new_callable=AsyncMock,
            side_effect=[
                {
                    "success": True,
                    "profile": {
                        "profession": "teacher",
                        "situation": "I teach Form 3 chemistry.",
                        "goals": "Build stronger critical-thinking sessions.",
                        "barrier_type": "time",
                        "last_frame_topic": "classroom assessment design",
                        "cis_journey_summary": "framed classroom issues and tested alternatives",
                    },
                },
                {
                    "success": True,
                    "examples": [
                        {"example_text": "A class planning example."},
                        {"example_text": "A CBC competency example."},
                        {"example_text": "A student feedback example."},
                    ],
                },
                {
                    "success": True,
                    "intervention": {"intervention_text": "Use one 5-minute framing sprint."},
                },
            ],
        ), patch(
            "cis_controller.llm_integration._call_openai_compatible",
            new_callable=AsyncMock,
            return_value=("ok", {"total_cost_usd": 0.0}),
        ) as mock_provider:
            await call_agent_with_context(agent, context, "Help me think", [])

        system_prompt = mock_provider.await_args.kwargs["system_prompt"].lower()
        assert "task 6.3 personalization context" in system_prompt
        assert marker in system_prompt

    @pytest.mark.asyncio
    async def test_prompt_falls_back_to_generic_when_personalization_missing(self):
        context = SimpleNamespace(
            discord_id="1234567890",
            current_week=2,
            zone="zone_1",
            emotional_state="curious",
            jtbd_primary_concern="career_direction",
            get_relevant_example=lambda _: "",
        )

        with patch(
            "cis_controller.llm_integration._ensure_system_prompt_loaded",
            return_value="SYSTEM PROMPT",
        ), patch(
            "cis_controller.llm_integration.get_active_provider",
            return_value="openai",
        ), patch(
            "cis_controller.llm_integration.get_active_model",
            return_value="gpt-4o-mini",
        ), patch(
            "cis_controller.llm_integration._call_context_engine_webhook",
            new_callable=AsyncMock,
            side_effect=[
                {"success": False, "error": "student_not_found"},
            ],
        ), patch(
            "cis_controller.llm_integration._call_openai_compatible",
            new_callable=AsyncMock,
            return_value=("ok", {"total_cost_usd": 0.0}),
        ) as mock_provider:
            await call_agent_with_context("frame", context, "I need help", [])

        assert mock_provider.await_args.kwargs["system_prompt"] == "SYSTEM PROMPT"

    @pytest.mark.asyncio
    async def test_other_profession_inference_on_first_frame_persists_and_routes_examples(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CONTEXT_ENGINE_WEBHOOK_URL", "https://example.test/context")

        db_path = tmp_path / "test_context_engine.db"
        store = StudentStateStore(str(db_path))
        set_runtime_store(store)
        try:
            store.create_student(discord_id="1234567890")
            store.conn.execute(
                """
                UPDATE students
                SET profession = ?, situation = ?, goals = ?
                WHERE discord_id = ?
                """,
                (
                    "other",
                    "I coordinate youth outreach in county offices.",
                    "Improve planning quality with AI support.",
                    "1234567890",
                ),
            )
            store.conn.commit()

            context = SimpleNamespace(
                discord_id="1234567890",
                current_week=4,
                zone="zone_2",
                profession="other",
                situation="I coordinate youth outreach in county offices.",
                goals="Improve planning quality with AI support.",
            )

            with patch(
                "cis_controller.llm_integration._ensure_system_prompt_loaded",
                return_value="SYSTEM PROMPT",
            ), patch(
                "cis_controller.llm_integration.get_active_provider",
                return_value="openai",
            ), patch(
                "cis_controller.llm_integration.get_active_model",
                side_effect=lambda provider, agent=None: (
                    "openai-fast" if agent in {"frame", "profession_inference"} else "openai-deep"
                ),
            ), patch(
                "cis_controller.llm_integration._call_context_engine_webhook",
                new_callable=AsyncMock,
                side_effect=[
                    {
                        "success": True,
                        "profile": {
                            "profession": "other",
                            "situation": "I coordinate youth outreach in county offices.",
                            "goals": "Improve planning quality with AI support.",
                        },
                    },
                    {
                        "success": True,
                        "examples": [
                            {"example_text": "Teacher example for this week."},
                        ],
                    },
                ],
            ) as mock_context_hook, patch(
                "cis_controller.llm_integration._infer_profession_for_other",
                new_callable=AsyncMock,
                return_value=("teacher", {"provider": "openai", "model": "openai-fast"}),
            ) as mock_infer, patch(
                "cis_controller.llm_integration._call_openai_compatible",
                new_callable=AsyncMock,
                return_value=("ok", {"total_cost_usd": 0.0, "provider": "openai", "model": "openai-fast"}),
            ):
                await call_agent_with_context("frame", context, "Help me frame this", [])

            mock_infer.assert_awaited_once()
            second_call = mock_context_hook.await_args_list[1]
            assert second_call.args[0] == "getExamplesByProfession"
            assert second_call.args[1]["profession"] == "teacher"

            student = store.get_student("1234567890")
            assert student is not None
            assert student["profession_inferred"] == "teacher"
        finally:
            set_runtime_store(None)
            store.close()


class TestInterventionLookup:
    @pytest.mark.asyncio
    async def test_get_context_engine_intervention_returns_profile_and_copy(self, monkeypatch):
        monkeypatch.setenv("CONTEXT_ENGINE_WEBHOOK_URL", "https://example.test/context")

        with patch(
            "cis_controller.llm_integration._call_context_engine_webhook",
            new_callable=AsyncMock,
            side_effect=[
                {
                    "success": True,
                    "profile": {
                        "profession": "teacher",
                        "barrier_type": "time",
                    },
                },
                {
                    "success": True,
                    "intervention": {
                        "intervention_text": "Use one focused 10-minute sprint.",
                    },
                },
            ],
        ):
            payload = await get_context_engine_intervention(
                discord_id="1234567890",
                current_week=4,
            )

        assert payload["success"] is True
        assert payload["profession"] == "teacher"
        assert payload["barrier_type"] == "time"
        assert "10-minute" in payload["intervention_text"]


class TestRuntimeFailureAlerts:
    @pytest.mark.asyncio
    async def test_runtime_failure_notifier_called_on_final_failure(self):
        notifier = AsyncMock()
        set_runtime_failure_notifier(notifier)
        try:
            with patch(
                "cis_controller.llm_integration._ensure_system_prompt_loaded",
                return_value="SYSTEM PROMPT",
            ), patch(
                "cis_controller.llm_integration.get_active_provider",
                return_value="openai",
            ), patch(
                "cis_controller.llm_integration.get_active_model",
                return_value="gpt-4o-mini",
            ), patch(
                "cis_controller.llm_integration._call_openai_compatible",
                new_callable=AsyncMock,
                side_effect=Exception("openai API HTTP 500"),
            ), patch(
                "cis_controller.llm_integration.asyncio.sleep",
                new_callable=AsyncMock,
            ):
                response, cost_data = await call_agent_with_context(
                    "frame",
                    None,
                    "hello",
                    [],
                )
                assert cost_data["fallback"] is True
                assert "PAUSE" in response or "Framer" in response
        finally:
            set_runtime_failure_notifier(None)

        notifier.assert_awaited_once()
        args = notifier.await_args.args
        assert args[0] == "openai"
        assert args[1] == "frame"
        assert "500" in args[2]


class TestProviderHealthProbe:
    @pytest.mark.asyncio
    async def test_provider_health_fails_when_config_invalid(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "openai")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        ok, details = await check_provider_api_health()
        assert ok is False
        assert "api key" in details.lower()
