# Configuration

This document summarizes environment variables and runtime configuration.

## Backend (.env / environment variables)

Core settings:
- `FRITZBOX_ADDRESS` – Fritzbox host (default: `fritz.box`)
- `FRITZBOX_USERNAME` – TR-064 username
- `FRITZBOX_PASSWORD` – TR-064 password
- `POLL_INTERVAL_SECONDS` – status polling interval (default: `60`)
- `DEVICE_LOG_POLL_INTERVAL_SECONDS` – log polling interval (default: `60`)
- `DATABASE_PATH` – optional SQLite path (default: `data/stoergeler.db`)

Outage keyword configuration (comma-separated lists):
- `OUTAGE_PLANNED_KEYWORDS`
- `OUTAGE_IPV4_DISCONNECT_KEYWORDS`
- `OUTAGE_IPV4_CONNECT_KEYWORDS`
- `OUTAGE_IPV6_DISCONNECT_KEYWORDS`
- `OUTAGE_IPV6_CONNECT_KEYWORDS`

If these are not set, defaults from `backend/outage_config.py` are used.

## Docker / Compose

In `docker-compose.yml`:
- Backend is exposed on `8001:8000`
- Frontend is served via `nginx:alpine` on `8080:80`
- SQLite data volume: `/volume1/docker/stoergeler/data:/app/data`
- Frontend static files volume: `/volume1/docker/stoergeler/frontend:/usr/share/nginx/html:ro`

## Frontend

The frontend uses the backend base URL resolved by `frontend/src/config.ts`:
- If `window.STOERGELER_BACKEND_URL` is set, it is used.
- Otherwise it uses the current host with `/api` appended.

To override, set in your static hosting environment:

```html
<script>
  window.STOERGELER_BACKEND_URL = "http://your-host:8001";
  window.STOERGELER_BACKEND_PATH = "/api";
</script>
```

## Notes

- `.env` is ignored by git (store secrets locally).
- `.env.example` is the canonical template for deployment.
