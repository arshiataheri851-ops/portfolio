# ERYNDEX — Company Website

Responsive bilingual (English/Persian) company website and engineering portfolio, published on Cloudflare Pages.

## Preview
- English: https://eryndex.pages.dev/
- Persian: https://eryndex.pages.dev/fa/

## Structure
- `index.html` — English homepage
- `fa/index.html` — Persian homepage
- `services/` — dedicated service pages
- `work/` — project case-study pages
- `assets/style.css` — shared responsive styles
- `assets/script.js` — navigation, scroll progress and inquiry-form client logic
- `contact-api/` — Cloudflare Worker source for server-side inquiry delivery

## Cloudflare Pages deployment

Connect the `arshiataheri851-ops/portfolio` GitHub repository to Cloudflare Pages and use these settings:
- Production branch: `main`
- Root directory: `eryndex`
- Framework preset: `None` (or `No framework`)
- Build command: leave empty
- Build output directory: `.`
- No environment variables are required for the static frontend at this stage.

The site is plain HTML, CSS and JavaScript; there is no package installation or frontend build step. The `_headers` file in this directory is intended for Cloudflare Pages and will be applied when this directory is used as the deployment output. When the contact Worker is deployed, update `connect-src` in `_headers` to include its exact HTTPS origin, then test the browser policy.

## Important deployment status
The contact form interface and validation are present. Until the Worker is deployed, configured with secrets and tested, submissions fall back to opening the visitor's email application. The online form is **not yet a live server-side submission service**. Follow `contact-api/README.md`.

GitHub Pages is static hosting. It does not run the Worker or allow arbitrary HTTP response headers. The current HTML Content Security Policy is a partial browser-side control, not a replacement for server response headers. For production, place the site behind a host/CDN that can enforce security headers, configure rate limiting and bot protection, and test the deployed configuration.

## Project accuracy
RoutePilot and SignalDesk details are based on their repository READMEs. Other case-study pages deliberately avoid unverified architecture or performance claims; inspect the linked source repositories and update the pages only from verified implementation details.

## Profile publication
Detailed CV, education, employment history, dates and performance metrics are withheld pending verification and approval. Team roles are described at a high level only.

## Before production launch
1. Deploy and test the contact Worker, configure a verified sender domain and store provider credentials as Worker secrets.
2. Add rate limiting and bot protection, and confirm the privacy notice and retention policy.
3. Configure production security response headers and HTTPS at the hosting/CDN layer.
4. Audit all service claims and project case studies against code and tests.
5. Confirm brand/legal identity and publish legal details only after formal verification.
6. Add reviewed team biographies and verified credentials only with each person's approval.

The site is plain HTML, CSS and JavaScript and requires no frontend build step.
