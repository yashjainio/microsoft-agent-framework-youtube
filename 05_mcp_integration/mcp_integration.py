# ============================================================
# 05 - MAF Agent using Local MCP stdio Server
# ============================================================

# --- SECTION 1: IMPORTS ---
import asyncio
import sys

from agent_framework import Agent, MCPStdioTool
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()


# --- SECTION 3: AGENT WITH MCP ---
async def main():
    async with MCPStdioTool(
        name="local_mcp",
        command=sys.executable,
        args=["05_mcp_integration/mcp_server.py"],
        load_prompts=False,
    ) as mcp_server:
        agent = Agent(
            client=OpenAIChatClient(),
            name="MCPAgent",
            instructions=(
                "You are a local developer assistant with filesystem and system tools via MCP. "
                "Always use the available tools for files, time, calculations, and system info. "
                "Never guess file contents — always read them."
            ),
            tools=mcp_server,
        )

        # Independent single-turn calls — no thread needed
        prompts = [
            "What is today's date and time?",
            "List all files in the current directory (path = '.')",
            "Write a file 'hello_maf.txt' with content: 'Hello from MAF + MCP via stdio!'",
            "Read the file 'hello_maf.txt' and tell me what is inside.",
            "What Python version am I running and what OS?",
            "Calculate 2 ** 10 + 24",
        ]

        for prompt in prompts:
            print(f"\n💬 User: {prompt}")
            result = await agent.run(prompt)
            print(f"🤖 Agent: {result}")


asyncio.run(main())
