# DHI Data Lake

An AI-powered data lake for DHI group companies. Parquet files are stored in MinIO, catalogued with Apache Iceberg via Nessie, queryable through Trino, and exposed through a REST API and Claude-powered chat agents.

---

## Architecture

```
Parquet Files
     │
     ▼
  MinIO (S3-like storage)           ← stores all raw Parquet files
     │
     ├── Nessie (Iceberg catalog)   ← tracks table schemas & versions (backed by PostgreSQL)
     │
     └── Trino (SQL engine)         ← queries Parquet files in MinIO using SQL
                │
         ┌──────┴──────┐
         ▼             ▼
      API (8000)   Agents (8001)
    REST endpoints  Claude AI chat
                        │
                    MCP Server     ← tools that agents call to fetch data
```

---

## Project Structure

```
scripts/
├── configs.py              # Table definitions (paths, schema, location in MinIO)
├── convert.py              # Cleans and re-uploads Parquet files in MinIO
├── load_to_iceberg.py      # Registers Parquet files as Iceberg tables via Trino
│
├── infrastructure/
│   ├── docker-compose.yml  # MinIO + PostgreSQL + Nessie + Trino containers
│   ├── setup.sh            # One-time infrastructure setup
│   └── trino/etc/          # Trino config files (catalog, config.properties)
│
├── api/
│   ├── main.py             # FastAPI app entry point (port 8000)
│   ├── db.py               # Trino connection
│   └── routers/
│       ├── drukair.py      # Drukair API endpoints
│       └── bhutan_telecom.py  # Bhutan Telecom API endpoints
│
├── mcp_server/
│   ├── server.py           # MCP server definition
│   ├── main.py             # Entry point (launched as subprocess by agents)
│   └── tools/
│       ├── drukair.py      # MCP tools for Drukair data
│       └── bhutan_telecom.py  # MCP tools for Bhutan Telecom data
│
└── agents/
    ├── main.py             # FastAPI app entry point (port 8001)
    └── graph.py            # LangGraph agent definitions + system prompts
```

---

## Infrastructure (Docker)

Four containers defined in `infrastructure/docker-compose.yml`:

| Container | Port | What it does |
|---|---|---|
| MinIO | 9000 (API), 9001 (UI) | S3-compatible storage for Parquet files |
| PostgreSQL | 5432 | Stores Nessie metadata (table definitions, schema history) |
| Nessie | 19120 | Iceberg catalog — like Git for data (tracks schema changes, versions) |
| Trino | 8080 | SQL query engine — queries Parquet files in MinIO as if they were tables |

```bash
# Start infrastructure
cd infrastructure
docker compose up -d

# Stop infrastructure
docker compose down
```

---

## Data Pipeline

### 1. Configure tables — `configs.py`

Defines every table: its local Parquet path, Iceberg schema/table name, and S3 location in MinIO.

### 2. Clean Parquet files — `convert.py`

Downloads each Parquet file from MinIO, fixes data types (datetime columns, numeric columns), and re-uploads the cleaned version in-place.

```bash
python convert.py
```

What it does per file:
- Parses datetime columns (`STARTTIME`, `RECEIVEDDATE`) to `datetime64[us]`
- Casts numeric columns to correct types (`float`, `Int64`)
- Re-uploads with Snappy compression

### 3. Load to Iceberg — `load_to_iceberg.py`

Registers the Parquet files in MinIO as Iceberg tables via Trino + Nessie.

```bash
python load_to_iceberg.py
```

---

## Services

### API — port 8000

REST API that serves data by running SQL queries against Trino.

```bash
curl http://localhost:8000/
# {"message":"Data Lake API is running"}
```

### Agents — port 8001

AI chat agents powered by Claude (`claude-sonnet-4-6`) via LangGraph + MCP. Each company has a dedicated agent with its own system prompt and filtered tool set. A master agent has access to all companies.

```bash
curl http://localhost:8001/
# {"message":"DHI Chat Agent is running"}
```

The MCP server is not a separate service — it launches automatically as a subprocess of the agents service.

---

## Companies

| Company | API prefix | MCP tool prefix | Agent |
|---|---|---|---|
| Drukair (Royal Bhutan Airlines) | `/drukair/` | `get_drukair_` | `DRUKAIR_PROMPT` |
| Bhutan Telecom | `/bhutan-telecom/` | `get_bt_` | `BHUTAN_TELECOM_PROMPT` |

---

## Deployment

See [OPERATIONS.md](OPERATIONS.md) for full server operations. Quick reference:

```bash
make deploy          # pull + sync packages + restart all services
make restart-api     # restart API only
make restart-agents  # restart agents + MCP only
make status          # check all services
make logs-agents     # follow agent logs
```

---

## Adding a New Company

1. Add table configs to `configs.py`
2. Clean and load data: `convert.py` → `load_to_iceberg.py`
3. Add API router: `api/routers/company_name.py`
4. Add MCP tools: `mcp_server/tools/company_name.py`
5. Add prefix mapping and agent prompt in `agents/graph.py`
6. Add chat endpoint in `agents/main.py`
7. Deploy: `make deploy`

The master agent automatically picks up new MCP tools — no other changes needed.

---

## Environment Files

| File | Used by |
|---|---|
| `infrastructure/.env` | Docker compose (MinIO/Postgres credentials) |
| `api/.env` | API service (Trino connection, credentials) |
| `agents/.env` | Agents service (Anthropic API key) |
| `mcp_server/.env` | MCP server (Trino connection) |

Copy the `.env.example` files in each directory to get started.
