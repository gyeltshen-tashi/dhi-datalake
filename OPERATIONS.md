# DHI Data Lake — Operations Guide

## Overview

This guide covers day-to-day server operations for the DHI Data Lake project.

### Services

| Service | Port | systemd Unit | Description |
|---|---|---|---|
| Data API | 8000 | `dhi-api.service` | REST API serving financial and operational data |
| Chat Agents | 8001 | `dhi-agents.service` | AI chat agents powered by Claude + MCP |
| MCP Server | — | No separate unit | Subprocess of `dhi-agents`, launched automatically |

> **Note:** There is no `dhi-mcp.service`. MCP starts and stops automatically with `dhi-agents`.

---

## Important Paths

| What | Path |
|---|---|
| Project root | `/home/lake/dhi-datalake` |
| API code | `/home/lake/dhi-datalake/api` |
| Agents code | `/home/lake/dhi-datalake/agents` |
| MCP server code | `/home/lake/dhi-datalake/mcp_server` |
| Shared virtual env | `/home/lake/dhi-datalake/.venv` |
| API env file | `/home/lake/dhi-datalake/api/.env` |
| Agents env file | `/home/lake/dhi-datalake/agents/.env` |
| MCP env file | `/home/lake/dhi-datalake/mcp_server/.env` |
| API service file | `/etc/systemd/system/dhi-api.service` |
| Agents service file | `/etc/systemd/system/dhi-agents.service` |

---

## 1. Checking Service Health

### Status of both services

```bash
sudo systemctl status dhi-api --no-pager
sudo systemctl status dhi-agents --no-pager
```

Healthy output includes `Active: active (running)`.

### Quick health check via HTTP endpoints

```bash
curl http://localhost:8000/
curl http://localhost:8001/
```

Expected responses:

```json
{"message":"Data Lake API is running"}
{"message":"DHI Chat Agent is running"}
```

### Check if services are enabled for auto-start on boot

```bash
systemctl is-enabled dhi-api
systemctl is-enabled dhi-agents
```

Expected: `enabled` for both.

### Check if services are currently active

```bash
systemctl is-active dhi-api
systemctl is-active dhi-agents
```

Expected: `active` for both.

---

## 2. Starting, Stopping, and Restarting

### Start a service

```bash
sudo systemctl start dhi-api
sudo systemctl start dhi-agents
```

Starts the service immediately. Does **not** enable it on boot.

### Stop a service

```bash
sudo systemctl stop dhi-api
sudo systemctl stop dhi-agents
```

> Stopping `dhi-agents` also stops the MCP subprocess.

### Restart a service

```bash
sudo systemctl restart dhi-api
sudo systemctl restart dhi-agents
```

Stops and immediately starts the service. Use this after any code or config change.

### Restart both at once

```bash
sudo systemctl restart dhi-api dhi-agents
```

### Enable a service to start on boot

```bash
sudo systemctl enable dhi-api
sudo systemctl enable dhi-agents
```

Does **not** start it now — only configures auto-start after reboot.

### Enable and start immediately (initial setup only)

```bash
sudo systemctl enable --now dhi-api
sudo systemctl enable --now dhi-agents
```

### Disable a service from starting on boot

```bash
sudo systemctl disable dhi-api
sudo systemctl disable dhi-agents
```

---

## 3. Viewing Logs

All service logs are managed by `journalctl`.

### Follow logs in real time

```bash
sudo journalctl -u dhi-api -f
sudo journalctl -u dhi-agents -f
```

Press `Ctrl+C` to stop following.

### Show last 100 lines

```bash
sudo journalctl -u dhi-api -n 100 --no-pager
sudo journalctl -u dhi-agents -n 100 --no-pager
```

### Show logs since current boot

```bash
sudo journalctl -u dhi-api -b --no-pager
sudo journalctl -u dhi-agents -b --no-pager
```

---

## 4. Code Deployment

### Standard deployment (both services changed)

```bash
cd ~/dhi-datalake
git pull origin main
uv sync --all-packages
sudo systemctl restart dhi-api dhi-agents
sudo systemctl status dhi-api --no-pager
sudo systemctl status dhi-agents --no-pager
```

### Only API code changed

```bash
cd ~/dhi-datalake
git pull origin main
uv sync --all-packages
sudo systemctl restart dhi-api
sudo systemctl status dhi-api --no-pager
```

### Only agents or MCP code changed

```bash
cd ~/dhi-datalake
git pull origin main
uv sync --all-packages
sudo systemctl restart dhi-agents
sudo systemctl status dhi-agents --no-pager
```

> Restarting `dhi-agents` is sufficient for MCP changes — MCP runs as a subprocess of agents.

### After editing a systemd service file

```bash
sudo nano /etc/systemd/system/dhi-api.service
# or
sudo nano /etc/systemd/system/dhi-agents.service
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl restart dhi-api dhi-agents
sudo systemctl status dhi-api --no-pager
sudo systemctl status dhi-agents --no-pager
```

> **Important distinction:**
> - Python code change → `restart` service only
> - `.service` file change → `daemon-reload` first, then `restart`
> - `.env` file change → `restart` service only (no `daemon-reload` needed)

---

## 5. Environment File Management

### Edit env files

```bash
nano ~/dhi-datalake/api/.env
nano ~/dhi-datalake/agents/.env
nano ~/dhi-datalake/mcp_server/.env
```

After editing, restart the affected service:

```bash
sudo systemctl restart dhi-api        # if api/.env changed
sudo systemctl restart dhi-agents     # if agents/.env or mcp_server/.env changed
```

### Verify env file permissions

```bash
ls -l ~/dhi-datalake/api/.env
ls -l ~/dhi-datalake/agents/.env
ls -l ~/dhi-datalake/mcp_server/.env
```

Expected: `-rw-------` (only owner can read/write).

### Fix permissions if needed

```bash
chmod 600 ~/dhi-datalake/api/.env
chmod 600 ~/dhi-datalake/agents/.env
chmod 600 ~/dhi-datalake/mcp_server/.env
```

### View env keys without exposing secrets

```bash
sed 's/=.*$/=***/' ~/dhi-datalake/api/.env
sed 's/=.*$/=***/' ~/dhi-datalake/agents/.env
sed 's/=.*$/=***/' ~/dhi-datalake/mcp_server/.env
```

---

## 6. Port and Process Troubleshooting

### Check what is using a port

```bash
sudo lsof -i :8000
sudo lsof -i :8001
```

Use this when a service fails to start with "address already in use."

### List all Python/uvicorn processes

```bash
ps aux | grep -E "uvicorn|python" | grep -v grep
```

Use this to find stray manual processes that may conflict with systemd services.

### Kill a specific process

```bash
kill <PID>
```

### Force kill a stuck process

```bash
kill -9 <PID>
```

> Use only if normal `kill` does not work.

### View systemd service file contents

```bash
cat /etc/systemd/system/dhi-api.service
cat /etc/systemd/system/dhi-agents.service
```

### List all DHI service files

```bash
ls /etc/systemd/system | grep dhi
```

---

## 7. Reboot and Recovery

### Test auto-start after reboot

```bash
sudo reboot
```

After reconnecting via SSH:

```bash
sudo systemctl status dhi-api --no-pager
sudo systemctl status dhi-agents --no-pager
curl http://localhost:8000/
curl http://localhost:8001/
```

Both services should be `active (running)` without manual intervention.

---

## 8. Adding a New Company

When a new company joins the data lake:

1. Add API endpoints: `api/routers/company_name.py`
2. Add MCP tools: `mcp_server/tools/company_name.py`
3. Add prefix mapping in `agents/graph.py`
4. Add chat endpoint in `agents/main.py`
5. Push to GitHub, then deploy:

```bash
cd ~/dhi-datalake
git pull origin main
uv sync --all-packages
sudo systemctl restart dhi-api dhi-agents
```

> The master agent automatically discovers new tools — no other changes needed.

---

## 9. Key Rules to Remember

| Scenario | What to run |
|---|---|
| Python code changed | `systemctl restart <service>` |
| `.env` file changed | `systemctl restart <service>` |
| `.service` file changed | `daemon-reload` → then `restart` |
| New package added (`pyproject.toml`) | `uv sync --all-packages` → then `restart` |
| MCP code changed | `systemctl restart dhi-agents` (MCP is a subprocess) |
| Port conflict on startup | `lsof -i :<port>` → `kill <PID>` |

---

## 10. Quick Reference

```bash
# Check services
sudo systemctl status dhi-api --no-pager
sudo systemctl status dhi-agents --no-pager

# Start / stop / restart
sudo systemctl start dhi-api
sudo systemctl stop dhi-api
sudo systemctl restart dhi-api dhi-agents

# Enable on boot
sudo systemctl enable dhi-api
sudo systemctl enable dhi-agents

# View logs
sudo journalctl -u dhi-api -f
sudo journalctl -u dhi-agents -f

# Deploy update
cd ~/dhi-datalake
git pull origin main
uv sync --all-packages
sudo systemctl restart dhi-api dhi-agents

# After editing service files only
sudo systemctl daemon-reload
sudo systemctl restart dhi-api dhi-agents

# Health checks
curl http://localhost:8000/
curl http://localhost:8001/

# Troubleshooting
sudo lsof -i :8000
sudo lsof -i :8001
ps aux | grep -E "uvicorn|python" | grep -v grep
```

## 11. Makefile Commands (Preferred)

The Makefile wraps common operations into short commands. Use these instead of running
systemctl and git commands manually.

| Command | What it does |
|---|---|
| `make deploy` | Pull latest code + sync packages + restart all services |
| `make update` | Pull latest code + sync packages only (no restart) |
| `make restart` | Restart all services (infra + API + agents) |
| `make restart-infra` | Restart Docker infrastructure only |
| `make restart-api` | Restart API service only |
| `make restart-agents` | Restart agents service only |
| `make logs-infra` | Follow Docker infrastructure logs |
| `make logs-api` | Follow API logs |
| `make logs-agents` | Follow agents logs |
| `make status` | Show status of all services and Docker containers |

### Most common workflows

**Deploy an update:**
```bash
make deploy
```

**Only agents or MCP code changed:**
```bash
make restart-agents
```

**Only API code changed:**
```bash
make restart-api
```

**Check everything is healthy:**
```bash
make status
```

**Watch agent logs in real time:**
```bash
make logs-agents
```
