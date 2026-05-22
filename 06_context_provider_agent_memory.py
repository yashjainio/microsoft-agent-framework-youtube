# ============================================================
# 06 - Context Providers & Agent Memory
#
# CORRECT API:
#   from agent_framework import ContextProvider, SessionContext
#   from agent_framework import InMemoryHistoryProvider
#   TextContextProvider / FileContextProvider do NOT exist —
#   subclass ContextProvider and implement before_run() instead.
# ============================================================


# --- SECTION 1: IMPORTS ---
import asyncio
from typing import Any

from agent_framework import Agent, AgentSession, ContextProvider, SessionContext
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()


# --- SECTION 3: CUSTOM CONTEXT PROVIDERS ---
class FAQContextProvider(ContextProvider):
    """Injects static FAQ text as instructions before every agent run."""

    def __init__(self, faq_text: str):
        super().__init__("faq-provider")
        self._faq = faq_text

    async def before_run(
        self,
        *,
        agent: Any,
        session: AgentSession,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        context.extend_instructions(self.source_id, self._faq)


class FileContextProvider(ContextProvider):
    """Reads a file and injects its contents as instructions before every run."""

    def __init__(self, filepath: str):
        super().__init__("file-provider")
        self._filepath = filepath

    async def before_run(
        self,
        *,
        agent: Any,
        session: AgentSession,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        try:
            with open(self._filepath, "r") as f:
                content = f.read()
            context.extend_instructions(self.source_id, content)
        except FileNotFoundError:
            pass


# --- SECTION 4: SETUP ---
with open("product_catalog.txt", "w") as f:
    f.write(
        """PRODUCT CATALOG — TechCorp India
- MAF Starter Kit:   ₹2,999 | AI agent development bundle
- Cloud Deploy Pro:  ₹7,499 | Azure deployment tools
- DevOps Suite:      ₹4,999 | CI/CD automation pack
"""
    )

faq_provider = FAQContextProvider(
    """
COMPANY FAQ — TechCorp India
- Office: Bengaluru, Karnataka
- Support: support@techcorp.in
- Hours: Mon–Fri, 9am–6pm IST
- Return policy: 30 days, no questions asked
- CEO: Yash Jain  |  Founded: 2018
"""
)
catalog_provider = FileContextProvider("product_catalog.txt")

support_agent = Agent(
    client=OpenAIChatClient(),
    name="SupportAgent",
    instructions=(
        "You are a customer support agent for TechCorp India. "
        "Answer ONLY using the context provided to you. "
        "If the answer is not in the context, say: 'I will escalate this to our team.'"
    ),
    context_providers=[faq_provider, catalog_provider],
)


# --- SECTION 5: RUN & TEST ---
async def main():
    questions = [
        "Who is the CEO of your company?",
        "What are your office hours?",
        "How much does Cloud Deploy Pro cost?",
        "Do you have a 60-day return policy?",
        "What city is your office in?",
    ]
    for q in questions:
        print(f"\n❓ {q}")
        r = await support_agent.run(q)
        print(f"💬 {r}")


asyncio.run(main())
