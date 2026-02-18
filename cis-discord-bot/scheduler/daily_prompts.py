"""
Daily Prompt Library Loader
Story 2.1 Implementation: Daily Prompt Scheduling

Loads and parses the daily-prompt-library.md file for automated posting.
"""

import os
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional


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
        message = f"{self.emoji} **TODAY'S PRACTICE: {self.title}**\n\n"
        message += f"{self.context}\n\n"
        message += f"**Task:**\n{self.task}\n\n"
        message += f"{self.habit_emoji} **HABIT PRACTICE:** {self.habit_practice}\n\n"
        message += f"{self.closing}"

        # Add peer visibility note if applicable
        if self.has_peer_visibility:
            message += "\n\n**Peer Visibility Moment:** Agent will aggregate anonymized responses in evening message."

        return message


class DailyPromptLibrary:
    """Loads and manages the daily prompt library"""

    def __init__(self, library_path: Optional[str] = None):
        """
        Initialize the prompt library.

        Args:
            library_path: Path to daily-prompt-library.md. If None, uses default.
        """
        if library_path is None:
            # Default path relative to project root
            project_root = Path(__file__).resolve().parent.parent.parent
            library_path = project_root / "_bmad-output" / "cohort-design-artifacts" / "playbook-v2" / "03-sessions" / "daily-prompt-library.md"

        self.library_path = Path(library_path)
        self.prompts: dict[tuple[int, WeekDay], DailyPrompt] = {}
        self._load_library()

    def _load_library(self):
        """Parse the daily prompt library markdown file"""
        if not self.library_path.exists():
            raise FileNotFoundError(f"Daily prompt library not found: {self.library_path}")

        with open(self.library_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse prompts using regex
        # Pattern matches: #### **{Day} (Week {N}): {Title}**
        prompt_pattern = r'#### \*\*(Monday|Tuesday|Wednesday|Thursday|Friday) \(Week (\d+)\): (.+)\*\*'

        current_week = None
        current_day = None
        current_title = None
        sections = {}

        lines = content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Match prompt header
            header_match = re.match(prompt_pattern, line)
            if header_match:
                day_name, week_str, title = header_match.groups()
                current_week = int(week_str)
                current_day = WeekDay[day_name.upper()]
                current_title = title

                # Extract emoji from title if present
                emoji_match = re.search(r'([🎯⏸️🔄🧠🌟])', title)
                emoji = emoji_match.group(1) if emoji_match else "🎯"

                # Initialize prompt sections
                sections = {
                    'emoji': emoji,
                    'context': '',
                    'task': '',
                    'habit_practice': '',
                    'habit_emoji': '',
                    'closing': ''
                }

                # Look for peer visibility note
                has_peer_visibility = False

                # Parse sections until next prompt or end
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()

                    # Check if we hit another prompt
                    if re.match(prompt_pattern, next_line):
                        break

                    # Check for key section markers
                    if next_line.startswith('🎯 TODAY\'S PRACTICE:') or \
                       next_line.startswith('⏸️→🎯 PRACTICE:') or \
                       next_line.startswith('🔄 TODAY\'S PRACTICE:') or \
                       next_line.startswith('🧠 TODAY\'S PRACTICE:'):
                        # Skip, this is the title we already captured
                        pass

                    elif 'HABIT PRACTICE:' in next_line or 'HABIT CHECK:' in next_line:
                        # Extract habit emoji and practice
                        habit_match = re.search(r'([⏸️🎯🔄🧠]+)(?:→| )?HABIT (?:\d+ )?PRACTICE|CHECK:', next_line)
                        if habit_match:
                            sections['habit_emoji'] = habit_match.group(1)

                        # Extract practice text (may span multiple lines)
                        i += 1
                        practice_lines = []
                        while i < len(lines) and not lines[i].strip().startswith(('**', '⏸️', '🎯', '🔄', '🧠', '**Peer')):
                            practice_lines.append(lines[i].strip())
                            i += 1
                        sections['habit_practice'] = ' '.join(practice_lines).strip()
                        i -= 1  # Back up one line

                    elif '**Task:**' in next_line or '**OPTION A:**' in next_line:
                        # Extract task content (may span multiple lines)
                        i += 1
                        task_lines = []
                        while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(('⏸️', '🎯', '🔄', '🧠', '**Peer', '**Note')):
                            task_lines.append(lines[i].strip())
                            i += 1
                        sections['task'] = '\n'.join(task_lines).strip()
                        i -= 1  # Back up one line

                    elif next_line.startswith('**Peer Visibility Moment:**'):
                        has_peer_visibility = True

                    elif not next_line.startswith(('####', '---', '**Task:', '**OPTION')):
                        # Context or closing content
                        if not sections['context']:
                            # First paragraph is context
                            context_lines = []
                            while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(('**Task', '**OPTION', '⏸️', '🎯')):
                                context_lines.append(lines[i].strip())
                                i += 1
                            sections['context'] = ' '.join(context_lines).strip()
                            i -= 1
                        elif not sections['closing']:
                            # Last paragraph before next header is closing
                            if lines[i].strip() and not lines[i].startswith(('####', '---')):
                                sections['closing'] = lines[i].strip()

                    i += 1

                # Create the prompt object
                prompt = DailyPrompt(
                    week=current_week,
                    day=current_day,
                    title=current_title,
                    emoji=sections['emoji'],
                    context=sections['context'],
                    task=sections['task'],
                    habit_practice=sections['habit_practice'],
                    habit_emoji=sections['habit_emoji'],
                    closing=sections['closing'],
                    has_peer_visibility=has_peer_visibility
                )

                self.prompts[(current_week, current_day)] = prompt
                continue

            i += 1

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
        return [
            self.prompts[(week, day)]
            for day in WeekDay
            if (week, day) in self.prompts
        ]

    def get_all_prompts(self) -> List[DailyPrompt]:
        """Get all prompts in the library"""
        return list(self.prompts.values())
