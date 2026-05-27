# ============================================================
# 12 - A2A Agent Server
# ============================================================

import uvicorn
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface
from agent_framework import Agent
from agent_framework.a2a import A2AExecutor
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv
from starlette.applications import Starlette

load_dotenv()

data_analyst = Agent(
    client=OpenAIChatClient(),
    name="DataAnalystAgent",
    instructions=(
        "You are a data analyst. Given raw data or a description, "
        "provide statistical insights, trends, and actionable recommendations."
    ),
)

public_agent_card = AgentCard(
    name="DataAnalystAgent",
    description="A data analyst agent that provides statistical insights and actionable recommendations.",
    version="1.0.0",
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(streaming=True),
    supported_interfaces=[
        AgentInterface(url="http://localhost:8765/", protocol_binding="JSONRPC"),
    ],
    skills=[],
)

request_handler = DefaultRequestHandler(
    agent_executor=A2AExecutor(data_analyst, stream=True),
    task_store=InMemoryTaskStore(),
    agent_card=public_agent_card,
)

app = Starlette(
    routes=[
        *create_agent_card_routes(public_agent_card),
        *create_jsonrpc_routes(request_handler, "/"),
    ],
)

if __name__ == "__main__":
    print("🚀 DataAnalystAgent A2A server on http://localhost:8765")
    uvicorn.run(app, host="localhost", port=8765)
