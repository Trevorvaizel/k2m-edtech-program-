"""
Quick Fix: Add emoji prefixes to existing Discord channels
Renames channels without deleting them (preserves message history)
"""

import sys
import discord
import os
from dotenv import load_dotenv

# Fix UTF-8 encoding on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

# Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SERVER_NAME = "K2M Cohort #1 - AI Thinking Skills"

# Channel emoji mappings (from Story 5.1 spec)
CHANNEL_EMOJIS = {
    # Information & Onboarding
    "welcome": "👋",
    "announcements": "📢",
    "resources": "📚",
    "introductions": "🤝",

    # Core Interaction Spaces
    "thinking-lab": "🧪",
    "thinking-showcase": "✨",
    "general": "💬",

    # Weekly Progression
    "week-1-wonder": "🌟",
    "week-2-3-trust": "🤝",
    "week-4-5-converse": "💭",
    "week-6-7-direct": "🎯",
    "week-8-showcase": "🎊",

    # Admin & Operations
    "facilitator-dashboard": "📊",
    "bot-testing": "🤖",
    "moderation-logs": "🛡️"
}

# Setup Discord client
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = discord.Client(intents=intents)


@bot.event
async def on_ready():
    """Rename channels to add emoji prefixes"""

    print("=" * 60)
    print("  CHANNEL EMOJI FIX SCRIPT")
    print("=" * 60)

    # Find server
    guild = discord.utils.get(bot.guilds, name=SERVER_NAME)
    if not guild:
        print(f"❌ Error: Server '{SERVER_NAME}' not found!")
        await bot.close()
        return

    print(f"✅ Found server: {guild.name}\n")

    renamed_count = 0
    skipped_count = 0

    # Process each channel that needs emoji
    for channel_name, emoji in CHANNEL_EMOJIS.items():
        # Find channel (try with and without emoji)
        channel = discord.utils.get(guild.text_channels, name=channel_name)

        if channel:
            # Channel exists without emoji
            new_name = f"{emoji}{channel_name}"

            # Check if it already has emoji
            if channel.name.startswith(emoji):
                print(f"  ⏭️  #{channel.name} - Already has emoji")
                skipped_count += 1
            else:
                try:
                    await channel.edit(name=new_name)
                    print(f"  ✅ Renamed: #{channel_name} → #{new_name}")
                    renamed_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to rename #{channel_name}: {e}")
        else:
            # Try to find with emoji already
            channel_with_emoji = discord.utils.get(guild.text_channels, name=f"{emoji}{channel_name}")
            if channel_with_emoji:
                print(f"  ⏭️  #{channel_with_emoji.name} - Already correct")
                skipped_count += 1
            else:
                print(f"  ⚠️  Channel '{channel_name}' not found (may not exist yet)")

    print(f"\n✅ Emoji fix complete!")
    print(f"   Renamed: {renamed_count} channels")
    print(f"   Skipped: {skipped_count} channels (already correct)")

    await bot.close()


# Run the bot
if __name__ == "__main__":
    print("\nStarting emoji fix script...")
    print("This will rename channels to add emoji prefixes.\n")

    bot.run(DISCORD_TOKEN)
