# StoerGeler - Project Context

StoerGeler is a full-stack application designed to monitor and visualize Fritzbox internet connectivity using the TR-064 protocol. It tracks online/offline status, parses device logs to identify outages, and provides a web interface for visualization.

## Project Overview

- **Backend**: FastAPI (Python 3.11+) handles polling the Fritzbox, processing logs, and exposing a REST API.
- **Frontend**: Vue 3 (Vite + TypeScript) with Naive UI and FullCalendar for data visualization.
- **Storage**: SQLite database (`data/stoergeler.db`) stores status changes and outage data.
- **Infrastructure**: Dockerized setup with `docker-compose.yml` for easy deployment.

## Architecture & Tech Stack

### Backend (`/backend`)
- **Framework**: FastAPI
- **Library**: `fritzconnection` for TR-064 communication.
- **Database**: SQLite with a repository pattern for data access.
- **Concurrency**: Background tasks for periodic polling.
- **Configuration**: Environment variables (managed in `backend/config.py`).

### Frontend (`/frontend`)
- **Framework**: Vue 3 (Composition API)
- **Styling**: Naive UI components.
- **Visualization**: FullCalendar for outage history.
- **Build Tool**: Vite with TypeScript.

## Building and Running

### Prerequisites
- Python 3.11+
- Node.js & npm
- Fritzbox credentials (TR-064)

### Local Development
The root `package.json` contains helper scripts to run both parts of the application:

- **Full Stack**: `npm run dev` (Starts both backend and frontend).
- **Backend Only**: `npm run dev:backend` (Requires active `.venv` with `pip install -r requirements.txt`).
- **Frontend Only**: `npm run dev:frontend`.

### Docker
- **Run all**: `docker compose up`
- **Frontend Port**: 8080 (default)
- **Backend Port**: 8001 (default)

## Development Conventions

- **Role**: Act as a senior full-stack engineer focusing on security, reliability, and maintainability.
- **Coding Style**:
    - **Python**: Prefer clear types, repository patterns, and Pydantic-like schemas.
    - **Frontend**: Use Vue 3 Composition API, TypeScript, and Naive UI components.
- **Commit Messages**: Follow [Conventional Commits](https://www.conventionalcommits.org/) with specific scopes:
    - `feat(frontend): description`
    - `fix(backend): description`
- **Versioning**: Managed by `semantic-release` based on commit message scopes.
- **Testing**: No automated test suite was found during initial analysis; manual verification via `npm run dev` is expected.

## Key Files & Directories

- `backend/main.py`: Entry point for the FastAPI application.
- `backend/config.py`: Configuration management and environment variables.
- `frontend/src/App.vue`: Root Vue component.
- `docker-compose.yml`: Production/Staging deployment configuration.
- `AGENTS.md`: Detailed operational rules for AI agents (precedes general rules).
- `CLAUDE.md`: (Optional) Existing context for other AI assistants.
