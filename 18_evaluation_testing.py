# ============================================================
# 18 - Evaluation & Testing Agents
# ============================================================
#
# evaluate_agent(...)  -> list[EvalResults]
#   Runs an agent against a list of test queries, captures each
#   query/response interaction, and submits them to one or more
#   evaluators. Returns one EvalResults per evaluator provider.
#
#   Main params:
#     agent              : the agent under test
#     queries            : str | list[str]    test inputs
#     evaluators         : Evaluator | list   checks to run
#     expected_output    : optional ground-truth answers
#     expected_tool_calls: optional expected tool invocations
#     responses          : pre-run AgentResponses (skip running)
#     eval_name          : display name (defaults to agent name)
#     num_repetitions    : run each query N times for consistency
#
#
# ── OBJECT STRUCTURES ──
#
# EvalItem                 — one query/response interaction to evaluate
#   conversation         : list[Message]      full conversation
#   tools                : list[FunctionTool] tools available to agent
#   context              : str | None         grounding doc
#   expected_output      : str | None         ground-truth answer
#   expected_tool_calls  : list[ExpectedToolCall] | None
#   split_strategy       : ConversationSplitter (default LAST_TURN)
#   .query     (property): str  — user input text
#   .response  (property): str  — agent output text
#
# CheckResult              — output of one custom check on one item
#   passed     : bool   did the check pass?
#   reason     : str    human-readable explanation
#   check_name : str    name of the check
#
# EvalResults              — results from a single evaluator provider
#   provider      : str                 e.g. "local", "foundry"
#   eval_id       : str                 provider eval definition id
#   run_id        : str                 provider run id
#   status        : "completed" | "failed" | "canceled" | "timeout"
#   result_counts : dict[str, int]      {"passed": N, "failed": M}
#   report_url    : str | None          link to provider portal
#   error         : str | None
#   per_evaluator : dict[str, dict[str, int]]   per-evaluator counts
#   items         : list[EvalItemResult]        per-item detail
#   sub_results   : dict[str, EvalResults]      per-agent breakdown
#   .passed / .failed / .total / .all_passed   (convenience props)
#
#
# --- SECTION 1: IMPORTS ---
import asyncio
from typing import Annotated

from agent_framework import (
    Agent,
    CheckResult,
    EvalItem,
    EvalResults,
    LocalEvaluator,
    evaluate_agent,
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


# Custom OR check — built-in keyword_check requires ALL keywords; we want ANY.
def any_keyword_check(*keywords: str, case_sensitive: bool = False):
    """Pass if the response contains at least ONE of the given keywords."""

    def _check(item: EvalItem) -> CheckResult:
        text = item.response if case_sensitive else item.response.lower()
        found = [k for k in keywords if (k if case_sensitive else k.lower()) in text]
        if found:
            return CheckResult(
                passed=True,
                reason=f"Found: {found}",
                check_name="any_keyword_check",
            )
        return CheckResult(
            passed=False,
            reason=f"None of {list(keywords)} found",
            check_name="any_keyword_check",
        )

    return _check


# Check 1 — keyword presence: did the response mention any weather word?
keyword_evaluator = LocalEvaluator(
    any_keyword_check("cloudy", "sunny", "rain", "humid"),  # at least one weather word
)

# Check 2 — tool usage: did the agent actually call get_weather?
tool_evaluator = LocalEvaluator(
    tool_called_check("get_weather"),
)


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
def _print_items(result: EvalResults) -> None:
    """Print each query, the LLM response, and per-evaluator scores."""
    for i, item in enumerate(result.items, start=1):
        print(f"\n  ── Item {i} ──")
        print(f"  Query   : {item.input_text}")
        print(f"  Response: {item.output_text}")
        for score in item.scores:
            mark = "✅" if score.passed else "❌"
            print(f"    {mark} {score.name}: {score.score}")


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
        _print_items(result)
        status = "✅ PASS" if result.all_passed else "❌ FAIL"
        print(f"\n  {status} — passed: {result.passed}, failed: {result.failed}, total: {result.total}")


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
        _print_items(result)
        status = "✅ PASS" if result.all_passed else "❌ FAIL"
        print(f"\n  {status} — passed: {result.passed}, failed: {result.failed}, total: {result.total}")


async def run_combined_eval():
    print("\n" + "=" * 60)
    print("🔬 EVAL 3: Combined — keyword + tool call checks together")
    print("=" * 60)
    combined = LocalEvaluator(
        any_keyword_check("cloudy", "sunny", "rain", "humid"),
        tool_called_check("get_weather"),
    )
    results: list[EvalResults] = await evaluate_agent(
        agent=weather_agent,
        queries=weather_queries,
        evaluators=combined,
        eval_name="WeatherCombinedEval",
    )

    for result in results:
        _print_items(result)

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
