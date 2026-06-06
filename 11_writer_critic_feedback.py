# ============================================================
# 11 - Writer-Critic Feedback Loop
# ============================================================


# --- SECTION 1: IMPORTS ---
import asyncio
import re

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()
client = OpenAIChatClient()

# --- SECTION 3: WRITER AND CRITIC ---
writer = Agent(
    client=client,
    name="Writer",
    instructions=(
        "You are a professional blog writer. Write or revise content based on the topic "
        "or feedback given. Aim for clarity, engagement, and accuracy. "
        "Keep the output to 150–200 words."
    ),
)
critic = Agent(
    client=client,
    name="Critic",
    instructions=(
        "You are a harsh but constructive editor. "
        "Review the text and respond in EXACTLY this format:\n"
        "SCORE: <number 1-10>\n"
        "FEEDBACK: <specific improvement suggestions>\n\n"
        "If the score is 8 or higher, start your response with 'APPROVED' instead."
    ),
)


# --- SECTION 4: FEEDBACK LOOP ---
async def writer_critic_loop(topic: str, max_iterations: int = 5) -> str:
    writer_session = writer.create_session()  # writer remembers its own drafts
    print(f"📝 Topic: {topic} | Max iterations: {max_iterations}\n")

    draft = (
        await writer.run(
            f"Write a blog intro about: {topic}",
            session=writer_session,
        )
    ).text

    for i in range(max_iterations):
        print(f"--- Iteration {i + 1} ---")
        print(f"📄 Draft: {draft[:100]}...\n")

        critique = (await critic.run(draft)).text  # stateless — no session needed
        print(f"🔍 Critique: {critique}\n")

        score_match = re.search(r"SCORE:\s*(\d+)", critique)
        score = score_match.group(1) if score_match else "0"
        print(f"📊 Score: {score}/10 — revising...\n")

        if int(score) >= 8:
            print(f"✅ Approved on iteration {i + 1}!")
            return draft

        draft = (
            await writer.run(
                f"Revise your previous draft based on this feedback:\n{critique}",
                session=writer_session,
            )
        ).text

    print("⚠️  Max iterations reached. Returning best version.")
    return draft


# --- SECTION 5: RUN & TEST ---
async def main():
    final = await writer_critic_loop("Why every developer should learn Microsoft Agent Framework in 2026")
    print("\n" + "=" * 60)
    print("📌 FINAL OUTPUT:")
    print("=" * 60)
    print(final)


asyncio.run(main())
