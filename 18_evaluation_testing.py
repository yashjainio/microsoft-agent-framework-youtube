# ============================================================
# 18 - Evaluation & Testing Agents
# ============================================================


# --- SECTION 1: IMPORTS ---
import asyncio
from typing import Annotated

from agent_framework import (
    Agent,
    EvalItem,
    EvalResults,
    LocalEvaluator,
    evaluate_agent,
    keyword_check,
    tool_called_check,
)
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()
client = OpenAIChatClient()


# --- SECTION 3: AGENT UNDER TEST ---
def get_weather(city: Annotated[str, "City name, e.g. 'Bengaluru'"]) -> str:
    """Returns current weather for a city (mock data)."""
    mock = {
        "bengaluru": "24°C, Partly Cloudy",
        "mumbai": "32°C, Hot and Humid",
        "delhi": "38°C, Sunny",
        "london": "15°C, Rainy",
    }
    return mock.get(city.lower(), "City not found")


def calculate(expression: Annotated[str, "A math expression, e.g. '2 + 2'"]) -> str:
    """Evaluates a mathematical expression."""
    try:
        return str(eval(expression, {"__builtins__": {}}))
    except Exception as e:
        return f"Error: {e}"


weather_agent = Agent(
    client=client,
    name="WeatherAgent",
    instructions=(
        "You are a weather assistant. Always use the get_weather tool for weather queries. "
        "For math questions, use the calculate tool."
    ),
    tools=[get_weather, calculate],
)


# --- SECTION 4: EVALUATORS ---
# LocalEvaluator runs checks offline — no extra API calls needed.
# Useful for CI pipelines and fast iteration.

# Check 1 — keyword presence: did the response mention the city's weather data?
keyword_evaluator = LocalEvaluator(
    keyword_check("cloudy", "sunny", "rainy", "humid"),  # at least one weather word
)

# Check 2 — tool usage: did the agent actually call get_weather?
tool_evaluator = LocalEvaluator(
    tool_called_check("get_weather"),
)


# Check 3 — custom check: no-tool response is a failure
def no_tool_call_is_failure(item: EvalItem) -> bool:
    """Fails if the agent answered without calling any tool at all."""
    from agent_framework import tool_calls_present

    result = tool_calls_present(item)
    return result.passed


# --- SECTION 5: TEST CASES ---
weather_queries = [
    "What's the weather like in Bengaluru?",
    "Is it raining in London?",
    "Tell me about the weather in Delhi.",
]

expected_keywords = [
    ["24", "cloudy", "bengaluru"],
    ["15", "rainy", "london"],
    ["38", "sunny", "delhi"],
]


# --- SECTION 6: RUN EVALS ---
async def run_keyword_eval():
    print("=" * 60)
    print("🔬 EVAL 1: Keyword Check — does the response contain weather words?")
    print("=" * 60)
    results: list[EvalResults] = await evaluate_agent(
        agent=weather_agent,
        queries=weather_queries,
        evaluators=keyword_evaluator,
        eval_name="WeatherKeywordEval",
    )
    for result in results:
        status = "✅ PASS" if result.all_passed else "❌ FAIL"
        print(f"  {status} — passed: {result.passed}, failed: {result.failed}, total: {result.total}")


async def run_tool_eval():
    print("\n" + "=" * 60)
    print("🔬 EVAL 2: Tool Call Check — did the agent use get_weather?")
    print("=" * 60)
    results: list[EvalResults] = await evaluate_agent(
        agent=weather_agent,
        queries=weather_queries,
        evaluators=tool_evaluator,
        eval_name="WeatherToolEval",
    )
    for result in results:
        status = "✅ PASS" if result.all_passed else "❌ FAIL"
        print(f"  {status} — passed: {result.passed}, failed: {result.failed}, total: {result.total}")


async def run_combined_eval():
    print("\n" + "=" * 60)
    print("🔬 EVAL 3: Combined — keyword + tool call checks together")
    print("=" * 60)
    combined = LocalEvaluator(
        keyword_check("°c", "cloudy", "sunny", "rainy", "humid"),
        tool_called_check("get_weather"),
    )
    results: list[EvalResults] = await evaluate_agent(
        agent=weather_agent,
        queries=weather_queries,
        evaluators=combined,
        eval_name="WeatherCombinedEval",
    )
    all_pass = all(r.all_passed for r in results)
    total_passed = sum(r.passed for r in results)
    total = sum(r.total for r in results)
    print(f"\n  Overall: {'✅ ALL PASS' if all_pass else '❌ SOME FAILED'}")
    print(f"  Score  : {total_passed}/{total} checks passed")


# --- SECTION 7: RUN & TEST ---
async def main():
    await run_keyword_eval()
    await run_tool_eval()
    await run_combined_eval()


asyncio.run(main())
