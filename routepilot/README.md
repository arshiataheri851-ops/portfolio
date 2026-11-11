# RoutePilot — Fleet & Delivery Operations Demonstrator

RoutePilot is a front-end portfolio demonstrator for a last-mile delivery workflow. It combines a fleet overview, illustrative GPS route map, delivery status table, proof-of-delivery states and a generated delivery-note preview.

## Included
- Responsive fleet operations dashboard
- Simulated vehicle positions and route paths (not connected to real GPS devices)
- Delivery table with status filtering
- Delivery-note preview for a completed stop
- Explicit sample-data and non-legal-document notices

## Run
Open `index.html` in a browser. No build step or external API is required.

## Production architecture direction
A real deployment could use a mobile driver app or GPS device gateway, an authenticated event-ingestion API, a geospatial store, a dispatch service, a document-rendering service, object storage and an auditable proof-of-delivery workflow. Location access, consent, retention, role permissions, document templates and jurisdiction-specific requirements must be designed before production use.

## Important scope
This repository is a concept demonstrator with illustrative data. It does not connect to live vehicles, issue legally valid transport documents, collect signatures or provide a real dispatch service. No operational performance claims are made.

Built as an ERYNDEX portfolio project.

## Run the working API backend
The project now includes a FastAPI + SQLite backend. Start it with Docker from this folder using `docker compose up --build`, or follow [backend setup](backend/README.md). The dashboard reads delivery records from the API at `http://127.0.0.1:8000` when the API is running. Interactive API documentation is available at `/docs`.