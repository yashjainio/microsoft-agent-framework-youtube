# ============================================================
# 09 - Concurrent / Fan-Out Workflows
# ============================================================

# --- SECTION 1: IMPORTS ---
import asyncio
import time

from agent_framework import AgentResponse
from agent_framework.openai import OpenAIChatClient
from agent_framework.orchestrations import ConcurrentBuilder
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()
client = OpenAIChatClient()

# --- SECTION 3: PARALLEL AGENTS ---
hindi_translator = client.as_agent(
    name="HindiTranslator",
    instructions="Translate the given English text to Hindi. Return ONLY the Hindi translation.",
)
kannada_translator = client.as_agent(
    name="KannadaTranslator",
    instructions="Translate the given English text to Kannada. Return ONLY the Kannada translation.",
)
french_translator = client.as_agent(
    name="FrenchTranslator",
    instructions="Translate the given English text to French. Return ONLY the French translation.",
)
sentiment_analyzer = client.as_agent(
    name="SentimentAnalyzer",
    instructions=(
        "Analyze the sentiment of the given text. "
        'Return JSON only: {"sentiment": "positive|negative|neutral", "confidence": 0.0-1.0, "reason": "..."}'
    ),
)
keyword_extractor = client.as_agent(
    name="KeywordExtractor",
    instructions="Extract the top 5 keywords. Return as a comma-separated list.",
)

# --- SECTION 4: BUILD AND RUN WORKFLOW ---
workflow = ConcurrentBuilder(
    participants=[
        hindi_translator,
        kannada_translator,
        french_translator,
        sentiment_analyzer,
        keyword_extractor,
    ]
).build()


async def main():
    text = "Microsoft Agent Framework 1.0 is production-ready and supports multi-agent AI workflows."
    print(f"📥 Input: {text}\n")
    print("🔀 Running 5 agents in parallel...\n")

    start = time.time()
    events = await workflow.run(text)
    elapsed = time.time() - start

    outputs = events.get_outputs()
    if outputs:
        final: AgentResponse = outputs[0]
        for msg in final.messages:
            name = msg.author_name or "assistant"
            print(f"[{name}]\n{msg.text}\n")

    print(f"⏱  Total time (parallel): {elapsed:.2f}s")
    print(f"💡 Sequential would take ~{elapsed * 5:.1f}s — 5× slower!")


asyncio.run(main())
