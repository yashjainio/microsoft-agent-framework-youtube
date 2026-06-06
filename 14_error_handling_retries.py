# ============================================================
# 14 - Error Handling & Retries
# ============================================================


# --- SECTION 1: IMPORTS ---
import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import Annotated

from agent_framework import (
    Agent,
    AgentContext,
    AgentMiddleware,
    FunctionInvocationContext,
    FunctionMiddleware,
    MiddlewareTermination,
)
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()
client = OpenAIChatClient()


# --- SECTION 3: RETRY MIDDLEWARE ---
# Retries the entire agent call when it fails (network glitch, rate-limit, etc.)
class RetryMiddleware(AgentMiddleware):
    def __init__(self, max_retries: int = 3, delay_seconds: float = 1.0):
        self.max_retries = max_retries
        self.delay_seconds = delay_seconds

    async def process(
        self,
        context: AgentContext,
        call_next: Callable[[], Awaitable[None]],
    ):
        for attempt in range(1, self.max_retries + 1):
            try:
                await call_next()
                return  # success — stop retrying
            except Exception as e:
                if attempt == self.max_retries:
                    print(f"  RetryMiddleware ❌ All {self.max_retries} retries exhausted. Last error: {e}")
                    raise
                print(f"  ⚠️  Attempt {attempt} failed ({e}). Retrying in {self.delay_seconds}s...")
                await asyncio.sleep(self.delay_seconds)


# --- SECTION 4: TOOL-LEVEL ERROR MIDDLEWARE ---
# Catches tool/function failures and returns a safe fallback string
# so the agent can continue instead of crashing the whole run.
class SafeToolMiddleware(FunctionMiddleware):
    def __init__(self, max_retries: int = 3, delay_seconds: float = 0.5):
        self.max_retries = max_retries
        self.delay_seconds = delay_seconds

    async def process(
        self,
        context: FunctionInvocationContext,
        call_next: Callable[[], Awaitable[None]],
    ):
        for attempt in range(1, self.max_retries + 1):
            try:
                await call_next()
                return
            except Exception as e:
                tool_name = context.function.name
                if attempt == self.max_retries:
                    context.result = f"[Tool '{tool_name}' failed: {e}. Please try a different approach.]"
                    print(
                        f"  SafeToolMiddleware ❌ All {self.max_retries} retries exhausted for {tool_name}."
                        f" Last error: {e}"
                    )
                    raise MiddlewareTermination()  # stop the middleware chain with our fallback

                print(f"  ⚠️  Attempt {attempt} failed ({e}). Retrying in {self.delay_seconds}s...")
                await asyncio.sleep(self.delay_seconds)


# --- SECTION 5: FLAKY TOOLS (simulate real-world unreliability) ---
_call_counts: dict[str, int] = {}


def flaky_stock_price(ticker: Annotated[str, "Stock ticker symbol, e.g. 'MSFT'"]) -> str:
    """Returns the current stock price for a ticker. May fail on the first attempt."""
    _call_counts[ticker] = _call_counts.get(ticker, 0) + 1
    if _call_counts[ticker] < 2:
        raise ConnectionError(f"Timeout fetching price for {ticker}")
    prices = {"MSFT": 420.50, "GOOGL": 185.30, "AMZN": 230.10}
    price = prices.get(ticker.upper(), 99.99)
    return f"{ticker.upper()}: ${price}"


def unreliable_calculator(expression: Annotated[str, "A math expression, e.g. '10 * 5'"]) -> str:
    """Evaluates a math expression. Randomly fails 40% of the time."""
    if random.random() < 0.8:  # 40% of time fail
        raise RuntimeError("Calculator service temporarily unavailable")
    result = eval(expression, {"__builtins__": {}})
    return f"{expression} = {result}"


# --- SECTION 6: AGENT WITH BOTH MIDDLEWARE LAYERS ---
resilient_agent = Agent(
    client=client,
    name="ResilientAgent",
    instructions=(
        "You are a financial assistant. Use your tools to fetch stock prices and "
        "calculate values. If a tool fails, explain what happened and retry or suggest alternatives."
    ),
    tools=[flaky_stock_price, unreliable_calculator],
    middleware=[
        RetryMiddleware(max_retries=3, delay_seconds=0.5),
        SafeToolMiddleware(max_retries=3, delay_seconds=0.5),
    ],
)


# --- SECTION 7: RUN & TEST ---
async def main():
    queries = [
        "What is the current price of MSFT?",
        "Calculate 250 * 1.08 for me.",
        "What is the price of GOOGL and calculate 185.30 * 100?",
    ]

    for query in queries:
        print(f"\n💬 {query}")
        try:
            response = await resilient_agent.run(query)
            print(f"🤖 {response.text}")
        except Exception as e:
            print(f"💥 Unrecoverable error: {e}")
        print("-" * 55)


asyncio.run(main())
