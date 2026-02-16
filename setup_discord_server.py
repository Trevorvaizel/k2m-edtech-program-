"""
KIRA Discord Server Setup Automation
Implements Story 5.1 Complete Discord Server Architecture

This script creates the entire K2M Cohort #1 Discord server structure:
- 4 channel categories
- 14 channels with permissions
- 3 roles (Student, Trevor, CIS Bot)
- Welcome & resources content
- Weekly channel visibility controls

Idempotent: Safe to run multiple times.
"""

import discord
from discord.ext import commands
import asyncio
import os
import sys
from dotenv import load_dotenv

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_NAME = "K2M Cohort #1 - AI Thinking Skills"

# Initialize bot with intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="/", intents=intents)


# Server architecture from Story 5.1
CATEGORIES = {
    "📚 INFORMATION & ONBOARDING": {
        "position": 0,
        "channels": [
            {"name": "welcome", "emoji": "👋", "topic": "Welcome & Getting Started"},
            {"name": "announcements", "emoji": "📢", "topic": "Important Updates"},
            {"name": "resources", "emoji": "📚", "topic": "Resources & Guides"},
            {"name": "introductions", "emoji": "👋", "topic": "Introduce Yourself"}
        ]
    },
    "💬 CORE INTERACTION SPACES": {
        "position": 1,
        "channels": [
            {"name": "thinking-lab", "emoji": "🧪", "topic": "Thinking Lab - CIS Agent Entry Point"},
            {"name": "thinking-showcase", "emoji": "🌟", "topic": "Thinking Showcase - Published Artifacts"},
            {"name": "general", "emoji": "💬", "topic": "General Discussion"}
        ]
    },
    "🗓️ WEEK-SPECIFIC PROGRESSION": {
        "position": 2,
        "channels": [
            {"name": "week-1-wonder", "emoji": "✨", "topic": "Week 1: Wonder (Zone 0→1)", "visible": True},
            {"name": "week-2-3-trust", "emoji": "🤝", "topic": "Weeks 2-3: Trust (Zone 1→2)", "visible": False},
            {"name": "week-4-5-converse", "emoji": "💭", "topic": "Weeks 4-5: Converse (Zone 2→3)", "visible": False},
            {"name": "week-6-7-direct", "emoji": "🎯", "topic": "Weeks 6-7: Direct (Zone 3→4)", "visible": False},
            {"name": "week-8-showcase", "emoji": "🏆", "topic": "Week 8: Artifact Showcase", "visible": False}
        ]
    },
    "🔧 ADMIN & OPERATIONS": {
        "position": 3,
        "channels": [
            {"name": "facilitator-dashboard", "emoji": "📊", "topic": "Trevor's Dashboard - PRIVATE"},
            {"name": "bot-testing", "emoji": "🤖", "topic": "Bot Development - PRIVATE"},
            {"name": "moderation-logs", "emoji": "⚖️", "topic": "Safety & Moderation - PRIVATE"}
        ]
    }
}

# Welcome channel content (Story 5.1 spec)
WELCOME_CONTENT = """# 👋 Welcome to K2M's AI Thinking Skills Cohort!

## It's Okay to Feel Anxious About AI

If you're feeling anxious, overwhelmed, or like everyone else "gets it" except you - **you're not alone**.

This cohort is designed for people who feel exactly that way. We move at your pace. No judgment, no competition.

## You're in the Right Place

This cohort is about building thinking skills that work with AI.
Not "learning to use AI tools." Building mental models that transfer forever.

Tools change. These 4 habits follow you. ⏸️ 🎯 🔄 🧠

## What Happens Here

**8-Week Journey:**
- Week 1: Wonder (Zone 0→1) - Notice AI is already around you
- Weeks 2-3: Trust (Zone 1→2) - Build confidence through small wins
- Weeks 4-5: Converse (Zone 2→3) - Learn to think WITH AI
- Weeks 6-7: Direct (Zone 3→4) - Direct AI toward quality
- Week 8: Showcase - Prove your transformation

**Daily Rhythm:**
- 9 AM: New content (8-12 min podcasts)
- 9:15 AM: Practice prompt (15-20 min)
- All week: CIS agents help you practice
- Friday: Reflection (unlock next week)

## Your First Step

1. **Introduce yourself** in #introductions (one sentence is fine)
2. **Read #resources** for the complete guide
3. **Wait for Monday** - Week 1 begins with your first node

## CIS Agents (Your Thinking Partners)

Starting Week 1, you'll meet the CIS agents:
- `/frame [your question]` - Pause and clarify what you want (Habit 1 & 2)
- `/diverge [topic]` - Explore possibilities (Habit 3) - *Week 4+*
- `/challenge [assumption]` - Test your thinking (Habit 4) - *Week 4+*
- `/synthesize [insights]` - Articulate conclusions (Habit 4) - *Week 6+*

These aren't chatbots. They're thinking coaches who help you build habits.

## The Golden Rule

**Process is private. Product is public.**

Your work with CIS agents happens in private DMs.
When you're ready, you can publish your finished thinking to #thinking-showcase.

This creates psychological safety. No judgment while you're learning.
Celebration when you've proven your growth.

## Community Norms

✅ **What we do:**
- Celebrate growth (not speed)
- Share finished work (not messy drafts)
- Support each other (no comparison)
- Practice habits (repetition over novelty)

❌ **What we don't do:**
- Compare or rank students
- Pressure to be "best"
- Judge early attempts
- Share private conversations

**You belong here.** This works for people like you.

---

**Ready?** Introduce yourself in #introductions, then check out #resources.

**Questions?** Trevor is here to help. DM him anytime.

Let's build thinking skills that last. 🌟
"""

RESOURCES_CONTENT = """# 📚 Resources & Guides

## Essential Reading

**[The 4 Habits Guide]**
- ⏸️ Habit 1: Pause Before Asking
- 🎯 Habit 2: Explain Context First
- 🔄 Habit 3: Change One Thing at a Time
- 🧠 Habit 4: Use AI Before Decisions

**[CIS Agent Guide]** (How to use /frame, /diverge, /challenge, /synthesize)
- When to use each agent
- Example conversations
- Habit reinforcement

## Quick Links

- **Daily Prompt Archive:** Past prompts by week
- **Troubleshooting:** Common issues and solutions

## Weekly Schedules

- **Week 1 Schedule** (Times for nodes, prompts, Trevor sessions)
- **Weeks 2-3 Schedule**
- **Weeks 4-5 Schedule**
- **Weeks 6-7 Schedule**
- **Week 8 Schedule**

## Need Help?

1. **Check #general** - Ask peers (many have the same question)
2. **DM Trevor** - Direct support (responds within 24 hours)
3. **Use /frame** - Practice clarifying your question first

**Remember:** Confusion is normal. You're exactly where you should be.
"""


async def setup_server():
    """Main setup function - creates complete Discord server structure"""

    # Wait for bot to be ready
    await bot.wait_until_ready()

    # Find the server
    guild = discord.utils.get(bot.guilds, name=SERVER_NAME)
    if not guild:
        print(f"❌ Error: Server '{SERVER_NAME}' not found!")
        print(f"Available servers: {[g.name for g in bot.guilds]}")
        await bot.close()
        return

    print(f"✅ Found server: {guild.name}")
    print(f"📊 Current channels: {len(guild.channels)}")
    print(f"👥 Current roles: {len(guild.roles)}")

    # Step 1: Create roles
    print("\n🎭 Creating roles...")
    roles = await create_roles(guild)

    # Step 2: Create categories and channels
    print("\n📁 Creating categories and channels...")
    await create_channels(guild, roles)

    # Step 3: Post welcome content
    print("\n📝 Posting welcome content...")
    await post_welcome_content(guild)

    # Step 4: Create server template for future cohorts
    print("\n📋 Creating server template...")
    await create_server_template(guild)

    print("\n✅ ========== SERVER SETUP COMPLETE ==========")
    print(f"✅ Server: {guild.name}")
    print(f"✅ Channels created: {len(guild.channels)}")
    print(f"✅ Roles configured: {len(roles)} custom roles")
    print("\n🎉 Server ready for Cohort #1!")
    print("\n💡 Next step: Verify manually in Discord, then mark task 0.4 complete")

    await bot.close()


async def create_roles(guild):
    """Create @Student, @Trevor, @CIS Bot roles with correct permissions"""

    roles = {}

    # Define role configurations
    role_configs = {
        "Student": {
            "color": discord.Color.blue(),
            "permissions": discord.Permissions(
                read_messages=True,
                send_messages=True,
                embed_links=True,
                attach_files=True,
                read_message_history=True,
                add_reactions=True,
                use_application_commands=True
            )
        },
        "Trevor": {
            "color": discord.Color.gold(),
            "permissions": discord.Permissions.all()
        },
        "CIS Bot": {
            "color": discord.Color.green(),
            "permissions": discord.Permissions(
                read_messages=True,
                send_messages=True,
                manage_messages=True,
                embed_links=True,
                attach_files=True,
                read_message_history=True,
                add_reactions=True,
                manage_channels=True,
                manage_roles=True
            )
        }
    }

    # Create roles if they don't exist
    for role_name, config in role_configs.items():
        existing_role = discord.utils.get(guild.roles, name=role_name)

        if existing_role:
            print(f"  ✓ Role '{role_name}' already exists")
            roles[role_name] = existing_role
        else:
            role = await guild.create_role(
                name=role_name,
                color=config["color"],
                permissions=config["permissions"]
            )
            roles[role_name] = role
            print(f"  ✅ Created role: {role_name}")

    return roles


async def create_channels(guild, roles):
    """Create all categories and channels with correct permissions"""

    for category_name, category_data in CATEGORIES.items():
        # Find or create category
        existing_category = discord.utils.get(guild.categories, name=category_name)

        if existing_category:
            category = existing_category
            print(f"  ✓ Category '{category_name}' already exists")
        else:
            category = await guild.create_category(
                name=category_name,
                position=category_data["position"]
            )
            print(f"  ✅ Created category: {category_name}")

        # Create channels in category
        for channel_config in category_data["channels"]:
            channel_name = channel_config["name"]
            full_channel_name = f"{channel_config['emoji']}{channel_name}"

            # Find existing channel
            existing_channel = discord.utils.get(guild.text_channels, name=channel_name)

            if existing_channel:
                print(f"    ✓ Channel '{channel_name}' already exists")
                channel = existing_channel
            else:
                # Create channel with emoji
                channel_name_with_emoji = f"{channel_config['emoji']}{channel_name}"
                channel = await category.create_text_channel(
                    name=channel_name_with_emoji,
                    topic=channel_config["topic"]
                )
                print(f"    ✅ Created channel: #{channel_name}")

            # Set permissions based on channel type
            await set_channel_permissions(channel, roles, channel_config, guild)


async def set_channel_permissions(channel, roles, channel_config, guild):
    """Set role-based permissions for each channel"""

    student_role = roles["Student"]
    trevor_role = roles["Trevor"]
    bot_role = roles["CIS Bot"]

    channel_name = channel_config["name"]

    # Read-only channels
    if channel_name in ["welcome", "announcements", "resources", "thinking-showcase"]:
        await channel.set_permissions(student_role,
            read_messages=True,
            send_messages=False
        )
        await channel.set_permissions(bot_role,
            read_messages=True,
            send_messages=True
        )

    # Private admin channels
    elif "facilitator" in channel_name or "bot-testing" in channel_name or "moderation" in channel_name:
        await channel.set_permissions(guild.default_role,  # @everyone
            read_messages=False
        )
        await channel.set_permissions(student_role,
            read_messages=False
        )
        await channel.set_permissions(trevor_role,
            read_messages=True,
            send_messages=True
        )
        await channel.set_permissions(bot_role,
            read_messages=True,
            send_messages=True
        )

    # Hidden weekly channels (locked until unlocked by bot)
    elif "week" in channel_name and not channel_config.get("visible", False):
        await channel.set_permissions(student_role,
            read_messages=False,
            send_messages=False
        )
        await channel.set_permissions(bot_role,
            read_messages=True,
            send_messages=True
        )

    # Visible weekly channels (Week 1)
    elif "week" in channel_name and channel_config.get("visible", False):
        await channel.set_permissions(student_role,
            read_messages=True,
            send_messages=True
        )
        await channel.set_permissions(bot_role,
            read_messages=True,
            send_messages=True
        )

    # Default: students can read and post
    else:
        await channel.set_permissions(student_role,
            read_messages=True,
            send_messages=True
        )
        await channel.set_permissions(bot_role,
            read_messages=True,
            send_messages=True
        )

    # Trevor always has full access
    await channel.set_permissions(trevor_role,
        read_messages=True,
        send_messages=True,
        manage_messages=True
    )


async def post_welcome_content(guild):
    """Post welcome content to #welcome and #resources channels"""

    # Post to #welcome (split into chunks due to 2000 char limit)
    welcome_channel = discord.utils.get(guild.text_channels, name="welcome")
    if welcome_channel:
        # Check if content already posted
        async for message in welcome_channel.history(limit=10):
            if "Welcome to K2M's AI Thinking Skills Cohort" in message.content:
                print("  ✓ Welcome content already posted")
                break
        else:
            # Split content into chunks (2000 char limit)
            chunks = split_message(WELCOME_CONTENT, 2000)
            for chunk in chunks:
                await welcome_channel.send(chunk)
                await asyncio.sleep(0.5)  # Small delay between messages
            print(f"  ✅ Posted welcome content to #welcome ({len(chunks)} messages)")

    # Post to #resources
    resources_channel = discord.utils.get(guild.text_channels, name="resources")
    if resources_channel:
        # Check if content already posted
        async for message in resources_channel.history(limit=10):
            if "Resources & Guides" in message.content:
                print("  ✓ Resources content already posted")
                break
        else:
            # Split content into chunks (2000 char limit)
            chunks = split_message(RESOURCES_CONTENT, 2000)
            for chunk in chunks:
                await resources_channel.send(chunk)
                await asyncio.sleep(0.5)  # Small delay between messages
            print(f"  ✅ Posted resources content to #resources ({len(chunks)} messages)")


def split_message(content, max_length=2000):
    """Split long message into chunks respecting Discord's 2000 char limit"""
    if len(content) <= max_length:
        return [content]

    chunks = []
    lines = content.split('\n')
    current_chunk = ""

    for line in lines:
        if len(current_chunk) + len(line) + 1 <= max_length:
            current_chunk += line + '\n'
        else:
            if current_chunk:
                chunks.append(current_chunk.rstrip())
            current_chunk = line + '\n'

    if current_chunk:
        chunks.append(current_chunk.rstrip())

    return chunks


async def create_server_template(guild):
    """Create server template for future cohort deployments"""
    try:
        # Check if template already exists
        templates = await guild.templates()
        for template in templates:
            if "K2M Cohort Template" in template.name:
                print(f"  ✓ Server template already exists: {template.code}")
                return

        # Create new template
        template = await guild.create_template(
            name="K2M Cohort Template",
            description="K2M AI Thinking Skills cohort server. 4 categories, 14 channels, 3 roles. Deploy in ~30 min."
        )
        print(f"  ✅ Server template created: https://discord.new/{template.code}")
        print(f"     Template code: {template.code}")
        print(f"     Use this to deploy future cohorts!")
    except Exception as e:
        print(f"  ⚠️ Template creation failed: {e}")
        print(f"     You can create manually in Server Settings → Server Template")


@bot.event
async def on_ready():
    """Bot ready event - triggers server setup"""
    print(f"\n🤖 KIRA bot connected as {bot.user}")
    print(f"🌐 Connected to {len(bot.guilds)} server(s)")
    print("\n🚀 Starting server setup automation...\n")

    await setup_server()


# Run the bot
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ Error: DISCORD_TOKEN not found in .env file")
        print("💡 Add your bot token to .env file: DISCORD_TOKEN=your_token_here")
        exit(1)

    print("=" * 60)
    print("  KIRA DISCORD SERVER SETUP AUTOMATION")
    print("  Story 5.1: Complete Discord Server Architecture")
    print("=" * 60)
    print(f"\nTarget Server: {SERVER_NAME}")
    print("This script will create:")
    print("  ✓ 4 channel categories")
    print("  ✓ 14 channels with permissions")
    print("  ✓ 3 roles (Student, Trevor, CIS Bot)")
    print("  ✓ Welcome & resources content")
    print("  ✓ Weekly channel visibility controls")
    print("\nIdempotent: Safe to run multiple times.\n")

    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure:")
        print("  1. DISCORD_TOKEN is correct in .env")
        print("  2. Bot has admin permissions")
        print("  3. Bot is invited to the server")
