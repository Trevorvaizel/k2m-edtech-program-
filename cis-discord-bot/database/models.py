"""
Database Models - StudentContext ORM
Story 4.7 Implementation: StudentContext & Database Schema

Rich domain model representing a student's complete context.
Passed to CIS agents for personalized, zone-aware responses.
"""

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


# Constants per spec (Story 1.4: 4 Habits)
HABIT_NAMES = {1: "PAUSE", 2: "CONTEXT", 3: "ITERATE", 4: "THINK FIRST"}
HABIT_ICONS = {
    1: ":pause_button:",
    2: ":dart:",
    3: ":repeat:",
    4: ":brain:",
}
HABIT_UNLOCK_WEEK = {1: 1, 2: 1, 3: 4, 4: 4}

# Zone identity labels (Story 1.2: JTBD)
ZONE_LABELS = {
    "zone_0": "outsider",
    "zone_1": "observer",
    "zone_2": "experimenter",
    "zone_3": "collaborator",
    "zone_4": "director",
}


@dataclass
class HabitProgress:
    """Tracks student's progress on one of the 4 Habits."""

    habit_id: int
    name: str
    icon: str
    practiced_count: int = 0
    last_practiced: Optional[datetime] = None
    confidence: str = "emerging"  # emerging, growing, strong
    unlocked: bool = False


@dataclass
class ArtifactProgress:
    """Tracks 6-section artifact creation progress (Story 4.6)."""

    section_1_question: str = ""
    section_2_reframed: str = ""
    section_3_explored: str = ""
    section_4_challenged: str = ""
    section_5_concluded: str = ""
    section_6_reflection: str = ""
    completed_sections: List[str] = field(default_factory=list)
    current_section: int = 0
    status: str = "not_started"  # not_started, in_progress, completed, published
    started_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    def is_complete(self) -> bool:
        """True when all 6 sections have content."""
        return all(
            [
                self.section_1_question,
                self.section_2_reframed,
                self.section_3_explored,
                self.section_4_challenged,
                self.section_5_concluded,
                self.section_6_reflection,
            ]
        )

    def get_next_section(self) -> int:
        """Return index (1-6) of next incomplete section, 0 if all done."""
        sections = [
            self.section_1_question,
            self.section_2_reframed,
            self.section_3_explored,
            self.section_4_challenged,
            self.section_5_concluded,
            self.section_6_reflection,
        ]
        for idx, section in enumerate(sections, start=1):
            if not section:
                return idx
        return 0

    def days_since_activity(self) -> int:
        """Return whole days since last artifact activity."""
        if self.last_activity is None:
            return 999
        delta = datetime.now() - self.last_activity
        return max(delta.days, 0)


@dataclass
class StudentContext:
    """
    Rich domain model representing student's complete context.

    Passed to CIS agents to enable personalized, zone-aware,
    JTBD-aligned responses (Story 4.1).
    """

    # Identity
    discord_id: str
    zone: str
    current_week: int
    cohort_start_date: datetime

    # JTBD (Jobs-to-be-Done, Story 1.2)
    jtbd_primary_concern: str
    emotional_state: str

    # Habits (Story 1.4)
    habit_journey: Dict[int, HabitProgress] = field(default_factory=dict)

    # Artifact (Story 4.6)
    artifact_progress: ArtifactProgress = field(default_factory=ArtifactProgress)

    # State
    current_state: str = "none"
    unlocked_agents: List[str] = field(default_factory=lambda: ["frame"])
    interaction_count: int = 0

    def get_altitude(self) -> str:
        """
        Map week + zone to JTBD altitude level (1-5).
        Controls language complexity of CIS agent responses.
        """
        if self.current_week == 1:
            return "Level 1 - Ground (Concrete/Immediate)"
        if self.current_week <= 3:
            return "Level 2 - Pattern (Observable Truth)"
        if self.current_week <= 5:
            return "Level 3 - Framework (System/Structure)"
        return "Level 4 - Transform (What Becomes Possible)"

    def get_zone_label(self) -> str:
        """Return human-readable zone identity label."""
        return ZONE_LABELS.get(self.zone, "unknown")

    def get_relevant_example(self, agent: str) -> str:
        """
        Pull JTBD-matched example for agent response context.
        NOTE: Example selector implemented in Task 1.3.
        """
        return ""  # Stub until Task 1.3


def _get_value(obj: Any, key: str, default: Any = None) -> Any:
    """Read field from sqlite3.Row, dict, or simple object."""
    if obj is None:
        return default

    if isinstance(obj, dict):
        return obj.get(key, default)

    try:
        return obj[key]
    except (TypeError, KeyError, IndexError):
        return getattr(obj, key, default)


def _parse_datetime(value: Any) -> Optional[datetime]:
    """Parse timestamp-like values to datetime."""
    if value in (None, ""):
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        candidate = value.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(candidate)
        except ValueError:
            return None

    return None


def _infer_zone(current_week: int) -> str:
    """Infer zone from cohort week progression."""
    if current_week == 1:
        return "zone_0"
    if current_week <= 3:
        return "zone_1"
    if current_week <= 5:
        return "zone_2"
    if current_week <= 7:
        return "zone_3"
    return "zone_4"


def _infer_unlocked_agents(current_week: int) -> List[str]:
    """Infer unlocked agents from Decision 11 schedule."""
    unlocked = ["frame"]
    if current_week >= 4:
        unlocked.extend(["diverge", "challenge"])
    if current_week >= 6:
        unlocked.extend(["synthesize", "create-artifact"])
    return unlocked


def _parse_unlocked_agents(raw_value: Any, current_week: int) -> List[str]:
    """Parse unlocked agent list from JSON with safe fallback."""
    if isinstance(raw_value, list):
        return raw_value

    if isinstance(raw_value, str) and raw_value:
        try:
            parsed = json.loads(raw_value)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass

    return _infer_unlocked_agents(current_week)


def _load_habit_journey(
    conn: Optional[sqlite3.Connection],
    discord_id: str,
    current_week: int,
) -> Dict[int, HabitProgress]:
    """Load habit progress rows and map them into the domain model."""
    journey: Dict[int, HabitProgress] = {
        habit_id: HabitProgress(
            habit_id=habit_id,
            name=HABIT_NAMES[habit_id],
            icon=HABIT_ICONS[habit_id],
            practiced_count=0,
            last_practiced=None,
            confidence="emerging",
            unlocked=current_week >= HABIT_UNLOCK_WEEK[habit_id],
        )
        for habit_id in (1, 2, 3, 4)
    }

    if conn is None:
        return journey

    try:
        rows = conn.execute(
            """
            SELECT habit_id, practiced_count, last_practiced, confidence
            FROM habit_practice
            WHERE student_id = ?
            """,
            (discord_id,),
        ).fetchall()
    except sqlite3.Error:
        return journey

    for row in rows:
        habit_id = int(_get_value(row, "habit_id", 0) or 0)
        if habit_id not in journey:
            continue

        journey[habit_id] = HabitProgress(
            habit_id=habit_id,
            name=HABIT_NAMES[habit_id],
            icon=HABIT_ICONS[habit_id],
            practiced_count=int(_get_value(row, "practiced_count", 0) or 0),
            last_practiced=_parse_datetime(_get_value(row, "last_practiced")),
            confidence=_get_value(row, "confidence", "emerging") or "emerging",
            unlocked=current_week >= HABIT_UNLOCK_WEEK[habit_id],
        )

    return journey


def _load_artifact_progress(
    conn: Optional[sqlite3.Connection],
    discord_id: str,
) -> ArtifactProgress:
    """Load artifact progress row into ArtifactProgress model."""
    if conn is None:
        return ArtifactProgress()

    try:
        row = conn.execute(
            "SELECT * FROM artifact_progress WHERE student_id = ?",
            (discord_id,),
        ).fetchone()
    except sqlite3.Error:
        return ArtifactProgress()

    if row is None:
        return ArtifactProgress()

    completed_sections_raw = _get_value(row, "completed_sections", "[]")
    if isinstance(completed_sections_raw, list):
        completed_sections = completed_sections_raw
    else:
        try:
            parsed_sections = json.loads(completed_sections_raw or "[]")
            completed_sections = parsed_sections if isinstance(parsed_sections, list) else []
        except json.JSONDecodeError:
            completed_sections = []

    return ArtifactProgress(
        section_1_question=_get_value(row, "section_1_question", "") or "",
        section_2_reframed=_get_value(row, "section_2_reframed", "") or "",
        section_3_explored=_get_value(row, "section_3_explored", "") or "",
        section_4_challenged=_get_value(row, "section_4_challenged", "") or "",
        section_5_concluded=_get_value(row, "section_5_concluded", "") or "",
        section_6_reflection=_get_value(row, "section_6_reflection", "") or "",
        completed_sections=completed_sections,
        current_section=int(_get_value(row, "current_section", 0) or 0),
        status=_get_value(row, "status", "not_started") or "not_started",
        started_at=_parse_datetime(_get_value(row, "started_at")),
        last_activity=_parse_datetime(_get_value(row, "last_activity")),
        completed_at=_parse_datetime(_get_value(row, "completed_at")),
        published_at=_parse_datetime(_get_value(row, "published_at")),
    )


def build_student_context(
    db_student: Any,
    conn: Optional[sqlite3.Connection] = None,
) -> StudentContext:
    """
    Factory method: create StudentContext from database student row.

    Args:
        db_student: SQLite Row/dict/object from students table
        conn: Optional SQLite connection for loading related data tables

    Returns:
        Populated StudentContext domain model
    """
    if db_student is None:
        raise ValueError("Cannot build StudentContext from None student")

    discord_id = str(_get_value(db_student, "discord_id", ""))
    if not discord_id:
        raise ValueError("Cannot build StudentContext without discord_id")

    raw_week = _get_value(db_student, "current_week", 1)
    try:
        current_week = int(raw_week or 1)
    except (TypeError, ValueError):
        current_week = 1

    zone = _get_value(db_student, "zone") or _infer_zone(current_week)

    cohort_start_date = _parse_datetime(_get_value(db_student, "start_date"))
    if cohort_start_date is None:
        cohort_start_date = datetime.now()

    unlocked_agents = _parse_unlocked_agents(
        _get_value(db_student, "unlocked_agents"),
        current_week,
    )

    habit_journey = _load_habit_journey(conn, discord_id, current_week)
    artifact_progress = _load_artifact_progress(conn, discord_id)

    return StudentContext(
        discord_id=discord_id,
        zone=zone,
        current_week=current_week,
        cohort_start_date=cohort_start_date,
        jtbd_primary_concern=_get_value(db_student, "jtbd_concern", "career_direction") or "career_direction",
        emotional_state=_get_value(db_student, "emotional_state", "curious") or "curious",
        habit_journey=habit_journey,
        artifact_progress=artifact_progress,
        current_state=_get_value(db_student, "current_state", "none") or "none",
        unlocked_agents=unlocked_agents,
        interaction_count=int(_get_value(db_student, "interaction_count", 0) or 0),
    )
