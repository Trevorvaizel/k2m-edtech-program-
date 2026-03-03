#!/usr/bin/env python3
"""
Quick Bot Diagnostic Test
Tests if the bot can connect and whether provider config is valid.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from cis_controller.llm_integration import (
    get_active_model,
    get_active_provider,
    validate_provider_configuration,
)

# Load environment
BOT_DIR = Path(__file__).resolve().parent
if not load_dotenv(dotenv_path=BOT_DIR / ".env", override=False):
    load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
AI_PROVIDER = get_active_provider()
LLM_MODEL = get_active_model(AI_PROVIDER)
provider_ok, provider_details = validate_provider_configuration()

print("=" * 60)
print("K2M CIS Bot Diagnostic")
print("=" * 60)

# Check Discord Token
if DISCORD_TOKEN and DISCORD_TOKEN != "your_discord_bot_token_here":
    print("DISCORD_TOKEN: configured")
    print(f"  Token prefix: {DISCORD_TOKEN[:20]}...")
else:
    print("DISCORD_TOKEN: NOT configured")
    print("  -> Get from https://discord.com/developers/applications")
    sys.exit(1)

# Check active provider configuration
if provider_ok:
    print(f"AI provider: ready ({AI_PROVIDER} / {LLM_MODEL})")
    print(f"  Details: {provider_details}")
else:
    print(f"AI provider: invalid ({AI_PROVIDER} / {LLM_MODEL})")
    print(f"  Details: {provider_details}")
    print("  -> /frame may fall back until provider config is fixed")

print()
print("=" * 60)
print("Bot Architecture Check")
print("=" * 60)

required_files = [
    "main.py",
    "cis_controller/router.py",
    "cis_controller/llm_integration.py",
    "commands/frame.py",
    "database/store.py",
    "agents/framer_prompt.py",
]

for path in required_files:
    if os.path.exists(path):
        print(f"OK  {path}")
    else:
        print(f"MISSING  {path}")

print()
print("=" * 60)
print("Start Bot Test")
print("=" * 60)
print()
print("1) Run: python main.py")
print("2) In Discord, run slash command: /ping")
print("3) In #thinking-lab or #bot-testing, run: /frame <question>")
print()
print("Expected:")
print("- /ping responds with latency")
print("- /frame routes to private DM response")
print("- /framer works as alias to /frame")
print()

try:
    import discord  # noqa: F401

    print("discord.py: installed")
except ImportError:
    print("discord.py: NOT installed - run: pip install -r requirements.txt")
    sys.exit(1)

try:
    import anthropic  # noqa: F401

    print("anthropic SDK: installed")
except ImportError:
    print("anthropic SDK: not installed (only needed for AI_PROVIDER=anthropic)")

print()
print("Ready to start bot. Run: python main.py")
