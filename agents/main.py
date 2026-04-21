# main.py
import os 
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
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
                        # same session_id = agent remembers previous messages
                        # different session_id = fresh conversation

class ChatResponse(BaseModel):
    response: str       # the agent's answer
    session_id: str     # echoed back so frontend knows which session this is


# ============================================================
# HELPER FUNCTION
# Runs any agent with a message and returns the response
# ============================================================

async def run_agent(agent, message: str, session_id: str) -> str:
    """
    Sends a message to an agent and returns its response.

    config with thread_id is how LangGraph identifies which conversation to load from memory. 
    same thread_id = same conversation.
    """
    config = {"configurable": {"thread_id": session_id}}

    try: 
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=message)]},
            config=config,
        )
        # result["messages"] is a list of all messages in the conversation
        # [-1] gets the last one — which is the agent's response
        return result["messages"][-1].content
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

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


@app.post("/chat/drukair", response_model=ChatResponse)
async def chat_drukair(request: ChatRequest):
    response = await run_agent(agents["drukair"], request.message, request.session_id)
    return ChatResponse(response=response, session_id=request.session_id)


@app.post("/chat/bhutan_telecom", response_model=ChatResponse)
async def chat_bt(request: ChatRequest):
    response = await run_agent(agents["bhutan_telecom"], request.message, request.session_id)
    return ChatResponse(response=response, session_id=request.session_id)


@app.post("/chat/master", response_model=ChatResponse)
async def chat_master(request: ChatRequest):
    """
    Chat endpoint for master dashboard.
    Has access to ALL company data.
    Can perform cross-company analysis.
    """
    response = await run_agent(agents["master"], request.message, request.session_id)
    return ChatResponse(response=response, session_id=request.session_id)


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