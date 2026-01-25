# Backend

FastAPI service that talks to the Fritzbox via TR-064, stores logs/outages in SQLite, and exposes a REST API.

## Local dev

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

Health check: `http://localhost:8001/api/health`

For environment variables, see the root `README.md` and `.env.example`.
