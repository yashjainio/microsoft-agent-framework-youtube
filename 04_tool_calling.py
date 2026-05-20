# ============================================================
# 04 Tools & Function Calling
# ============================================================

# --- SECTION 1: IMPORTS ---
import asyncio
import datetime
import json
from typing import Annotated

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()

# --- SECTION 3: TOOL DEFINITIONS ---
# Docstring = tool description (shown to the model).
# Annotated[type, "..."] = parameter description (shown to the model).


def get_current_datetime() -> str:
    """Returns the current local date, time, and day of the week."""
    now = datetime.datetime.now()
    return now.strftime("Date: %Y-%m-%d | Time: %H:%M:%S | Day: %A")


def calculate(expression: Annotated[str, "A math expression, e.g. '2 + 2' or '(10 ** 3) / 4'"]) -> str:
    """Evaluates a safe mathematical expression and returns the numeric result."""
    try:
        result = eval(expression, {"__builtins__": {}})
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error: {e}"


def get_weather(city: Annotated[str, "City name, e.g. 'Bengaluru' or 'London'"]) -> str:
    """Returns current weather conditions for a city (mock data for demo)."""
    mock = {
        "bengaluru": {"temp": "24°C", "condition": "Partly Cloudy", "humidity": "65%"},
        "mumbai": {"temp": "32°C", "condition": "Hot and Humid", "humidity": "80%"},
        "delhi": {"temp": "38°C", "condition": "Sunny", "humidity": "30%"},
        "london": {"temp": "15°C", "condition": "Rainy", "humidity": "85%"},
    }
    data = mock.get(city.lower(), {"temp": "N/A", "condition": "City not found", "humidity": "N/A"})
    return json.dumps(data)


def save_note(
    filename: Annotated[str, "Filename to save, e.g. 'notes.txt'"],
    content: Annotated[str, "Text content to write into the file"],
) -> str:
    """Saves a text note to a local file on disk."""
    try:
        with open(filename, "w") as f:
            f.write(content)
        return f"✅ Saved '{filename}' ({len(content)} chars)"
    except Exception as e:
        return f"❌ Error: {e}"


# --- SECTION 4: AGENT WITH TOOLS ---
agent = Agent(
    client=OpenAIChatClient(),
    name="ToolAgent",
    instructions=(
        "You are a helpful assistant with tools. "
        "Always use a tool when asked for real data like time, weather, or math. "
        "Never guess numbers or dates."
    ),
    tools=[
        get_current_datetime,
        calculate,
        get_weather,
        save_note,
    ],
)


# --- SECTION 5: RUN & TEST ---
# These are all independent single-turn calls — no thread needed.
async def main():
    prompts = [
        "What is today's date and time?",
        "Calculate (10 * 99) + 10",
        "What is the weather in Bengaluru?",
        "Save a note called 'maf_notes.txt' with content: 'Tools in Microsoft Agent Framework are awesome!'",
    ]
    for prompt in prompts:
        print(f"\n💬 {prompt}")
        result = await agent.run(prompt)
        print(f"🤖 {result}")


asyncio.run(main())
