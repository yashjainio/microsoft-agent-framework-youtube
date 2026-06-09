# ============================================================
# 19 - Production Deployment (FastAPI + Streaming)
# ============================================================


# --- SECTION 1: IMPORTS ---
import json
import os
from typing import Annotated

import uvicorn
from agent_framework import Agent, AgentResponseUpdate, ResponseStream
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route

# --- SECTION 2: CONFIGURATION ---
# OpenAIChatClient() with no args reads OPENAI_API_KEY + OPENAI_MODEL from env.
load_dotenv()
client = OpenAIChatClient()
PORT = int(os.getenv("PORT", 8000))


# --- SECTION 3: TOOLS ---
def get_weather(city: Annotated[str, "City name, e.g. 'Bengaluru'"]) -> str:
    """Returns current weather for a city (mock data)."""
    mock = {
        "bengaluru": "24°C, Partly Cloudy",
        "mumbai": "32°C, Hot and Humid",
        "delhi": "38°C, Sunny",
        "london": "15°C, Rainy",
    }
    return mock.get(city.lower(), "City not found")


def calculate(expression: Annotated[str, "A math expression, e.g. '2 + 2'"]) -> str:
    """Evaluates a mathematical expression."""
    try:
        return str(eval(expression, {"__builtins__": {}}))
    except Exception as e:
        return f"Error: {e}"


# --- SECTION 4: AGENT ---
agent = Agent(
    client=client,
    name="ProductionAgent",
    instructions=(
        "You are a helpful assistant with weather and calculator tools. "
        "Always use tools when the user asks for weather or math."
    ),
    tools=[get_weather, calculate],
)


# --- SECTION 5: API ENDPOINTS ---
async def health(request: Request) -> JSONResponse:
    """GET /health — liveness check."""
    return JSONResponse({"status": "ok", "agent": agent.name})


async def chat(request: Request) -> JSONResponse:
    """POST /chat — single-turn, returns full response as JSON."""
    body = await request.json()
    message = body.get("message", "").strip()
    if not message:
        return JSONResponse({"error": "message field is required"}, status_code=400)

    response = await agent.run(message)
    return JSONResponse({"reply": response.text})


async def chat_stream(request: Request) -> StreamingResponse:
    """POST /chat/stream — streams tokens as server-sent events (SSE).

    Each event is a JSON line:  {"token": "..."} or {"done": true}
    Clients can consume this with EventSource or fetch + ReadableStream.
    """
    body = await request.json()
    message = body.get("message", "").strip()
    if not message:
        return JSONResponse({"error": "message field is required"}, status_code=400)

    async def event_generator():
        stream: ResponseStream = agent.run(message, stream=True)
        async for update in stream:
            update: AgentResponseUpdate
            if update.text:
                data = json.dumps({"token": update.text})
                yield f"data: {data}\n\n"
        yield "data: " + json.dumps({"done": True}) + "\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable nginx buffering for SSE
        },
    )


# --- SECTION 6: APP ---
app = Starlette(
    routes=[
        Route("/health", health, methods=["GET"]),
        Route("/chat", chat, methods=["POST"]),
        Route("/chat/stream", chat_stream, methods=["POST"]),
    ]
)


# --- SECTION 7: RUN ---
# Start the server:  python 18_production_deployment.py
# Test non-streaming:  curl -X POST http://localhost:8000/chat \
#                       -H "Content-Type: application/json" \
#                       -d '{"message": "What is the weather in Bengaluru?"}'
#
# Test streaming:      curl -X POST http://localhost:8000/chat/stream \
#                       -H "Content-Type: application/json" \
#                       -d '{"message": "Explain async programming in 3 sentences"}' \
#                       --no-buffer
if __name__ == "__main__":
    print("🚀 Agent API running at http://localhost:{PORT}")
    print("   GET  /health")
    print("   POST /chat         — full JSON response")
    print("   POST /chat/stream  — server-sent events")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
