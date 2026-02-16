"""
Discord Server Template Creation
Attempts to create a server template via Discord API
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

# Setup Discord client
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = discord.Client(intents=intents)


@bot.event
async def on_ready():
    """Create server template"""

    print("=" * 60)
    print("  DISCORD SERVER TEMPLATE CREATION")
    print("=" * 60)

    # Find server
    guild = discord.utils.get(bot.guilds, name=SERVER_NAME)
    if not guild:
        print(f"❌ Error: Server '{SERVER_NAME}' not found!")
        await bot.close()
        return

    print(f"✅ Found server: {guild.name}\n")

    # Check if template already exists
    try:
        existing_templates = await guild.templates()
        if existing_templates:
            print(f"📋 Existing templates found: {len(existing_templates)}")
            for template in existing_templates:
                print(f"   - {template.name}: {template.code}")
                print(f"     URL: https://discord.new/{template.code}")
            print("\n✅ Templates already exist. Use these for multi-cohort deployment.")
            await bot.close()
            return
    except Exception as e:
        print(f"⚠️  Could not check existing templates: {e}")

    # Create new template
    print("📋 Creating server template...")

    template_name = "K2M Cohort Template"
    template_description = "K2M AI Thinking Skills cohort. 4 categories, 15 channels, 3 roles. Deploy ~30 min."

    # Ensure description is under 120 chars
    if len(template_description) > 120:
        template_description = template_description[:117] + "..."

    print(f"   Name: {template_name}")
    print(f"   Description: {template_description} ({len(template_description)} chars)")

    try:
        template = await guild.create_template(
            name=template_name,
            description=template_description
        )

        print(f"\n✅ Template created successfully!")
        print(f"   Code: {template.code}")
        print(f"   URL: https://discord.new/{template.code}")
        print(f"\n🎉 Save this URL for future cohort deployments!")

    except discord.HTTPException as e:
        print(f"\n❌ HTTP Error creating template: {e}")
        print(f"   Status: {e.status}")
        print(f"   Code: {e.code}")
        print(f"   Text: {e.text}")

        if e.status == 403:
            print("\n💡 Permission issue. Try manual creation:")
            print("   1. Go to Server Settings → Server Template")
            print("   2. Click 'Create Template'")
            print(f"   3. Name: {template_name}")
            print(f"   4. Description: {template_description}")

        elif "already exists" in str(e).lower():
            print("\n💡 Template might already exist. Check Server Settings → Server Template")

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print(f"   Type: {type(e).__name__}")
        print("\n💡 Try manual creation in Server Settings → Server Template")

    await bot.close()


# Run the bot
if __name__ == "__main__":
    print("\nAttempting to create Discord server template...\n")
    bot.run(DISCORD_TOKEN)
