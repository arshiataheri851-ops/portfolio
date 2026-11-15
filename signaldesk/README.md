# SignalDesk — Service Operations Demo

An executable service-desk portfolio demo: FastAPI, PostgreSQL 16, Alembic migrations and a static browser dashboard for ticket intake, assignment, SLA triage and audit history.

## Run on Windows

1. Copy `.env.example` to `.env` and set a unique `POSTGRES_PASSWORD`, a random `AUTH_JWT_SECRET` (at least 32 characters), `BOOTSTRAP_ORG_NAME`, `BOOTSTRAP_ADMIN_EMAIL` and `BOOTSTRAP_ADMIN_PASSWORD` (at least 14 characters). Never commit `.env`.
2. From this folder, run:
   ```powershell
   docker compose up --build
   ```
3. In a second terminal, serve the dashboard:
   ```powershell
   py -m http.server 5500
   ```
4. Open http://127.0.0.1:5500 and sign in with the bootstrap values from `.env`.

The API listens on http://127.0.0.1:8001; interactive docs: http://127.0.0.1:8001/docs. PostgreSQL persists in a Docker volume. The first run applies migrations and seeds sample tickets for the bootstrap organization.

## Demonstrated workflows

- Login with short-lived bearer tokens; role checks and organization-scoped ticket access.
- Search and filter by priority and SLA risk.
- Create tickets, assign an operator, change status and inspect audit history.
- Deterministic, explainable SLA-risk and priority scoring.
- Optional outbound SMTP email endpoint with ticket ownership check and audit event.

## Email configuration

Set `SMTP_HOST`, `SMTP_PORT`, `SMTP_FROM` and (when needed) `SMTP_USERNAME` / `SMTP_PASSWORD` in local `.env`. STARTTLS is used by default; configure SSL only when required by the provider. Never commit credentials. The SMTP send is synchronous and has no retry queue or inbound email ingestion yet.

## Important limitations

This is a portfolio demonstration, not a production service desk. No inbound email processing, queued retries, provider delivery webhooks, production TLS/domain, monitoring, rate limiting or formal security review are included. SLA rules are illustrative and must be configured to a real service contract before operational use. Do not use real customer data or expose it publicly without those controls.

## Tests

`cd backend; py -m pip install -r requirements.txt; py -m pytest -q`. CI also runs the API suite against PostgreSQL 16.
