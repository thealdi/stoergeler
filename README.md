# StoerGeler

Python-Backend und Vue-Frontend zur Erfassung und Visualisierung der Internetverbindung einer Fritzbox über TR-064.

## Architekturüberblick

- **Backend**: FastAPI-Anwendung (`backend/main.py`) pollt die TR-064-Schnittstelle (`fritzconnection`) in Hintergrundtasks, persistiert Statuswechsel sowie Device-Log-Einträge und berechnet daraus Störungsintervalle.
- **Persistenz**: SQLite-Datenbank unter `data/stoergeler.db` (Pfad via `DATABASE_PATH` konfigurierbar).
- **Frontend**: Vue 3 + Vite + TypeScript (`frontend-vue/`) mit Naive UI und FullCalendar. Kalender zeigt Störungen, Klick öffnet Drawer mit gefilterten Logeinträgen.
- **Legacy**: Das alte statische Frontend liegt in `frontend-deprecated/` und wird nicht mehr weiterentwickelt.

## Voraussetzungen

- Python ≥ 3.11
- Zugriffsdaten für die Fritzbox (Benutzername/Passwort für TR-064-Service)

## Installation & Start Backend

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Notwendige Umgebungsvariablen (Beispiele):

```bash
export FRITZBOX_ADDRESS="fritz.box"
export FRITZBOX_USERNAME="homeauto"
export FRITZBOX_PASSWORD="geheimes-passwort"
export POLL_INTERVAL_SECONDS=60
export DEVICE_LOG_POLL_INTERVAL_SECONDS=60
```

Backend starten (läuft unter `/api`, z. B. `http://localhost:8000/api/health`):

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Die OpenAPI-Dokumentation ist anschließend unter `http://localhost:8000/docs` erreichbar.

### Betrieb mit Docker / Docker Compose

Schnellstart (Backend auf Port 8001, Frontend auf 8080):

```bash
docker compose up --build
```

Wichtige Punkte:

- Der Backend-Container wird aus dem mitgelieferten `Dockerfile` gebaut und nutzt `/volume1/docker/stoergeler/data` (anpassbar) als Host-Verzeichnis für die SQLite-Datenbank.
- Die relevanten Umgebungsvariablen (z. B. `FRITZBOX_USERNAME`, `FRITZBOX_PASSWORD`) können per `.env` oder direkt im Compose-/Portainer-UI gesetzt werden (siehe `docker-compose.yml`).
- Der Frontend-Container basiert auf `nginx:alpine` und serviert die statischen Dateien aus `/volume1/docker/stoergeler/frontend` (Volume).
- Aufruf nach dem Start: `http://<host>:8080` für das Frontend, `http://<host>:8001/api/health` für die API.

> Hinweis: Das Compose-Setup verwendet ein Host-Verzeichnis `/volume1/docker/stoergeler/data` für die Persistenz. Auf einem Synology NAS kannst du dieses Verzeichnis direkt einsehen und sichern. Eine Beispiel-Env-Datei liegt als `./.env.example`. Optional kannst du `DOCKER_PLATFORM` setzen (Standard `linux/amd64`, bei ARM-NAS `linux/arm64`).

## Frontend lokal entwickeln (Vue)

Frontend installieren und starten:

```bash
cd frontend-vue
npm install
npm run dev
```

Danach im Browser `http://localhost:5173` öffnen. Das Frontend ruft die API unter `http://localhost:8000/api` auf.

### Frontend Build für Nginx

```bash
cd frontend-vue
npm install
npm run build
```

Die Ausgabe liegt in `frontend-vue/dist/` und kann in das Nginx-Volume kopiert werden (z. B. `/volume1/docker/stoergeler/frontend`).

## API-Überblick

- `GET /api/health` – einfacher Gesundheitscheck
- `GET /api/status` – führt einen unmittelbaren TR-064 Poll durch und liefert den aktuellen Status zurück.
- `GET /api/device-log?limit=<int>` – ruft das Fritzbox-Ereignisprotokoll aus der Datenbank ab und liefert strukturierte Einträge (`timestamp`, `message`, `raw`).
- `GET /api/outages` – liefert die aus dem gespeicherten Device-Log abgeleiteten Offline-Zeitfenster (aktualisiert durch den Hintergrundtask).
- `GET /api/connection-check` – prüft, ob sich mit den TR-064-Credentials eine Verbindung aufbauen lässt.

## Datenhaltung

Die Anwendung speichert Statuswechsel (`online`, `offline`, `error`) sowie alle gelesenen Fritzbox-Gerätelogzeilen in SQLite (`data/stoergeler.db`). Aus den persistierten Logeinträgen werden Ausfallintervalle berechnet und in einer separaten Tabelle abgelegt; offene Störungen bleiben dort mit `end = NULL` erhalten.

## Frontend Features

- **Kalenderansicht**: Störungen als rote (ungeplant) bzw. blaue (planmäßige Zwangstrennung) Balken.
- **Drawer-Logansicht**: Klick auf ein Ereignis öffnet ein Drawer mit gefilterten Fritzbox-Logs.
- **Störungsliste**: Tabelle mit Start/Ende, Dauer, Status inkl. Pagination.
- **Ereignisprotokoll**: Fritzbox-Logs mit Pagination.
- **Manueller TR-064-Check**: Button ruft `/api/connection-check` auf.

## Tests (Empfehlung)

- Unit-Tests für Repositories & OutageService (`pytest`, `pytest-asyncio`).
- API-Tests per `TestClient` gegen FastAPI.
- Optional Frontend-Tests (Jest/Vitest, Playwright) für Filter-/Kalenderlogik.
