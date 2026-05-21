# ============================================================
# VIDEO 07 | Local MCP Server using FastMCP (stdio transport)
# pip install fastmcp "mcp --pre"
# Run: python mcp_server.py
# Keep running while mcp_integration.py connects to it.
# ============================================================

import datetime
import json
import os
import sys
import warnings

from fastmcp import FastMCP

warnings.simplefilter("ignore")

# --- SECTION 1: CREATE SERVER ---
mcp = FastMCP(name="local-dev-tools")


# --- SECTION 2: DEFINE TOOLS ---
@mcp.tool()
def get_datetime() -> str:
    """Returns the current local date, time, and day of the week."""
    return datetime.datetime.now().strftime("Date: %Y-%m-%d | Time: %H:%M:%S | Day: %A")


@mcp.tool()
def calculate(expression: str) -> str:
    """Evaluates a safe math expression and returns the result.

    Args:
        expression: Math expression e.g. '2 + 2' or '10 ** 3'
    """
    try:
        value = eval(expression, {"__builtins__": {}})
        return f"{expression} = {value}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def list_directory(path: str) -> str:
    """Lists all files and folders in a given directory path.

    Args:
        path: Directory path to list, e.g. '.' for current directory
    """
    try:
        entries = sorted(os.listdir(path))
        lines = [f"{'📁' if os.path.isdir(os.path.join(path, e)) else '📄'} {e}" for e in entries]
        return f"Contents of '{path}':\n" + "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def read_file(filepath: str) -> str:
    """Reads and returns the text content of a local file.

    Args:
        filepath: Path to the file to read
    """
    try:
        with open(filepath, "r") as f:
            return f"Contents of '{filepath}':\n{f.read()}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def write_file(filepath: str, content: str) -> str:
    """Writes text content to a local file (creates or overwrites).

    Args:
        filepath: Path to write to
        content: Text content to write
    """
    try:
        with open(filepath, "w") as f:
            f.write(content)
        return f"✅ Written {len(content)} chars to '{filepath}'"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def get_system_info() -> str:
    """Returns OS name, Python version, and current working directory."""
    import platform

    return json.dumps(
        {
            "os": platform.system(),
            "os_version": platform.version(),
            "python": sys.version,
            "cwd": os.getcwd(),
        },
        indent=2,
    )


# --- SECTION 3: START SERVER ---
if __name__ == "__main__":
    print("🚀 FastMCP server started (6 tools available).", file=sys.stderr, flush=True)
    mcp.run(transport="stdio")
