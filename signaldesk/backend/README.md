# SignalDesk API

## Run locally
```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

## Docker
From the project root: `docker compose up --build` (API on port 8001).

## Endpoints
- GET /health
- GET /tickets?status=&queue=&priority=&q=
- POST /tickets
- PATCH /tickets/{id}/assign
- PATCH /tickets/{id}/status
- GET /analytics/summary

## Behavior
Ticket records persist in SQLite. The API computes SLA risk from due_at and ranks tickets using a transparent weighted rule based on priority, remaining SLA time and account tier. This is deterministic rule-based triage, not an AI model.

## Production considerations
Add authentication, role-based permissions, tenant isolation, audit events, rate limits, migrations and a production database before handling real customer information.

## Tests
Install `pytest httpx` and run `pytest` from this directory.