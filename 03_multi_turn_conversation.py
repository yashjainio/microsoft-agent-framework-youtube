# ============================================================
# 03 - Agent Sessions & Multi-Turn Conversations
# ============================================================


# --- SECTION 1: IMPORTS ---
import asyncio
import warnings

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

warnings.simplefilter("ignore")

# --- SECTION 2: CONFIGURATION ---
load_dotenv()

# --- SECTION 3: AGENT DEFINITION ---
agent = Agent(
    client=OpenAIChatClient(),
    name="MemoryAgent",
    instructions=(
        "You are a helpful personal assistant. " "Remember everything the user tells you in this conversation."
    ),
)


# --- SECTION 4A: WITHOUT SESSION — stateless (default) ---
async def demo_no_memory():
    print("=== WITHOUT SESSION (stateless — default behaviour) ===\n")

    query = "My name is Yash."
    await agent.run("My name is Yash.")
    print(f"Query: {query}")

    query = "What is my name?"
    response = await agent.run(query)  # no session → no memory
    print(f"\nQuery: {query}")
    print(f"Result: {response}")
    print("👆 Agent has no idea — each call is a fresh conversation.")
    input()


# --- SECTION 4B: WITH SESSION — persistent memory ---
async def demo_with_memory():
    print("\n\n=== WITH SESSION (stateful — multi-turn memory) ===\n")

    session = agent.create_session()  # creates a conversation history container

    query = "My name is Yash. I am a backend developer in Bengaluru."
    response_1 = await agent.run(query, session=session)
    print(f"Query: {query}")
    print(f"Turn 1: {response_1}")

    query = "I am currently learning Microsoft Agent Framework."
    response_2 = await agent.run(query, session=session)
    print(f"\nQuery: {query}")
    print(f"Turn 2: {response_2}")

    query = "What is my name, city, and what am I learning?"
    response_3 = await agent.run(query, session=session)
    print(f"\nQuery: {query}")
    print(f"Turn 3 (recall): {response_3}")

    query = "Suggest a side project I can build to practise MAF."
    r4 = await agent.run(query, session=session)
    print(f"\nQuery: {query}")
    print(f"Turn 4 (context-aware): {r4}")
    input()


# --- SECTION 4C: TWO SEPARATE SESSIONS — two independent conversations ---
async def demo_two_sessions():
    print("\n\n=== TWO SESSIONS — two independent conversations ===\n")

    session_a = agent.create_session()
    session_b = agent.create_session()

    await agent.run("My name is Yash.", session=session_a)
    await agent.run("My name is Codex.", session=session_b)

    response_a = await agent.run("What is my name?", session=session_a)
    response_b = await agent.run("What is my name?", session=session_b)

    print(f"Session A: {response_a}")  # → Yash
    print(f"Session B: {response_b}")  # → Codex
    print("👆 Two sessions = two completely separate conversations.\n")


async def main():
    await demo_no_memory()
    await demo_with_memory()
    await demo_two_sessions()


asyncio.run(main())
