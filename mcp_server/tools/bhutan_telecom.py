# tools/bhutan_telecom.py
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

from server import mcp

# Try .env inside mcp_server/ first, then project root (scripts/)
env_path = Path(__file__).resolve().parent.parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"

load_dotenv(dotenv_path=env_path, override=True)

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")


@mcp.tool()
def get_bt_cdr_postpaid_voice(
    year: int | None = None,
    month: int | None = None,
    page: int = 1,
    limit: int = 500,
) -> str:
    """
    Get Bhutan Telecom postpaid voice call detail records.
    Use this when the user asks about:
    - Voice call usage or volume
    - Postpaid voice charges or billing amounts
    - Call patterns or trends over time

    Args:
        year: Filter by year.
        month: Filter by month number (1=January, 12=December).
        page: Page number.
        limit: Records to return.
    """
    params = {"page": page, "limit": limit}
    if year:
        params["year"] = year
    if month:
        params["month"] = month

    try:
        response = httpx.get(
            f"{API_BASE}/bhutan_telecom/cdr_postpaid_voice",
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching BT postpaid voice CDR: {str(e)}"


@mcp.tool()
def get_bt_cdr_postpaid_sms(
    year: int | None = None,
    month: int | None = None,
    page: int = 1,
    limit: int = 500,
) -> str:
    """
    Get Bhutan Telecom postpaid SMS call detail records.
    Use this when the user asks about:
    - SMS usage or volume
    - Postpaid SMS charges
    - SMS patterns over time

    Args:
        year: Filter by year.
        month: Filter by month number.
        page: Page number.
        limit: Records to return.
    """
    params = {"page": page, "limit": limit}
    if year:
        params["year"] = year
    if month:
        params["month"] = month

    try:
        response = httpx.get(
            f"{API_BASE}/bhutan_telecom/cdr_postpaid_sms",
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching BT postpaid SMS CDR: {str(e)}"


@mcp.tool()
def get_bt_cdr_postpaid_data(
    year: int | None = None,
    month: int | None = None,
    page: int = 1,
    limit: int = 500,
) -> str:
    """
    Get Bhutan Telecom postpaid data usage records.
    Use this when the user asks about:
    - Data usage volume
    - Postpaid data charges
    - Internet usage patterns

    Args:
        year: Filter by year.
        month: Filter by month number.
        page: Page number.
        limit: Records to return.
    """
    params = {"page": page, "limit": limit}
    if year:
        params["year"] = year
    if month:
        params["month"] = month

    try:
        response = httpx.get(
            f"{API_BASE}/bhutan_telecom/cdr_postpaid_data",
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching BT postpaid data CDR: {str(e)}"


@mcp.tool()
def get_bt_cdr_prepaid_data(
    year: int | None = None,
    month: int | None = None,
    page: int = 1,
    limit: int = 500,
) -> str:
    """
    Get Bhutan Telecom prepaid data usage records.
    Use this when the user asks about:
    - Prepaid data usage
    - Prepaid internet patterns
    - Data usage by APN

    Args:
        year: Filter by year.
        month: Filter by month number.
        page: Page number.
        limit: Records to return.
    """
    params = {"page": page, "limit": limit}
    if year:
        params["year"] = year
    if month:
        params["month"] = month

    try:
        response = httpx.get(
            f"{API_BASE}/bhutan_telecom/cdr_prepaid_data",
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching BT prepaid data CDR: {str(e)}"


@mcp.tool()
def get_bt_cell_tower_details(region: str | None = None) -> str:
    """
    Get Bhutan Telecom cell tower site details and locations.
    Use this when the user asks about:
    - Cell tower locations or coordinates
    - Network coverage by region
    - Which towers support LTE, 3G, 5G, 2G
    - Number of towers in a region

    Args:
        region: Filter by region code (e.g. 'WR', 'ER', 'CR', 'SWR').
    """
    params = {}
    if region:
        params["region"] = region

    try:
        response = httpx.get(
            f"{API_BASE}/bhutan_telecom/cell_tower_details",
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching BT cell tower details: {str(e)}"


@mcp.tool()
def get_bt_cell_tower_data_traffic(
    year: int | None = None,
    month: str | None = None,
) -> str:
    """
    Get Bhutan Telecom cell tower data traffic statistics.
    Use this when the user asks about:
    - Monthly data traffic volume (LTE, 3G, 5G)
    - Total data traffic trends
    - Traffic breakdown by technology

    Args:
        year: Filter by year.
        month: Filter by month name (e.g. 'january').
    """
    params = {}
    if year:
        params["year"] = year
    if month:
        params["months"] = month

    try:
        response = httpx.get(
            f"{API_BASE}/bhutan_telecom/cell_tower_data_traffic",
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching BT cell tower data traffic: {str(e)}"


@mcp.tool()
def get_bt_cell_tower_voice_traffic(
    year: int | None = None,
    month: str | None = None,
) -> str:
    """
    Get Bhutan Telecom cell tower voice traffic statistics.
    Use this when the user asks about:
    - Monthly voice traffic volume
    - VoLTE vs 3G vs 2G voice traffic
    - Voice network usage patterns

    Args:
        year: Filter by year.
        month: Filter by month name (e.g. 'january').
    """
    params = {}
    if year:
        params["year"] = year
    if month:
        params["month"] = month

    try:
        response = httpx.get(
            f"{API_BASE}/bhutan_telecom/cell_tower_voice_traffic",
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching BT cell tower voice traffic: {str(e)}"


@mcp.tool()
def get_bt_cell_tower_data_traffic_summary(
    year: int | None = None,
    region: str | None = None,
) -> str:
    """
    Get Bhutan Telecom cell tower data traffic summary by region.
    Use this when the user asks about:
    - Data traffic by region
    - Regional network usage comparison
    - Monthly traffic by region

    Args:
        year: Filter by year.
        region: Filter by region name (e.g. 'Eastern Region').
    """
    params = {}
    if year:
        params["year"] = year
    if region:
        params["region"] = region

    try:
        response = httpx.get(
            f"{API_BASE}/bhutan_telecom/cell_tower_data_traffic_summary",
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching BT data traffic summary: {str(e)}"


@mcp.tool()
def get_bt_cell_tower_kpi(
    year: int | None = None,
    technology: str | None = None,
) -> str:
    """
    Get Bhutan Telecom cell tower KPI metrics.
    Use this when the user asks about:
    - Network performance metrics
    - BTS availability or uptime
    - Call drop rates or success rates
    - KPI benchmarks vs actual performance

    Args:
        year: Filter by year.
        technology: Filter by technology (e.g. 'GSM', 'LTE', '5G').
    """
    params = {}
    if year:
        params["year"] = year
    if technology:
        params["technology"] = technology

    try:
        response = httpx.get(
            f"{API_BASE}/bhutan_telecom/cell_tower_kpi",
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching BT cell tower KPI: {str(e)}"


@mcp.tool()
def get_bt_cell_tower_kpi_report(location: str | None = None) -> str:
    """
    Get Bhutan Telecom KPI report by location.
    Use this when the user asks about:
    - KPI performance at specific locations
    - Packet switch drop rate or success rate
    - Download throughput by location

    Args:
        location: Filter by location name (e.g. 'Thimphu').
    """
    params = {}
    if location:
        params["location"] = location

    try:
        response = httpx.get(
            f"{API_BASE}/bhutan_telecom/cell_tower_kpi_report",
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching BT KPI report: {str(e)}"


@mcp.tool()
def get_bt_customer_complaints(
    year: int | None = None,
    dzongkhag: str | None = None,
    complaint_type: str | None = None,
    status: str | None = None,
    page: int = 1,
    limit: int = 500,
) -> str:
    """
    Get Bhutan Telecom customer complaint tickets.
    Use this when the user asks about:
    - Number of complaints or complaint trends
    - Complaints by district (dzongkhag)
    - Complaint types (Mobile, Broadband, etc.)
    - Resolved vs open complaints

    Args:
        year: Filter by year.
        dzongkhag: Filter by district (e.g. 'Thimphu', 'Haa').
        complaint_type: Filter by type (e.g. 'Mobile').
        status: Filter by status (e.g. 'Close', 'Open').
        page: Page number.
        limit: Records to return.
    """
    params = {"page": page, "limit": limit}
    if year:
        params["year"] = year
    if dzongkhag:
        params["dzongkhag"] = dzongkhag
    if complaint_type:
        params["complaint_type"] = complaint_type
    if status:
        params["status"] = status

    try:
        response = httpx.get(
            f"{API_BASE}/bhutan_telecom/customer_complaints",
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching BT customer complaints: {str(e)}"


@mcp.tool()
def get_bt_monthly_revenue_data(
    year: int | None = None,
    month: int | None = None,
) -> str:
    """
    Get Bhutan Telecom monthly revenue from data/internet services.
    Use this when the user asks about:
    - Data service revenue
    - Internet revenue trends
    - Monthly data revenue

    Args:
        year: Filter by year.
        month: Filter by month number.
    """
    params = {}
    if year:
        params["year"] = year
    if month:
        params["month"] = month

    try:
        response = httpx.get(
            f"{API_BASE}/bhutan_telecom/monthly_revenue_data",
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching BT monthly revenue data: {str(e)}"


@mcp.tool()
def get_bt_monthly_revenue_sms(
    year: int | None = None,
    month: int | None = None,
) -> str:
    """
    Get Bhutan Telecom monthly revenue from SMS services.
    Use this when the user asks about:
    - SMS service revenue
    - SMS revenue trends
    - Monthly SMS revenue

    Args:
        year: Filter by year.
        month: Filter by month number.
    """
    params = {}
    if year:
        params["year"] = year
    if month:
        params["month"] = month

    try:
        response = httpx.get(
            f"{API_BASE}/bhutan_telecom/monthly_revenue_sms",
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching BT monthly SMS revenue: {str(e)}"


@mcp.tool()
def get_bt_monthly_revenue_voice(
    year: int | None = None,
    month: int | None = None,
) -> str:
    """
    Get Bhutan Telecom monthly revenue from voice services.
    Use this when the user asks about:
    - Voice service revenue
    - Voice revenue trends
    - Monthly voice revenue

    Args:
        year: Filter by year.
        month: Filter by month number.
    """
    params = {}
    if year:
        params["year"] = year
    if month:
        params["month"] = month

    try:
        response = httpx.get(
            f"{API_BASE}/bhutan_telecom/monthly_revenue_voice",
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching BT monthly voice revenue: {str(e)}"


@mcp.tool()
def get_bt_postpaid_tariffs() -> str:
    """
    Get all Bhutan Telecom postpaid tariff plans.
    Use this when the user asks about:
    - Postpaid plan prices or packages
    - Data quota for postpaid plans
    - Voice or SMS charges for postpaid
    """
    try:
        booster = httpx.get(
            f"{API_BASE}/bhutan_telecom/postpaid_tariff_booster", timeout=30
        )
        monthly = httpx.get(
            f"{API_BASE}/bhutan_telecom/postpaid_tariff_monthly", timeout=30
        )
        sms = httpx.get(
            f"{API_BASE}/bhutan_telecom/postpaid_tariff_sms", timeout=30
        )
        voice = httpx.get(
            f"{API_BASE}/bhutan_telecom/postpaid_tariff_voice", timeout=30
        )
        return f"""
Booster Plans: {booster.text}
Monthly Plans: {monthly.text}
SMS Tariffs: {sms.text}
Voice Tariffs: {voice.text}
"""
    except Exception as e:
        return f"Error fetching BT postpaid tariffs: {str(e)}"


@mcp.tool()
def get_bt_prepaid_tariffs() -> str:
    """
    Get all Bhutan Telecom prepaid tariff plans.
    Use this when the user asks about:
    - Prepaid plan prices or packages
    - Air fibre plans and pricing
    - Voice or SMS charges for prepaid
    """
    try:
        air_fibre = httpx.get(
            f"{API_BASE}/bhutan_telecom/prepaid_tariff_air_fibre", timeout=30
        )
        data_plan = httpx.get(
            f"{API_BASE}/bhutan_telecom/prepaid_tariff_data_plan", timeout=30
        )
        voice_sms = httpx.get(
            f"{API_BASE}/bhutan_telecom/prepaid_tariff_voice_sms", timeout=30
        )
        return f"""
Air Fibre Plans: {air_fibre.text}
Data Plans: {data_plan.text}
Voice and SMS Tariffs: {voice_sms.text}
"""
    except Exception as e:
        return f"Error fetching BT prepaid tariffs: {str(e)}"


@mcp.tool()
def get_bt_complaint_dzongkhags() -> str:
    """
    Get all unique dzongkhags that have customer complaints.
    Use this when you need to know available districts before filtering.
    """
    try:
        response = httpx.get(
            f"{API_BASE}/bhutan_telecom/helper/customer_complaints/dzongkhags",
            timeout=30,
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching BT dzongkhags: {str(e)}"


@mcp.tool()
def get_bt_cell_tower_regions() -> str:
    """
    Get all unique regions that have cell towers.
    Use this when you need to know available regions before filtering.
    """
    try:
        response = httpx.get(
            f"{API_BASE}/bhutan_telecom/helper/cell_tower_details/regions",
            timeout=30,
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching BT cell tower regions: {str(e)}"