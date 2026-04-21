# routers/drukair.py
from fastapi import APIRouter
from db import run_query, run_paginated_query

router = APIRouter(prefix="/drukair", tags=["Drukair"])


# ============================================================
# BALANCE SHEET
# Filters: year, category (Assets / Liabilities)
# ============================================================
@router.get("/balance_sheet")
def balance_sheet(year: int = None, category: str = None):
    sql = """
        SELECT
            date,
            category,
            subcategory,
            particulars,
            note,
            amount
        FROM iceberg.drukair.balance_sheet
    """ 
    filters = []
    if year:
        filters.append(f"year = {year}")
    if category and category.upper() != "NONE":
        filters.append(f"UPPER(category) = UPPER('{category}')")
    if filters:
        sql += " WHERE " + " AND ".join(filters)

    sql += " ORDER BY date, category, particulars"
    return {"data": run_query(sql)}


# ============================================================
# CASH FLOW
# Filters: year, category
# ============================================================
@router.get("/cash_flow")
def cash_flow(year: int = None, category: str = None):
    sql = """
        SELECT
            date,
            category,
            particulars,
            amount
        FROM iceberg.drukair.cash_flow
    """
    filters = []
    if year:
        filters.append(f"year = {year}")
    if category and category.upper() != "NONE":
        filters.append(f"UPPER(category) = UPPER('{category}')")
    if filters:
        sql += " WHERE " + " AND ".join(filters)

    sql += " ORDER BY date, category"
    return {"data": run_query(sql)}


# ============================================================
# PROFIT & LOSS
# Filters: year, category
# ============================================================
@router.get("/profit_loss")
def profit_loss(year: int = None, category: str = None):
    sql = """
        SELECT
            date,
            category,
            particulars,
            note,
            amount
        FROM iceberg.drukair.profit_loss
    """
    filters = []
    if year:
        filters.append(f"year = {year}")
    if category and category.upper() != "NONE":
        filters.append(f"UPPER(category) = UPPER('{category}')")
    if filters:
        sql += " WHERE " + " AND ".join(filters)

    sql += " ORDER BY date, category"
    return {"data": run_query(sql)}


# ============================================================
# PASSENGER TRAFFIC
# Individual ticket/booking transactions
# Filters: year, month, origin (orac), destination (dstc),
#          dom_int (DOM/INT), fare_type
# ============================================================
@router.get("/passenger_traffic")
def passenger_traffic(
    year: int = None,
    month: int = None,
    origin: str = None,
    destination: str = None,
    dom_int: str = None,
    fare_type: str = None,
    page: int = 1,
    limit: int = 100,
):
    sql = """
        SELECT
            mnth, zone, ftda, orac, dstc, carr, ftnr, imma,
            fare_type, cpvf, npax, dom_int, fltp, own_oa,
            gl_post_date, gl_status, emis_cutp, tpax,
            yq, tmff, cpvf_no_vat, vat_amount, pxnm
        FROM iceberg.drukair.passenger_traffic
    """
    # All filters at the same level — not nested
    filters = []
    if year:
        filters.append(f"year = {year}")
    if month:
        filters.append(f"MONTH(mnth) = {month}")
    if origin and origin.upper() != "NONE":
        filters.append(f"UPPER(orac) = UPPER('{origin}')")
    if destination and destination.upper() != "NONE":
        filters.append(f"UPPER(dstc) = UPPER('{destination}')")
    if dom_int and dom_int.upper() != "NONE":
        filters.append(f"UPPER(dom_int) = UPPER('{dom_int}')")
    if fare_type and fare_type.upper() != "NONE":
        filters.append(f"UPPER(fare_type) = UPPER('{fare_type}')")
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    sql += " ORDER BY mnth DESC"

    return run_paginated_query(sql, page, limit)


# ============================================================
# MASTER DATA (combined across all years)
# Flight operation stats: sectors, seat allocation, load factors
# Filters: year, flight_type, sector
# ============================================================

# These are columns that exist consistently across all years
MASTER_DATA_COLUMNS = """
    flight_type,
    sector,
    distance,
    mins,
    block_time,
    seat_allocation,
    seat_available,
    no_of_flts,
    total_pax,
    ask,
    rpk,
    bh_month,
    capacity_produced
"""

MASTER_DATA_YEARS = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]


@router.get("/master_data")
def master_data(
    year: int = None,
    flight_type: str = None,
    sector: str = None,
    page: int = 1,
    limit: int = 100,
):
    if year and year in MASTER_DATA_YEARS:
        # Single year — query just that one table
        sql = f"""
            SELECT {MASTER_DATA_COLUMNS}, {year} AS year
            FROM iceberg.drukair.master_data_{year}
        """
        filters = []
        if flight_type and flight_type.upper() != "NONE":
            filters.append(f"UPPER(flight_type) = UPPER('{flight_type}')")
        if sector and sector.upper() != "NONE":
            filters.append(f"UPPER(sector) = UPPER('{sector}')")
        if filters:
            sql += " WHERE " + " AND ".join(filters)
        sql += " ORDER BY sector"

    else:
        # All years — UNION ALL then filter on the outside
        year_queries = []
        for y in MASTER_DATA_YEARS:
            year_queries.append(f"""
                SELECT {MASTER_DATA_COLUMNS}, {y} AS year
                FROM iceberg.drukair.master_data_{y}
            """)
        unioned = " UNION ALL ".join(year_queries)

        filters = []
        if flight_type and flight_type.upper() != "NONE":
            filters.append(f"UPPER(flight_type) = UPPER('{flight_type}')")
        if sector and sector.upper() != "NONE":
            filters.append(f"UPPER(sector) = UPPER('{sector}')")

        if filters:
            where_clause = " AND ".join(filters)
            sql = f"""
                SELECT * FROM ({unioned}) AS combined
                WHERE {where_clause}
                ORDER BY year, sector
            """
        else:
            sql = f"""
                SELECT * FROM ({unioned}) AS combined
                ORDER BY year, sector
            """

    return run_paginated_query(sql, page, limit)


# ============================================================
# HELPER ENDPOINTS
# Useful for frontend dropdowns / filters
# ============================================================

@router.get("/master_data/sectors")
def master_data_sectors():
    """Returns all unique sectors — useful for frontend dropdown"""
    sql = """
        SELECT DISTINCT sector
        FROM iceberg.drukair.master_data_2025
        ORDER BY sector
    """
    return {"data": run_query(sql)}


@router.get("/master_data/flight_types")
def master_data_flight_types():
    """Returns all unique flight types — useful for frontend dropdown"""
    sql = """
        SELECT DISTINCT flight_type
        FROM iceberg.drukair.master_data_2025
        ORDER BY flight_type
    """
    return {"data": run_query(sql)}


@router.get("/passenger_traffic/routes")
def passenger_traffic_routes():
    """Returns all unique origin-destination pairs"""
    sql = """
        SELECT DISTINCT orac, dstc
        FROM iceberg.drukair.passenger_traffic
        ORDER BY orac, dstc
    """
    return {"data": run_query(sql)}