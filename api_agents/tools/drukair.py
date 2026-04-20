import os
import httpx 
from langchain.tools import tool

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

@tool
def get_drukair_balance_sheet(year: int = None, category: str = None) -> str:
    """
    Get Drukair balance sheet data showing assets, liabilities and equity.
    Use this when the user asks about:
    - Total assets or specific assets (property, equipment, receivables)
    - Total liabilities or specific liabilities (borrowings, payables)
    - Equity, share capital, retained earnings
    - Financial position at a specific date

    Args:
        year: Filter by year (e.g. 2024). Leave empty for all years.
        category: Filter by 'Assets' or 'Liabilities'. Leave empty for both.
    """
    params = {}
    if year: 
        params["year"] = year
    if category:
        params["category"] = category

    try:
        response = httpx.get(
            f"{API_BASE}/drukair/balance_sheet",
            params=params,
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching balance sheet: {str(e)}"
    

@tool
def get_drukair_cash_flow(year: int = None, category: str = None) -> str:
    """
    Get Drukair cash flow statement data.
    Use this when the user asks about:
    - Operating cash flow or cash from operations
    - Investing activities (capital expenditure, purchases)
    - Financing activities (loans, repayments)
    - Net cash position or cash movement

    Args:
        year: Filter by year. Leave empty for all years.
        category: Filter by cash flow category. Leave empty for all.
    """
    params = {}
    if year:
        params["year"] = year
    if category:
        params["category"] = category
        
    try:
        response = httpx.get(
            f"{API_BASE}/drukair/cash_flow",
            params=params,
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching cash flow: {str(e)}"


@tool
def get_drukair_profit_loss(year: int = None, category: str = None) -> str:
    """
    Get Drukair profit and loss statement data.
    Use this when the user asks about:
    - Revenue or income (traffic revenue, other income)
    - Expenses or costs (fuel, staff, maintenance)
    - Net profit or net loss
    - Operating profit or EBITDA
    - Financial performance for a year or quarter

    Args:
        year: Filter by year. Leave empty for all years.
        category: Filter by 'Income' or 'Expenses'. Leave empty for both.
    """
    params = {}
    if year:
        params["year"] = year
    if category:
        params["category"] = category

    try:
        response = httpx.get(
            f"{API_BASE}/drukair/profit_loss",
            params=params,
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching profit and loss: {str(e)}"


@tool
def get_drukair_passenger_traffic(
    year: int = None,
    month: int = None,
    origin: str = None,
    destination: str = None,
    dom_int: str = None,
    page: int = 1,
    limit: int = 500,
) -> str:
    """
    Get Drukair passenger ticket and booking transaction data.
    Use this when the user asks about:
    - Number of passengers on a route or period
    - Domestic vs international passenger counts
    - Fares or ticket prices
    - Specific routes (e.g. PBH to BKK)
    - Passenger trends over time

    Args:
        year: Filter by year.
        month: Filter by month number (1=January, 12=December).
        origin: Origin airport code (e.g. PBH for Paro, BKK for Bangkok).
        destination: Destination airport code.
        dom_int: 'DOM' for domestic flights, 'INT' for international.
        page: Page number for pagination (default 1).
        limit: Number of records to return (default 500).
    """
    params = {"page": page, "limit": limit}
    if year:
        params["year"] = year
    if month:
        params["month"] = month
    if origin:
        params["origin"] = origin
    if destination:
        params["destination"] = destination
    if dom_int:
        params["dom_int"] = dom_int

    try:
        response = httpx.get(
            f"{API_BASE}/drukair/passenger_traffic",
            params=params,
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching passenger traffic: {str(e)}"


@tool
def get_drukair_master_data(
    year: int = None,
    flight_type: str = None,
    sector: str = None,
    page: int = 1,
    limit: int = 500,
) -> str:
    """
    Get Drukair flight operations master data with capacity and performance metrics.
    Use this when the user asks about:
    - Seat allocation or seat availability
    - Available Seat Kilometres (ASK) or Revenue Passenger Kilometres (RPK)
    - Load factor or capacity utilisation
    - Number of flights operated on a route
    - Flight types or aircraft types used
    - Sector performance over multiple years

    Args:
        year: Filter by year (2018-2025). Leave empty for all years.
        flight_type: Filter by flight type.
        sector: Filter by route sector (e.g. PBH-BKK).
        page: Page number for pagination.
        limit: Number of records to return.
    """
    params = {"page": page, "limit": limit}
    if year:
        params["year"] = year
    if flight_type:
        params["flight_type"] = flight_type
    if sector:
        params["sector"] = sector

    try:
        response = httpx.get(
            f"{API_BASE}/drukair/master_data",
            params=params,
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching master data: {str(e)}"


@tool
def get_drukair_routes() -> str:
    """
    Get all unique Drukair flight routes showing origin and destination pairs.
    Use this when the user asks about:
    - What routes does Drukair fly?
    - Which destinations does Drukair serve?
    - Available origin or destination airports
    """
    try:
        response = httpx.get(
            f"{API_BASE}/drukair/passenger_traffic/routes",
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching routes: {str(e)}"


@tool
def get_drukair_sectors() -> str:
    """
    Get all unique flight sectors from Drukair master data.
    Use this when you need to know available sectors before filtering master data.
    """
    try:
        response = httpx.get(
            f"{API_BASE}/drukair/master_data/sectors",
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching sectors: {str(e)}"


# This list is imported by graph.py
# It tells the agent which tools are available for Drukair
drukair_tools = [
    get_drukair_balance_sheet,
    get_drukair_cash_flow,
    get_drukair_profit_loss,
    get_drukair_passenger_traffic,
    get_drukair_master_data,
    get_drukair_routes,
    get_drukair_sectors,
]