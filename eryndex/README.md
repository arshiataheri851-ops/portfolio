# ERYNDEX — Company Website

Responsive bilingual (English/Persian) company website and engineering portfolio, published on Cloudflare Pages.

## Public pages

- English: https://eryndex.pages.dev/
- Persian: https://eryndex.pages.dev/fa/
- English leadership profile: https://eryndex.pages.dev/profile/
- Persian leadership profile: https://eryndex.pages.dev/fa/profile/

## Structure

- `index.html` — English homepage
- `fa/index.html` — Persian homepage
- `profile/` and `fa/profile/` — concise bilingual leadership profiles
- `services/` — four service detail pages
- `work/` — five detailed engineering case studies
- `assets/` — shared styles, scripts, and contact configuration
- `contact-api/` — Cloudflare Worker source for inquiry delivery
- `COMPANY_PROFILE.md` — canonical company profile
- `PORTFOLIO_INDEX.md` — 16-project inventory and status notes
- `PUBLICATION_AUDIT.md` — current cross-site consistency review

## Cloudflare Pages deployment

Connect the `arshiataheri851-ops/portfolio` repository to Cloudflare Pages with:

- Production branch: `main`
- Root directory: `eryndex`
- Framework preset: `None`
- Build command: empty
- Build output directory: `.`

The frontend is plain HTML, CSS and JavaScript and has no build step. Cloudflare Pages serves the static frontend and applies the `_headers` file when this directory is used as the deployment output. The contact Worker is a separate service and must be deployed independently.

## Contact form status

The form interface and client-side validation are present. The configured contact endpoint in `assets/config.js` is currently blank, so submissions use the visitor's email application as a fallback. The online form is **not yet a live server-side submission service**.

Before enabling the Worker:
1. Deploy the Worker from `contact-api/`.
2. Configure exact `ALLOWED_ORIGINS`, `CONTACT_TO`, and a verified `CONTACT_FROM`.
3. Store `RESEND_API_KEY` as a Worker secret.
4. Add rate limiting and bot protection.
5. Set the deployed HTTPS Worker URL in `assets/config.js`.
6. Add that exact Worker origin to `connect-src` in `_headers`.
7. Test valid and invalid submissions, CORS preflight, provider failures, and successful delivery end to end.

## Privacy and security

The current form asks for a name, email, optional company, service selection, project brief and consent. The Worker forwards valid submissions to the configured mail-delivery provider and inquiry mailbox; it does not intentionally persist inquiry records. Provider and mailbox retention still need an explicit policy.

A complete public privacy notice, data-retention period, and legally verified controller/entity details have not yet been published. Do not ask visitors to submit sensitive personal information, credentials, confidential customer data or secrets.

Cloudflare Pages can apply response headers using `_headers`. The current policy is a baseline and must be reviewed whenever third-party endpoints or services are added. The Worker is not a replacement for edge rate limiting, abuse protection, monitoring or an operational incident process.

## Portfolio accuracy

The homepage lists 16 projects. FarsiPulse, AtlasRAG and RelayForge have dedicated product-site links; current uptime was not independently confirmed during the latest content audit. The other entries link to source repositories and are labelled as demonstrators, concepts or MVPs where appropriate.

Important technical boundaries:
- AtlasRAG currently uses PostgreSQL lexical full-text search; its source README explicitly says it does not yet use vector embeddings or semantic retrieval, and it does not claim LLM-generated answers.
- RelayForge provides at-least-once delivery attempts, not exactly-once delivery.
- RoutePilot uses simulated vehicle positions and is not connected to live GPS hardware.
- SignalDesk is a service-desk MVP with deterministic prioritization, not an AI triage system.

## Profile publication

Public leadership pages are intentionally limited to the company role and responsibilities. Personal contact details, detailed CV claims, education, employment history and credentials require verification and explicit approval before publication.

## Before public launch

- Deploy and test the contact Worker.
- Publish a complete privacy notice and define retention.
- Verify all live product-site links and deployment status.
- Confirm legal company identity and any claims about customers, team size, credentials, certifications or delivery metrics.
- Review security headers, abuse controls, monitoring and backups.
