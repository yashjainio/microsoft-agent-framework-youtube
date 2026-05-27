# ============================================================
# 12 - A2A Orchestrator — calls remote agent via HTTP
# ============================================================

import asyncio

from agent_framework import Agent
from agent_framework.a2a import A2AAgent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

load_dotenv()

remote_analyst = A2AAgent(
    url="http://localhost:8765",
    name="RemoteDataAnalyst",
    description="Remote data analyst agent that provides statistical insights.",
)

orchestrator = Agent(
    client=OpenAIChatClient(),
    name="OrchestratorAgent",
    instructions=(
        "You are a business manager. When data analysis is needed, delegate to RemoteDataAnalyst. "
        "Then synthesize the analyst's findings into a final business recommendation."
    ),
    tools=[remote_analyst.as_tool()],
)


async def main():
    prompt = (
        "Monthly sales: Jan=120k, Feb=95k, Mar=140k, Apr=160k, May=130k. "
        "Analyse the trend and advise if Yash should hire more sales staff this quarter."
    )
    print(f"💬 Yash: {prompt}\n")
    result = await orchestrator.run(prompt)
    print(f"🤖 Orchestrator (via A2A): {result}")


asyncio.run(main())
