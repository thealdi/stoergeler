# StoerGeler

Python-Backend und statisches Frontend zur Erfassung und Visualisierung der Internetverbindung einer Fritzbox über TR-064.

## Architekturüberblick

- **Backend**: FastAPI-Anwendung (`backend/main.py`) pollt die TR-064-Schnittstelle (`fritzconnection`) in Hintergrundtasks, persistiert Statuswechsel sowie Device-Log-Einträge und berechnet daraus Störungsintervalle.
- **Persistenz**: SQLite-Datenbank unter `data/stoergeler.db` (Pfad via `DATABASE_PATH` konfigurierbar).
- **Frontend**: Statische HTML/JS-App (`frontend/`) mit Kalender zur Visualisierung der Ausfallfenster (Klick auf ein Offline-Ereignis filtert das Log), Ereignisprotokoll und manueller TR-064-Verbindungsprüfung.

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

Backend starten:

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
- Der Frontend-Container basiert auf `nginx:alpine` und serviert die statischen Dateien. Das Frontend erwartet den Backend-Service auf Port 8001 (konfigurierbar über `window.STOERGELER_BACKEND_URL`, optional per zusätzlichem `<script>` oder Reverse-Proxy).
- Aufruf nach dem Start: `http://<host>:8080` für das Frontend, `http://<host>:8001` für die API.

> Hinweis: Das Compose-Setup verwendet ein Host-Verzeichnis `/volume1/docker/stoergeler/data` für die Persistenz. Auf einem Synology NAS kannst du dieses Verzeichnis direkt einsehen und sichern. Eine Beispiel-Env-Datei liegt als `./.env.example`. Optional kannst du `DOCKER_PLATFORM` setzen (Standard `linux/amd64`, bei ARM-NAS `linux/arm64`).

## Frontend lokal ausliefern

Die statischen Dateien können mit jedem beliebigen Webserver bereitgestellt werden, z. B. mittels Python:

```bash
python -m http.server 5173 --directory frontend
```

Danach im Browser `http://localhost:5173` öffnen. Das Frontend verbindet sich ohne weitere Konfiguration automatisch mit `http://localhost:8000` (bzw. dem über `window.STOERGELER_BACKEND_URL` gesetzten Wert).

## API-Überblick

- `GET /health` – einfacher Gesundheitscheck
- `GET /status` – führt einen unmittelbaren TR-064 Poll durch und liefert den aktuellen Status zurück.
- `GET /device-log?limit=<int>` – ruft das Fritzbox-Ereignisprotokoll aus der Datenbank ab und liefert strukturierte Einträge (`timestamp`, `message`, `raw`).
- `GET /outages` – liefert die aus dem gespeicherten Device-Log abgeleiteten Offline-Zeitfenster (aktualisiert durch den Hintergrundtask).
- `GET /connection-check` – prüft, ob sich mit den TR-064-Credentials eine Verbindung aufbauen lässt.

## Datenhaltung

Die Anwendung speichert Statuswechsel (`online`, `offline`, `error`) sowie alle gelesenen Fritzbox-Gerätelogzeilen in SQLite (`data/stoergeler.db`). Aus den persistierten Logeinträgen werden Ausfallintervalle berechnet und in einer separaten Tabelle abgelegt; offene Störungen bleiben dort mit `end = NULL` erhalten.

## Frontend Features

- **Kalenderansicht**: Störungen als rote (ungeplant) bzw. blaue (planmäßige Zwangstrennung) Balken; Klick filtert das Ereignisprotokoll.
- **Störungsliste**: Tabelle mit Start/Ende, Dauer, Status (z. B. `closed`, `planned`) inkl. Pagination (Default 5 Einträge pro Seite).
- **Ereignisprotokoll**: Fritzbox-Logs mit Pagination (20 Einträge pro Seite).
- **Manueller TR-064-Check**: Button ruft `/connection-check` auf.

## Tests (Empfehlung)

- Unit-Tests für Repositories & OutageService (`pytest`, `pytest-asyncio`).
- API-Tests per `TestClient` gegen FastAPI.
- Optional Frontend-Tests (Jest/Vitest, Playwright) für Filter-/Kalenderlogik.
