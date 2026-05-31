# ============================================================
# 08 - Sequential Multi-Agent Workflow
# ============================================================


# --- SECTION 1: IMPORTS ---
import asyncio

from agent_framework import Agent, AgentResponse
from agent_framework.openai import OpenAIChatClient
from agent_framework.orchestrations import SequentialBuilder
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()
client = OpenAIChatClient()

# --- SECTION 3: PIPELINE AGENTS ---
researcher = Agent(
    client=client,
    name="Researcher",
    instructions=(
        "You are a research analyst. Given a topic, return exactly 5 key facts "
        "as a numbered list. Be factual and concise."
    ),
)
summarizer = Agent(
    client=client,
    name="Summarizer",
    instructions=(
        "You are a summarizer. Take the numbered facts and write " "a single, coherent 3-sentence paragraph summary."
    ),
)
linkedin_writer = Agent(
    client=client,
    name="LinkedInWriter",
    instructions=(
        "You are a LinkedIn content creator. Take the summary and write an engaging "
        "LinkedIn post: hook opening, 3 emoji takeaways, and a question at the end. "
        "Max 200 words."
    ),
)

# --- SECTION 4: BUILD WORKFLOW ---
workflow = SequentialBuilder(
    participants=[
        researcher,
        summarizer,
        linkedin_writer,
    ],
    intermediate_outputs=True,
).build()


# --- SECTION 5: RUN & TEST ---
async def main():
    topic = "Microsoft Agent Framework 1.0 GA release"
    print("=" * 75)
    print(f"📌 Topic: {topic}")
    print("Pipeline: Researcher → Summarizer → LinkedInWriter\n")

    events = await workflow.run(topic)

    print("\n================ FINAL OUTPUT ================\n")
    outputs = events.get_outputs()

    for agent_response in outputs:
        agent_response: AgentResponse = agent_response
        # in our case we have one msg from this for loop, but in case of tool call it have have multiple
        for msg in agent_response.messages:
            name = msg.author_name or "assistant"
            print(f"[{name}]")
            print(msg.text)
            print()


asyncio.run(main())
