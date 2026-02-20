"""
Daily Prompt Library Loader
Story 2.1 Implementation: Daily Prompt Scheduling

Loads and parses the daily-prompt-library.md file for automated posting.
"""

from dataclasses import dataclass
from enum import Enum
import os
from pathlib import Path
from typing import List, Optional
import re


class WeekDay(Enum):
    """Days of the week for scheduling"""

    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5


@dataclass
class DailyPrompt:
    """Single daily prompt data structure"""

    week: int
    day: WeekDay
    title: str
    emoji: str
    context: str
    task: str
    habit_practice: str
    habit_emoji: str
    closing: str
    has_peer_visibility: bool = False

    def format_for_discord(self) -> str:
        """Format prompt for Discord posting"""
        message = f"{self.emoji} **TODAY'S PRACTICE:** {self.title}\n\n"
        message += f"{self.context}\n\n"
        message += f"**Task:**\n{self.task}\n\n"
        message += f"{self.habit_emoji} **HABIT PRACTICE:** {self.habit_practice}\n\n"
        message += f"{self.closing}"

        if self.has_peer_visibility:
            message += (
                "\n\n**Peer Visibility Moment:** Agent will aggregate anonymized responses "
                "in evening message."
            )

        return message


class DailyPromptLibrary:
    """Loads and manages the daily prompt library"""

    HEADER_PATTERN = re.compile(
        r"^#### \*\*(Monday|Tuesday|Wednesday|Thursday|Friday) \(Week (\d+)\): (.+)\*\*$",
        re.MULTILINE,
    )
    KNOWN_EMOJIS = ("🎯", "⏸️", "🔄", "🧠", "🌟")

    def __init__(self, library_path: Optional[str] = None):
        """
        Initialize the prompt library.

        Args:
            library_path: Path to daily-prompt-library.md. If None, uses default.
        """
        if library_path is None:
            env_override = os.getenv("DAILY_PROMPT_LIBRARY_PATH", "").strip()
            if env_override:
                library_path = env_override
            else:
                project_root = Path(__file__).resolve().parent.parent.parent
                candidate_paths = [
                    project_root
                    / "_bmad-output"
                    / "cohort-design-artifacts"
                    / "playbook-v2"
                    / "03-sessions"
                    / "daily-prompt-library.md",
                    Path(__file__).resolve().parent / "daily-prompt-library.md",
                ]
                library_path = next(
                    (path for path in candidate_paths if path.exists()),
                    candidate_paths[0],
                )

        self.library_path = Path(library_path)
        self.prompts: dict[tuple[int, WeekDay], DailyPrompt] = {}
        self._load_library()

    def _load_library(self):
        """Parse the daily prompt library markdown file."""
        if not self.library_path.exists():
            raise FileNotFoundError(f"Daily prompt library not found: {self.library_path}")

        with open(self.library_path, "r", encoding="utf-8") as f:
            content = f.read()

        matches = list(self.HEADER_PATTERN.finditer(content))
        for idx, match in enumerate(matches):
            day_name, week_str, title = match.groups()
            week = int(week_str)
            day = WeekDay[day_name.upper()]

            start = match.end()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
            block = content[start:end]

            parsed = self._parse_prompt_block(title, block)
            self.prompts[(week, day)] = DailyPrompt(
                week=week,
                day=day,
                title=title,
                emoji=parsed["emoji"],
                context=parsed["context"],
                task=parsed["task"],
                habit_practice=parsed["habit_practice"],
                habit_emoji=parsed["habit_emoji"],
                closing=parsed["closing"],
                has_peer_visibility=parsed["has_peer_visibility"],
            )

    def _parse_prompt_block(self, title: str, block: str) -> dict:
        """Parse one markdown block under a prompt header."""
        lines = [line.strip() for line in block.splitlines() if line.strip()]

        emoji = self._extract_emoji(title) or "🎯"
        for line in lines:
            found = self._extract_emoji(line)
            if found:
                emoji = found
                break

        task_start = self._find_first_index(
            lines, lambda line: line.startswith("**Task:**") or line.startswith("**OPTION")
        )

        context_lines: List[str] = []
        search_until = task_start if task_start is not None else len(lines)
        for line in lines[:search_until]:
            if "TODAY'S PRACTICE" in line:
                continue
            if line.startswith(("####", "---", "**")):
                continue
            if "HABIT PRACTICE:" in line or "HABIT CHECK:" in line:
                continue
            context_lines.append(line)
        context = " ".join(context_lines).strip()

        task_lines: List[str] = []
        if task_start is not None:
            for line in lines[task_start + 1 :]:
                if line.startswith(("####", "---", "**Peer Visibility Moment:**")):
                    break
                if self._is_habit_line(line):
                    break
                task_lines.append(line)
        task = "\n".join(task_lines).strip()

        habit_line = next(
            (line for line in lines if self._is_habit_line(line)),
            "",
        )
        habit_emoji = self._extract_emoji(habit_line) or "⏸️"
        if ":" in habit_line:
            habit_practice = habit_line.split(":", 1)[1].strip()
        else:
            habit_practice = ""

        closing = ""
        habit_idx = self._find_first_index(lines, self._is_habit_line)
        if habit_idx is not None:
            for line in lines[habit_idx + 1 :]:
                if line.startswith(("####", "---", "**Peer Visibility Moment:**")):
                    break
                if line.startswith(("**Task:**", "**OPTION")):
                    continue
                closing = line
                break

        has_peer_visibility = any(
            line.startswith("**Peer Visibility Moment:**") for line in lines
        )

        return {
            "emoji": emoji,
            "context": context,
            "task": task,
            "habit_practice": habit_practice,
            "habit_emoji": habit_emoji,
            "closing": closing,
            "has_peer_visibility": has_peer_visibility,
        }

    def _extract_emoji(self, text: str) -> Optional[str]:
        """Return first known emoji from text."""
        for emoji in self.KNOWN_EMOJIS:
            if emoji in text:
                return emoji
        return None

    def _find_first_index(self, lines: List[str], predicate) -> Optional[int]:
        """Return first index that matches predicate."""
        for i, line in enumerate(lines):
            if predicate(line):
                return i
        return None

    def _is_habit_line(self, line: str) -> bool:
        """Detect habit lines like `HABIT PRACTICE:` or `HABIT 1 PRACTICE:`."""
        return bool(re.search(r"HABIT(?:\s+\d+)?\s+(PRACTICE|CHECK):", line))

    def get_prompt(self, week: int, day: WeekDay) -> Optional[DailyPrompt]:
        """
        Get a specific prompt by week and day.

        Args:
            week: Week number (1-8)
            day: Day of week

        Returns:
            DailyPrompt if found, None otherwise
        """
        return self.prompts.get((week, day))

    def get_week_prompts(self, week: int) -> List[DailyPrompt]:
        """
        Get all prompts for a specific week.

        Args:
            week: Week number (1-8)

        Returns:
            List of DailyPrompt objects for the week
        """
        return [self.prompts[(week, day)] for day in WeekDay if (week, day) in self.prompts]

    def get_all_prompts(self) -> List[DailyPrompt]:
        """Get all prompts in the library"""
        return list(self.prompts.values())
