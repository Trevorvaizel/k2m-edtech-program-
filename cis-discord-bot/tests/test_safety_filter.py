"""
Tests for SafetyFilter - Anti-comparison validation (Guardrail #3)
Story 4.7 Implementation

Verifies that the SafetyFilter correctly blocks comparison/ranking
language from appearing in public Discord channels per Guardrail #3.
"""

import pytest
import sys
import os
from unittest.mock import AsyncMock, Mock, patch

# Ensure cis-discord-bot root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cis_controller.safety_filter import (
    SafetyFilter,
    ComparisonViolationError,
    CrisisDetectedError,
    notify_trevor_safety_violation,
)


class TestSafetyFilterPassCases:
    """Messages that should pass the safety filter"""

    def setup_method(self):
        self.filter = SafetyFilter()

    def test_count_only_message_passes(self):
        """Non-comparative aggregate counts should pass"""
        assert self.filter.validate_no_comparison(
            "15 students practiced /frame this week"
        ) is True

    def test_celebration_message_passes(self):
        """Celebration messages without comparison pass"""
        assert self.filter.validate_no_comparison(
            "Great thinking session today! ✨ Keep going!"
        ) is True

    def test_empty_string_passes(self):
        """Empty messages pass (no comparison possible)"""
        assert self.filter.validate_no_comparison("") is True

    def test_habit_practice_message_passes(self):
        """Habit practice messages without comparison pass"""
        assert self.filter.validate_no_comparison(
            "You practiced Habit 1 (⏸️ PAUSE) today!"
        ) is True

    def test_encouragement_passes(self):
        """Pure encouragement messages pass"""
        assert self.filter.validate_no_comparison(
            "You're on track. Keep going!"
        ) is True


class TestSafetyFilterBlockCases:
    """Messages that must be blocked by the safety filter"""

    def setup_method(self):
        self.filter = SafetyFilter()

    def test_blocks_top_student(self):
        """`top student` is forbidden - Guardrail #3"""
        with pytest.raises(ComparisonViolationError):
            self.filter.validate_no_comparison("top student this week is doing great")

    def test_blocks_best_student(self):
        """`best student` is forbidden"""
        with pytest.raises(ComparisonViolationError):
            self.filter.validate_no_comparison("The best student award goes to...")

    def test_blocks_better_than(self):
        """`better than` creates implicit comparison"""
        with pytest.raises(ComparisonViolationError):
            self.filter.validate_no_comparison(
                "Your artifact is better than what most students produce"
            )

    def test_blocks_leaderboard(self):
        """`leaderboard` is explicitly forbidden"""
        with pytest.raises(ComparisonViolationError):
            self.filter.validate_no_comparison("Check the leaderboard!")

    def test_blocks_ranking(self):
        """`ranking` is forbidden"""
        with pytest.raises(ComparisonViolationError):
            self.filter.validate_no_comparison("Weekly ranking update:")

    def test_blocks_top_n_pattern(self):
        """Regex pattern: `top [number]` is forbidden"""
        with pytest.raises(ComparisonViolationError):
            self.filter.validate_no_comparison("Top 3 students this week:")

    def test_blocks_first_place(self):
        """`first place` is forbidden"""
        with pytest.raises(ComparisonViolationError):
            self.filter.validate_no_comparison("You're in 1st place!")

    def test_blocks_most_active(self):
        """`most active` creates implicit comparison"""
        with pytest.raises(ComparisonViolationError):
            self.filter.validate_no_comparison("The most active student this week")

    def test_case_insensitive_detection(self):
        """Detection must be case insensitive"""
        with pytest.raises(ComparisonViolationError):
            self.filter.validate_no_comparison("TOP STUDENT award goes to...")

    def test_blocks_rank_keyword(self):
        """`rank` alone is forbidden"""
        with pytest.raises(ComparisonViolationError):
            self.filter.validate_no_comparison("Let's see how you rank")


class TestSafetyFilterAggregateMessages:
    """Test aggregate message validation"""

    def setup_method(self):
        self.filter = SafetyFilter()

    def test_aggregate_count_without_names_passes(self):
        """Aggregate counts without names are allowed"""
        assert self.filter.validate_aggregate_message(
            "15 students completed their artifacts this week",
            []
        ) is True

    def test_aggregate_with_empty_names_list_passes(self):
        """Empty names list always passes"""
        assert self.filter.validate_aggregate_message(
            "Great participation this week!",
            []
        ) is True

    def test_aggregate_with_names_and_action_verbs_fails(self):
        """Names + action verbs = implicit comparison"""
        with pytest.raises(ComparisonViolationError):
            self.filter.validate_aggregate_message(
                "Sarah, John, and Mary practiced /frame this week",
                ["Sarah", "John", "Mary"]
            )

    def test_aggregate_completed_with_names_fails(self):
        """`completed` + names = implicit comparison"""
        with pytest.raises(ComparisonViolationError):
            self.filter.validate_aggregate_message(
                "Alex and Sam completed their reflections",
                ["Alex", "Sam"]
            )


class TestCrisisDetection:
    """Task 2.3: Crisis keyword detection (Level 4 intervention)"""

    def setup_method(self):
        self.filter = SafetyFilter()

    def test_detects_suicide_keyword(self):
        """`suicide` triggers crisis detection"""
        assert self.filter.detect_crisis("I'm thinking about suicide") == "mental_health_crisis"

    def test_detects_self_harm_keyword(self):
        """`self-harm` triggers crisis detection"""
        assert self.filter.detect_crisis("I want to self-harm") == "mental_health_crisis"

    def test_detects_want_to_die_phrase(self):
        """`want to die` triggers crisis detection"""
        assert self.filter.detect_crisis("I want to die") == "mental_health_crisis"

    def test_detects_cant_go_on_phrase(self):
        """`can't go on` triggers crisis detection"""
        assert self.filter.detect_crisis("I can't go on anymore") == "mental_health_crisis"

    def test_detects_hopeless_keyword(self):
        """`hopeless` triggers crisis detection"""
        assert self.filter.detect_crisis("I feel hopeless and worthless") == "mental_health_crisis"

    def test_detects_end_it_all_phrase(self):
        """`end it all` triggers crisis detection"""
        assert self.filter.detect_crisis("I want to end it all") == "mental_health_crisis"

    def test_no_crisis_in_normal_message(self):
        """Normal messages return None (no crisis)"""
        assert self.filter.detect_crisis("I'm stuck on my homework") is None

    def test_no_crisis_in_frustration_message(self):
        """Frustration without crisis keywords returns None"""
        assert self.filter.detect_crisis("This is so hard, I don't know what to do") is None

    def test_case_insensitive_crisis_detection(self):
        """Crisis detection is case insensitive"""
        assert self.filter.detect_crisis("I feel HOPELESS") == "mental_health_crisis"
        assert self.filter.detect_crisis("I WANT TO DIE") == "mental_health_crisis"

    def test_crisis_detection_with_whitespace_variations(self):
        """Detects crisis keywords with different spacing"""
        assert self.filter.detect_crisis("I can't  go   on") == "mental_health_crisis"
        assert self.filter.detect_crisis("self harm") == "mental_health_crisis"


class TestShowcaseContentValidation:
    """Task 2.3: Showcase content validation (blocks unfinished work)"""

    def setup_method(self):
        self.filter = SafetyFilter()

    def test_blocks_still_working_on(self):
        """`still working on` indicates unfinished work"""
        with pytest.raises(ComparisonViolationError) as exc_info:
            self.filter.validate_showcase_content("I'm still working on my artifact")
        assert "finished work only" in str(exc_info.value)

    def test_blocks_draft(self):
        """`draft` indicates unfinished work"""
        with pytest.raises(ComparisonViolationError) as exc_info:
            self.filter.validate_showcase_content("Here's my draft artifact")
        assert "finished work only" in str(exc_info.value)

    def test_blocks_work_in_progress(self):
        """`work in progress` indicates unfinished work"""
        with pytest.raises(ComparisonViolationError) as exc_info:
            self.filter.validate_showcase_content("Work in progress: my thinking process")
        assert "finished work only" in str(exc_info.value)

    def test_blocks_not_finished(self):
        """`not finished` indicates unfinished work"""
        with pytest.raises(ComparisonViolationError) as exc_info:
            self.filter.validate_showcase_content("This artifact is not finished yet")
        assert "finished work only" in str(exc_info.value)

    def test_allows_complete_artifact(self):
        """Polished, complete artifacts pass validation"""
        assert self.filter.validate_showcase_content(
            "Here's my complete artifact on how I used AI to explore university options"
        ) is True

    def test_allows_finished_work(self):
        """Messages indicating completion pass"""
        assert self.filter.validate_showcase_content(
            "I'm excited to share my finished thinking process"
        ) is True

    def test_allows_reflection_on_learning(self):
        """Reflection messages pass"""
        assert self.filter.validate_showcase_content(
            "This artifact shows how I grew from feeling anxious to confident"
        ) is True

    def test_case_insensitive_showcase_validation(self):
        """Showcase validation is case insensitive"""
        with pytest.raises(ComparisonViolationError):
            self.filter.validate_showcase_content("Here's my DRAFT artifact")


class TestKenyaCrisisResponse:
    """Task 2.3: Kenya crisis response message"""

    def setup_method(self):
        self.filter = SafetyFilter()

    def test_crisis_response_contains_hotline(self):
        """Crisis response includes Kenya Crisis Hotline: 119"""
        assert "119" in self.filter.KENYA_CRISIS_RESPONSE
        assert "free" in self.filter.KENYA_CRISIS_RESPONSE.lower()

    def test_crisis_response_contains_trevor_contact(self):
        """Crisis response includes Trevor's contact"""
        assert "0116 405604" in self.filter.KENYA_CRISIS_RESPONSE
        assert "Trevor" in self.filter.KENYA_CRISIS_RESPONSE

    def test_crisis_response_contains_emergency(self):
        """Crisis response includes emergency instructions"""
        assert "999" in self.filter.KENYA_CRISIS_RESPONSE or "hospital" in self.filter.KENYA_CRISIS_RESPONSE

    def test_crisis_response_is_empathetic(self):
        """Crisis response is supportive and empathetic"""
        assert "matter" in self.filter.KENYA_CRISIS_RESPONSE.lower()
        assert "not alone" in self.filter.KENYA_CRISIS_RESPONSE.lower()

    def test_crisis_response_mentions_1_hour_response(self):
        """Crisis response promises Trevor response within 1 hour"""
        assert "1 hour" in self.filter.KENYA_CRISIS_RESPONSE or "1hour" in self.filter.KENYA_CRISIS_RESPONSE


class TestTrevorSafetyAlerts:
    """Task 2.3 regression tests for Trevor safety escalation payloads."""

    @pytest.mark.asyncio
    async def test_crisis_alert_includes_context_payload(self, monkeypatch):
        monkeypatch.setenv("FACILITATOR_DISCORD_ID", "999888777")

        trevor_user = Mock()
        trevor_user.send = AsyncMock()

        bot = Mock()
        bot.fetch_user = AsyncMock(return_value=trevor_user)

        with patch(
            "cis_controller.safety_filter._load_crisis_context",
            return_value={
                "emotional_state": "stuck",
                "last_messages": [
                    "user: I feel overwhelmed",
                    "assistant: Let's pause and breathe",
                    "user: I can't go on",
                ],
            },
        ), patch(
            "cis_controller.safety_filter._log_to_moderation_logs",
            new_callable=AsyncMock,
        ) as mock_log:
            await notify_trevor_safety_violation(
                bot=bot,
                violation_type="crisis",
                message="I can't go on",
                student_discord_id=123456,
            )

        bot.fetch_user.assert_awaited_once_with(999888777)
        trevor_user.send.assert_awaited_once()
        sent_alert = trevor_user.send.await_args.args[0]
        assert "Last 3 messages" in sent_alert
        assert "stuck" in sent_alert
        mock_log.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_comparison_alert_logs_to_moderation(self, monkeypatch):
        monkeypatch.setenv("FACILITATOR_DISCORD_ID", "999888777")

        trevor_user = Mock()
        trevor_user.send = AsyncMock()

        bot = Mock()
        bot.fetch_user = AsyncMock(return_value=trevor_user)

        with patch(
            "cis_controller.safety_filter._log_to_moderation_logs",
            new_callable=AsyncMock,
        ) as mock_log:
            await notify_trevor_safety_violation(
                bot=bot,
                violation_type="comparison",
                message="Top student this week...",
                student_discord_id=123456,
            )

        trevor_user.send.assert_awaited_once()
        mock_log.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_crisis_falls_back_to_db_logging_when_escalation_system_fails(
        self,
        monkeypatch,
        tmp_path,
    ):
        from database.store import StudentStateStore

        db_path = tmp_path / "safety_crisis_fallback.db"
        bootstrap_store = StudentStateStore(str(db_path))
        bootstrap_store.create_student("123456")
        bootstrap_store.close()

        monkeypatch.setenv("DATABASE_PATH", str(db_path))
        monkeypatch.setenv("FACILITATOR_DISCORD_ID", "999888777")

        trevor_user = Mock()
        trevor_user.send = AsyncMock()

        bot = Mock()
        bot.fetch_user = AsyncMock(return_value=trevor_user)
        bot.guilds = []

        escalation_system = Mock()
        escalation_system.escalate_level_4_crisis = AsyncMock(
            side_effect=RuntimeError("forced escalation failure")
        )

        with patch(
            "cis_controller.safety_filter._load_crisis_context",
            return_value={
                "emotional_state": "stuck",
                "last_messages": ["user: I can't go on"],
            },
        ), patch(
            "cis_controller.safety_filter._log_to_moderation_logs",
            new_callable=AsyncMock,
        ):
            await notify_trevor_safety_violation(
                bot=bot,
                violation_type="crisis",
                message="I can't go on",
                student_discord_id=123456,
                escalation_system=escalation_system,
            )

        escalation_system.escalate_level_4_crisis.assert_awaited_once()

        verify_store = StudentStateStore(str(db_path))
        level4_count = verify_store.conn.execute(
            """
            SELECT COUNT(*) AS c
            FROM escalations
            WHERE discord_id = ? AND escalation_level = 4
            """,
            ("123456",),
        ).fetchone()["c"]
        verify_store.close()

        assert level4_count >= 1
