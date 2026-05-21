# ============================================================
# 01 - Setup & Installation
# ============================================================

# --- SECTION 1: IMPORTS ---
import asyncio

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()


# --- SECTION 3: AGENT DEFINITION ---
# OpenAIChatClient() with no args reads OPENAI_API_KEY + OPENAI_MODEL from env.
agent = Agent(
    client=OpenAIChatClient(),
    name="SetupTestAgent",
    instructions="You are a helpful assistant. Reply in exactly one sentence.",
)


# --- SECTION 4: RUN & TEST ---
async def main():
    result = await agent.run(
        "Hello Everyone and Yash is going to teach Microsoft Agent Framework for building Agents!"
    )
    print(f"\n🤖 Agent: {result}")


asyncio.run(main())
