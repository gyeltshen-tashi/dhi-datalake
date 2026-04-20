# main.py

from fastapi import FastAPI
from routers import (
    drukair,
    bhutan_telecom,
)

app = FastAPI(title="DHI Data Lake API")

app.include_router(drukair.router)
app.include_router(bhutan_telecom.router)

@app.get("/")
def home():
    return {"message" : "Data Lake API is running"}


@app.get("/debug/config")
def debug_config():
    from db import TRINO_HOST, TRINO_PORT
    import os
    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parent
    env_path_1 = BASE_DIR / ".env"
    env_path_2 = BASE_DIR.parent / ".env"
    return {
        "TRINO_HOST": TRINO_HOST,
        "TRINO_PORT": TRINO_PORT,
        "env_in_api_folder": str(env_path_1) + " exists: " + str(env_path_1.exists()),
        "env_in_parent_folder": str(env_path_2) + " exists: " + str(env_path_2.exists()),
        "shell_TRINO_HOST": os.getenv("TRINO_HOST", "NOT SET"),
    }