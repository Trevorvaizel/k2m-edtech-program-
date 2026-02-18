"""
Frame Command Handler
Story 4.7 Implementation: /frame command

This module handles the /frame Discord command.
Students use /frame to practice Habit 1 (Pause) and Habit 2 (Context).

Task 1.4: Full implementation with provider-routed LLM integration, DM workflow,
StudentContext-aware responses, and habit celebration system.

Task 1.6: Rate limiting + cost controls integration
"""

import discord
from discord.ext import commands
from database.store import StudentStateStore
from cis_controller.llm_integration import call_agent_with_context
from cis_controller.state_machine import celebrate_habit, transition_state
from cis_controller.safety_filter import safety_filter
from cis_controller.rate_limiter import rate_limiter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

store = StudentStateStore()


async def handle_frame(message: discord.Message, student):
    """
    Handle /frame command with full provider-routed LLM integration.

    Workflow (Decision 12 + Task 1.6 Rate Limiting):
    1. Check rate limits (50 messages/day per student)
    2. Create private DM with student
    3. Load StudentContext for personalized response
    4. Call Framer agent via active provider
    5. Track API costs and update budget metrics
    6. Append habit celebration if milestone reached
    7. Save conversation to database
    8. Ask if student wants to share to #thinking-showcase

    Args:
        message: Discord message object
        student: Student database row

    Task 1.4 Implementation:
    - Provider-routed LLM integration with prompt caching
    - StudentContext-aware responses (zone, altitude, emotional state)
    - Habit 1 (Pause) + Habit 2 (Context) scaffolding
    - Conversation lifecycle (initiation → scaffolding → completion → optional share)
    - Habit celebration system (milestones at 3, 7, 14, 21, 30 practices)
    - Error handling with graceful fallback

    Task 1.6 Implementation:
    - Rate limiting: 50 interactions/day per student
    - Cost tracking: Token counts, cost breakdown, total USD
    - Budget alerts: Daily threshold at $10, weekly cap at $50
    """
    discord_id = str(message.author.id)

    # Step 1: Check rate limits (Task 1.6)
    allowed, error_message = rate_limiter.check_rate_limit(discord_id)
    if not allowed:
        await message.reply(error_message)
        logger.warning(f"Rate limit blocked /frame for {discord_id}")
        return

    # Step 2: Create private DM channel
    try:
        dm_channel = await message.author.create_dm()
    except discord.Forbidden:
        await message.reply(
            "🚫 **Cannot start DM** - I need permission to send you private messages. "
            "Please enable DMs in your privacy settings, then try /frame again."
        )
        return

    # Step 3: Build StudentContext for personalized response
    student_context = store.build_student_context(discord_id)
    if not student_context:
        await message.reply("❌ Error loading your profile. Please try again.")
        logger.error(f"Failed to build StudentContext for {discord_id}")
        return

    # Load conversation history (last 10 messages)
    conversation_history = store.get_conversation_history(discord_id, "frame", limit=10)

    # Extract user message content (remove /frame command if present)
    user_message = message.content.replace("/frame", "").strip()
    if not user_message:
        user_message = "I want to practice framing a question."

    # Step 4: Call Framer agent via active provider
    try:
        logger.info(f"Calling Framer agent for {discord_id}")

        framer_response, cost_data = await call_agent_with_context(
            agent="frame",
            student_context=student_context,
            user_message=user_message,
            conversation_history=conversation_history
        )

        # Step 5: Track interaction for rate limiting and cost monitoring (Task 1.6)
        rate_limiter.track_interaction(
            discord_id=discord_id,
            agent="frame",
            tokens=cost_data.get("total_tokens", 0),
            cost_usd=cost_data.get("total_cost_usd", 0.0)
        )

        # Validate response safety before delivery
        safety_filter.validate_no_comparison(framer_response)

        # Step 6: Save conversation to database
        store.save_conversation(
            discord_id=discord_id,
            agent="frame",
            role="user",
            content=user_message
        )
        store.save_conversation(
            discord_id=discord_id,
            agent="frame",
            role="assistant",
            content=framer_response
        )

        # Update habit practice count (Habit 1 - Pause)
        store.update_habit_practice(discord_id, habit_id=1)

        # Step 7: Generate habit celebration after increment (milestone-aware)
        refreshed_student = store.get_student(discord_id)
        celebration = celebrate_habit(refreshed_student, habit_id=1)

        # Combine response with celebration
        if celebration:
            full_response = f"{framer_response}\n\n{celebration}"
        else:
            full_response = framer_response

        # Post response in DM
        await dm_channel.send(full_response)

        # Update state machine (transition from current state to framing)
        current_state = student_context.current_state
        new_state = transition_state(current_state, "frame", student=student, store=store)

        # Log observability event
        store.log_observability_event(
            discord_id,
            "agent_used",
            {
                "agent": "frame",
                "week": student_context.current_week,
                "zone": student_context.zone,
                "cost_usd": cost_data.get("total_cost_usd", 0.0)
            }
        )

        # Step 8: Offer to share to #thinking-showcase (optional)
        await dm_channel.send(
            "\n---\n"
            "💡 **Want to share this to #thinking-showcase?**\n\n"
            "You can share your framed question publicly so others can learn from your thinking. "
            "Or keep it private - it's up to you!\n\n"
            "Type **share** to publish, or **keep private** to continue working."
        )

        logger.info(
            f"Successfully handled /frame for {discord_id} | "
            f"Tokens: {cost_data.get('total_tokens', 0)} | "
            f"Cost: ${cost_data.get('total_cost_usd', 0.0):.4f}"
        )

    except Exception as e:
        # Graceful fallback if API fails
        logger.error(f"Error in handle_frame for {discord_id}: {e}")

        await dm_channel.send(
            "**⏸️ The Framer is taking a short break.**\n\n"
            "Try this on your own:\n"
            "1. **PAUSE**: What do you actually want to know?\n"
            "2. **ADD CONTEXT**: What's your situation?\n\n"
            f"Your question: _{user_message}_\n\n"
            "**You're practicing Habit 1 (⏸️ PAUSE) - you've got this!**\n\n"
            "Try /frame again in a moment."
        )
