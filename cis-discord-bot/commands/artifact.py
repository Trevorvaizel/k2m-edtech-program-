"""
Artifact Command Handler
Story 4.6 Implementation: /create-artifact command

Students use /create-artifact to build their 6-section Thinking Artifact.
Available from Week 6 onwards (Decision 11).
All 4 CIS agents are available during artifact creation.
"""

import discord
from database.store import StudentStateStore
from database.models import ArtifactProgress
from datetime import datetime
from typing import Optional

store = StudentStateStore()


# ============================================================
# ARTIFACT INTRODUCTION & TEMPLATES (Story 4.6)
# ============================================================

ARTIFACT_INTRODUCTION = """
**Thinking Artifact Creation** 🎯

Your Thinking Artifact shows your thinking journey — where you started, what you explored, and how you think differently now.

**What it is:**
- A 6-section document showing your thinking process
- A snapshot of how you've grown as a thinker
- A chance to see how the 4 Habits helped you work through a real question

**What it's NOT:**
- An essay about "how I use AI"
- AI-generated content (this must be YOUR voice)
- A test or assessment (there's no grading, no "wrong answers")

**Feeling nervous? That's normal.** 🌟

Many students feel anxious about sharing their thinking. That's okay. This artifact isn't about being impressive — it's about being real. Honest thinking beats polished perfection every time.

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

Using /frame, I realized my question wasn't "What should I study?" but "What do I value?" I discovered I care about: solving real problems, creative work, and having options — not just "helping people" (medicine) or "being good at tech" (CS).

**WHAT I EXPLORED:**

Using /diverge, I explored 3 angles:
1. **What if I combined them?** (Medical technology, health tech startups)
2. **What if I questioned the binary?** (Maybe neither medicine nor CS — what about data science for public health?)
3. **What if I tried before committing?** (Volunteer at hospital, build a health app, see what I actually enjoy)

**WHAT I CHALLENGED:**

Using /challenge, I tested my assumptions:
- "My parents will be disappointed if I don't do medicine" → *Challenge:* What if they want me to be happy, not just be a doctor?
- "I need to decide now" → *Challenge:* What if the first year is FOR exploration? I don't have to commit forever.
- "Computer science isn't helping people" → *Challenge:* What if health tech helps more people than one doctor ever could?

**WHAT I CONCLUDED:**

Using /synthesize, I crystalized my insight: The real question isn't medicine vs CS — it's "How do I want to help people?" I'm going to:
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
**Section 1 of 6: THE QUESTION I WRESTLED WITH** ⏸️

Your artifact starts with a real question you're facing. It could be about:
- University/career decisions
- Academic challenges
- Personal dilemmas
- Future uncertainty
- Anything you're genuinely wrestling with

**What makes a good artifact question:**
✅ It's REAL (you're actually facing this)
✅ It's COMPLEX (no easy answers)
✅ It matters TO YOU (you genuinely want clarity)
✅ You haven't fully solved it yet (room to explore)

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
✅ **Got it!** Your question is saved.

**Your Question:**
"{question}"

**Next Step: Refine Your Question**

Now we'll use /frame to clarify what you're really asking. Sometimes our first question isn't the TRUE question — it's just the surface.

Type: **/frame [your question]** to work with The Framer on refining your question.

Example: /frame I need to choose between medicine and computer science but I feel stuck

**If you're new to /frame:**
The Framer helps you see what you're REALLY asking — not just the surface question. Just type your question and see what happens. The Framer will ask clarifying questions that help you dig deeper.

**No pressure** - this conversation helps you clarify. There's no "wrong" answer.

This will open a conversation with The Framer to help you clarify what you're really wrestling with.
"""

SECTION_2_PROMPT = """
**Section 2 of 6: HOW I REFRAMED IT** 🎯

Great work using /frame! Now let's capture what you discovered.

**What to include in this section:**
- Your original question (from Section 1)
- What /frame helped you see about your question
- Your refined/clarity question (if it changed)
- What made the question clearer

**Example:**

"I originally thought I was choosing between medicine and computer science. But using /frame, I realized I'm actually asking 'What do I value?' I care about solving real problems, creative work, and having options — not just 'helping people' vs 'being good at tech.'"

**Your turn:**

Based on your /frame conversation, write 2-3 sentences about:
1. What you originally thought you were asking
2. What /frame helped you see
3. How your question clarified (if it changed)

Type your response when ready, or type **/frame** again if you want to keep refining.
"""

SECTION_3_INTRO = """
**Section 3 of 6: WHAT I EXPLORED** 🔄

Now let's explore! Using /diverge, you'll examine multiple angles on your question.

**Type: /diverge [your clarified question]** to work with The Explorer.

The Explorer will help you:
- Try different angles
- See options you haven't considered
- Discover what you didn't know you were looking for

**If you're new to /diverge:**
The Explorer helps you see options you haven't considered. Think of it like brainstorming — no idea is too crazy. Share your question and see what angles emerge. You might be surprised what you discover.

**If you feel stuck:** Try "What are 3 angles I haven't considered?" as a starting prompt.

After your /diverge conversation, come back here and we'll capture what you explored.
"""

SECTION_3_PROMPT = """
**Section 3: WHAT I EXPLORED** 🔄

Great exploration! Now let's document it.

**What to include:**
- 2-3 angles you explored (not just one - show breadth)
- What each angle revealed (insights, surprises)
- What you discovered that you didn't expect

**Example:**

"Using /diverge, I explored 3 angles:
1. **What if I combined them?** Medical technology, health tech startups — fields that blend medicine and CS
2. **What if I questioned the binary?** Maybe neither medicine nor CS — what about data science for public health?
3. **What if I tried before committing?** Volunteer at hospital, build a health app, see what I actually enjoy

The big surprise: I don't have to choose forever. I can explore both before committing."

**Your turn:**

Based on your /diverge conversation, write 3-4 sentences about what you explored and what you discovered.

Type your response when ready, or type **/diverge** again to explore more angles.
"""

SECTION_4_INTRO = """
**Section 4 of 6: WHAT I CHALLENGED** 🧠

Now let's stress-test your thinking! Using /challenge, you'll examine your assumptions.

**Type: /challenge [what you're assuming about your question]** to work with The Challenger.

The Challenger will help you:
- Identify what you're taking for granted
- Question beliefs you haven't examined
- Test your assumptions before committing

**If you're new to /challenge:**
The Challenger helps you question what you assume is true. Challenging your own thinking feels uncomfortable — that's normal! Start with "What if I'm wrong about..." and see what happens. You don't have to change your mind — just test your thinking.

**If challenging feels scary:** Start SMALL. Challenge something minor, not your core belief. Remember: Challenging ≠ changing your mind. It just means testing.

After your /challenge conversation, come back here and we'll capture what you challenged.
"""

SECTION_4_PROMPT = """
**Section 4: WHAT I CHALLENGED** 🧠

Great critical thinking! Now let's document it.

**What to include:**
- 2-3 assumptions you questioned
- What testing each assumption revealed
- How challenging changed your thinking

**Example:**

"Using /challenge, I tested my assumptions:
1. **'My parents will be disappointed if I don't do medicine'** → *Challenge:* What if they want me to be happy, not just be a doctor? I realized I haven't actually talked to them about what they want FOR me (not what they want FROM me).
2. **'I need to decide now'** → *Challenge:* What if the first year is FOR exploration? I'm 17 - how could I be certain about a 40-year career?
3. **'Computer science isn't helping people'** → *Challenge:* What if health tech helps more people than one doctor ever could?

Challenging these assumptions made me realize I'm operating on fear and pressure, not my own values."

**Your turn:**

Based on your /challenge conversation, write 3-4 sentences about what you challenged and what you discovered.

Type your response when ready, or type **/challenge** again to test more assumptions.
"""

SECTION_5_INTRO = """
**Section 5 of 6: WHAT I CONCLUDED** ✨

Now let's bring it all together! Using /synthesize, you'll crystalize your insights into clear conclusions.

**Type: /synthesize [what you've learned from all sections so far]** to work with The Synthesizer.

The Synthesizer will help you:
- Integrate insights from all previous sections
- Find the through-line in your thinking
- Crystalize what you've concluded

After your /synthesize conversation, come back here and we'll capture your conclusion.
"""

SECTION_5_PROMPT = """
**Section 5: WHAT I CONCLUDED** ✨

Beautiful synthesis! Now let's document your conclusion.

🔗 **Node 3.1 Connection:** Remember - "First draft is raw material" (from Week 6)
Your conclusion isn't final! It's your current best thinking. You can always iterate later. Think of this as a snapshot, not a permanent decision.

**What to include:**
- Your core insight (what you learned through this whole process)
- Your conclusion or decision (if you made one)
- What you're taking forward (even if you don't have a final answer)

**Example:**

"Using /synthesize, I crystalized my insight: The real question isn't medicine vs CS — it's 'How do I want to help people?'

**My conclusion:**
I'm going to:
1. **Try both:** Volunteer at a hospital AND build a small health project this year
2. **Keep options open:** Apply to both, but look for programs that combine tech + health
3. **Decide later:** I don't need to know now. The first year is for exploration.

The big shift: I'm not looking for 'the right choice' anymore. I'm looking for 'the right next step' — and that's much less pressure."

**Your turn:**

Based on your /synthesize conversation, write 3-4 sentences about what you concluded and what you're taking forward.

Type your response when ready, or type **/synthesize** again to refine your conclusion.
"""

SECTION_6_PROMPT = """
**Section 6 of 6: WHAT THIS TAUGHT ME** 🌟

This is the most important section! It's where you show how you've grown as a thinker.

🔗 **Node 3.2 Connection:** Remember - "I have opinions about quality" (from Week 6)
What standards do you now hold for your own thinking? What do you consider "good thinking"?

**What to include:**
- How you thought BEFORE this process (your "before" self)
- How you think NOW (your "after" self)
- Which 4 Habits you used (⏸️ 🎯 🔄 🧠) and how
- **How you'll use these thinking habits in university, your career, or your life** (Future Application)

**Example:**

"Before K2M, I thought I had to choose between making my parents happy and being happy myself. I rushed to decisions, accepted assumptions without questioning, and felt overwhelmed by options.

Now I realize:
- **Habit 1 (Pause):** I stopped rushing to decide and really thought about what I value. I took 3 minutes before big choices instead of reacting.
- **Habit 2 (Context):** I explained my full situation instead of just 'medicine vs CS.' The right context made the question clearer.
- **Habit 3 (Iterate):** I explored multiple angles instead of picking the first 'good enough' answer. I discovered options I didn't know existed.
- **Habit 4 (Think First):** I questioned my assumptions instead of accepting them as true. I realized I was operating on fear, not my own values.

🚀 **Future Application:**
When I get to university, I'll use Habit 2 (Context) when I'm confused about assignments — I'll explain my full situation instead of staying stuck. I'll use Habit 4 (Think First) before choosing my courses. These habits aren't just for AI — they're how I'll approach decisions in my life.

I'm not someone who 'made the right choice.' I'm someone who learned HOW to think through choices. That skill will follow me forever, even if I change my mind later."

**Your turn:**

Write 5-7 sentences reflecting on:
1. How you thought before (your "before" self)
2. How you think now (your "after" self)
3. Which 4 Habits you used and how
4. **How you'll apply these thinking habits in university, your career, or your life** (be specific — which habits will you use when?)

Type your reflection when ready. This is the final section!
"""

COMPLETION_MESSAGE = """
🎉 **Congratulations! Your Thinking Artifact is Complete!** 🎉

**What you've created:**
✅ Section 1: THE QUESTION I WRESTLED WITH
✅ Section 2: HOW I REFRAMED IT (🎯 Habit 2: Context)
✅ Section 3: WHAT I EXPLORED (🔄 Habit 3: Iterate)
✅ Section 4: WHAT I CHALLENGED (🧠 Habit 4: Think First)
✅ Section 5: WHAT I CONCLUDED
✅ Section 6: WHAT THIS TAUGHT ME (⏸️ Habit 1: Pause)

**What this proves:**
You've become someone who can think clearly with AI. You didn't just "use tools" — you transformed how you approach problems.

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

**You should be proud of this.** This artifact proves real growth. 🌟
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
            "**Thinking Artifact** 🎯\n\n"
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

    # Acknowledge and guide to Section 2
    response = SECTION_2_INTRO.format(question=content)
    await message.reply(response)
    await message.reply(
        "**Voice Check:** 🎤\n\n"
        "Does your Section 1 question sound like YOUR real concern? "
        "If not, rewrite it in your own words before moving on."
    )


async def handle_section_2_input(message: discord.Message, content: str) -> None:
    """Process Section 2 input."""
    discord_id = str(message.author.id)

    # Save Section 2
    store.update_artifact_section(discord_id, 2, content)

    # Voice check prompt
    voice_check = """
**Voice Check:** 🎤

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

    # Voice check
    await message.reply(content + "\n\n**Voice Check:** 🎤\n\nDoes this sound like your authentic voice? If yes, continue. If it sounds generic or AI-written, try adding more specifics from your actual /diverge conversation.")

    # Guide to Section 4
    await message.reply(SECTION_4_INTRO)


async def handle_section_4_input(message: discord.Message, content: str) -> None:
    """Process Section 4 input."""
    discord_id = str(message.author.id)

    # Save Section 4
    store.update_artifact_section(discord_id, 4, content)

    # Voice check
    await message.reply(content + "\n\n**Voice Check:** 🎤\n\nAuthentic thinking includes uncertainty. Did you share your real doubts and questions, or did it sound too polished? Keep it real.")

    # Guide to Section 5
    await message.reply(SECTION_5_INTRO)


async def handle_section_5_input(message: discord.Message, content: str) -> None:
    """Process Section 5 input."""
    discord_id = str(message.author.id)

    # Save Section 5
    store.update_artifact_section(discord_id, 5, content)

    # Voice check
    await message.reply(
        content
        + "\n\n**Voice Check:** 🎤\n\n"
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

    # Final voice check
    await message.reply(
        "**Voice Check:** 🎤\n\n"
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
**Welcome back to your Thinking Artifact!** 📝

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
        summaries.append("✅ Section 1: Question defined")
    if artifact_progress.section_2_reframed:
        summaries.append("✅ Section 2: Reframed with /frame")
    if artifact_progress.section_3_explored:
        summaries.append("✅ Section 3: Explored with /diverge")
    if artifact_progress.section_4_challenged:
        summaries.append("✅ Section 4: Challenged with /challenge")
    if artifact_progress.section_5_concluded:
        summaries.append("✅ Section 5: Concluded with /synthesize")
    if artifact_progress.section_6_reflection:
        summaries.append("✅ Section 6: Reflection complete")

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
**Your Complete Thinking Artifact** 📝

---

**THE QUESTION I WRESTLED WITH:**

{artifact_progress.section_1_question}

**HOW I REFRAMED IT:** 🎯

{artifact_progress.section_2_reframed}

**WHAT I EXPLORED:** 🔄

{artifact_progress.section_3_explored}

**WHAT I CHALLENGED:** 🧠

{artifact_progress.section_4_challenged}

**WHAT I CONCLUDED:** ✨

{artifact_progress.section_5_concluded}

**WHAT THIS TAUGHT ME:** ⏸️

{artifact_progress.section_6_reflection}

---

**Polish Checklist:** ✅

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


async def handle_artifact_commands(message: discord.Message, student, command: str) -> None:
    """
    Handle artifact sub-commands: save, review, publish.

    Args:
        message: Discord message
        student: Student database row
        command: Sub-command name (save, review, publish)
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
            "✅ **Artifact saved!** Type `/create-artifact` anytime to continue."
        )

    elif command == 'review':
        # Show complete artifact for review
        artifact_row = store.get_artifact_progress_row(discord_id)
        if artifact_row:
            await show_artifact_review(message, artifact_row)
        else:
            await message.reply("You haven't started an artifact yet. Type `/create-artifact` to begin.")

    elif command == 'publish':
        if student['current_week'] < 8:
            await message.reply(
                "**Publish to #thinking-showcase** 🚀\n\n"
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
            return

        # Publication handoff is completed in Task 4.2.
        await message.reply(
            "**Publish to #thinking-showcase** 🚀\n\n"
            "Artifact validation passed. Task 4.2 will complete the final publish-to-showcase post."
        )


async def handle_artifact_text_input(message: discord.Message, student) -> bool:
    """
    Handle plain-text DM messages for artifact workflow progression.

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

    # Allow text variants of sub-commands in DM.
    if artifact_row and normalized in {"save", "review", "publish"}:
        await handle_artifact_commands(message, student, normalized)
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

        edit_section = _parse_edit_section(content)
        if edit_section is not None:
            await message.reply(
                f"Paste your updated text for **Section {edit_section}** in your next message."
            )
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
