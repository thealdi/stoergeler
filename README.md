# StoerGeler

Python backend and Vue frontend to monitor and visualize Fritzbox internet connectivity via TR-064.

**Version:** v1.0.0

## Architecture Overview

- **Backend**: FastAPI app (`backend/main.py`) polls TR-064 (`fritzconnection`) in background tasks, stores status changes and device logs, and calculates outage windows.
- **Persistence**: SQLite DB at `data/stoergeler.db` (configurable via `DATABASE_PATH`).
- **Frontend**: Vue 3 + Vite + TypeScript (`frontend-vue/`) with Naive UI + FullCalendar. Clicking an outage opens a drawer with filtered device logs.
- **Legacy**: The old static frontend has been removed.

## Requirements

- Python ≥ 3.11
- Fritzbox TR-064 credentials (user/password)

## Backend Setup & Run

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

Start backend (serves under `/api`, e.g. `http://localhost:8000/api/health`):

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

OpenAPI docs: `http://localhost:8000/docs`

### Docker / Docker Compose

Quick start (backend on 8001, frontend on 8080):

```bash
docker compose up --build
```

Notes:

- Backend image is built from `Dockerfile` and persists SQLite under `/volume1/docker/stoergeler/data` (adjust as needed).
- Environment variables can be provided via `.env` or Portainer/Compose UI (see `docker-compose.yml`).
- Frontend container uses `nginx:alpine` and serves static files from `/volume1/docker/stoergeler/frontend`.
- After start: `http://<host>:8080` (frontend) and `http://<host>:8001/api/health` (API).

> The Compose setup uses `/volume1/docker/stoergeler/data` for persistence. On Synology NAS you can inspect/backup this path directly. Example env file: `./.env.example`. Optional: `DOCKER_PLATFORM` (default `linux/amd64`, for ARM NAS use `linux/arm64`).

## Frontend Local Dev (Vue)

```bash
cd frontend-vue
npm install
npm run dev
```

Open `http://localhost:5173`. The frontend calls `http://localhost:8000/api`.

### Frontend Build for Nginx

```bash
cd frontend-vue
npm install
npm run build
```

Build output is in `frontend-vue/dist/` and can be copied to the Nginx volume (e.g. `/volume1/docker/stoergeler/frontend`).

## API Overview

- `GET /api/health` – health check
- `GET /api/status` – triggers a TR-064 poll and returns current status
- `GET /api/device-log?limit=<int>` – returns device log entries
- `GET /api/outages` – returns calculated outage windows
- `GET /api/connection-check` – live TR-064 connection check

## Data Model

The backend stores:
- status changes (`online`, `offline`, `error`)
- raw device log lines
- derived outage intervals (`open`, `closed`, `planned`)

All persisted in SQLite (`data/stoergeler.db`).

## Frontend Features

- **Calendar**: outages as red (unplanned) or blue (planned) events
- **Drawer**: clicking an outage opens filtered device logs
- **Outage table**: start/end/duration/status with pagination
- **Device log table**: paginated Fritzbox logs
- **Manual TR-064 check**: calls `/api/connection-check`

## Testing (Optional)

- Unit tests for repositories & outage logic (`pytest`, `pytest-asyncio`)
- API tests with `TestClient`
- Optional UI tests (Vitest/Playwright)
