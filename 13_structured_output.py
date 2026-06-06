# ============================================================
# 13 - Structured Output / Response Models
# ============================================================


# --- SECTION 1: IMPORTS ---
import asyncio

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv
from pydantic import BaseModel

# --- SECTION 2: CONFIGURATION ---
load_dotenv()
client = OpenAIChatClient()


# --- SECTION 3: PYDANTIC RESPONSE MODELS ---
class SentimentResult(BaseModel):
    sentiment: str  # "positive", "negative", or "neutral"
    confidence: float  # 0.0 – 1.0
    key_phrases: list[str]  # words/phrases driving the sentiment
    summary: str  # one-sentence summary


class ActionPlan(BaseModel):
    goal: str
    steps: list[str]
    estimated_days: int
    blockers: list[str]


# --- SECTION 4: AGENTS WITH response_format ---
# Passing response_format tells the model to always return valid JSON
# matching that schema — no more regex parsing or string manipulation.
sentiment_agent = Agent(
    client=client,
    name="SentimentAnalyzer",
    instructions=("You are a sentiment analysis expert. " "Analyze the given text and return a structured result."),
    default_options={
        "response_format": SentimentResult,
    },
)

planner_agent = Agent(
    client=client,
    name="Planner",
    instructions=("You are a project planning expert. " "Break down the goal into a concrete, actionable plan."),
    default_options={
        "response_format": ActionPlan,
    },
)


# --- SECTION 5: HELPERS ---
async def analyze_sentiment(text: str) -> SentimentResult:
    response = await sentiment_agent.run(f"Analyze this review:\n\n{text}")
    return SentimentResult.model_validate_json(response.text)


async def build_plan(goal: str) -> ActionPlan:
    response = await planner_agent.run(f"Create a plan for: {goal}")
    return ActionPlan.model_validate_json(response.text)


# --- SECTION 6: RUN & TEST ---
async def main():
    reviews = [
        "The Microsoft Agent Framework is incredibly powerful! Setup was a breeze and the docs are top-notch.",
        "Disappointed — the MCP integration kept crashing and the error messages were useless.",
        "Decent framework. Does what it says, nothing more. Could use better examples.",
    ]

    print("=" * 60)
    print("📊 SENTIMENT ANALYSIS")
    print("=" * 60)
    for review in reviews:
        result = await analyze_sentiment(review)
        print(f"\n📝 Review: {review[:60]}...")
        print(f"   Sentiment  : {result.sentiment.upper()} ({result.confidence:.0%} confident)")
        print(f"   Key phrases: {', '.join(result.key_phrases)}")
        print(f"   Summary    : {result.summary}")
        print("-" * 60)

    print("\n" + "=" * 60)
    print("🗂️  ACTION PLAN")
    print("=" * 60)
    plan = await build_plan("Launch a YouTube series on Microsoft Agent Framework")
    print(f"\n🎯 Goal: {plan.goal}")
    print(f"⏱️  Estimated days: {plan.estimated_days}")
    print("📋 Steps:")
    for i, step in enumerate(plan.steps, 1):
        print(f"   {i}. {step}")
    if plan.blockers:
        print(f"⚠️  Blockers: {', '.join(plan.blockers)}")


asyncio.run(main())
