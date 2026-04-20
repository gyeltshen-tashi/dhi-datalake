import os 
import httpx
from langchain.tools import tool

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")


@tool
def get_bt_cdr_postpaid_voice(
    year: int=None,
    month: int=None,
    page: int=1,
    limit: int=500,
) -> str:
    """
    Get Bhutan Telecom postpaid voice call detail records (CDR).
    Use this when the user asks about:
    - Voice call usage or volume
    - Postpaid voice charges or billing amounts
    - Call patterns or trends over time
    - Number of voice calls made

    Args:
        year: Filter by year (e.g. 2025).
        month: Filter by month number (1=January, 12=December).
        page: Page number for pagination.
        limit: Number of records to return (default 500).
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
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching postpaid voice CDR: {str(e)}"
    

@tool
def get_bt_cdr_postpaid_sms(
    year: int = None,
    month: int = None,
    page: int = 1,
    limit: int = 500,
) -> str:
    """
    Get Bhutan Telecom postpaid SMS call detail records (CDR).
    Use this when the user asks about:
    - SMS usage or volume
    - Postpaid SMS charges or billing amounts
    - SMS patterns or trends over time

    Args:
        year: Filter by year.
        month: Filter by month number (1=January, 12=December).
        page: Page number for pagination.
        limit: Number of records to return.
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
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching postpaid SMS CDR: {str(e)}"


@tool
def get_bt_cdr_postpaid_data(
    year: int = None,
    month: int = None,
    page: int = 1,
    limit: int = 500,
) -> str:
    """
    Get Bhutan Telecom postpaid data usage call detail records (CDR).
    Use this when the user asks about:
    - Data usage volume or consumption
    - Postpaid data charges
    - Internet usage patterns or trends

    Args:
        year: Filter by year.
        month: Filter by month number (1=January, 12=December).
        page: Page number for pagination.
        limit: Number of records to return.
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
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching postpaid data CDR: {str(e)}"


@tool
def get_bt_cdr_prepaid_data(
    year: int = None,
    month: int = None,
    page: int = 1,
    limit: int = 500,
) -> str:
    """
    Get Bhutan Telecom prepaid data usage records.
    Use this when the user asks about:
    - Prepaid data usage or consumption
    - Prepaid internet usage patterns
    - Data usage by APN

    Args:
        year: Filter by year.
        month: Filter by month number (1=January, 12=December).
        page: Page number for pagination.
        limit: Number of records to return.
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
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching prepaid data CDR: {str(e)}"


@tool
def get_bt_cell_tower_details(region: str = None) -> str:
    """
    Get Bhutan Telecom cell tower site details and locations.
    Use this when the user asks about:
    - Cell tower locations or coordinates
    - Network coverage by region
    - Which towers support LTE, 3G, 5G, 2G
    - Number of towers in a region
    - Specific tower site information

    Args:
        region: Filter by region code (e.g. 'WR' for Western Region,
                'ER' for Eastern, 'CR' for Central, 'SWR' for South Western).
                Leave empty for all regions.
    """
    params = {}
    if region:
        params["region"] = region

    try:
        response = httpx.get(
            f"{API_BASE}/bhutan_telecom/cell_tower_details",
            params=params,
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching cell tower details: {str(e)}"


@tool
def get_bt_cell_tower_data_traffic(
    year: int = None,
    month: str = None,
) -> str:
    """
    Get Bhutan Telecom cell tower data traffic statistics.
    Use this when the user asks about:
    - Monthly data traffic volume (LTE, 3G, 5G)
    - Total data traffic trends
    - Traffic breakdown by technology (LTE vs 3G vs 5G)
    - Network data traffic growth

    Args:
        year: Filter by year.
        month: Filter by month name (e.g. 'january', 'february').
    """
    params = {}
    if year:
        params["year"] = year
    if month:
        params["month"] = month

    try:
        response = httpx.get(
            f"{API_BASE}/bhutan_telecom/cell_tower_data_traffic",
            params=params,
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching cell tower data traffic: {str(e)}"


@tool
def get_bt_cell_tower_voice_traffic(
    year: int = None,
    month: str = None,
) -> str:
    """
    Get Bhutan Telecom cell tower voice traffic statistics.
    Use this when the user asks about:
    - Monthly voice traffic volume
    - VoLTE vs 3G vs 2G voice traffic
    - Total voice traffic trends
    - Voice network usage patterns

    Args:
        year: Filter by year.
        month: Filter by month name (e.g. 'january', 'february').
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
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching cell tower voice traffic: {str(e)}"


@tool
def get_bt_cell_tower_data_traffic_summary(
    year: int = None,
    region: str = None,
) -> str:
    """
    Get Bhutan Telecom cell tower data traffic summary by region.
    Use this when the user asks about:
    - Data traffic by region or dzongkhag
    - Regional network usage comparison
    - Monthly traffic breakdown by region

    Args:
        year: Filter by year.
        region: Filter by region name (e.g. 'Eastern Region', 'Western Region').
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
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching data traffic summary: {str(e)}"


@tool
def get_bt_cell_tower_kpi(
    year: int = None,
    technology: str = None,
) -> str:
    """
    Get Bhutan Telecom cell tower KPI (Key Performance Indicator) metrics.
    Use this when the user asks about:
    - Network performance metrics
    - BTS availability or uptime
    - Call drop rates or success rates
    - KPI benchmarks vs actual performance
    - Performance by technology (GSM, LTE, 5G)

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
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching cell tower KPI: {str(e)}"


@tool
def get_bt_cell_tower_kpi_report(location: str = None) -> str:
    """
    Get Bhutan Telecom cell tower KPI report by location.
    Use this when the user asks about:
    - KPI performance at specific locations
    - Packet switch drop rate or success rate
    - Download throughput by location
    - Core area network performance

    Args:
        location: Filter by location name (e.g. 'Thimphu', 'Paro').
    """
    params = {}
    if location:
        params["location"] = location

    try:
        response = httpx.get(
            f"{API_BASE}/bhutan_telecom/cell_tower_kpi_report",
            params=params,
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching KPI report: {str(e)}"


@tool
def get_bt_customer_complaints(
    year: int = None,
    dzongkhag: str = None,
    complaint_type: str = None,
    status: str = None,
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
    - Customer service performance

    Args:
        year: Filter by year.
        dzongkhag: Filter by district (e.g. 'Thimphu', 'Haa', 'Paro').
        complaint_type: Filter by type (e.g. 'Mobile', 'Broadband').
        status: Filter by status (e.g. 'Close', 'Open').
        page: Page number for pagination.
        limit: Number of records to return.
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
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching customer complaints: {str(e)}"


@tool
def get_bt_monthly_revenue_data(
    year: int = None,
    month: int = None,
) -> str:
    """
    Get Bhutan Telecom monthly revenue from data/internet services.
    Use this when the user asks about:
    - Data service revenue
    - Internet revenue trends
    - Data usage in GB alongside revenue
    - Monthly data revenue performance

    Args:
        year: Filter by year.
        month: Filter by month number (1=January, 12=December).
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
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching monthly revenue data: {str(e)}"


@tool
def get_bt_monthly_revenue_sms(
    year: int = None,
    month: int = None,
) -> str:
    """
    Get Bhutan Telecom monthly revenue from SMS services.
    Use this when the user asks about:
    - SMS service revenue
    - SMS revenue trends
    - SMS usage volume alongside revenue
    - Monthly SMS revenue performance

    Args:
        year: Filter by year.
        month: Filter by month number (1=January, 12=December).
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
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching monthly SMS revenue: {str(e)}"


@tool
def get_bt_monthly_revenue_voice(
    year: int = None,
    month: int = None,
) -> str:
    """
    Get Bhutan Telecom monthly revenue from voice services.
    Use this when the user asks about:
    - Voice service revenue
    - Voice revenue trends
    - Voice usage duration alongside revenue
    - Monthly voice revenue performance

    Args:
        year: Filter by year.
        month: Filter by month number (1=January, 12=December).
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
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching monthly voice revenue: {str(e)}"
    

@tool
def get_bt_postpaid_tariffs() -> str:
    """
    Get Bhutan Telecom postpaid tariff plans including booster, monthly, SMS and voice tariffs.
    Use this when the user asks about:
    - Postpaid plan prices or packages
    - Data quota for postpaid plans
    - Voice or SMS charges for postpaid
    - Available postpaid plans
    """
    try:
        booster = httpx.get(f"{API_BASE}/bhutan_telecom/postpaid_tariff_booster", timeout=30)
        monthly = httpx.get(f"{API_BASE}/bhutan_telecom/postpaid_tariff_monthly", timeout=30)
        sms = httpx.get(f"{API_BASE}/bhutan_telecom/postpaid_tariff_sms", timeout=30)
        voice = httpx.get(f"{API_BASE}/bhutan_telecom/postpaid_tariff_voice", timeout=30)

        return f"""
Booster Plans: {booster.text}
Monthly Plans: {monthly.text}
SMS Tariffs: {sms.text}
Voice Tariffs: {voice.text}
"""
    except Exception as e:
        return f"Error fetching postpaid tariffs: {str(e)}"
    

@tool
def get_bt_prepaid_tariffs() -> str:
    """
    Get Bhutan Telecom prepaid tariff plans including data plans, air fibre and voice/SMS tariffs.
    Use this when the user asks about:
    - Prepaid plan prices or packages
    - Data quota for prepaid plans
    - Air fibre plans and pricing
    - Voice or SMS charges for prepaid
    - Available prepaid plans
    """
    try:
        air_fibre = httpx.get(f"{API_BASE}/bhutan_telecom/prepaid_tariff_air_fibre", timeout=30)
        data_plan = httpx.get(f"{API_BASE}/bhutan_telecom/prepaid_tariff_data_plan", timeout=30)
        voice_sms = httpx.get(f"{API_BASE}/bhutan_telecom/prepaid_tariff_voice_sms", timeout=30)

        return f"""
Air Fibre Plans: {air_fibre.text}
Data Plans: {data_plan.text}
Voice and SMS Tariffs: {voice_sms.text}
"""
    except Exception as e:
        return f"Error fetching prepaid tariffs: {str(e)}"


@tool
def get_bt_complaint_dzongkhags() -> str:
    """
    Get all unique dzongkhags (districts) that have customer complaints.
    Use this when you need to know available districts before filtering complaints.
    """
    try:
        response = httpx.get(
            f"{API_BASE}/bhutan_telecom/helper/customer_complaints/dzongkhags",
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching dzongkhags: {str(e)}"


@tool
def get_bt_cell_tower_regions() -> str:
    """
    Get all unique regions that have cell towers.
    Use this when you need to know available regions before filtering cell tower data.
    """
    try:
        response = httpx.get(
            f"{API_BASE}/bhutan_telecom/helper/cell_tower_details/regions",
            timeout=30
        )
        return response.text
    except Exception as e:
        return f"Error fetching cell tower regions: {str(e)}"


# List of all BT tools — imported by graph.py
bt_tools = [
    get_bt_cdr_postpaid_voice,
    get_bt_cdr_postpaid_sms,
    get_bt_cdr_postpaid_data,
    get_bt_cdr_prepaid_data,
    get_bt_cell_tower_details,
    get_bt_cell_tower_data_traffic,
    get_bt_cell_tower_voice_traffic,
    get_bt_cell_tower_data_traffic_summary,
    get_bt_cell_tower_kpi,
    get_bt_cell_tower_kpi_report,
    get_bt_customer_complaints,
    get_bt_monthly_revenue_data,
    get_bt_monthly_revenue_sms,
    get_bt_monthly_revenue_voice,
    get_bt_postpaid_tariffs,
    get_bt_prepaid_tariffs,
    get_bt_complaint_dzongkhags,
    get_bt_cell_tower_regions,
]