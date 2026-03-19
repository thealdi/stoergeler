from __future__ import annotations

import logging

from .config import settings

# --- Logging setup (before any other module creates loggers) ---
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
)
# Quiet noisy third-party loggers
for _name in ("httpcore", "httpx", "fritzconnection", "urllib3"):
    logging.getLogger(_name).setLevel(logging.WARNING)

from .app_factory import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
