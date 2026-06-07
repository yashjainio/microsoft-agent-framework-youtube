# ============================================================
# 16 - Single Agent State Persistence
# ============================================================


# --- SECTION 1: IMPORTS ---
import asyncio

from agent_framework import Agent, FileHistoryProvider
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()
client = OpenAIChatClient()

HISTORY_PATH = ".agent_history"  # single-agent conversation persistence


# --- SECTION 3: SESSION PERSISTENCE WITH FileHistoryProvider ---
# FileHistoryProvider writes every message to disk.
# On the next run, the agent picks up exactly where it left off —
# process restart does NOT wipe the conversation.
persistent_agent = Agent(
    client=client,
    name="PersistentAssistant",
    instructions=(
        "You are a helpful assistant. Remember everything the user tells you "
        "across multiple sessions — they expect you to recall past conversations."
    ),
    context_providers=[FileHistoryProvider(HISTORY_PATH)],
)


# --- SECTION 4: DEMO HELPERS ---
async def demo_session_persistence():
    print("=" * 60)
    print("💾 SESSION PERSISTENCE — FileHistoryProvider")
    print("   (Run this script twice to see memory survive restarts)")
    print("=" * 60)

    turns = [
        "Hi! My name is Yash and I'm building a YouTube series on Microsoft Agent Framework.",
        "What was the series I told you about?",
        "How many videos do you think I should have in the series?",
    ]

    session = persistent_agent.create_session()
    for msg in turns:
        print(f"\n💬 Yash: {msg}")
        response = await persistent_agent.run(msg, session=session)
        print(f"🤖 Agent: {response.text}")


# --- SECTION 5: RUN & TEST ---
async def main():
    await demo_session_persistence()


asyncio.run(main())
