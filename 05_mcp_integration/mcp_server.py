# ============================================================
# 05 - Local MCP Server — stdio transport
# ============================================================

# --- SECTION 1: IMPORTS ---
import asyncio
import datetime
import json
import os
import sys

from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# --- SECTION 2: SERVER SETUP ---
app = Server("local-dev-tools")


# --- SECTION 3: ADVERTISE TOOLS ---
@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_datetime",
            description="Returns the current local date, time, and day of the week.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="calculate",
            description="Evaluates a safe math expression and returns the result.",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression e.g. '2 + 2' or '10 ** 3'",
                    }
                },
                "required": ["expression"],
            },
        ),
        types.Tool(
            name="list_directory",
            description="Lists all files and folders in a given directory path.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to list, e.g. '.' for current directory",
                    }
                },
                "required": ["path"],
            },
        ),
        types.Tool(
            name="read_file",
            description="Reads and returns the text content of a local file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the file to read",
                    }
                },
                "required": ["filepath"],
            },
        ),
        types.Tool(
            name="write_file",
            description="Writes text content to a local file (creates or overwrites).",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to write to"},
                    "content": {"type": "string", "description": "Text to write"},
                },
                "required": ["filepath", "content"],
            },
        ),
        types.Tool(
            name="get_system_info",
            description="Returns OS name, Python version, and current working directory.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]


# --- SECTION 4: TOOL HANDLERS ---
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "get_datetime":
        result = datetime.datetime.now().strftime("Date: %Y-%m-%d | Time: %H:%M:%S | Day: %A")

    elif name == "calculate":
        expr = arguments["expression"]
        try:
            value = eval(expr, {"__builtins__": {}})
            result = f"{expr} = {value}"
        except Exception as e:
            result = f"Error: {e}"

    elif name == "list_directory":
        path = arguments["path"]
        try:
            entries = sorted(os.listdir(path))
            lines = [f"{'📁' if os.path.isdir(os.path.join(path, e)) else '📄'} {e}" for e in entries]
            result = f"Contents of '{path}':\n" + "\n".join(lines)
        except Exception as e:
            result = f"Error: {e}"

    elif name == "read_file":
        fp = arguments["filepath"]
        try:
            with open(fp, "r") as f:
                result = f"Contents of '{fp}':\n{f.read()}"
        except Exception as e:
            result = f"Error: {e}"

    elif name == "write_file":
        fp, content = arguments["filepath"], arguments["content"]
        try:
            with open(fp, "w") as f:
                f.write(content)
            result = f"✅ Written {len(content)} chars to '{fp}'"
        except Exception as e:
            result = f"Error: {e}"

    elif name == "get_system_info":
        import platform

        result = json.dumps(
            {
                "os": platform.system(),
                "os_version": platform.version(),
                "python": sys.version,
                "cwd": os.getcwd(),
            },
            indent=2,
        )

    else:
        result = f"Unknown tool: {name}"

    return [types.TextContent(type="text", text=result)]


# --- SECTION 5: START SERVER ---
async def main():
    print("🚀 MCP stdio server started (6 tools available).", file=sys.stderr, flush=True)
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
