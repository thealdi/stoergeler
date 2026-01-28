# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

StoerGeler monitors and visualizes Fritzbox internet connectivity using TR-064 protocol. It consists of a Python FastAPI backend and Vue 3 TypeScript frontend.

**Key Features:**
- Polls Fritzbox TR-064 API for connection status and device logs
- Stores status changes, device logs, and calculated outage windows in SQLite
- Classifies outages as planned/unplanned based on keyword matching
- Tracks separate IPv4 and IPv6 connection state
- Provides calendar visualization using FullCalendar

## Development Commands

### Backend (FastAPI + Python)

```bash
# Setup
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run backend (serves API under /api prefix)
uvicorn backend.main:app --host 0.0.0.0 --port 8001

# Or use the npm script from project root
npm run dev:backend
```

Backend runs on port 8001. API docs at `http://localhost:8001/docs`.

### Frontend (Vue 3 + Vite + TypeScript)

```bash
# From project root
npm run dev:frontend

# Or from frontend directory
cd frontend
npm install
npm run dev

# Build for production
npm run build
```

Frontend runs on port 5173 with Vite proxy (`/api` → `http://localhost:8001`).

### Run Both Together

```bash
npm run dev  # Starts backend and frontend concurrently
```

### Docker

```bash
docker compose up  # Backend on 8001, frontend on 8080
```

## Architecture

### Backend Structure

The backend is organized in a service-oriented architecture:

- **`backend/main.py`**: FastAPI app entry point with `/api` root path. Initializes all components and defines REST endpoints.
- **`backend/config.py`**: Loads environment variables using `python-dotenv`. Supports CSV parsing for outage keywords.
- **`backend/database.py`**: SQLite persistence layer with three repositories:
  - `StatusRepository`: Records online/offline/error status changes
  - `DeviceLogRepository`: Stores raw Fritzbox device log entries (unique by timestamp+message)
  - `OutageRepository`: Stores calculated outage intervals (replaced entirely on each recalculation)
- **`backend/fritzbox_client.py`**: TR-064 client wrapper using `fritzconnection` library
- **`backend/tracker.py`**: `ConnectionTracker` orchestrates periodic polling:
  - Status polling (default 60s): Checks connection state, records changes only
  - Device log polling (default 60s): Syncs device logs and recalculates outages
- **`backend/periodic_runner.py`**: Asyncio-based background task runner
- **`backend/device_log_sync.py`**: Fetches device logs from Fritzbox and triggers outage recalculation
- **`backend/outage_calculator.py`**: Core logic that derives outage intervals from device log entries. Maintains separate state machines for IPv4 and IPv6:
  - Matches disconnect/connect events using configurable keywords
  - Supports "planned_hint" entries that mark the next disconnect as planned
  - Generates open outages when disconnect has no matching reconnect
- **`backend/outage_classifier.py`**: Keyword matching to categorize log entries
- **`backend/outage_config.py`**: Default keywords for planned/unplanned outage detection
- **`backend/schemas.py`**: Pydantic models for API request/response
- **`backend/models.py`**: Domain models for database records

**Key Backend Patterns:**
- Status changes are only recorded when different from latest stored event
- Device logs are deduplicated using UNIQUE constraint on (log_timestamp, message)
- Outages table is fully replaced on each sync (simplifies state management)
- Separate state tracking for IPv4 and IPv6 allows detection of protocol-specific issues

### Frontend Structure

Vue 3 SPA with Composition API:

- **`frontend/src/App.vue`**: Root component with Naive UI theme provider, menu navigation
- **`frontend/src/views/`**: Three main views (HomeView, OutagesView, LogsView)
- **`frontend/src/components/`**: Reusable components:
  - `AppHeader.vue`: Top navigation with responsive mobile menu (uses `useBreakpoints`)
  - `CalendarView.vue`: FullCalendar integration for outage visualization
  - `OutageTable.vue`: Tabular outage display
  - `DeviceLogTable.vue`: Device log entries with pagination
- **`frontend/src/composables/`**: Shared reactive logic:
  - `useDashboardData.ts`: Central data fetching and state management
  - `useStoergelerState.ts`: Reactive state for outages/logs/status
  - `usePagination.ts`: Pagination logic
  - `useBreakpoints.ts`: Responsive breakpoint detection
  - `useCalendarHeader.ts`: Calendar view switching for mobile
- **`frontend/src/api/`**: Backend API client functions
- **`frontend/src/config.ts`**: Runtime config (resolves backend URL)
- **`frontend/src/theme.ts`**: Naive UI theme customization

**Frontend Patterns:**
- Uses Naive UI component library for UI components
- Responsive design with mobile-specific layouts (breakpoint at 768px)
- Calendar switches from month view (desktop) to list view (mobile)
- All backend communication through `api/client.ts` functions
- No Vue Router (single view controlled by state in App.vue)

## Environment Variables

Backend requires these environment variables:

```bash
FRITZBOX_ADDRESS=fritz.box
FRITZBOX_USERNAME=homeauto
FRITZBOX_PASSWORD=secret
POLL_INTERVAL_SECONDS=60
DEVICE_LOG_POLL_INTERVAL_SECONDS=60
DATABASE_PATH=data/stoergeler.db
```

Optional keyword customization (CSV format):
```bash
OUTAGE_PLANNED_KEYWORDS="Internetverbindung wurde getrennt,Zwangstrennung"
OUTAGE_IPV4_DISCONNECT_KEYWORDS="PPPoE-Fehler,Zeitüberschreitung"
OUTAGE_IPV4_CONNECT_KEYWORDS="PPPoE,DSL antwortet"
OUTAGE_IPV6_DISCONNECT_KEYWORDS="IPv6-Präfix,Präfix verloren"
OUTAGE_IPV6_CONNECT_KEYWORDS="IPv6-Präfix wurde erfolgreich bezogen"
```

## Data Flow

1. **Periodic Status Polling** (tracker.py):
   - `ConnectionTracker` polls Fritzbox TR-064 every 60s
   - Only writes to `status_events` table when status changes

2. **Device Log Sync** (device_log_sync.py):
   - Fetches latest device logs from Fritzbox every 60s
   - Inserts new entries into `device_log_entries` (deduped by timestamp+message)
   - Triggers `OutageCalculator.calculate()` on all log entries
   - Replaces entire `outages` table with new calculations

3. **Outage Calculation** (outage_calculator.py):
   - Parses all device log entries chronologically
   - Maintains separate IPv4/IPv6 state machines
   - Matches disconnect → connect pairs to create outage windows
   - Classifies as planned/unplanned based on preceding hints
   - Generates "open" outages for unmatched disconnects

4. **Frontend Display**:
   - Fetches `/api/outages` and `/api/device-log` on mount and refresh
   - Displays outages in calendar and table views
   - Shows device logs with pagination

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/status` - Trigger immediate poll, return current status
- `GET /api/connection-check` - Live TR-064 connection check
- `GET /api/device-log?limit=500` - Device log entries (descending)
- `GET /api/outages` - Calculated outage windows
- `GET /api/version` - Backend version info

## Release Process

Uses semantic-release with Angular commit convention:

- Backend releases: `scope: backend` → tag `backend-v1.2.3`
- Frontend releases: `scope: frontend` → tag `frontend-v1.2.3`
- Commit format: `<type>(<scope>): <message>`
  - Types: `feat`, `fix`, `perf`, `chore`, etc.
  - Example: `feat(frontend): add mobile responsive layout`

GitHub Actions workflows handle automated releases on main branch.

## Mobile Responsiveness

The frontend has mobile-specific behavior:

- Header switches to hamburger menu below 768px
- Calendar view switches from month to list view on mobile
- Uses `useBreakpoints` composable for responsive checks
- All layout adjustments in component templates using `isMobile` reactive ref

## Database Schema

Three tables in SQLite (`data/stoergeler.db`):

1. **status_events**: Connection status changes (online/offline/error)
2. **device_log_entries**: Raw Fritzbox logs with UNIQUE(log_timestamp, message)
3. **outages**: Calculated outage intervals (fully replaced on each sync)

Foreign keys link outages to start/end log entries for traceability.
