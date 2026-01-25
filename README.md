# StoerGeler

Python backend and Vue frontend to monitor and visualize Fritzbox internet connectivity via TR-064.

## Overview

- **Backend**: FastAPI app (`backend/main.py`) polls TR-064 (`fritzconnection`), stores status changes and device logs, and calculates outage windows.
- **Frontend**: Vue 3 + Vite + TypeScript (`frontend/`) with Naive UI + FullCalendar.
- **Storage**: SQLite at `data/stoergeler.db` (configurable via `DATABASE_PATH`).

## Requirements

- Python ≥ 3.11
- Fritzbox TR-064 credentials

## Local Dev

### Backend

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Environment variables (examples):

```bash
export FRITZBOX_ADDRESS="fritz.box"
export FRITZBOX_USERNAME="homeauto"
export FRITZBOX_PASSWORD="secret-password"
export POLL_INTERVAL_SECONDS=60
export DEVICE_LOG_POLL_INTERVAL_SECONDS=60
```

Start backend (serves under `/api`, e.g. `http://localhost:8001/api/health`):

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

OpenAPI docs: `http://localhost:8001/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` to `http://localhost:8001` (see `frontend/vite.config.ts`).

## Docker / Docker Compose

Quick start (backend on 8001, frontend on 8080):

```bash
docker compose up
```

Notes:

- Backend image is `thealdi/stoergeler-backend` and persists SQLite under `/volume1/docker/stoergeler/data` (adjust as needed).
- Environment variables can be provided via `.env` or Portainer/Compose UI (see `docker-compose.yml`).
- Frontend image is `thealdi/stoergeler-frontend`.
- After start: `http://<host>:8080` (frontend) and `http://<host>:8001/api/health` (API).

> The Compose setup uses `/volume1/docker/stoergeler/data` for persistence. Example env file: `./.env.example`. Optional: `DOCKER_PLATFORM` (default `linux/amd64`, for ARM NAS use `linux/arm64`).

## API Overview

- `GET /api/health` – health check
- `GET /api/status` – triggers a TR-064 poll and returns current status
- `GET /api/device-log?limit=<int>` – returns device log entries
- `GET /api/outages` – returns calculated outage windows
- `GET /api/connection-check` – live TR-064 connection check

## Data Model

- status changes (`online`, `offline`, `error`)
- raw device log lines
- derived outage intervals (`open`, `closed`, `planned`)
