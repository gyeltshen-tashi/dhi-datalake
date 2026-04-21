# routers/bhutan_telecom.py
from fastapi import APIRouter
from db import run_query, run_paginated_query

router = APIRouter(prefix="/bhutan_telecom", tags=["Bhutan Telecom"])


# ============================================================
# CDR — POSTPAID VOICE
# Large data, paginated
# Filters: year, month
# ============================================================
@router.get("/cdr_postpaid_voice")
def cdr_postpaid_voice(
    year: int = None,
    month: int = None,
    page: int = 1,
    limit: int = 100,
):
    sql = """
        SELECT
            s_p_number_address,
            o_p_number_address,
            starttime,
            receiveddate,
            rated_flat_amount,
            tariff_info_sncode,
            rated_volume
        FROM iceberg.bhutan_telecom.cdr_postpaid_voice
    """
    filters = []
    if year:
        filters.append(f"""
            YEAR(
                COALESCE(
                    TRY(CAST(starttime AS TIMESTAMP)),
                    TRY(date_parse(starttime, '%m-%d-%Y %H:%i:%s'))
                )
            ) = {year}
        """)
    if month:
        filters.append(f"""
            MONTH(
                COALESCE(
                    TRY(CAST(starttime AS TIMESTAMP)),
                    TRY(date_parse(starttime, '%m-%d-%Y %H:%i:%s'))
                )
            ) = {month}
        """)
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    sql += " ORDER BY starttime DESC"
    return run_paginated_query(sql, page, limit)



# ============================================================
# CDR — POSTPAID SMS
# Large data, paginated
# ============================================================
@router.get("/cdr_postpaid_sms")
def cdr_postpaid_sms(
    year: int = None,
    month: int = None,
    page: int = 1,
    limit: int = 100,
):
    sql = """
        SELECT
            s_p_number_address,
            o_p_number_address,
            starttime,
            receiveddate,
            rated_flat_amount,
            tariff_info_sncode,
            rated_volume
        FROM iceberg.bhutan_telecom.cdr_postpaid_sms
    """
    filters = []
    if year:
        filters.append(f"""
            YEAR(
                COALESCE(
                    TRY(CAST(starttime AS TIMESTAMP)),
                    TRY(date_parse(starttime, '%m-%d-%Y %H:%i:%s'))
                )
            ) = {year}
        """)
    if month:
        filters.append(f"""
            MONTH(
                COALESCE(
                    TRY(CAST(starttime AS TIMESTAMP)),
                    TRY(date_parse(starttime, '%m-%d-%Y %H:%i:%s'))
                )
            ) = {month}
        """)
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    sql += " ORDER BY starttime DESC"
    return run_paginated_query(sql, page, limit)


# ============================================================
# CDR — POSTPAID DATA
# Large data, paginated
# ============================================================
@router.get("/cdr_postpaid_data")
def cdr_postpaid_data(
    year: int = None,
    month: int = None, 
    page: int = 1,
    limit: int = 100,
):
    sql = """
        SELECT
            s_p_number_address,
            o_p_number_address,
            starttime,
            receiveddate,
            rated_flat_amount,
            tariff_info_sncode,
            rated_volume
        FROM iceberg.bhutan_telecom.cdr_postpaid_data
    """
    filters = []
    if year:
        filters.append(f"YEAR(starttime) = {year}")
    if month:
        filters.append(f"MONTH(starttime) = {month}")
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    sql += " ORDER BY starttime DESC"
    return run_paginated_query(sql, page, limit)


# ============================================================
# CDR — PREPAID DATA
# Large data, paginated
# ============================================================
@router.get("/cdr_prepaid_data")
def cdr_prepaid_data(
    year: int = None,
    month: int = None,
    page: int = 1,
    limit: int = 100,
):
    sql = """
        SELECT
            request_date,
            msisdn,
            apn,
            total_usage_mb
        FROM iceberg.bhutan_telecom.cdr_prepaid_data
    """
    filters = []
    if year:
        filters.append(f"YEAR(request_date) = {year}")
    if month:
        filters.append(f"MONTH(request_date) = {month}")
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    sql += " ORDER BY request_date DESC"
    return run_paginated_query(sql, page, limit)


# ============================================================
# CELL TOWER DETAILS
# Static data, no pagination needed
# Filters: region (ER, CR, WR, SWR)
# ============================================================
@router.get("/cell_tower_details")
def cell_tower_details(region: str = None):
    sql = """
        SELECT
            regions,
            site_name_,
            site_id,
            lte_1800,
            lte_700_,
            lte_850,
            tdd_2300,
            lte_900,
            network_2g,
            network_3g,
            network_5g,
            nokia,
            latitude,
            longitude
        FROM iceberg.bhutan_telecom.cell_tower_details
    """
    filters = []
    if region and region.upper() != "NONE":
        filters.append(f"UPPER(regions) = UPPER('{region}')")
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    sql += " ORDER BY regions, site_name_"
    return {"data": run_query(sql)}


# ============================================================
# CELL TOWER DATA TRAFFIC
# Small data, no pagination needed
# ============================================================
@router.get("/cell_tower_data_traffic")
def cell_tower_data_traffic(year: int = None, months: str = None):
    sql = """
        SELECT
            year,
            months,
            lte,
            data_3g,
            data_5g,
            total_data
        FROM iceberg.bhutan_telecom.cell_tower_data_traffic
    """
    filters = []
    if year:
        filters.append(f"year = {year}")
    if months and months.upper() != "NONE":
        filters.append(f"UPPER(months) = UPPER('{months}')")
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    sql += " ORDER BY year, months"
    return {"data": run_query(sql)}


# ============================================================
# CELL TOWER VOICE TRAFFIC
# Small data, no pagination needed
# ============================================================
@router.get("/cell_tower_voice_traffic")
def cell_tower_voice_traffic(year: int = None, month: str = None):
    sql = """
        SELECT
            year,
            month,
            voice_3g,
            voice_2g,
            volte,
            total_voice
        FROM iceberg.bhutan_telecom.cell_tower_voice_traffic
    """
    filters = []
    if year:
        filters.append(f"year = {year}")
    if month and month.upper() != "NONE":
        filters.append(f"UPPER(month) = UPPER('{month}')")
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    sql += " ORDER BY year, month"
    return {"data": run_query(sql)}


# ============================================================
# CELL TOWER DATA TRAFFIC SUMMARY
# Small data, no pagination needed
# Filters: year, region (eastern region, central region etc.)
# ============================================================
@router.get("/cell_tower_data_traffic_summary")
def cell_tower_data_traffic_summary(year: int = None, region: str = None):
    sql = """
        SELECT
            regions,
            year,
            january,
            february,
            march,
            april,
            may,
            june,
            july,
            august,
            september,
            october,
            november,
            december
        FROM iceberg.bhutan_telecom.cell_tower_data_traffic_summary
    """
    filters = []
    if year:
        filters.append(f"year = {year}")
    if region and region.upper() != "NONE":
        filters.append(f"UPPER(regions) = UPPER('{region}')")
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    sql += " ORDER BY year, regions"
    return {"data": run_query(sql)}


# ============================================================
# CELL TOWER KPI
# Small data, no pagination needed
# Filters: year, technology
# ============================================================
@router.get("/cell_tower_kpi")
def cell_tower_kpi(year: int = None, technology: str = None):
    sql = """
        SELECT
            parameters,
            technology,
            benchmark,
            year,
            january,
            february,
            march,
            april,
            may,
            june,
            july,
            august,
            september,
            october,
            november,
            december
        FROM iceberg.bhutan_telecom.cell_tower_kpi
    """
    filters = []
    if year:
        filters.append(f"year = {year}")
    if technology and technology.upper() != "NONE":
        filters.append(f"UPPER(technology) = UPPER('{technology}')")
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    sql += " ORDER BY year, technology, parameters"
    return {"data": run_query(sql)}


# ============================================================
# CELL TOWER KPI REPORT
# Small data, no pagination needed
# Filters: location (tyangtse, thimphu etc)
# ============================================================
@router.get("/cell_tower_kpi_report")
def cell_tower_kpi_report(location: str = None):
    sql = """
        SELECT
            location_of_core_areas,
            ps_drop_rate,
            ps_success_rate,
            dl_user_throughput_mbps
        FROM iceberg.bhutan_telecom.cell_tower_kpi_report
    """
    filters = []
    if location and location.upper() != "NONE":
        filters.append(f"UPPER(location_of_core_areas) = UPPER('{location}')")
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    sql += " ORDER BY location_of_core_areas"
    return {"data": run_query(sql)}


# ============================================================
# CUSTOMER COMPLAINTS
# Medium data, paginated
# Filters: year, dzongkhag, complaint_type, status
# ============================================================
@router.get("/customer_complaints")
def customer_complaints(
    year: int = None,
    dzongkhag: str = None,
    complaint_type: str = None,
    status: str = None,
    page: int = 1,
    limit: int = 100,
):
    sql = """
        SELECT
            ticket_id,
            caller_id,
            dzongkhag,
            complaint_type,
            service,
            status,
            assigned_to,
            shift,
            mode_type,
            year
        FROM iceberg.bhutan_telecom.customer_complaints
    """
    filters = []
    if year:
        filters.append(f"year = {year}")
    if dzongkhag and dzongkhag.upper() != "NONE":
        filters.append(f"UPPER(dzongkhag) = UPPER('{dzongkhag}')")
    if complaint_type and complaint_type.upper() != "NONE":
        filters.append(f"UPPER(complaint_type) = UPPER('{complaint_type}')")
    if status and status.upper() != "NONE":
        filters.append(f"UPPER(status) = UPPER('{status}')")
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    sql += " ORDER BY year, dzongkhag"
    return run_paginated_query(sql, page, limit)


# ============================================================
# MONTHLY REVENUE — DATA
# Small data, no pagination needed
# ============================================================
@router.get("/monthly_revenue_data")
def monthly_revenue_data(year: int=None, month: int=None):
    sql = """
        SELECT
            month,
            revenue,
            internet_data_gb
        FROM iceberg.bhutan_telecom.monthly_revenue_data
    """
    filters = []
    if year: 
        filters.append(f"YEAR(month) = {year}")
    if month: 
        filters.append(f"MONTH(month) = {month}")
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    sql += " ORDER BY month"
    return {"data": run_query(sql)}


# ============================================================
# MONTHLY REVENUE — SMS
# Small data, no pagination needed
# ============================================================
@router.get("/monthly_revenue_sms")
def monthly_revenue_sms(year: int=None, month: int=None):
    sql = """
        SELECT
            month,
            revenue,
            usage
        FROM iceberg.bhutan_telecom.monthly_revenue_sms
    """
    filters = []
    if year: 
        filters.append(f"YEAR(month) = {year}")
    if month: 
        filters.append(f"MONTH(month) = {month}")
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    sql += " ORDER BY month"
    return {"data": run_query(sql)}


# ============================================================
# MONTHLY REVENUE — VOICE
# Small data, no pagination needed
# ============================================================
@router.get("/monthly_revenue_voice")
def monthly_revenue_voice(year: int=None, month: int=None):
    sql = """
        SELECT
            month,
            revenue,
            usage_duration_minutes
        FROM iceberg.bhutan_telecom.monthly_revenue_voice
    """
    filters = []
    if year: 
        filters.append(f"YEAR(month) = {year}")
    if month: 
        filters.append(f"MONTH(month) = {month}")
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    sql += " ORDER BY month"
    return {"data": run_query(sql)}


# ============================================================
# TARIFFS — static reference data, no pagination needed
# ============================================================
@router.get("/postpaid_tariff_booster")
def postpaid_tariff_booster():
    sql = """
        SELECT plans, price, data_quota_mb, validity
        FROM iceberg.bhutan_telecom.postpaid_tariff_booster
        ORDER BY price
    """
    return {"data": run_query(sql)}


@router.get("/postpaid_tariff_monthly")
def postpaid_tariff_monthly():
    sql = """
        SELECT plans, price, data_quota_mb, validity
        FROM iceberg.bhutan_telecom.postpaid_tariff_monthly
        ORDER BY price
    """
    return {"data": run_query(sql)}


@router.get("/postpaid_tariff_sms")
def postpaid_tariff_sms():
    sql = """
        SELECT
            call_type,
            standard_4am_12_midnight,
            midnight_12_midnight_4am
        FROM iceberg.bhutan_telecom.postpaid_tariff_sms
    """
    return {"data": run_query(sql)}


@router.get("/postpaid_tariff_voice")
def postpaid_tariff_voice():
    sql = """
        SELECT
            call_type_1_unit_15_sec,
            off_peak_hour_6am_3pm,
            peak_hour_3pm_10pm,
            economy_hour_4am_6am,
            late_night_12am_4am
        FROM iceberg.bhutan_telecom.postpaid_tariff_voice
    """
    return {"data": run_query(sql)}


@router.get("/prepaid_tariff_air_fibre")
def prepaid_tariff_air_fibre():
    sql = """
        SELECT
            package_name,
            rate_nu,
            bw_mbps,
            data_volume_gb,
            cost_gb,
            fair_usage,
            validity
        FROM iceberg.bhutan_telecom.prepaid_tariff_air_fibre
        ORDER BY rate_nu
    """
    return {"data": run_query(sql)}


@router.get("/prepaid_tariff_data_plan")
def prepaid_tariff_data_plan():
    sql = """
        SELECT data_pack, rate, quota_mb, validity_days
        FROM iceberg.bhutan_telecom.prepaid_tariff_data_plan
        ORDER BY rate
    """
    return {"data": run_query(sql)}


@router.get("/prepaid_tariff_voice_sms")
def prepaid_tariff_voice_sms():
    sql = """
        SELECT call_type, timing, tariff_nu
        FROM iceberg.bhutan_telecom.prepaid_tariff_voice_sms
    """
    return {"data": run_query(sql)}


# ============================================================
# HELPER ENDPOINTS — for frontend dropdowns
# ============================================================
@router.get("/helper/customer_complaints/dzongkhags")
def complaint_dzongkhags():
    sql = """
        SELECT DISTINCT dzongkhag
        FROM iceberg.bhutan_telecom.customer_complaints
        ORDER BY dzongkhag
    """
    return {"data": run_query(sql)}


@router.get("/helper/customer_complaints/types")
def complaint_types():
    sql = """
        SELECT DISTINCT complaint_type
        FROM iceberg.bhutan_telecom.customer_complaints
        ORDER BY complaint_type
    """
    return {"data": run_query(sql)}


@router.get("/helper/cell_tower_details/regions")
def cell_tower_regions():
    sql = """
        SELECT DISTINCT regions
        FROM iceberg.bhutan_telecom.cell_tower_details
        ORDER BY regions
    """
    return {"data": run_query(sql)}


# ============================================================
# Debug Endpoints
# ============================================================

@router.get("/debug")
def bt_sample(table: str):
    return {"data": run_query(f"SELECT * FROM iceberg.bhutan_telecom.{table}")}