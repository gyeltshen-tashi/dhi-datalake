# main.py
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessageChunk
from contextlib import asynccontextmanager

load_dotenv(dotenv_path=Path(__file__).resolve().parent/".env", override=True)

from graph import (
    get_tools,
    create_datalake_agent,
    DRUKAIR_PROMPT,
    BHUTAN_TELECOM_PROMPT,
    MASTER_PROMPT,
)


# ============================================================
# AGENTS
# Created at startup using MCP tools
# ============================================================

agents = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs when the FastAPI app starts up.
    Creates all agents by fetching tools from MCP server.

    Why lifespan?
    Because get_tools() is async — we need an async context
    to run it. Lifespan runs before the first request.
    """
    print("Starting up — connecting to MCP server...")

    # Fetch tools per company from MCP server
    drukair_tools = await get_tools("drukair")
    bt_tools = await get_tools("bhutan_telecom")
    all_tools = await get_tools("all")

    print(f"Drukair tools: {len(drukair_tools)}")
    print(f"BT tools: {len(bt_tools)}")
    print(f"All tools: {len(all_tools)}")

    # create agent with filtered tools
    agents["drukair"] = await create_datalake_agent(drukair_tools, DRUKAIR_PROMPT)
    agents["bhutan_telecom"] = await create_datalake_agent(bt_tools, BHUTAN_TELECOM_PROMPT)
    agents["master"] = await create_datalake_agent(all_tools, MASTER_PROMPT)

    print("All agents ready.")
    yield
    print("Shutting down.")


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(title="DHI Data Lake Chat Agent", lifespan=lifespan)

# CORS middleware — allows the frontend (running on a different
# origin/port) to call this.
# Without this, browsers block cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST AND RESPONSE MODELS
# Pydantic models define the shape of data coming in and going out
# FastAPI automatically validates the request against these models
# ============================================================

class ChatRequest(BaseModel):
    message: str        # the user's question
    session_id: str     # identifies the conversation


# ============================================================
# STREAM AGENT
# Stream the AI responses
# ============================================================
async def stream_agent(agent, message: str, session_id: str):
    config = {"configurable": {"thread_id": session_id}}

    async for chunk in agent.astream(
        {"messages": [HumanMessage(content=message)]},
        config=config,
        stream_mode="message",
    ):
        # chunk is (message chunk, metadata)
        msg, metadata = chunk
        if isinstance(msg, AIMessageChunk) and msg.content:
            text = msg.content if isinstance(msg.content, str) else ""
            if text:
                yield f"data: {json.dumps({'text': text})}\n\n"

    # Send a done event so frontend knows it's finished
    yield f"data: {json.dumps({'done': True, 'session_id': session_id})}\n\n"


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/")
def home():
    return {"message": "DHI Chat Agent is running"}


@app.get("/health")
def health():
    """Health check endpoint — used to verify the agent is running"""
    return {
        "status": "healthy",
        "agents": list(agents.keys()),
        "api_base": os.getenv("API_BASE_URL", "http://localhost:8000")
    }


@app.post("/chat/drukair")
async def chat_drukair(request: ChatRequest):
    return StreamingResponse(
        stream_agent(agents["drukair"], request.message, request.session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@app.post("/chat/bhutan_telecom")
async def chat_bt(request: ChatRequest):
    return StreamingResponse(
        stream_agent(agents["bhutan_telecom"], request.message, request.session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@app.post("/chat/master")
async def chat_master(request: ChatRequest):
    """
    Chat endpoint for master dashboard.
    Has access to ALL company data.
    Can perform cross-company analysis.
    """
    return StreamingResponse(
        stream_agent(agents["master"], request.message, request.session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no", # Disable nginx buffering
        }
    )


# ============================================================
# SESSION MANAGEMENT
# ============================================================

@app.delete("/chat/{session_id}")
def clear_session(session_id: str):
    """
    Clears conversation history for a session.
    Frontend can call this when user clicks "New Chat".
    
    Note: With MemorySaver, we can't truly delete a session.
    The simplest approach is to use a new session_id for new conversations.
    """
    return {"message": f"Use a new session_id to start a fresh conversation"}