# RoutePilot API

## Run locally
```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs for interactive API documentation.

## Run with Docker
From the project root: `docker compose up --build`

## Endpoints
- GET /health
- GET, POST /vehicles
- POST /vehicles/{vehicle_id}/positions — GPS telemetry ingestion (latitude/longitude validated)
- GET, POST /deliveries
- PATCH /deliveries/{delivery_id}/status
- POST /deliveries/{delivery_id}/proof
- GET /deliveries/{delivery_id}/note — document data preview

## Data and privacy
SQLite is used for a self-contained local demo. GPS records are sample/explicitly submitted coordinates; no background device tracking exists. Production deployment requires authentication, authorization, TLS, consent and retention controls, input rate limits, audit logs and a production database. The delivery note endpoint returns structured preview data, not a legally valid transport or tax document.

## Tests
Install `pytest httpx` and run `pytest` from this directory.
