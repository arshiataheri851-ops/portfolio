# SignalDesk — Service Operations Intelligence MVP

SignalDesk is an executable service-desk MVP with a FastAPI + SQLite backend and browser dashboard for creating, assigning, prioritizing and tracking support tickets.

## Included
- Sample operations overview with queue metrics
- Searchable request queue
- Priority and SLA-risk filters
- API-backed assignment, status changes and per-ticket audit history
- Queue distribution visualization
- Transparent rule-based prioritization explanation

## Run
Open `index.html` in a modern browser. No build step or backend is required.

## Production architecture direction
A production version could integrate authenticated intake APIs, a ticketing database, event-driven SLA timers, role-based assignment, audit events and analytics. Any AI-assisted triage should be separately evaluated, explainable, permission-aware and subject to human review.

## Important scope
Initial records are illustrative. New tickets, assignments and status changes persist in SQLite when the API is running. SLA risk and priority are transparent deterministic rules, not AI predictions. The MVP does not yet include authentication, roles, tenant isolation, email intake or notifications; do not expose it publicly or store real customer data before these controls are added.

Built as an ERYNDEX portfolio project.

## Run the working API backend
A FastAPI + SQLite backend is included. Start it with Docker from this folder using `docker compose up --build`, or follow [backend setup](backend/README.md). The dashboard reads and assigns tickets through the API at `http://127.0.0.1:8001`. Interactive API documentation is available at `/docs`.