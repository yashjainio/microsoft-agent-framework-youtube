# ============================================================
# 10 - Conditional Routing & Handoffs
# ============================================================


# --- SECTION 1: IMPORTS ---
import asyncio

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()
client = OpenAIChatClient()

# --- SECTION 3: SPECIALIST + ROUTER AGENTS ---
billing_agent = Agent(
    client=client,
    name="BillingAgent",
    instructions=(
        "You are a billing specialist. Handle ONLY payment, invoice, and subscription issues. "
        "Be precise and professional."
    ),
)
tech_support_agent = Agent(
    client=client,
    name="TechSupportAgent",
    instructions=(
        "You are a technical support engineer. Handle ONLY bugs, errors, and setup issues. "
        "Ask for error messages and system details when relevant."
    ),
)
sales_agent = Agent(
    client=client,
    name="SalesAgent",
    instructions=(
        "You are a sales representative. Handle ONLY pricing, demos, and new feature questions. "
        "Be enthusiastic and highlight product value."
    ),
)
general_agent = Agent(
    client=client,
    name="GeneralAgent",
    instructions="You are a general support agent. Handle all other queries helpfully.",
)
router_agent = Agent(
    client=client,
    name="RouterAgent",
    instructions=(
        "You are a customer support ticket classifier. "
        "Read the user message and respond with EXACTLY ONE WORD: "
        "BILLING, TECH, SALES, or GENERAL. No other text."
    ),
)

ROUTE_MAP = {
    "BILLING": billing_agent,
    "TECH": tech_support_agent,
    "SALES": sales_agent,
    "GENERAL": general_agent,
}


# --- SECTION 4: ROUTING LOGIC ---
async def handle_query(query: str) -> str:
    # Run the router agent to know which agent to call
    router_response = await router_agent.run(query)
    category = router_response.messages[-1].text.strip().upper()

    # Check the given agent is available in ROUTE_MAP
    category = category if category in ROUTE_MAP else "GENERAL"
    specialist = ROUTE_MAP[category]
    print(f"  📍 Routed to: {specialist.name}")

    # Call the agent provided by route agent
    specialist_response = await specialist.run(query)
    return specialist_response.messages[-1].text


# --- SECTION 5: RUN & TEST ---
async def main():
    queries = [
        "My invoice shows a double charge this month.",
        "I get a 'ConnectionRefused' error when starting the agent.",
        "Can I get a demo of the enterprise plan features?",
        "What are your office hours?",
    ]
    for q in queries:
        print(f"\n💬 Yash: {q}")
        response = await handle_query(q)
        print(f"🤖 Response: {response}")
        print("=" * 60)


asyncio.run(main())
