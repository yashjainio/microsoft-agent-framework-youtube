# ============================================================
# VIDEO 07 | MAF Agent using Local FastMCP stdio Server
# Microsoft Agent Framework v1.4.0
# pip install fastmcp "mcp --pre"
# STEP 1: Run mcp_server.py first (keep it running)
# STEP 2: Run this file
# ============================================================

# --- SECTION 1: IMPORTS ---
import asyncio
import sys
import warnings

from agent_framework import Agent, MCPStdioTool
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

warnings.simplefilter("ignore")

# --- SECTION 2: CONFIGURATION ---
load_dotenv()


# --- SECTION 3: RUN ---
async def main():
    async with (
        MCPStdioTool(
            name="local-dev-tools",  # must match FastMCP server name
            command=sys.executable,  # path to current Python interpreter
            args=["05_mcp_integration/mcp_server.py"],  # your FastMCP server script
        ) as mcp_tool,
        Agent(
            client=OpenAIChatClient(),
            name="MCPAgent",
            instructions=(
                "You are Yash's local developer assistant with filesystem and system tools via MCP. "
                "Always use the available tools for files, time, calculations, and system info. "
                "Never guess file contents — always read them."
            ),
        ) as agent,
    ):
        prompts = [
            "What is today's date and time?",
            "List all files in the current directory (path = '.')",
            "Write a file 'hello_maf.txt' with content: 'Hello from Yash using MAF + FastMCP!'",
            "Read the file 'hello_maf.txt' and tell me what is inside.",
            "What Python version am I running and what OS?",
            "Calculate 2 ** 10 + 24",
        ]

        for prompt in prompts:
            print(f"\n💬 Yash: {prompt}")
            # tools passed to agent.run() — NOT to Agent() constructor
            result = await agent.run(prompt, tools=mcp_tool)
            print(f"🤖 Agent: {result}")


asyncio.run(main())
