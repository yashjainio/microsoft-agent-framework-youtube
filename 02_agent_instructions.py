# ============================================================
# 02 - Agent Instructions & System Prompts
# ============================================================

# --- SECTION 1: IMPORTS ---
import asyncio

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()

# One shared client — all agents reuse the same OpenAI connection.
client = OpenAIChatClient()

# --- SECTION 3: THREE AGENTS WITH DIFFERENT INSTRUCTIONS ---

tech_writer = Agent(
    client=client,
    name="TechWriter",
    instructions=(
        "You are a senior technical writer at Microsoft. "
        "Always respond in formal English with bullet points for lists. "
        "Never use slang, emojis, or casual language. "
        "End every response with: 'Refer to official documentation for details.'"
    ),
)

onboarding_bot = Agent(
    client=client,
    name="OnboardingBot",
    instructions=(
        "You are a warm, encouraging onboarding assistant for new developers. "
        "Use simple language and short sentences. "
        "Always end with an emoji and a motivational one-liner."
    ),
)

security_reviewer = Agent(
    client=client,
    name="SecurityReviewer",
    instructions=(
        "You are a strict security code reviewer. "
        "Look ONLY for: hardcoded secrets, SQL injection, missing input validation, "
        "insecure dependencies. Ignore style or formatting issues entirely. "
        "If no issues found, respond: 'No security issues detected.'"
    ),
)

# --- SECTION 4: RUN & TEST ---
TOPIC = "How do I store an API key in my Python application?"

CODE = """
import requests
API_KEY = "sk-1234abcd"   # hardcoded in source
def get_data():
    return requests.get(f"https://api.example.com?key={API_KEY}")
"""


async def main():
    print("=" * 60)
    print("SAME QUESTION — 3 DIFFERENT SYSTEM PROMPTS")
    print("=" * 60)

    response_1 = await tech_writer.run(TOPIC)
    print(f"\n📝 TechWriter:\n{response_1}")
    print("=" * 60)

    response_2 = await onboarding_bot.run(TOPIC)
    print(f"\n👋 OnboardingBot:\n{response_2}")
    print("=" * 60)

    response_3 = await security_reviewer.run(f"Review this code:\n{CODE}")
    print(f"\n🔐 SecurityReviewer:\n{response_3}")
    print("=" * 60)


asyncio.run(main())
