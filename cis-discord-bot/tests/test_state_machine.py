"""
Tests for CIS Controller State Machine
Story 4.7 Implementation

Tests student state management, valid state constants,
state transitions, and habit celebration stubs.
"""

import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cis_controller.state_machine import (
    celebrate_habit,
    get_student_state,
    transition_state,
    is_valid_state,
    STATE_NONE, STATE_FRAMING, STATE_EXPLORING,
    STATE_CHALLENGING, STATE_SYNTHESIZING, STATE_COMPLETE,
    VALID_STATES,
    HABIT_NAMES,
)


class TestStateConstants:
    """Verify all required state constants are defined per spec"""

    def test_state_none_value(self):
        assert STATE_NONE == 'none'

    def test_state_framing_value(self):
        assert STATE_FRAMING == 'framing'

    def test_state_exploring_value(self):
        assert STATE_EXPLORING == 'exploring'

    def test_state_challenging_value(self):
        assert STATE_CHALLENGING == 'challenging'

    def test_state_synthesizing_value(self):
        assert STATE_SYNTHESIZING == 'synthesizing'

    def test_state_complete_value(self):
        assert STATE_COMPLETE == 'complete'

    def test_valid_states_contains_all_six(self):
        """VALID_STATES must contain exactly all 6 states"""
        assert len(VALID_STATES) == 6

    def test_all_constants_in_valid_states(self):
        for state in [STATE_NONE, STATE_FRAMING, STATE_EXPLORING,
                      STATE_CHALLENGING, STATE_SYNTHESIZING, STATE_COMPLETE]:
            assert state in VALID_STATES


class TestHabitNames:
    """Verify habit name and icon constants match spec (Story 1.4)"""

    def test_habit_1_name(self):
        assert HABIT_NAMES[1][0] == "PAUSE"
        assert HABIT_NAMES[1][1] == "⏸️"

    def test_habit_2_name(self):
        assert HABIT_NAMES[2][0] == "CONTEXT"
        assert HABIT_NAMES[2][1] == "🎯"

    def test_habit_3_name(self):
        assert HABIT_NAMES[3][0] == "ITERATE"
        assert HABIT_NAMES[3][1] == "🔄"

    def test_habit_4_name(self):
        assert HABIT_NAMES[4][0] == "THINK FIRST"
        assert HABIT_NAMES[4][1] == "🧠"


class TestIsValidState:
    """Test state validation function"""

    def test_all_valid_states_accepted(self):
        for state in ['none', 'framing', 'exploring', 'challenging', 'synthesizing', 'complete']:
            assert is_valid_state(state) is True

    def test_invalid_string_rejected(self):
        assert is_valid_state('invalid') is False

    def test_empty_string_rejected(self):
        assert is_valid_state('') is False

    def test_whitespace_rejected(self):
        assert is_valid_state(' ') is False

    def test_partial_state_rejected(self):
        assert is_valid_state('fram') is False


class TestTransitionState:
    """Test command → state transitions"""

    def test_frame_transitions_to_framing(self):
        result = transition_state(STATE_NONE, 'frame')
        assert result == STATE_FRAMING

    def test_diverge_transitions_to_exploring(self):
        result = transition_state(STATE_FRAMING, 'diverge')
        assert result == STATE_EXPLORING

    def test_challenge_transitions_to_challenging(self):
        result = transition_state(STATE_EXPLORING, 'challenge')
        assert result == STATE_CHALLENGING

    def test_synthesize_transitions_to_synthesizing(self):
        result = transition_state(STATE_CHALLENGING, 'synthesize')
        assert result == STATE_SYNTHESIZING

    def test_unknown_command_preserves_current_state(self):
        assert transition_state(STATE_FRAMING, 'unknown') == STATE_FRAMING

    def test_unknown_command_from_none_preserves_none(self):
        assert transition_state(STATE_NONE, 'unknown') == STATE_NONE


class TestCelebrateHabit:
    """Test habit celebration (stub until Task 1.3)"""

    def test_returns_none_for_habit_1(self):
        assert celebrate_habit(None, 1) is None

    def test_returns_none_for_habit_2(self):
        assert celebrate_habit(None, 2) is None

    def test_returns_none_for_habit_3(self):
        assert celebrate_habit(None, 3) is None

    def test_returns_none_for_habit_4(self):
        assert celebrate_habit(None, 4) is None

    def test_invalid_habit_id_returns_none(self):
        """Invalid habit IDs don't raise errors"""
        assert celebrate_habit(None, 99) is None
        assert celebrate_habit(None, 0) is None
        assert celebrate_habit(None, -1) is None

    def test_returns_none_or_string(self):
        """Return type is always None or str (never other types)"""
        result = celebrate_habit(None, 1)
        assert result is None or isinstance(result, str)

    def test_milestone_logging_uses_consistent_metadata_keys(self):
        mock_store = Mock()
        mock_store.get_habit_journey.return_value = [{"habit_id": 1, "practiced_count": 3}]

        with patch("cis_controller.state_machine.store", mock_store):
            message = celebrate_habit({"discord_id": "123456789"}, 1)

        assert isinstance(message, str)
        mock_store.log_observability_event.assert_called_once()
        _, event_type, payload = mock_store.log_observability_event.call_args[0]
        assert event_type == "milestone_reached"
        assert payload["milestone"] == 3
        assert payload["practiced_count"] == 3


class TestGetStudentState:
    """Test get_student_state with edge cases"""

    def test_none_student_returns_state_none(self):
        assert get_student_state(None) == STATE_NONE

    def test_returns_valid_state_constant(self):
        result = get_student_state(None)
        assert result in VALID_STATES
