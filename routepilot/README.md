# RoutePilot — Fleet & Delivery Operations MVP

RoutePilot is an executable fleet and delivery workflow MVP with a FastAPI + SQLite backend and browser dashboard. It supports vehicle records, submitted GPS telemetry, delivery creation/status, proof-of-delivery metadata and delivery-note preview.

## Included
- Responsive fleet operations dashboard
- Simulated vehicle positions and route paths (not connected to real GPS devices)
- Delivery table with status filtering and API-backed delivery creation
- Proof-of-delivery metadata capture and delivery-note preview
- Explicit sample-data and non-legal-document notices

## Run
Open `index.html` in a browser. No build step or external API is required.

## Production architecture direction
A real deployment could use a mobile driver app or GPS device gateway, an authenticated event-ingestion API, a geospatial store, a dispatch service, a document-rendering service, object storage and an auditable proof-of-delivery workflow. Location access, consent, retention, role permissions, document templates and jurisdiction-specific requirements must be designed before production use.

## Important scope
The API and dashboard are usable as a local MVP. Initial records are sample data. It does not connect to live vehicle hardware, store uploaded photographs or biometric signatures, issue legally valid transport documents, or include authentication/tenant isolation. Do not expose it publicly or enter real personal data until those controls are implemented.

Built as an ERYNDEX portfolio project.

## Run the working API backend
The project now includes a FastAPI + SQLite backend. Start it with Docker from this folder using `docker compose up --build`, or follow [backend setup](backend/README.md). The dashboard reads delivery records from the API at `http://127.0.0.1:8000` when the API is running. Interactive API documentation is available at `/docs`.