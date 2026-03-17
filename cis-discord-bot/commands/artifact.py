"""
Artifact Command Handler
Story 4.6 Implementation: /create-artifact command

Students use /create-artifact to build their 6-section Thinking Artifact.
Available from Week 6 onwards (Decision 11).
All 4 CIS agents are available during artifact creation.
"""

import logging
import os

import discord
from database import get_runtime_store, get_store
from database.models import ArtifactProgress
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Student-level pending edit state for artifact section rewrites.
# Key: discord_id, Value: section number (1-6).
_PENDING_SECTION_EDITS: Dict[str, int] = {}

_fallback_store = None


def _resolve_store():
    """
    Resolve store lazily to avoid blocking DB initialization during module import.
    Prefer the runtime store initialized in main.py.
    """
    runtime_store = get_runtime_store()
    if runtime_store is not None:
        return runtime_store

    global _fallback_store
    if _fallback_store is None:
        _fallback_store = get_store()
    return _fallback_store


class _StoreProxy:
    def __getattr__(self, item):
        return getattr(_resolve_store(), item)


store = _StoreProxy()


def _read_value(record, key: str, default=None):
    """Read value from sqlite row/dict-like objects with safe fallback."""
    if record is None:
        return default
    if isinstance(record, dict):
        return record.get(key, default)
    try:
        return record[key]
    except Exception:
        return default


def _log_artifact_event(discord_id: str, event_type: str, metadata: Optional[Dict] = None) -> None:
    """
    Emit artifact lifecycle event to observability.

    Metadata excludes artifact body content by design.
    """
    metadata_payload = dict(metadata or {})
    try:
        artifact_row = store.get_artifact_progress_row(discord_id)
    except Exception:
        artifact_row = None

    started_at = str(_read_value(artifact_row, "started_at", "") or "").strip()
    if started_at and "artifact_session_id" not in metadata_payload:
        metadata_payload["artifact_session_id"] = started_at

    status = str(_read_value(artifact_row, "status", "") or "").strip()
    if status and "artifact_status" not in metadata_payload:
        metadata_payload["artifact_status"] = status

    current_section = _read_value(artifact_row, "current_section", None)
    if current_section is not None and "artifact_current_section" not in metadata_payload:
        metadata_payload["artifact_current_section"] = current_section

    compact = {
        key: value
        for key, value in metadata_payload.items()
        if value not in ("", None)
    }
    try:
        store.log_observability_event(discord_id, event_type, compact)
    except Exception as exc:
        logger.warning("Failed to log artifact event %s for %s: %s", event_type, discord_id, exc)


# ============================================================
# ARTIFACT INTRODUCTION & TEMPLATES (Story 4.6)
# ============================================================

ARTIFACT_INTRODUCTION = """
**Thinking Artifact Creation** ðŸŽ¯

Your Thinking Artifact shows your thinking journey â€” where you started, what you explored, and how you think differently now.

**What it is:**
- A 6-section document showing your thinking process
- A snapshot of how you've grown as a thinker
- A chance to see how the 4 Habits helped you work through a real question

**What it's NOT:**
- An essay about "how I use AI"
- AI-generated content (this must be YOUR voice)
- A test or assessment (there's no grading, no "wrong answers")

**Feeling nervous? That's normal.** ðŸŒŸ

Many students feel anxious about sharing their thinking. That's okay. This artifact isn't about being impressive â€” it's about being real. Honest thinking beats polished perfection every time.

**You'll create this over Weeks 6-8:**
- **Week 6:** Choose your question and start working through it
- **Weeks 6-7:** Work through CIS agent sections (at your own pace)
- **Week 8:** Polish and publish to #thinking-showcase

**Ready to start?** This will take 30-60 minutes to complete all 6 sections. You can save at any time and resume later.

Type: **start** to begin, or **show-example** to see a complete artifact first.
"""

ARTIFACT_EXAMPLE = """
**Example: Complete Thinking Artifact**

*This is just an example format. Your artifact will be about YOUR question and YOUR thinking.*

---

**THE QUESTION I WRESTLED WITH:**

"I need to decide what to study at university, but I feel stuck between my parents' expectations (medicine) and what I'm actually interested in (computer science)."

**HOW I REFRAMED IT:**

Using /frame, I realized my question wasn't "What should I study?" but "What do I value?" I discovered I care about: solving real problems, creative work, and having options â€” not just "helping people" (medicine) or "being good at tech" (CS).

**WHAT I EXPLORED:**

Using /diverge, I explored 3 angles:
1. **What if I combined them?** (Medical technology, health tech startups)
2. **What if I questioned the binary?** (Maybe neither medicine nor CS â€” what about data science for public health?)
3. **What if I tried before committing?** (Volunteer at hospital, build a health app, see what I actually enjoy)

**WHAT I CHALLENGED:**

Using /challenge, I tested my assumptions:
- "My parents will be disappointed if I don't do medicine" â†’ *Challenge:* What if they want me to be happy, not just be a doctor?
- "I need to decide now" â†’ *Challenge:* What if the first year is FOR exploration? I don't have to commit forever.
- "Computer science isn't helping people" â†’ *Challenge:* What if health tech helps more people than one doctor ever could?

**WHAT I CONCLUDED:**

Using /synthesize, I crystalized my insight: The real question isn't medicine vs CS â€” it's "How do I want to help people?" I'm going to:
1. **Try both:** Volunteer at a hospital AND build a small health project this year
2. **Keep options open:** Apply to both, but look for programs that combine tech + health
3. **Decide later:** I don't need to know now. The first year is for exploration.

**WHAT THIS TAUGHT ME:**

Before K2M, I thought I had to choose between making my parents happy and being happy myself. Now I realize:
- **Habit 1 (Pause):** I stopped rushing to decide and really thought about what I value
- **Habit 2 (Context):** I explained my full situation instead of just "medicine vs CS"
- **Habit 3 (Iterate):** I explored multiple angles instead of picking the first "good enough" answer
- **Habit 4 (Think First):** I questioned my assumptions instead of accepting them as true

I'm not someone who "made the right choice." I'm someone who learned HOW to think through choices. That skill will follow me forever, even if I change my mind later.

---

*Notice how this artifact shows thinking growth, not just "I used AI tools." The focus is on "I became someone who thinks clearly" not "I learned to use ChatGPT."*

**Ready to create your own?** Type **start** to begin.
"""


# ============================================================
# SECTION PROMPTS (Story 4.6)
# ============================================================

SECTION_1_PROMPT = """
**Section 1 of 6: THE QUESTION I WRESTLED WITH** â¸ï¸

Your artifact starts with a real question you're facing. It could be about:
- University/career decisions
- Academic challenges
- Personal dilemmas
- Future uncertainty
- Anything you're genuinely wrestling with

**What makes a good artifact question:**
âœ… It's REAL (you're actually facing this)
âœ… It's COMPLEX (no easy answers)
âœ… It matters TO YOU (you genuinely want clarity)
âœ… You haven't fully solved it yet (room to explore)

**Examples:**
- "I need to choose between [two universities/programs/careers]"
- "I'm struggling with [subject/skill] and don't know how to improve"
- "I feel pressure to [do X] but I'm not sure it's right for me"
- "I'm worried about [future concern] and don't know how to prepare"

**Your turn:**

In 1-2 sentences, describe the question you're wrestling with.

This doesn't have to be perfectly phrased. We'll refine it in the next section using /frame.

Type your question when ready:
"""

SECTION_2_INTRO = """
âœ… **Got it!** Your question is saved.

**Your Question:**
"{question}"

**Next Step: Refine Your Question**

Now we'll use /frame to clarify what you're really asking. Sometimes our first question isn't the TRUE question â€” it's just the surface.

Type: **/frame [your question]** to work with The Framer on refining your question.

Example: /frame I need to choose between medicine and computer science but I feel stuck

**If you're new to /frame:**
The Framer helps you see what you're REALLY asking â€” not just the surface question. Just type your question and see what happens. The Framer will ask clarifying questions that help you dig deeper.

**No pressure** - this conversation helps you clarify. There's no "wrong" answer.

This will open a conversation with The Framer to help you clarify what you're really wrestling with.
"""

SECTION_2_PROMPT = """
**Section 2 of 6: HOW I REFRAMED IT** ðŸŽ¯

Great work using /frame! Now let's capture what you discovered.

**What to include in this section:**
- Your original question (from Section 1)
- What /frame helped you see about your question
- Your refined/clarity question (if it changed)
- What made the question clearer

**Example:**

"I originally thought I was choosing between medicine and computer science. But using /frame, I realized I'm actually asking 'What do I value?' I care about solving real problems, creative work, and having options â€” not just 'helping people' vs 'being good at tech.'"

**Your turn:**

Based on your /frame conversation, write 2-3 sentences about:
1. What you originally thought you were asking
2. What /frame helped you see
3. How your question clarified (if it changed)

Type your response when ready, or type **/frame** again if you want to keep refining.
"""

SECTION_3_INTRO = """
**Section 3 of 6: WHAT I EXPLORED** ðŸ”„

Now let's explore! Using /diverge, you'll examine multiple angles on your question.

**Type: /diverge [your clarified question]** to work with The Explorer.

The Explorer will help you:
- Try different angles
- See options you haven't considered
- Discover what you didn't know you were looking for

**If you're new to /diverge:**
The Explorer helps you see options you haven't considered. Think of it like brainstorming â€” no idea is too crazy. Share your question and see what angles emerge. You might be surprised what you discover.

**If you feel stuck:** Try "What are 3 angles I haven't considered?" as a starting prompt.

After your /diverge conversation, come back here and we'll capture what you explored.
"""

SECTION_3_PROMPT = """
**Section 3: WHAT I EXPLORED** ðŸ”„

Great exploration! Now let's document it.

**What to include:**
- 2-3 angles you explored (not just one - show breadth)
- What each angle revealed (insights, surprises)
- What you discovered that you didn't expect

**Example:**

"Using /diverge, I explored 3 angles:
1. **What if I combined them?** Medical technology, health tech startups â€” fields that blend medicine and CS
2. **What if I questioned the binary?** Maybe neither medicine nor CS â€” what about data science for public health?
3. **What if I tried before committing?** Volunteer at hospital, build a health app, see what I actually enjoy

The big surprise: I don't have to choose forever. I can explore both before committing."

**Your turn:**

Based on your /diverge conversation, write 3-4 sentences about what you explored and what you discovered.

Type your response when ready, or type **/diverge** again to explore more angles.
"""

SECTION_4_INTRO = """
**Section 4 of 6: WHAT I CHALLENGED** ðŸ§ 

Now let's stress-test your thinking! Using /challenge, you'll examine your assumptions.

**Type: /challenge [what you're assuming about your question]** to work with The Challenger.

The Challenger will help you:
- Identify what you're taking for granted
- Question beliefs you haven't examined
- Test your assumptions before committing

**If you're new to /challenge:**
The Challenger helps you question what you assume is true. Challenging your own thinking feels uncomfortable â€” that's normal! Start with "What if I'm wrong about..." and see what happens. You don't have to change your mind â€” just test your thinking.

**If challenging feels scary:** Start SMALL. Challenge something minor, not your core belief. Remember: Challenging â‰  changing your mind. It just means testing.

After your /challenge conversation, come back here and we'll capture what you challenged.
"""

SECTION_4_PROMPT = """
**Section 4: WHAT I CHALLENGED** ðŸ§ 

Great critical thinking! Now let's document it.

**What to include:**
- 2-3 assumptions you questioned
- What testing each assumption revealed
- How challenging changed your thinking

**Example:**

"Using /challenge, I tested my assumptions:
1. **'My parents will be disappointed if I don't do medicine'** â†’ *Challenge:* What if they want me to be happy, not just be a doctor? I realized I haven't actually talked to them about what they want FOR me (not what they want FROM me).
2. **'I need to decide now'** â†’ *Challenge:* What if the first year is FOR exploration? I'm 17 - how could I be certain about a 40-year career?
3. **'Computer science isn't helping people'** â†’ *Challenge:* What if health tech helps more people than one doctor ever could?

Challenging these assumptions made me realize I'm operating on fear and pressure, not my own values."

**Your turn:**

Based on your /challenge conversation, write 3-4 sentences about what you challenged and what you discovered.

Type your response when ready, or type **/challenge** again to test more assumptions.
"""

SECTION_5_INTRO = """
**Section 5 of 6: WHAT I CONCLUDED** âœ¨

Now let's bring it all together! Using /synthesize, you'll crystalize your insights into clear conclusions.

**Type: /synthesize [what you've learned from all sections so far]** to work with The Synthesizer.

The Synthesizer will help you:
- Integrate insights from all previous sections
- Find the through-line in your thinking
- Crystalize what you've concluded

After your /synthesize conversation, come back here and we'll capture your conclusion.
"""

SECTION_5_PROMPT = """
**Section 5: WHAT I CONCLUDED** âœ¨

Beautiful synthesis! Now let's document your conclusion.

ðŸ”— **Node 3.1 Connection:** Remember - "First draft is raw material" (from Week 6)
Your conclusion isn't final! It's your current best thinking. You can always iterate later. Think of this as a snapshot, not a permanent decision.

**What to include:**
- Your core insight (what you learned through this whole process)
- Your conclusion or decision (if you made one)
- What you're taking forward (even if you don't have a final answer)

**Example:**

"Using /synthesize, I crystalized my insight: The real question isn't medicine vs CS â€” it's 'How do I want to help people?'

**My conclusion:**
I'm going to:
1. **Try both:** Volunteer at a hospital AND build a small health project this year
2. **Keep options open:** Apply to both, but look for programs that combine tech + health
3. **Decide later:** I don't need to know now. The first year is for exploration.

The big shift: I'm not looking for 'the right choice' anymore. I'm looking for 'the right next step' â€” and that's much less pressure."

**Your turn:**

Based on your /synthesize conversation, write 3-4 sentences about what you concluded and what you're taking forward.

Type your response when ready, or type **/synthesize** again to refine your conclusion.
"""

SECTION_6_PROMPT = """
**Section 6 of 6: WHAT THIS TAUGHT ME** ðŸŒŸ

This is the most important section! It's where you show how you've grown as a thinker.

ðŸ”— **Node 3.2 Connection:** Remember - "I have opinions about quality" (from Week 6)
What standards do you now hold for your own thinking? What do you consider "good thinking"?

**What to include:**
- How you thought BEFORE this process (your "before" self)
- How you think NOW (your "after" self)
- Which 4 Habits you used (â¸ï¸ ðŸŽ¯ ðŸ”„ ðŸ§ ) and how
- **How you'll use these thinking habits in university, your career, or your life** (Future Application)

**Example:**

"Before K2M, I thought I had to choose between making my parents happy and being happy myself. I rushed to decisions, accepted assumptions without questioning, and felt overwhelmed by options.

Now I realize:
- **Habit 1 (Pause):** I stopped rushing to decide and really thought about what I value. I took 3 minutes before big choices instead of reacting.
- **Habit 2 (Context):** I explained my full situation instead of just 'medicine vs CS.' The right context made the question clearer.
- **Habit 3 (Iterate):** I explored multiple angles instead of picking the first 'good enough' answer. I discovered options I didn't know existed.
- **Habit 4 (Think First):** I questioned my assumptions instead of accepting them as true. I realized I was operating on fear, not my own values.

ðŸš€ **Future Application:**
When I get to university, I'll use Habit 2 (Context) when I'm confused about assignments â€” I'll explain my full situation instead of staying stuck. I'll use Habit 4 (Think First) before choosing my courses. These habits aren't just for AI â€” they're how I'll approach decisions in my life.

I'm not someone who 'made the right choice.' I'm someone who learned HOW to think through choices. That skill will follow me forever, even if I change my mind later."

**Your turn:**

Write 5-7 sentences reflecting on:
1. How you thought before (your "before" self)
2. How you think now (your "after" self)
3. Which 4 Habits you used and how
4. **How you'll apply these thinking habits in university, your career, or your life** (be specific â€” which habits will you use when?)

Type your reflection when ready. This is the final section!
"""

COMPLETION_MESSAGE = """
ðŸŽ‰ **Congratulations! Your Thinking Artifact is Complete!** ðŸŽ‰

**What you've created:**
âœ… Section 1: THE QUESTION I WRESTLED WITH
âœ… Section 2: HOW I REFRAMED IT (ðŸŽ¯ Habit 2: Context)
âœ… Section 3: WHAT I EXPLORED (ðŸ”„ Habit 3: Iterate)
âœ… Section 4: WHAT I CHALLENGED (ðŸ§  Habit 4: Think First)
âœ… Section 5: WHAT I CONCLUDED
âœ… Section 6: WHAT THIS TAUGHT ME (â¸ï¸ Habit 1: Pause)

**What this proves:**
You've become someone who can think clearly with AI. You didn't just "use tools" â€” you transformed how you approach problems.

**Next Steps:**

**Week 8: Polish and Publish**

This week, you'll:
1. Review your artifact for clarity and voice
2. Make any final edits
3. Publish to #thinking-showcase for your peers to see
4. Earn your 4 Habits graduation badge!

**Want to review now?** Type **review** to see your complete artifact and make edits.

**Ready to polish later?** Type **save** and come back in Week 8. I'll remind you!

---

**You should be proud of this.** This artifact proves real growth. ðŸŒŸ
"""


# ============================================================
# COMMAND HANDLERS
# ============================================================

def _normalize_artifact_text(content: str) -> str:
    """Normalize student text for artifact flow matching."""
    return " ".join((content or "").strip().lower().split())


def _parse_edit_section(content: str) -> Optional[int]:
    """Parse plain-text `edit section N` command."""
    normalized = _normalize_artifact_text(content)
    if not normalized.startswith("edit section "):
        return None

    section_raw = normalized.replace("edit section ", "", 1).strip()
    if not section_raw.isdigit():
        return None

    section = int(section_raw)
    if 1 <= section <= 6:
        return section
    return None


def _parse_section_number_arg(raw_args: str) -> Optional[int]:
    """Parse `/edit` argument variants such as `3` or `section 3`."""
    normalized = _normalize_artifact_text(raw_args)
    if not normalized:
        return None

    if normalized.startswith("section "):
        normalized = normalized.replace("section ", "", 1).strip()

    if not normalized.isdigit():
        return None

    section = int(normalized)
    if 1 <= section <= 6:
        return section
    return None


def _get_next_section_prompt(next_section: int) -> str:
    """Get section writing prompt for continue/resume actions."""
    if next_section == 1:
        return SECTION_1_PROMPT
    if next_section == 2:
        return SECTION_2_PROMPT
    if next_section == 3:
        return SECTION_3_PROMPT
    if next_section == 4:
        return SECTION_4_PROMPT
    if next_section == 5:
        return SECTION_5_PROMPT
    if next_section == 6:
        return SECTION_6_PROMPT
    return "All sections complete. Type **review** to polish your artifact."


def _build_stuck_pattern_nudge(
    artifact_progress: ArtifactProgress,
    force: bool = False,
) -> Optional[str]:
    """
    Build section-specific stuck-pattern interventions.

    We support six patterns (one per section). Nudges trigger after 2+ days
    inactivity unless `force=True` (e.g., student explicitly types `help`).
    """
    if not force and artifact_progress.days_since_activity() < 2:
        return None

    next_section = artifact_progress.get_next_section()
    patterns = {
        1: (
            "**Quick nudge for Section 1**\n\n"
            "Choose one real question you are actively wrestling with.\n"
            "Try: `I'm trying to decide/understand ...`"
        ),
        2: (
            "**Section 2 nudge: reframing**\n\n"
            "Use `/frame` to clarify your real question, then write:\n"
            "1) original question, 2) what changed, 3) clearer version."
        ),
        3: (
            "**Section 3 nudge: exploring**\n\n"
            "Try `/diverge What are 3 angles I haven't considered?`\n"
            "Then capture 2-3 angles and what they revealed."
        ),
        4: (
            "**Section 4 nudge: challenging**\n\n"
            "Use `/challenge` on one assumption you're carrying and note what changed."
        ),
        5: (
            "**Section 5 nudge: concluding**\n\n"
            "You do not need a final answer. Share your current best thinking."
        ),
        6: (
            "**Section 6 nudge: reflection**\n\n"
            "Name your before-vs-after shift and how each Habit showed up."
        ),
    }
    return patterns.get(next_section)


async def _complete_artifact_if_ready(message: discord.Message, discord_id: str) -> None:
    """Persist completion state and send completion guidance."""
    from database.models import _load_artifact_progress

    artifact_progress = _load_artifact_progress(store.conn, discord_id)
    artifact_progress.status = "completed"
    artifact_progress.completed_at = datetime.now()
    store.save_artifact_progress(discord_id, artifact_progress)
    _log_artifact_event(
        discord_id,
        "artifact_completed",
        {"completed_sections": len(artifact_progress.completed_sections)},
    )
    await message.reply(COMPLETION_MESSAGE)


async def handle_create_artifact(message: discord.Message, student) -> None:
    """
    Handle /create-artifact command.

    Entry point for the 6-section artifact creation workflow.
    Creates private DM workspace with save/resume functionality.

    Args:
        message: Discord message triggering the command
        student: Student database row
    """
    # Check week (only available Week 6+)
    if student['current_week'] < 6:
        await message.reply(
            "**Thinking Artifact** ðŸŽ¯\n\n"
            "Your Thinking Artifact is a Week 6-8 project. "
            "You'll get access when Week 6 begins!\n\n"
            "This is where you'll prove how you've grown as a thinker by showing a real problem you worked through using the CIS agents."
        )
        return

    discord_id = str(message.author.id)

    # Get or create artifact progress
    artifact_row = store.get_artifact_progress_row(discord_id)

    if artifact_row is None:
        # Persist explicit intro state so plain-text "start" can be handled safely.
        store.save_artifact_progress(discord_id, ArtifactProgress(status="not_started"))
        await show_artifact_introduction(message)

    elif artifact_row['status'] == 'not_started':
        # Show introduction
        await show_artifact_introduction(message)

    elif artifact_row['status'] == 'in_progress':
        # Resume from where they left off
        from database.models import _load_artifact_progress

        artifact_progress = _load_artifact_progress(store.conn, discord_id)
        stuck_nudge = _build_stuck_pattern_nudge(artifact_progress)
        if stuck_nudge:
            await message.reply(stuck_nudge)
        await resume_artifact_creation(message, student, artifact_row)

    elif artifact_row['status'] == 'completed':
        # Ready to polish/publish
        await show_artifact_review(message, artifact_row)

    elif artifact_row['status'] == 'published':
        await message.reply(
            "Your artifact is already published to #thinking-showcase. "
            "Type **review** to view what you submitted."
        )


async def show_artifact_introduction(message: discord.Message) -> None:
    """Display artifact introduction (Story 4.6)."""
    await message.reply(ARTIFACT_INTRODUCTION)


async def show_artifact_example(message: discord.Message) -> None:
    """Display complete artifact example."""
    await message.reply(ARTIFACT_EXAMPLE)


async def start_artifact(message: discord.Message, student) -> None:
    """
    Start artifact creation - initialize progress and show Section 1 prompt.

    Args:
        message: Discord message
        student: Student database row
    """
    discord_id = str(message.author.id)

    # Initialize artifact progress
    artifact_progress = ArtifactProgress(
        status='in_progress',
        started_at=datetime.now(),
        last_activity=datetime.now()
    )

    store.save_artifact_progress(discord_id, artifact_progress)
    _log_artifact_event(
        discord_id,
        "artifact_started",
        {
            "entrypoint": "create-artifact",
            "week": _read_value(student, "current_week", None),
        },
    )

    # Show Section 1 prompt
    await message.reply(SECTION_1_PROMPT)


async def handle_section_1_input(message: discord.Message, content: str) -> None:
    """
    Process Section 1 input and guide to Section 2.

    Args:
        message: Discord message
        content: Student's question
    """
    discord_id = str(message.author.id)

    # Save Section 1
    store.update_artifact_section(discord_id, 1, content)
    _log_artifact_event(
        discord_id,
        "artifact_section_saved",
        {"section": 1},
    )

    # Acknowledge and guide to Section 2
    response = SECTION_2_INTRO.format(question=content)
    await message.reply(response)
    await message.reply(
        "**Voice Check:** ðŸŽ¤\n\n"
        "Does your Section 1 question sound like YOUR real concern? "
        "If not, rewrite it in your own words before moving on."
    )


async def handle_section_2_input(message: discord.Message, content: str) -> None:
    """Process Section 2 input."""
    discord_id = str(message.author.id)

    # Save Section 2
    store.update_artifact_section(discord_id, 2, content)
    _log_artifact_event(
        discord_id,
        "artifact_section_saved",
        {"section": 2},
    )

    # Voice check prompt
    voice_check = """
**Voice Check:** ðŸŽ¤

Quick check before we continue: Does this sound like YOUR voice, or did it start sounding like AI wrote it?

- **If it sounds like you:** Perfect! Continue.
- **If it sounds AI-generated:** Try rewriting in your own words. Parents want to hear YOU, not ChatGPT.

Remember: Honest > Perfect.
"""

    await message.reply(content + "\n\n" + voice_check)

    # Guide to Section 3
    await message.reply(SECTION_3_INTRO)


async def handle_section_3_input(message: discord.Message, content: str) -> None:
    """Process Section 3 input."""
    discord_id = str(message.author.id)

    # Save Section 3
    store.update_artifact_section(discord_id, 3, content)
    _log_artifact_event(
        discord_id,
        "artifact_section_saved",
        {"section": 3},
    )

    # Voice check
    await message.reply(content + "\n\n**Voice Check:** ðŸŽ¤\n\nDoes this sound like your authentic voice? If yes, continue. If it sounds generic or AI-written, try adding more specifics from your actual /diverge conversation.")

    # Guide to Section 4
    await message.reply(SECTION_4_INTRO)


async def handle_section_4_input(message: discord.Message, content: str) -> None:
    """Process Section 4 input."""
    discord_id = str(message.author.id)

    # Save Section 4
    store.update_artifact_section(discord_id, 4, content)
    _log_artifact_event(
        discord_id,
        "artifact_section_saved",
        {"section": 4},
    )

    # Voice check
    await message.reply(content + "\n\n**Voice Check:** ðŸŽ¤\n\nAuthentic thinking includes uncertainty. Did you share your real doubts and questions, or did it sound too polished? Keep it real.")

    # Guide to Section 5
    await message.reply(SECTION_5_INTRO)


async def handle_section_5_input(message: discord.Message, content: str) -> None:
    """Process Section 5 input."""
    discord_id = str(message.author.id)

    # Save Section 5
    store.update_artifact_section(discord_id, 5, content)
    _log_artifact_event(
        discord_id,
        "artifact_section_saved",
        {"section": 5},
    )

    # Voice check
    await message.reply(
        content
        + "\n\n**Voice Check:** ðŸŽ¤\n\n"
        "Does this conclusion feel authentic to YOUR thinking process? "
        "It's okay to say \"I'm not sure yet\" or \"I'm still figuring this out.\""
    )

    # Guide to Section 6
    await message.reply(SECTION_6_PROMPT)


async def handle_section_6_input(message: discord.Message, content: str) -> None:
    """Process Section 6 input and complete artifact."""
    discord_id = str(message.author.id)

    # Save Section 6
    store.update_artifact_section(discord_id, 6, content)
    _log_artifact_event(
        discord_id,
        "artifact_section_saved",
        {"section": 6},
    )

    # Final voice check
    await message.reply(
        "**Voice Check:** ðŸŽ¤\n\n"
        "Final check: does this reflection sound unmistakably like YOU?"
    )

    # Mark artifact as completed
    artifact_row = store.get_artifact_progress_row(discord_id)
    if artifact_row:
        await _complete_artifact_if_ready(message, discord_id)


async def resume_artifact_creation(message: discord.Message, student, artifact_row) -> None:
    """
    Resume artifact creation from last section.

    Args:
        message: Discord message
        student: Student database row
        artifact_row: Artifact progress database row
    """
    from database.models import _load_artifact_progress

    artifact_progress = _load_artifact_progress(store.conn, str(message.author.id))
    next_section = artifact_progress.get_next_section()
    completed_count = len(artifact_progress.completed_sections)

    message_content = f"""
**Welcome back to your Thinking Artifact!** ðŸ“

**Progress: {completed_count}/6 sections complete**

**Where you left off:**
{get_progress_summary(artifact_progress)}

**Next step:**
{get_section_prompt(next_section)}

**Options:**
- Type **continue** to work on Section {next_section}
- Type **review** to see what you've written so far
"""

    await message.reply(message_content)


def get_progress_summary(artifact_progress: ArtifactProgress) -> str:
    """Generate summary of completed sections."""
    summaries = []

    if artifact_progress.section_1_question:
        summaries.append("âœ… Section 1: Question defined")
    if artifact_progress.section_2_reframed:
        summaries.append("âœ… Section 2: Reframed with /frame")
    if artifact_progress.section_3_explored:
        summaries.append("âœ… Section 3: Explored with /diverge")
    if artifact_progress.section_4_challenged:
        summaries.append("âœ… Section 4: Challenged with /challenge")
    if artifact_progress.section_5_concluded:
        summaries.append("âœ… Section 5: Concluded with /synthesize")
    if artifact_progress.section_6_reflection:
        summaries.append("âœ… Section 6: Reflection complete")

    return "\n".join(summaries) if summaries else "No sections completed yet"


def get_section_prompt(section_number: int) -> str:
    """Get prompt for next section."""
    if section_number == 1:
        return "Defining your question (Section 1)"
    elif section_number == 2:
        return "Reframing with /frame (Section 2)"
    elif section_number == 3:
        return "Exploring with /diverge (Section 3)"
    elif section_number == 4:
        return "Challenging with /challenge (Section 4)"
    elif section_number == 5:
        return "Synthesizing with /synthesize (Section 5)"
    elif section_number == 6:
        return "Final reflection (Section 6)"
    else:
        return "Artifact complete!"


async def show_artifact_review(message: discord.Message, artifact_row) -> None:
    """
    Show complete artifact for review (Week 8 polish flow).

    Args:
        message: Discord message
        artifact_row: Artifact progress database row
    """
    from database.models import _load_artifact_progress

    artifact_progress = _load_artifact_progress(store.conn, str(message.author.id))

    if not artifact_progress.is_complete():
        await message.reply("You haven't completed all 6 sections yet. Type `/create-artifact` to continue.")
        return

    # Display formatted artifact
    formatted = f"""
**Your Complete Thinking Artifact** ðŸ“

---

**THE QUESTION I WRESTLED WITH:**

{artifact_progress.section_1_question}

**HOW I REFRAMED IT:** ðŸŽ¯

{artifact_progress.section_2_reframed}

**WHAT I EXPLORED:** ðŸ”„

{artifact_progress.section_3_explored}

**WHAT I CHALLENGED:** ðŸ§ 

{artifact_progress.section_4_challenged}

**WHAT I CONCLUDED:** âœ¨

{artifact_progress.section_5_concluded}

**WHAT THIS TAUGHT ME:** â¸ï¸

{artifact_progress.section_6_reflection}

---

**Polish Checklist:** âœ…

Before publishing, review your artifact:
- [ ] **Clarity:** Does each section make sense to someone who doesn't know your story?
- [ ] **Voice:** Is this YOUR voice? (Not AI-written - parents should hear YOU in this)
- [ ] **Specifics:** Did you include concrete details from your CIS conversations?
- [ ] **4 Habits:** Are all 4 habits visible in your reflection?
- [ ] **Identity Transformation:** Does this prove "I've become someone who thinks clearly"?

**Want to edit?** Type: **edit section [1-6]**

**Ready to publish?** Type: **publish**
"""

    await message.reply(formatted)


async def handle_artifact_commands(
    message: discord.Message,
    student,
    command: str,
    command_args: str = "",
) -> None:
    """
    Handle artifact sub-commands: save, review, edit, publish.

    Args:
        message: Discord message
        student: Student database row
        command: Sub-command name (save, review, edit, publish)
        command_args: Optional argument text after slash command
    """
    discord_id = str(message.author.id)

    if command == 'save':
        # Save current progress (refresh last_activity timestamp).
        artifact_row = store.get_artifact_progress_row(discord_id)
        if artifact_row is None:
            await message.reply("You haven't started an artifact yet. Type `/create-artifact` to begin.")
            return

        from database.models import _load_artifact_progress
        artifact_progress = _load_artifact_progress(store.conn, discord_id)
        artifact_progress.last_activity = datetime.now()
        store.save_artifact_progress(discord_id, artifact_progress)

        await message.reply(
            "âœ… **Artifact saved!** Type `/create-artifact` anytime to continue."
        )

    elif command == 'review':
        # Show complete artifact for review
        artifact_row = store.get_artifact_progress_row(discord_id)
        if artifact_row:
            await show_artifact_review(message, artifact_row)
        else:
            await message.reply("You haven't started an artifact yet. Type `/create-artifact` to begin.")

    elif command == 'edit':
        artifact_row = store.get_artifact_progress_row(discord_id)
        if not artifact_row:
            await message.reply("You haven't started an artifact yet. Type `/create-artifact` to begin.")
            return

        if artifact_row["status"] == "published":
            await message.reply(
                "This artifact is already published. Create a new artifact cycle to make post-publication edits."
            )
            return

        section_number = _parse_section_number_arg(command_args)
        if section_number is None:
            await message.reply(
                "Use `/edit <section-number>` or `/edit section <section-number>`.\n"
                "Example: `/edit 3`"
            )
            return

        _PENDING_SECTION_EDITS[discord_id] = section_number
        await message.reply(
            f"**Editing Section {section_number}**\n\n"
            "Paste your new version in your next message.\n"
            "Type **cancel** to abort."
        )

    elif command == 'publish':
        if student['current_week'] < 8:
            await message.reply(
                "**Publish to #thinking-showcase** ðŸš€\n\n"
                "Publishing opens in **Week 8**. Keep refining with **review** for now."
            )
            return

        artifact_row = store.get_artifact_progress_row(discord_id)
        if not artifact_row:
            await message.reply("You haven't started an artifact yet. Type `/create-artifact` to begin.")
            return

        from database.models import _load_artifact_progress
        artifact_progress = _load_artifact_progress(store.conn, discord_id)
        if not artifact_progress.is_complete():
            await message.reply("Complete all 6 sections before publishing. Type **continue** to keep going.")
            _log_artifact_event(
                discord_id,
                "artifact_publish_failed",
                {"reason": "not_complete"},
            )
            return

        _log_artifact_event(
            discord_id,
            "artifact_publish_requested",
            {
                "week": _read_value(student, "current_week", None),
                "options": "public,anonymous,private",
            },
        )
        # Task 4.2: Complete publication flow
        await publish_artifact_to_showcase(message, discord_id, artifact_progress)


# ============================================================
# TASK 4.2: ARTIFACT PUBLICATION TO SHOWCASE
# ============================================================

async def publish_artifact_to_showcase(
    message: discord.Message,
    discord_id: str,
    artifact_progress
) -> None:
    """
    Task 4.2: Complete publication flow for Thinking Artifacts to #thinking-showcase.

    Args:
        message: Discord message triggering publish
        discord_id: Student's Discord ID
        artifact_progress: Completed ArtifactProgress object
    """
    # Step 1: Prompt for publication preference (Public/Anonymous/Private)
    preference_prompt = (
        "**Publish Your Thinking Artifact** ðŸš€\n\n"
        "Choose one publication option:\n\n"
        "- **confirm public**: Publish with your name to #thinking-showcase\n"
        "- **confirm anonymous**: Publish anonymously to #thinking-showcase\n"
        "- **confirm private**: Share privately with Trevor only\n\n"
        "**What happens next:**\n"
        "- Public/anonymous posts go to #thinking-showcase\n"
        "- Private posts are delivered to Trevor only\n"
        "- Publication completion awards your 4 Habits badge\n\n"
        "**Ready to confirm?**\n"
        "- Type: **confirm public**, **confirm anonymous**, or **confirm private**\n"
        "- Or type: **cancel** to review more"
    )
    await message.reply(preference_prompt)


async def generate_weekly_artifact_celebration(
    bot,
    days_back: int = 7
) -> Optional[str]:
    """
    Generate aggregate celebration message for artifacts published this week.

    Task 4.2: Weekly summary of artifact publications to #general or #announcements.
    Guardrail #3 compliant: No comparison/ranking language.

    Args:
        bot: Discord bot instance
        days_back: Number of days to look back (default 7)

    Returns:
        Formatted aggregate celebration message
    """
    from datetime import timedelta

    cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

    # Count artifact publications this week
    cursor = store.conn.execute(
        """
        SELECT COUNT(*) as count
        FROM showcase_publications
        WHERE publication_type = 'artifact_completion'
          AND visibility_level IN ('public', 'anonymous')
          AND timestamp >= ?
        """,
        (cutoff_date,)
    )
    result = cursor.fetchone()
    published_count = result['count'] if result else 0

    if published_count == 0:
        return None  # No artifacts published this week

    # Generate Guardrail #3 compliant celebration message
    celebration = (
        f"**Weekly Artifact Celebration** ðŸŽ‰\n\n"
        f"{published_count} student{'s' if published_count > 1 else ''} "
        f"published their Thinking Artifacts to #thinking-showcase this week!\n\n"
        "Each artifact shows a unique thinking journey. "
        "Students wrestled with real questions, explored multiple angles, "
        "challenged their assumptions, and crystalized their conclusions.\n\n"
        "These artifacts prove real growth. Each student showed how they've "
        "become someone who can think clearly with AI.\n\n"
        "**Check out #thinking-showcase** to celebrate your peers' thinking growth!\n\n"
        "**Want to publish yours?** Type `/publish` to complete your artifact.\n\n"
        "Tools change. Habits transfer forever. â¸ï¸ ðŸŽ¯ ðŸ”„ ðŸ§ "
    )

    return celebration


async def post_weekly_artifact_celebration(bot, channel_id: str = None) -> bool:
    """
    Post weekly artifact celebration to general channel.

    Task 4.2: Aggregate celebration posts.
    Should be called once per week (e.g., via background job).

    Args:
        bot: Discord bot instance
        channel_id: Target channel ID (defaults to #general or env var)

    Returns:
        True if posted successfully, False otherwise
    """
    import os

    # Generate celebration message
    celebration = await generate_weekly_artifact_celebration(bot)
    if not celebration:
        return False  # No artifacts to celebrate

    # Find target channel
    target_channel = None

    if channel_id:
        try:
            target_channel = bot.get_channel(int(channel_id))
        except Exception:
            pass

    if not target_channel:
        # Try #general channel
        guild = bot.guilds[0] if bot.guilds else None
        if guild:
            channels = getattr(guild, "text_channels", None) or getattr(guild, "channels", []) or []
            for channel in channels:
                name = str(getattr(channel, "name", "")).lower()
                if name == "general" or name == "announcements":
                    target_channel = channel
                    break

    if not target_channel:
        return False  # No suitable channel found

    # Post celebration
    try:
        await target_channel.send(celebration)
        return True
    except Exception:
        return False



def _find_showcase_channel(bot):
    """Find #thinking-showcase channel (reused from showcase.py)"""
    import os

    CHANNEL_THINKING_SHOWCASE = os.getenv("CHANNEL_THINKING_SHOWCASE", "").strip()

    guild = bot.guilds[0] if bot.guilds else None
    if not guild:
        return None

    if CHANNEL_THINKING_SHOWCASE:
        try:
            configured_id = int(CHANNEL_THINKING_SHOWCASE)
            by_id = guild.get_channel(configured_id)
            if by_id is not None and getattr(by_id, "id", None) == configured_id:
                return by_id
        except ValueError:
            pass

    channels = getattr(guild, "text_channels", None) or getattr(guild, "channels", []) or []
    for channel in channels:
        name = str(getattr(channel, "name", "")).lower()
        if name == "thinking-showcase" or name.endswith("thinking-showcase") or "thinking-showcase" in name:
            return channel
    return None


def format_artifact_for_showcase(
    student_name: str,
    artifact_progress,
    visibility: str
) -> str:
    """
    Format the complete artifact for #thinking-showcase publication.

    Args:
        student_name: Student's display name or "Anonymous"
        artifact_progress: Completed ArtifactProgress object
        visibility: 'public', 'anonymous', or 'private'

    Returns:
        Formatted artifact markdown
    """
    display_name = student_name if visibility == "public" else "Anonymous"

    formatted = f"""
**Thinking Artifact: {display_name}** ðŸŒŸ

*Completed: Week 8*

---

**THE QUESTION I WRESTLED WITH:**

{artifact_progress.section_1_question}

**HOW I REFRAMED IT:** ðŸŽ¯

{artifact_progress.section_2_reframed}

**WHAT I EXPLORED:** ðŸ”„

{artifact_progress.section_3_explored}

**WHAT I CHALLENGED:** ðŸ§ 

{artifact_progress.section_4_challenged}

**WHAT I CONCLUDED:** âœ¨

{artifact_progress.section_5_concluded}

**WHAT THIS TAUGHT ME:** â¸ï¸

{artifact_progress.section_6_reflection}

---

**4 Habits Earned:** â¸ï¸ ðŸŽ¯ ðŸ”„ ðŸ§ 

*Celebrate with reactions below! ðŸ‘‡*
"""
    return formatted.strip()


async def handle_confirm_publish(
    bot,
    message: discord.Message,
    discord_id: str,
    visibility: str
) -> None:
    """
    Handle publication confirmation and post to #thinking-showcase.

    Args:
        bot: Discord bot instance
        message: Discord message
        discord_id: Student's Discord ID
        visibility: 'public', 'anonymous', or 'private'
    """
    discord_id = str(discord_id)

    from cis_controller.safety_filter import (
        ComparisonViolationError,
        post_to_discord_safe,
    )
    from database.models import _load_artifact_progress

    artifact_progress = _load_artifact_progress(store.conn, discord_id)
    if not artifact_progress or not artifact_progress.is_complete():
        await message.reply("Artifact not complete. Type `/create-artifact` to continue.")
        _log_artifact_event(
            discord_id,
            "artifact_publish_failed",
            {"visibility": visibility, "reason": "not_complete"},
        )
        return

    _log_artifact_event(
        discord_id,
        "artifact_publish_confirmed",
        {"visibility": visibility},
    )

    student_name = "Anonymous"
    if bot and getattr(bot, "guilds", None):
        try:
            member = await bot.guilds[0].fetch_member(int(discord_id))
            student_name = member.display_name
        except Exception:
            student_name = "Anonymous"

    # Handle private publications (Trevor-only)
    if visibility == "private":
        facilitator_discord_id = os.getenv("FACILITATOR_DISCORD_ID", "").strip()
        if not facilitator_discord_id:
            await message.reply(
                "**Private publish unavailable right now.** Trevor contact is not configured."
            )
            _log_artifact_event(
                discord_id,
                "artifact_publish_failed",
                {"visibility": visibility, "reason": "facilitator_not_configured"},
            )
            return

        private_artifact = format_artifact_for_showcase(
            student_name=student_name,
            artifact_progress=artifact_progress,
            visibility="public",
        )
        private_payload = (
            "**Private Thinking Artifact Submission**\n\n"
            f"Student: {student_name} (`{discord_id}`)\n\n"
            f"{private_artifact}"
        )

        try:
            trevor_user = await bot.fetch_user(int(facilitator_discord_id))
            await trevor_user.send(private_payload)
        except Exception as exc:
            logger.error("Failed private artifact handoff to Trevor: %s", exc, exc_info=True)
            await message.reply(
                "**Private publish failed.** I could not deliver this to Trevor yet. "
                "Nothing was published."
            )
            _log_artifact_event(
                discord_id,
                "artifact_publish_failed",
                {"visibility": visibility, "reason": "trevor_dm_failed"},
            )
            return

        store.create_showcase_publication(
            discord_id=discord_id,
            publication_type="artifact_completion",
            visibility_level="private",
            celebration_message=private_payload,
            habits_demonstrated=["â¸ï¸", "ðŸŽ¯", "ðŸ”„", "ðŸ§ "],
            nodes_mastered=[],
            parent_email_included=False,
        )
        artifact_progress.status = "published"
        artifact_progress.published_at = datetime.now()
        store.save_artifact_progress(discord_id, artifact_progress)
        await message.reply(
            "**Artifact shared privately with Trevor.**\n\n"
            "Your artifact was delivered and recorded as a private publication."
        )
        _log_artifact_event(
            discord_id,
            "artifact_published",
            {"visibility": visibility, "destination": "trevor_dm"},
        )
        return

    showcase_channel = _find_showcase_channel(bot)
    if not showcase_channel:
        await message.reply("#thinking-showcase channel not found. Contact Trevor.")
        _log_artifact_event(
            discord_id,
            "artifact_publish_failed",
            {"visibility": visibility, "reason": "showcase_channel_not_found"},
        )
        return

    formatted_artifact = format_artifact_for_showcase(
        student_name=student_name,
        artifact_progress=artifact_progress,
        visibility=visibility
    )

    try:
        posted_message = await post_to_discord_safe(
            bot=bot,
            channel=showcase_channel,
            message_text=formatted_artifact,
            student_discord_id=int(discord_id),
            is_showcase=True,
        )

        # Add star reaction (Task 4.2 requirement)
        if posted_message and hasattr(posted_message, "add_reaction"):
            try:
                import asyncio
                reaction_result = posted_message.add_reaction("\N{WHITE MEDIUM STAR}")
                if asyncio.iscoroutine(reaction_result):
                    await reaction_result
            except Exception:
                pass

        store.create_showcase_publication(
            discord_id=discord_id,
            publication_type="artifact_completion",
            visibility_level=visibility,
            celebration_message=formatted_artifact,
            habits_demonstrated=["â¸ï¸", "ðŸŽ¯", "ðŸ”„", "ðŸ§ "],
            nodes_mastered=[],
            parent_email_included=False,
        )

        artifact_progress.status = "published"
        artifact_progress.published_at = datetime.now()
        store.save_artifact_progress(discord_id, artifact_progress)

        if visibility == "public":
            confirm = (
                "**Posted to #thinking-showcase!** ðŸŽ‰\n\n"
                "Your artifact is now live. Your peers can see your thinking growth "
                "and celebrate with you.\n\n"
                "**You've officially earned:**\n"
                "â¸ï¸ **PAUSE** - Habit 1 Badge\n"
                "ðŸŽ¯ **CONTEXT** - Habit 2 Badge\n"
                "ðŸ”„ **ITERATE** - Habit 3 Badge\n"
                "ðŸ§  **THINK FIRST** - Habit 4 Badge\n\n"
                "ðŸ”— **Node 3.4: \"I Made This\"**\n\n"
                "You're not just someone who \"used AI.\" "
                "You're someone who directed AI to create something meaningful.\n\n"
                "That's the Zone 4 director identity - you own your thinking and your outcomes. "
                "You didn't just use tools - you learned to THINK WITH AI.\n\n"
                "That skill will follow you forever. Tools change - thinking lasts.\n\n"
                "**Congratulations!** ðŸŽ‰ðŸŒŸ"
            )
        else:
            confirm = (
                "**Posted anonymously to #thinking-showcase!** ðŸŽ‰\n\n"
                "Your artifact is now live. Peers can see your thinking growth "
                "and celebrate with you, but your name is hidden.\n\n"
                "**You've officially earned:**\n"
                "â¸ï¸ **PAUSE** - Habit 1 Badge\n"
                "ðŸŽ¯ **CONTEXT** - Habit 2 Badge\n"
                "ðŸ”„ **ITERATE** - Habit 3 Badge\n"
                "ðŸ§  **THINK FIRST** - Habit 4 Badge\n\n"
                "**Congratulations!** ðŸŽ‰ðŸŒŸ"
            )
        await message.reply(confirm)

    except ComparisonViolationError:
        await message.reply(
            "I kept this private for now. #thinking-showcase only accepts finished work."
        )
        _log_artifact_event(
            discord_id,
            "artifact_publish_blocked",
            {"visibility": visibility, "reason": "safety_filter"},
        )
    except Exception as exc:
        await message.reply(
            "**Something went wrong.** Your artifact is saved; try publishing again later."
        )
        _log_artifact_event(
            discord_id,
            "artifact_publish_failed",
            {"visibility": visibility, "reason": "unexpected_error"},
        )
        raise exc
    else:
        _log_artifact_event(
            discord_id,
            "artifact_published",
            {"visibility": visibility, "destination": "thinking_showcase"},
        )


# ============================================================
# TEXT INPUT HANDLERS
# ============================================================

async def handle_artifact_text_input(message: discord.Message, student, bot=None) -> bool:
    """
    Handle plain-text DM messages for artifact workflow progression.

    Args:
        message: Discord message
        student: Student database row
        bot: Discord bot instance (required for confirm publish commands)

    Returns True when the message was consumed by artifact flow.
    """
    content = (message.content or "").strip()
    if not content or content.startswith("/"):
        return False

    if student["current_week"] < 6:
        return False

    normalized = _normalize_artifact_text(content)
    discord_id = str(message.author.id)
    artifact_row = store.get_artifact_progress_row(discord_id)

    # Pending `/edit` or `edit section N` writeback.
    pending_section = _PENDING_SECTION_EDITS.get(discord_id)
    if pending_section is not None:
        if normalized == "cancel":
            _PENDING_SECTION_EDITS.pop(discord_id, None)
            await message.reply("Edit canceled. Type **review** to continue polishing.")
            return True

        if not artifact_row:
            _PENDING_SECTION_EDITS.pop(discord_id, None)
            await message.reply("No active artifact found. Type `/create-artifact` to begin again.")
            return True

        store.update_artifact_section(discord_id, pending_section, content)
        _log_artifact_event(
            discord_id,
            "artifact_section_saved",
            {"section": pending_section, "edit_mode": True},
        )
        _PENDING_SECTION_EDITS.pop(discord_id, None)
        await message.reply(
            f"âœ… **Section {pending_section} updated!** Type **review** to inspect your artifact."
        )
        return True

    # Allow text variants of sub-commands in DM.
    if artifact_row and normalized in {"save", "review", "publish"}:
        await handle_artifact_commands(message, student, normalized)
        return True

    # Allow plain-text edit command in DM (week 6+ workflow).
    edit_section = _parse_edit_section(content)
    if edit_section is not None:
        if artifact_row is None:
            await message.reply("You haven't started an artifact yet. Type `/create-artifact` to begin.")
            return True
        if artifact_row["status"] == "published":
            await message.reply("This artifact is already published and cannot be edited in place.")
            return True
        if artifact_row["status"] not in {"in_progress", "completed"}:
            await message.reply("Start your artifact first with `/create-artifact`.")
            return True

        _PENDING_SECTION_EDITS[discord_id] = edit_section
        await message.reply(
            f"**Editing Section {edit_section}**\n\n"
            "Paste your updated text in your next message.\n"
            "Type **cancel** to abort."
        )
        return True

    # Task 4.2: Handle publication confirmation commands
    if normalized in {
        "confirm public",
        "confirm private",
        "confirm anonymous",
        "public",
        "private",
        "anonymous",
    }:
        if not bot:
            await message.reply("Bot instance required for publication. Please try again.")
            return True

        if not artifact_row or artifact_row["status"] != "completed":
            await message.reply("Complete your artifact first with `/create-artifact` before publishing.")
            return True

        if normalized in {"confirm public", "public"}:
            visibility = "public"
        elif normalized in {"confirm anonymous", "anonymous"}:
            visibility = "anonymous"
        else:
            visibility = "private"
        await handle_confirm_publish(bot, message, discord_id, visibility)
        return True

    if normalized == "cancel":
        await message.reply("No problem. Type **review** whenever you want to continue.")
        return True

    if artifact_row is None:
        return False

    status = artifact_row["status"]

    if status == "not_started":
        if normalized in {"show-example", "show example", "example"}:
            await show_artifact_example(message)
            return True
        if normalized in {"start", "continue", "resume"}:
            await start_artifact(message, student)
            return True
        return False

    if status == "in_progress":
        from database.models import _load_artifact_progress

        artifact_progress = _load_artifact_progress(store.conn, discord_id)

        if normalized in {"show-example", "show example", "example"}:
            await show_artifact_example(message)
            return True

        if normalized == "help":
            nudge = _build_stuck_pattern_nudge(artifact_progress, force=True)
            if nudge:
                await message.reply(nudge)
            return True

        if normalized in {"continue", "resume"}:
            nudge = _build_stuck_pattern_nudge(artifact_progress)
            if nudge:
                await message.reply(nudge)
            await message.reply(_get_next_section_prompt(artifact_progress.get_next_section()))
            return True

        next_section = artifact_progress.get_next_section()
        if next_section == 1:
            await handle_section_1_input(message, content)
        elif next_section == 2:
            await handle_section_2_input(message, content)
        elif next_section == 3:
            await handle_section_3_input(message, content)
        elif next_section == 4:
            await handle_section_4_input(message, content)
        elif next_section == 5:
            await handle_section_5_input(message, content)
        elif next_section == 6:
            await handle_section_6_input(message, content)
        else:
            await _complete_artifact_if_ready(message, discord_id)

        return True

    if status in {"completed", "published"} and normalized in {"review", "publish"}:
        await handle_artifact_commands(message, student, normalized)
        return True

    return False


async def send_artifact_inactivity_nudges(bot, inactive_days: int = 3) -> int:
    """
    Send proactive DM nudges for students inactive in artifact flow.

    Story 4.6 expects background reminder nudges during Weeks 6-8.

    Args:
        bot: Discord bot instance (for user lookup + DM send)
        inactive_days: Minimum inactivity days before nudging

    Returns:
        Number of nudges successfully sent
    """
    from database.models import _load_artifact_progress

    cursor = store.conn.execute(
        """
        SELECT s.discord_id
        FROM students s
        JOIN artifact_progress ap ON ap.student_id = s.discord_id
        WHERE s.current_week IN (6, 7, 8)
          AND ap.status = 'in_progress'
        """
    )
    rows = cursor.fetchall()
    sent_count = 0

    for row in rows:
        discord_id = str(row["discord_id"])
        artifact_progress = _load_artifact_progress(store.conn, discord_id)
        days_inactive = artifact_progress.days_since_activity()

        if days_inactive < inactive_days:
            continue

        next_section = artifact_progress.get_next_section()
        completed_count = len(artifact_progress.completed_sections)
        targeted_nudge = _build_stuck_pattern_nudge(artifact_progress, force=True) or ""

        reminder_text = (
            "ðŸ“ **Thinking Artifact Reminder**\n\n"
            f"You've completed **{completed_count}/6** sections.\n"
            f"It's been **{days_inactive} day(s)** since your last artifact update.\n\n"
            "No pressure. Small progress counts.\n"
            "Type **continue** to resume your next section, **review** to inspect your draft, or **help** for support.\n\n"
            f"{targeted_nudge}"
        ).strip()

        try:
            user = await bot.fetch_user(int(discord_id))
            await user.send(reminder_text)
            sent_count += 1
            try:
                store.log_observability_event(
                    discord_id,
                    "artifact_stuck_nudge_sent",
                    {
                        "days_inactive": days_inactive,
                        "next_section": next_section,
                        "completed_sections": completed_count,
                    },
                )
            except Exception:
                logger.warning("Failed to log artifact nudge event for %s", discord_id)
        except Exception as exc:
            logger.warning("Failed artifact inactivity nudge for %s: %s", discord_id, exc)

    return sent_count

