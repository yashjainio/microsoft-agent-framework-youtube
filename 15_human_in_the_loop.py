# ============================================================
# 15 - Human-in-the-Loop
# ============================================================


# --- SECTION 1: IMPORTS ---
import asyncio
from collections.abc import Awaitable, Callable
from typing import Annotated

from agent_framework import (
    Agent,
    FunctionInvocationContext,
    FunctionMiddleware,
    MiddlewareTermination,
)
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()
client = OpenAIChatClient()


# --- SECTION 3: APPROVAL MIDDLEWARE ---
# Intercepts every tool call and pauses for human confirmation.
# If the human denies, MiddlewareTermination stops the tool and
# passes a rejection message back to the agent so it can respond gracefully.
class HumanApprovalMiddleware(FunctionMiddleware):
    def __init__(self, tools_requiring_approval: set[str] | None = None):
        # None = require approval for ALL tools
        self.tools_requiring_approval = tools_requiring_approval

    async def process(
        self,
        context: FunctionInvocationContext,
        call_next: Callable[[], Awaitable[None]],
    ):
        print("In the Middleware")
        tool_name = context.function.name
        needs_approval = tool_name in self.tools_requiring_approval

        if not needs_approval:
            await call_next()
            return

        print(f"\n  🔔 Tool requested: {tool_name}")
        print(f"     Arguments    : {context.arguments}")
        decision = input("  ✅ Allow? (y/n): ").strip().lower()

        if decision != "y":
            print(f"  🚫 Human denied '{tool_name}'.")
            context.result = f"[Action '{tool_name}' was denied by the user. Do not retry it.]"
            raise MiddlewareTermination()

        print(f"  ✅ Approved — executing '{tool_name}'...")
        await call_next()


# --- SECTION 4: SENSITIVE TOOLS ---
def send_email(
    to: Annotated[str, "Recipient email address"],
    subject: Annotated[str, "Email subject line"],
    body: Annotated[str, "Email body content"],
) -> str:
    """Sends an email to the specified recipient."""
    # Real implementation would call an email API here.
    return f"✅ Email sent to {to} | Subject: '{subject}' | Body: '{body}'"


def delete_file(path: Annotated[str, "Absolute file path to delete, e.g. '/tmp/report.txt'"]) -> str:
    """Permanently deletes a file from the filesystem."""
    # Real implementation would call os.remove(path) here.
    return f"✅ Deleted: {path}"


def read_file(path: Annotated[str, "File path to read, e.g. '/tmp/notes.txt'"]) -> str:
    """Reads the contents of a file."""
    return f"[Contents of {path}]: Hello from the file!"


# --- SECTION 5: AGENT ---
# Only destructive / irreversible tools require approval.
# read_file is considered safe and runs without prompting.
agent = Agent(
    client=client,
    name="AssistantWithOversight",
    instructions=(
        "You are a helpful assistant that can send emails, delete files, and read files. "
        "We have three tools available with us - 'send_email', 'delete_file', 'read_file'"
    ),
    tools=[send_email, delete_file, read_file],
    middleware=[HumanApprovalMiddleware(tools_requiring_approval={"send_email", "delete_file"})],
)


# --- SECTION 6: RUN & TEST ---
async def main():
    print("=" * 60)
    print("🔒 Human-in-the-Loop Demo")
    print("   Irreversible tools pause for your approval.")
    print("=" * 60)

    tasks = [
        "Read the file at /tmp/notes.txt and tell me what it says.",
        "Send an email to team@example.com with subject 'Weekly Update' and body 'All tasks are on track.'",
        "Delete the file at /tmp/old_report.txt.",
    ]

    for task in tasks:
        print(f"\n💬 Task: {task}")
        session = agent.create_session()
        response = await agent.run(task, session=session)
        print(f"🤖 {response.text}")
        print("-" * 55)


asyncio.run(main())
