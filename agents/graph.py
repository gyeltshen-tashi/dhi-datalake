# graph.py
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv(dotenv_path=Path(__file__).resolve().parent/".env", override=True)

# Path to the MCP server's main.py
# This tells the MCP client where to find the server
MCP_SERVER_PATH = str(
    Path(__file__).resolve().parent.parent / "mcp_server" / "main.py"
)

# This tells the MCP client which Python to use to run the server
# It uses the same uv virtual environment
PYTHON_PATH = str(
    Path(__file__).resolve().parent.parent / ".venv" / "bin" / "python"
)


async def get_tools(company: str = "all"):
    """
    Connects to MCP server and fetches tools.
    """
    # Note: MultiServerMCPClient uses a dictionary mapping server name to config
    client = MultiServerMCPClient(
        {
            "dhi_datalake": {
                "command": PYTHON_PATH,
                "args": [MCP_SERVER_PATH],
                "transport": "stdio",
            }
        }
    ) 

    # Get all tools from the connected client
    all_tools = await client.get_tools()

    if company == "all":
        return all_tools
    
    premix_map = {
        "drukair": "get_drukair_",
        "bhutan_telecom": "get_bt_"
    }

    prefix = premix_map.get(company)
    if not prefix:
        return all_tools
    
    # Filter tools by company prefix 
    filtered = [t for t in all_tools if t.name.startswith(prefix)]
    return filtered
    

async def create_datalake_agent(tools: list, system_prompt: str):
    """
    Creates a LangGraph agent with the given tools and prompt.
    """
    llm = ChatAnthropic(
        model = "claude-sonnet-4-6",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0
    )

    memory = MemorySaver()

    agent = create_agent(
        model=llm,
        tools=tools,
        checkpointer=memory,
        system_prompt= system_prompt,
    )

    return agent
    

# ============================================================
# SYSTEM PROMPTS
# These define each agent's personality, role and behavior
# The LLM reads this at the start of every conversation
# ============================================================

DRUKAIR_PROMPT = """You are a data analyst assistant for Drukair (Royal Bhutan Airlines).

You have access to the following data through your tools:
- Balance sheet (assets, liabilities, equity)
- Cash flow statements (operating, investing, financing)
- Profit and loss statements (revenue, expenses, net profit)
- Passenger traffic (individual ticket records, routes, fares)
- Master data (flight operations: sectors, capacity, ASK, RPK, load factors)

Your behavior rules:
1. ALWAYS call a tool to get real data. Never make up or estimate numbers.
2. If comparing years, make separate tool calls for each year.
3. If unsure which tool to use, start with the most relevant one.
4. Present financial numbers in Nu. (Ngultrum) with proper formatting.
5. If the data doesn't contain the answer, say so clearly.
6. For large datasets, summarize key findings rather than listing all rows.
7. Always mention the time period your answer covers.
"""

BHUTAN_TELECOM_PROMPT = """You are a data analyst assistant for Bhutan Telecom (BT).

You have access to the following data through your tools:
- CDR postpaid voice records (call records with timestamps and charges)
- CDR postpaid SMS records
- CDR postpaid data records
- CDR prepaid data records
- Cell tower details (locations, network types, regions)
- Cell tower data traffic (monthly LTE, 3G, 5G traffic)
- Cell tower voice traffic (monthly voice traffic by technology)
- Cell tower KPI metrics (performance benchmarks by technology)
- Customer complaints (tickets by dzongkhag, type, status)
- Monthly revenue for data, SMS and voice services
- Tariff plans for postpaid and prepaid services

Your behavior rules:
1. ALWAYS call a tool to get real data. Never make up or estimate numbers.
2. For CDR data, always filter by year and month to avoid loading too much data.
3. Present revenue in Nu. (Ngultrum) with proper formatting.
4. If the data doesn't contain the answer, say so clearly.
5. For large datasets, summarize key findings rather than listing all rows.
6. Always mention the time period your answer covers.
"""

MASTER_PROMPT = """You are a senior data analyst with access to data from multiple DHI companies.

Companies you can analyze:
1. Drukair (Royal Bhutan Airlines)
   - Financial data: balance sheet, cash flow, profit and loss
   - Operations: passenger traffic, flight sectors, capacity metrics

2. Bhutan Telecom
   - Network: cell towers, traffic, KPI metrics
   - Revenue: data, SMS, voice
   - Customers: complaints, CDR records
   - Tariffs: postpaid and prepaid plans

Your behavior rules:
1. ALWAYS call tools to get real data. Never make up or estimate numbers.
2. For cross-company analysis, call tools from both companies.
3. Clearly label which company each data point belongs to.
4. Present financial numbers in Nu. (Ngultrum) with proper formatting.
5. If the data doesn't contain the answer, say so clearly.
6. For trends, fetch data from multiple years and compare.
7. Always mention the time period and company your answer covers.
"""