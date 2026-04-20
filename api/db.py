# db.py
import os
from pathlib import Path
from dotenv import load_dotenv
from trino.dbapi import connect
from fastapi import HTTPException

BASE_DIR = Path(__file__).resolve().parent

# Try .env inside api/ first (server), then parent folder (local Mac)
env_path = BASE_DIR / ".env"
if not env_path.exists():
    env_path = BASE_DIR.parent / ".env"

load_dotenv(dotenv_path=env_path, override=True)

TRINO_HOST = os.getenv("TRINO_HOST", "100.85.189.71")
TRINO_PORT = int(os.getenv("TRINO_PORT", "8080"))

def run_query(sql: str):
    conn = None
    try:
        conn = connect(
            host=TRINO_HOST,
            port=TRINO_PORT,
            user="admin",
            catalog="iceberg",
        )
        cursor = conn.cursor()
        cursor.execute(sql)
        description = cursor.description
        if description is None:
            return []
        columns = [desc[0] for desc in description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()
    

def run_paginated_query(sql: str, page: int = 1, limit: int = 100):
    conn = None
    try:
        conn = connect(
            host=TRINO_HOST,
            port=TRINO_PORT,
            user="admin",
            catalog="iceberg",
        )
        cursor = conn.cursor()

        # Get total count first
        count_sql = f"SELECT COUNT(*) FROM ({sql}) AS count_query"
        cursor.execute(count_sql)
        total = cursor.fetchone()[0]

        # Get the actual page of data
        offset = (page - 1) * limit
        paged_sql = f"SELECT * FROM ({sql}) AS paged_query OFFSET {offset} LIMIT {limit}"
        cursor.execute(paged_sql)
        description = cursor.description
        if description is None:
            data = []
            columns = []
        else:
            columns = [desc[0] for desc in description]
            rows = cursor.fetchall()
            data = [dict(zip(columns, row)) for row in rows]

        total_pages = (total + limit - 1) // limit

        return {
            "data": data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_rows": total,
                "total_pages": total_pages,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()