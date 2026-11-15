# RoutePilot — Fleet & Delivery Operations Demo

An executable fleet-operations portfolio demo: FastAPI, PostgreSQL 16, Alembic migrations and a static browser dashboard. It demonstrates tenant-scoped delivery management, foreground browser GPS submission, proof-file uploads and delivery-note preview.

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
4. Open http://127.0.0.1:5500. Sign in with the bootstrap organization, email and password from `.env`.

The API listens on http://127.0.0.1:8000; interactive docs: http://127.0.0.1:8000/docs. PostgreSQL and proof uploads persist in Docker volumes. The first run applies migrations and seeds illustrative records for the bootstrap organization.

## Demonstrated workflows

- Login with short-lived bearer tokens; role checks and organization-scoped queries.
- Fleet and delivery listing; create deliveries and assign vehicles.
- Explicit foreground GPS sharing after browser permission; sharing stops when requested or when the page is closed.
- JPEG, PNG and PDF proof upload (10 MB limit), tenant-scoped file retrieval and delivery completion.
- Delivery-note preview marked as illustrative, not a legally valid transport document.

## Backups

From this folder, run `sh ops/backup-postgres.sh` to back up PostgreSQL and the proof-file volume. Restore with `sh ops/restore-postgres.sh database.dump proofs.tar.gz`. Restore is destructive; use a test environment first. Keep backups encrypted and off-host. A restore drill has not yet been certified.

## Important limitations

This is a portfolio demonstration, not a production fleet platform. GPS is foreground browser GPS, not guaranteed background/mobile tracking. Uploads are type/signature checked but do not yet have malware scanning, retention automation or production object storage. Email, production TLS/domain, monitoring, rate limits and formal security review remain outside this demo. Do not use real customer data or expose it publicly without those controls.

## Tests

`cd backend; py -m pip install -r requirements.txt; py -m pytest -q`. CI also runs the API suite against PostgreSQL 16.
