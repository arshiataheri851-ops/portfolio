# Production implementation and release gates

This document tracks the production-hardening work for RoutePilot and SignalDesk. It is intentionally explicit about what is not yet implemented. Neither product is approved for public deployment or real customer data until every release gate below is implemented and verified.

## Required implementation order

1. **Identity and tenant boundary**
   - Password hashing with Argon2id; short-lived signed access tokens; server-side active-user and role checks.
   - Organization membership is derived from the authenticated database user, never from a request body or query parameter.
   - Every business query, update, relationship lookup, attachment lookup and audit event is scoped by organization.
   - Admin-created accounts only; no public self-registration.
   - Cross-tenant and role-matrix tests for every route.

2. **PostgreSQL and migrations**
   - Replace direct sqlite3 access with a PostgreSQL-capable persistence layer.
   - Add Alembic migrations and migration tests from an empty database and a copy of the current SQLite schema/data.
   - Preserve legacy records under an explicit legacy organization; do not silently merge customer data.
   - Verify foreign keys, unique constraints, indexes, transaction boundaries and concurrent writes.
   - SQLite is not the production database after cutover.

3. **RoutePilot driver workflow**
   - Authenticated driver session and server-enforced vehicle/delivery assignment.
   - Foreground browser geolocation only while the driver page is active and the user has granted permission.
   - Visible tracking state, last-fix timestamp, accuracy, denied-permission and offline/error states.
   - Browser background tracking is not guaranteed after the tab is hidden, closed or suspended; do not market it as continuous background tracking.

4. **RoutePilot proof of delivery**
   - Authenticated multipart upload, file size/type limits, content sniffing, random object keys and malware-scanning integration.
   - Store files outside the web root (object storage in production); persist metadata and tenant-scoped references in PostgreSQL.
   - Signed, short-lived download links; authorization on both metadata and file retrieval.
   - Retention and deletion policy before real personal data is accepted.

5. **SignalDesk email and notifications**
   - Configurable inbound email adapter (provider webhook or controlled IMAP worker), verified webhook signatures and idempotency.
   - Outbound SMTP/provider adapter, retry queue, delivery status and audit log.
   - Notification preferences and tenant-scoped templates; never expose SMTP credentials to the browser.
   - Avoid treating email content as trusted instructions or executable content.

6. **Security, backup and restore**
   - Automated dependency/security checks, authorization regression tests, upload tests, rate limits and security headers.
   - Encrypted, off-host PostgreSQL backups with retention and monitoring.
   - Automated restore drill into an isolated database; backup success alone is not proof of recoverability.
   - Document RPO/RTO and incident response.

7. **Deployment**
   - Production environment variables and secret manager; no secrets committed to Git.
   - TLS reverse proxy, HTTPS-only origins, secure cookies or carefully scoped bearer-token strategy, firewall and non-root containers.
   - Separate staging and production databases, migration-before-release workflow, health/readiness checks and rollback plan.
   - DNS and certificate issuance must be verified from the actual domain.

## External prerequisites for the final deployment

The repository alone cannot provision a real server, control DNS, or issue a production certificate. Before production cutover, the project owner must provision:
- A VPS/cloud account and server in the intended region.
- A domain and access to its DNS records.
- A secrets manager or secure deployment secret store.
- An email provider/domain with verified sending identity and an inbound route/webhook.
- Object storage and (if required) malware-scanning service for proof-of-delivery files.

Do not send private SSH keys, passwords, API tokens, SMTP passwords or cloud credentials in chat or commit them to GitHub. Configure them directly in the hosting provider's secret store.

## Current baseline (at branch creation)

- Both APIs use SQLite and direct SQL.
- Neither API has authentication, role-based authorization or tenant isolation.
- RoutePilot accepts telemetry submitted to its API but does not yet have an authenticated driver app or browser GPS workflow.
- RoutePilot proof records are metadata only; there is no binary file upload.
- SignalDesk has no inbound/outbound email integration or notification worker.
- There is no PostgreSQL migration system, backup/restore automation or production host/domain configured in this repository.
- Existing CI runs API tests, but those tests do not constitute a security audit or production acceptance.

## Release rule

Do not label any item complete until its code is merged, tests pass in CI, deployment configuration is reviewed, and the relevant end-to-end acceptance test has been run. Do not expose either service publicly while any identity/tenant, database, upload or secret-management gate remains open.
