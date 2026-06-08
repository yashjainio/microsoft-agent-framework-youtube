# ============================================================
# 17 - Workflow State Persistence
# ============================================================


# --- SECTION 1: IMPORTS ---
import asyncio

from agent_framework import Agent, AgentResponse, FileCheckpointStorage
from agent_framework.openai import OpenAIChatClient
from agent_framework.orchestrations import SequentialBuilder
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()
client = OpenAIChatClient()

CHECKPOINT_PATH = ".wf_checkpoints"  # multi-agent workflow checkpoint persistence


# --- SECTION 3: WORKFLOW CHECKPOINT PERSISTENCE ---
# FileCheckpointStorage saves the full workflow state after each agent step.
# If the process crashes mid-pipeline, resume from the last checkpoint
# by passing checkpoint_id= to workflow.run().
researcher = Agent(
    client=client,
    name="Researcher",
    instructions="You research topics and return 5 concise bullet-point facts.",
)
writer = Agent(
    client=client,
    name="Writer",
    instructions=(
        "You are a blog writer. Take the research bullets and write a "
        "150-word blog intro. Return only the blog text."
    ),
)

checkpoint_storage = FileCheckpointStorage(CHECKPOINT_PATH)

workflow = SequentialBuilder(
    participants=[
        researcher,
        writer,
    ],
    intermediate_outputs=True,
    checkpoint_storage=checkpoint_storage,
).build()


# --- SECTION 4: DEMO HELPERS ---
async def demo_workflow_checkpoints():
    print("\n" + "=" * 60)
    print("🗂️  WORKFLOW CHECKPOINTS — FileCheckpointStorage")
    print("=" * 60)

    topic = "Benefits of using Microsoft Agent Framework in production"
    print(f"\n🚀 Running pipeline for: '{topic}'")

    result = await workflow.run(topic)
    outputs = result.get_outputs()
    for agent_response in outputs:
        agent_response: AgentResponse = agent_response
        for msg in agent_response.messages:
            name = msg.author_name or "assistant"
            print(f"\n[{name}]\n{msg.text}")

    # Show saved checkpoints so viewer can see they're on disk
    print("Workflow name:", workflow.name)
    saved = await checkpoint_storage.list_checkpoints(workflow_name=workflow.name)
    print(f"\n📌 {len(saved)} checkpoint(s) saved to '{CHECKPOINT_PATH}/'")
    if saved:
        latest = saved[-1]
        print(f"   Latest ID : {latest.checkpoint_id}")
        print(f"   Timestamp : {latest.timestamp}")
        print("\n💡 To resume from this checkpoint, pass:")
        print(f"   workflow.run(checkpoint_id='{latest.checkpoint_id}')")


# --- SECTION 5: RUN & TEST ---
async def main():
    await demo_workflow_checkpoints()


asyncio.run(main())
