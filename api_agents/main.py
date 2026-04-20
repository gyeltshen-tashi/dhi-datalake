import os 
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

load_dotenv(dotenv_path=Path(__file__).resolve().parent/".env", override=True)

from graph import (
    create_datalake_agent,
    DRUKAIR_PROMPT,
    BHUTAN_TELECOM_PROMPT,
    MASTER_PROMPT
)

from tools.drukair import drukair_tools
from tools.bhutan_telecom import bt_tools


# ============================================================
# CREATING THE AGENTS
# Each agent has different tools and a different system prompt
# ============================================================

drukair_agent = create_datalake_agent(
    tools=drukair_tools,
    system_prompt=DRUKAIR_PROMPT
)

bt_agent = create_datalake_agent(
    tools=bt_tools,
    system_prompt=BHUTAN_TELECOM_PROMPT
)

master_agent = create_datalake_agent(
    tools=drukair_tools + bt_tools,
    system_prompt=MASTER_PROMPT
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(title="DHI Data Lake Chat Agent")

# CORS middleware — allows the frontend (running on a different
# origin/port) to call this API
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

def run_agent(agent, message: str, session_id: str) -> str:
    """
    Sends a message to an agent and returns its response.

    config with thread_id is how LangGraph identifies which conversation to load from memory. 
    same thread_id = same conversation.
    """
    config = {"configurable": {"thread_id": session_id}}

    try: 
        result = agent.invoke(
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


@app.post("/chat/drukair", response_model=ChatResponse)
def chat_drukair(request: ChatRequest):
    """
    Chat endpoint for Drukair dashboard.
    Only has access to Drukair data.

    frondend sends:
    POST /chat/drukair
    {
        "message": "what was the revenue in 2024?",
        "session_id": "user123-drukair"
    }
    """
    response = run_agent(drukair_agent, request.message, request.session_id)
    return ChatResponse(response=response, session_id=request.session_id)


@app.post("/chat/bhutan_telecom", response_model=ChatResponse)
def chat_bt(request: ChatRequest):
    """
    Chat endpoint for Bhutan Telecom dashboard.
    Only has access to BT data.
    """
    response = run_agent(bt_agent, request.message, request.session_id)
    return ChatResponse(response=response, session_id=request.session_id)


@app.post("/chat/master", response_model=ChatResponse)
def chat_master(request: ChatRequest):
    """
    Chat endpoint for master dashboard.
    Has access to ALL company data.
    Can perform cross-company analysis.
    """
    response = run_agent(master_agent, request.message, request.session_id)
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
    return {"message": f"Start a new conversation by using a different session_id"}


@app.get("/health")
def health():
    """Health check endpoint — used to verify the agent is running"""
    return {
        "status": "healthy",
        "agents": ["drukair", "bhutan_telecom", "master"],
        "api_base": os.getenv("API_BASE_URL", "http://localhost:8000")
    }