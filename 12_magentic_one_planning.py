# ============================================================
# 12 - Magentic-One Orchestration Pattern
# ============================================================

# --- SECTION 1: IMPORTS ---
import asyncio

from agent_framework import Agent, AgentResponse
from agent_framework.openai import OpenAIChatClient
from agent_framework.orchestrations import MagenticBuilder
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()
client = OpenAIChatClient()

# --- SECTION 3: SPECIALIST AGENTS ---
web_researcher = Agent(
    client=client,
    name="WebResearcher",
    instructions="You research topics and return structured findings with key facts.",
)
code_writer = Agent(
    client=client,
    name="CodeWriter",
    instructions="You write clean, well-commented Python code examples for given concepts.",
)
technical_writer = Agent(
    client=client,
    name="TechnicalWriter",
    instructions="You turn research and code into clear, developer-friendly documentation.",
)
quality_critic = Agent(
    client=client,
    name="QualityCritic",
    instructions=(
        "You review outputs for accuracy, completeness, and clarity. "
        "Return PASS if good, or list specific FIXES needed."
    ),
)
orchestrator = Agent(
    client=client,
    name="Orchestrator",
    instructions=(
        "You are a Magentic-One orchestrator. Plan which specialist agents to invoke "
        "and in what order to complete the task. Re-plan dynamically based on results."
        "Perform this task under 60 seconds."
    ),
)

# --- SECTION 4: MAGENTIC-ONE ---
# Plans which agents to use, in what order, re-plans dynamically.
workflow = MagenticBuilder(
    participants=[
        web_researcher,
        code_writer,
        technical_writer,
        quality_critic,
    ],
    manager_agent=orchestrator,
).build()


# --- SECTION 5: RUN & TEST ---
async def main():
    task = (
        "Create a developer guide for building a sequential multi-agent workflow "
        "using Microsoft Agent Framework v1.4.0. Include: "
        "1) A conceptual explanation, "
        "2) A working Python code example, "
        "3) Three best practices."
    )
    print("=" * 60)
    print(f"🎯 Task: {task}\n")
    print("🧠 Magentic-One planning and executing...\n")

    events = await workflow.run(task)
    outputs = events.get_outputs()
    if outputs:
        final: AgentResponse = outputs[0]
        for msg in final.messages:
            print(msg.text)


asyncio.run(main())
