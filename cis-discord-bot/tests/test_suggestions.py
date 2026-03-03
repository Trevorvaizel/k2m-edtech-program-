"""
Tests for CIS Controller Suggestions System
Story 4.7 Implementation

Tests natural language classification, graduated intensity system,
and "Did you mean...?" suggestion UX (Story 4.1).
"""

import sys
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cis_controller.suggestions import (
    classify_intent,
    get_suggestion_template,
    INTENT_KEYWORDS,
    SUGGESTION_TEMPLATES,
    suggest_explicit_command,
)


class TestClassifyIntent:
    """Test natural language intent classification"""

    def test_classify_frame_keywords(self):
        """Messages with 'help', 'confused', 'question' classify as /frame"""
        messages = [
            "I need help with my question",
            "I'm confused about what to ask",
            "Can you help me understand?",
            "I'm not sure how to phrase this",
            "What should I do?"
        ]
        for msg in messages:
            result = classify_intent(msg)
            assert result == "frame", f"Message '{msg}' should classify as 'frame', got '{result}'"

    def test_classify_diverge_keywords(self):
        """Messages with 'explore', 'options', 'possibilities' classify as /diverge"""
        messages = [
            "I want to explore different options",
            "What are the possibilities?",
            "Could I try various approaches?",
            "What if I considered alternatives?"
        ]
        for msg in messages:
            result = classify_intent(msg)
            assert result == "diverge", f"Message '{msg}' should classify as 'diverge', got '{result}'"

    def test_classify_challenge_keywords(self):
        """Messages with 'assume', 'test', 'doubt' classify as /challenge"""
        messages = [
            "I want to challenge my assumption",
            "Can we test this idea?",
            "I doubt this is really true",
            "What am I taking for granted?"
        ]
        for msg in messages:
            result = classify_intent(msg)
            assert result == "challenge", f"Message '{msg}' should classify as 'challenge', got '{result}'"

    def test_classify_synthesize_keywords(self):
        """Messages with 'conclude', 'summary', 'wrap up' classify as /synthesize"""
        messages = [
            "I want to conclude my thinking",
            "Can you help me summarize?",
            "Let's wrap this up",
            "What's the main takeaway?"
        ]
        for msg in messages:
            result = classify_intent(msg)
            assert result == "synthesize", f"Message '{msg}' should classify as 'synthesize', got '{result}'"

    def test_no_match_returns_none(self):
        """Messages without keywords return None"""
        messages = [
            "Hello there",
            "I like pizza",
            "The weather is nice",
            ""
        ]
        for msg in messages:
            result = classify_intent(msg)
            assert result is None, f"Message '{msg}' should return None, got '{result}'"

    def test_case_insensitive_classification(self):
        """Classification should be case-insensitive"""
        assert classify_intent("I need HELP") == "frame"
        assert classify_intent("I want to EXPLORE") == "diverge"
        assert classify_intent("Can I CHALLENGE this?") == "challenge"

    def test_scores_multiple_keywords(self):
        """Messages with multiple matching keywords should score higher"""
        # Frame with 3 keywords
        result1 = classify_intent("I need help understanding my question")
        assert result1 == "frame"

        # Diverge with 2 keywords
        result2 = classify_intent("I want to explore different options")
        assert result2 == "diverge"


class TestGetSuggestionTemplate:
    """Test graduated intensity templates (Story 4.1)"""

    def test_week_1_frame_template_exists(self):
        """Week 1-2 frame template should be explicit"""
        template = get_suggestion_template(1, "frame")
        assert template is not None
        assert "🎯" in template
        assert "/frame" in template

    def test_week_1_diverge_template_exists(self):
        """Week 1-2 diverge template should be explicit"""
        template = get_suggestion_template(1, "diverge")
        assert template is not None
        assert "/diverge" in template

    def test_week_4_gentle_intensity(self):
        """Week 4-5 should use gentle intensity templates"""
        template = get_suggestion_template(4, "frame")
        assert template is not None
        assert "Have you" in template or "Ready" in template  # Gentle phrasing

    def test_week_6_minimal_intensity(self):
        """Week 6-7 should use minimal intensity templates"""
        template = get_suggestion_template(6, "frame")
        assert template is not None
        # Minimal templates are shorter
        assert len(template) < 100

    def test_week_8_no_suggestions(self):
        """Week 8 should return None (no suggestions)"""
        template = get_suggestion_template(8, "frame")
        assert template is None

        template = get_suggestion_template(8, "diverge")
        assert template is None

    def test_all_commands_have_week_1_templates(self):
        """All 4 commands should have explicit templates for Week 1"""
        for cmd in ["frame", "diverge", "challenge", "synthesize"]:
            template = get_suggestion_template(1, cmd)
            assert template is not None, f"Week 1 template for '{cmd}' should exist"
            assert f"/{cmd}" in template, f"Week 1 template for '{cmd}' should mention the command"

    def test_all_commands_have_week_4_templates(self):
        """All 4 commands should have gentle templates for Week 4"""
        for cmd in ["frame", "diverge", "challenge", "synthesize"]:
            template = get_suggestion_template(4, cmd)
            assert template is not None, f"Week 4 template for '{cmd}' should exist"

    def test_all_commands_have_week_6_templates(self):
        """All 4 commands should have minimal templates for Week 6"""
        for cmd in ["frame", "diverge", "challenge", "synthesize"]:
            template = get_suggestion_template(6, cmd)
            assert template is not None, f"Week 6 template for '{cmd}' should exist"


class TestIntentKeywords:
    """Verify intent keyword dictionaries are complete"""

    def test_frame_keywords_defined(self):
        """Frame keywords should cover confusion/help themes"""
        keywords = INTENT_KEYWORDS["frame"]
        assert len(keywords) >= 10
        assert "help" in keywords
        assert "confused" in keywords
        assert "question" in keywords

    def test_diverge_keywords_defined(self):
        """Diverge keywords should cover exploration themes"""
        keywords = INTENT_KEYWORDS["diverge"]
        assert len(keywords) >= 10
        assert "explore" in keywords
        assert "options" in keywords
        assert "possibilities" in keywords

    def test_challenge_keywords_defined(self):
        """Challenge keywords should cover critical thinking themes"""
        keywords = INTENT_KEYWORDS["challenge"]
        assert len(keywords) >= 10
        assert "assume" in keywords
        assert "test" in keywords
        assert "doubt" in keywords

    def test_synthesize_keywords_defined(self):
        """Synthesize keywords should cover conclusion themes"""
        keywords = INTENT_KEYWORDS["synthesize"]
        assert len(keywords) >= 10
        assert "conclude" in keywords
        assert "summary" in keywords
        assert "wrap up" in keywords


class TestSuggestionTemplates:
    """Verify suggestion template structure"""

    def test_week_1_2_section_exists(self):
        """Week 1-2 section must exist with explicit intensity"""
        assert "week_1_2" in SUGGESTION_TEMPLATES
        section = SUGGESTION_TEMPLATES["week_1_2"]
        assert section["intensity"] == "explicit"

    def test_week_4_5_section_exists(self):
        """Week 4-5 section must exist with gentle intensity"""
        assert "week_4_5" in SUGGESTION_TEMPLATES
        section = SUGGESTION_TEMPLATES["week_4_5"]
        assert section["intensity"] == "gentle"

    def test_week_6_7_section_exists(self):
        """Week 6-7 section must exist with minimal intensity"""
        assert "week_6_7" in SUGGESTION_TEMPLATES
        section = SUGGESTION_TEMPLATES["week_6_7"]
        assert section["intensity"] == "minimal"

    def test_week_8_section_exists(self):
        """Week 8 section must exist with none intensity"""
        assert "week_8" in SUGGESTION_TEMPLATES
        section = SUGGESTION_TEMPLATES["week_8"]
        assert section["intensity"] == "none"

    def test_all_sections_have_four_commands(self):
        """Each section should have templates for all 4 commands"""
        for section_name in ["week_1_2", "week_4_5", "week_6_7"]:
            section = SUGGESTION_TEMPLATES[section_name]
            for cmd in ["frame", "diverge", "challenge", "synthesize"]:
                assert cmd in section, f"Section '{section_name}' missing '{cmd}' template"


class TestGraduatedIntensityProgression:
    """Test that intensity decreases appropriately from Week 1 to Week 8"""

    def test_week_1_more_verbose_than_week_4(self):
        """Week 1 templates should be more verbose than Week 4"""
        week1_frame = get_suggestion_template(1, "frame")
        week4_frame = get_suggestion_template(4, "frame")

        assert len(week1_frame) > len(week4_frame), \
            "Week 1 should be more explicit (longer) than Week 4"

    def test_week_4_more_verbose_than_week_6(self):
        """Week 4 templates should be more verbose than Week 6"""
        week4_frame = get_suggestion_template(4, "frame")
        week6_frame = get_suggestion_template(6, "frame")

        assert len(week4_frame) > len(week6_frame), \
            "Week 4 should be more verbose than Week 6"

    def test_week_8_shortest(self):
        """Week 8 templates should be None (shortest possible)"""
        week8_frame = get_suggestion_template(8, "frame")
        assert week8_frame is None, "Week 8 should have no suggestions"


class TestSuggestionObservabilityPrivacy:
    """Observability metadata should not store raw student message content."""

    @pytest.mark.asyncio
    async def test_suggestion_logging_omits_raw_message_content(self):
        message = SimpleNamespace(
            content="I need help framing my question",
            author=SimpleNamespace(id=123456789),
            reply=AsyncMock(),
        )
        student = {"current_week": 1}

        with patch("cis_controller.suggestions.store") as mock_store, patch(
            "cis_controller.suggestions.is_agent_unlocked", return_value=True
        ):
            await suggest_explicit_command(message, student)

        mock_store.log_observability_event.assert_called_once()
        _, _, metadata = mock_store.log_observability_event.call_args[0]
        assert "original_message" not in metadata
        assert metadata["message_length"] == len(message.content)
