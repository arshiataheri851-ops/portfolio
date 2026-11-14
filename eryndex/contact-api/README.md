# ERYNDEX customer request tracking API

This Worker powers the ERYNDEX collaboration-request intake, customer tracking portal and private administration page. The code is prepared but is **not deployed or live** until the Cloudflare D1 database, Worker secrets and endpoint are configured and end-to-end tested.

## Components
- `worker.js`: creates requests, issues a reference, returns customer status/history, and provides token-protected admin list/update endpoints.
- `migrations/0001_requests.sql`: D1 schema for requests and public status events.
- `../requests/`: English customer tracking page.
- `../fa/requests/`: Persian customer tracking page.
- `../admin/`: private admin interface. It is not linked in public navigation.

## Cloudflare setup
1. Create a D1 database named `eryndex-requests`.
2. Replace `REPLACE_AFTER_CREATING_D1` in `wrangler.toml` with the database ID.
3. Run `wrangler d1 migrations apply eryndex-requests --remote`.
4. Deploy the Worker from this directory using Wrangler.
5. Set Worker variables:
   - `ALLOWED_ORIGINS=https://eryndex.pages.dev`
   - `CONTACT_TO=eryndexco@gmail.com`
   - `CONTACT_FROM=<verified sender address>`
6. Add `RESEND_API_KEY` and a long random `ADMIN_API_TOKEN` as Worker secrets. Never commit or paste these secrets into frontend code or GitHub.
7. Set `window.ERYNDEX_CONTACT_ENDPOINT` in `assets/config.js` to the deployed Worker URL ending in `/api/requests`.
8. Test valid and invalid submissions, customer lookup with matching and non-matching email, admin unauthorized access, status updates, CORS, database failure and email delivery. Add Cloudflare rate limiting and Turnstile before public launch.

## Endpoints
- `POST /api/requests`: validates and stores a customer request; responds with a reference such as `ERX-2026-XXXXXXXX`.
- `POST /api/track`: requires both reference and the request email; returns customer-visible status history only.
- `GET /api/admin/requests`: requires `Authorization: Bearer <ADMIN_API_TOKEN>`.
- `PATCH /api/admin/requests/:id`: updates status, priority, internal note, proposal fields and customer-visible event message.
- `GET /health`: health check.

## Status values
`submitted`, `under_review`, `needs_information`, `proposal_sent`, `awaiting_approval`, `approved`, `in_progress`, `completed`, `declined`.

## Security and operational notes
- The admin token is a shared-secret MVP control, not a full user/role system. Restrict the admin page further with Cloudflare Access before production use; rotate the token if exposed.
- Customer lookup requires both reference and email. Do not expose request IDs or admin notes in customer responses.
- Configure rate limiting and Turnstile/other abuse controls at the edge before public launch.
- The current email notification is best-effort; database persistence is authoritative. Configure delivery monitoring and retries before relying on email as the sole alert channel.
- Define a privacy notice, retention period and deletion process appropriate to the business and applicable law.
- No secrets, paid services, DNS records or custom domains are configured by this code change.
