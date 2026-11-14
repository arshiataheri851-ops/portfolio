# ERYNDEX — Public Consistency Audit

**Audit date:** 2026-11-14  
**Scope:** GitHub repository content, English and Persian homepages, service pages, leadership profile routes, five detailed case-study pages, sitemap, contact-form code and deployment documentation, plus the linked source READMEs for FarsiPulse, AtlasRAG and RelayForge.

## Executive result

The public company description is consistent at the brand level: ERYNDEX is presented as a software engineering and applied-AI partner, with four service lines and a four-stage delivery approach. The audit identified content and navigation inconsistencies. The corrections below address the issues that could be resolved safely from repository evidence.

## Corrections made

- Replaced the public leadership profile's unverified CV-style claims and personal contact details with a concise company-role profile in English and Persian.
- Normalized the FarsiPulse, AtlasRAG and RelayForge source links to the projects on the linked repository's default `main` branch.
- Rewrote the FarsiPulse, AtlasRAG and RelayForge detailed case-study pages against their current source READMEs, including explicit technical limitations.
- Added both leadership profile routes to the XML sitemap.
- Corrected hosting documentation to describe Cloudflare Pages as the static frontend host and the contact Worker as a separately deployed service.
- Corrected the contact Worker deployment guide so its initial allowed origin is `https://eryndex.pages.dev`, not an unrelated GitHub Pages origin.

## Verified content baseline

### Company identity and services

- Public brand: **ERYNDEX**
- Positioning: software engineering and applied AI partner
- Services: Backend & API Engineering; Applied AI Integration; Knowledge Retrieval & RAG; Integration & Delivery Systems
- Leadership roles: Arshia Taheri — Co-founder, Business Development; Engineer Taher — Co-founder, Technical Leadership
- Delivery approach: Understand → Scope → Build → Handover

### Portfolio inventory

The English and Persian homepages each list 16 projects. Three have dedicated product-site links and source repositories: FarsiPulse, AtlasRAG and RelayForge. The remaining entries link to source implementations; RoutePilot and SignalDesk also have detailed case-study pages.

The existence of a public URL does not prove current uptime, production readiness or customer use. Product-site uptime was not independently verified in this audit.

### Technical claim boundaries

- **FarsiPulse:** the source README documents a typed FastAPI service for binary Persian review sentiment, single and batch prediction, Persian normalization, lazy pinned Hugging Face model loading and reproducible evaluation. Published benchmark results are in-domain only and are not a general performance guarantee.
- **AtlasRAG:** the source README documents authenticated multi-tenant document retrieval backed by PostgreSQL full-text search. The current retrieval is lexical; it does not use vector embeddings or claim semantic/hybrid retrieval. The service does not claim LLM-generated answers.
- **RelayForge:** the source README documents a durable webhook workflow with HMAC-SHA256 signing, allowlisted HTTPS delivery, DNS-pinned connections, bounded retries and dead-letter handling. Delivery semantics are at-least-once, not exactly-once.
- **RoutePilot:** simulated vehicle positions are not live GPS telemetry.
- **SignalDesk:** prioritization is deterministic; the MVP is not an AI triage system.

## Remaining items requiring owner or operational confirmation

1. **Contact backend:** `assets/config.js` still has an empty endpoint. The form therefore falls back to the visitor's email application. The Worker is not established as a live submission service by the repository configuration.
2. **Privacy notice and retention:** the form collects inquiry details and consent, and the Worker forwards them through an email provider. A complete public privacy notice, controller/legal identity, retention period and visitor-rights process still need review and publication.
3. **Live links:** verify FarsiPulse, AtlasRAG and RelayForge product URLs in an ordinary browser and confirm current deployment health before advertising them as operational.
4. **Legal company details:** legal entity name, registration, jurisdiction, registered address, formal ownership and official business contact details remain unpublished pending verification.
5. **Team credentials:** publish education, employment history, certificates, biographies, team size and technical proficiency claims only after the relevant people approve the exact wording and evidence.
6. **Commercial claims:** customer names, testimonials, production outcomes, revenue, user counts, guaranteed timelines, SLAs, certifications and security-audit claims require independent evidence and publication permission.
7. **Repository branding:** the website currently lives in a subdirectory of a personal portfolio repository. A dedicated ERYNDEX GitHub organization or company repository may provide a clearer long-term public identity, but should be created only after the company account and ownership decision is confirmed.

## Deployment and security checks still required

- Deploy and test the contact Worker.
- Configure Worker secrets outside source control.
- Apply rate limiting and bot protection at the edge.
- Add the deployed Worker origin to `connect-src` in `_headers`.
- Verify deployed HTTP security headers and HTTPS behavior.
- Test contact submission, invalid input, CORS preflight, provider failure and successful delivery.
- Establish privacy/retention procedures and operational monitoring before accepting public inquiries.

## Audit status

**Content and repository corrections:** applied; post-commit verification remains.  
**Production readiness:** not certified. Live deployment, uptime, form delivery, security controls, privacy/legal review and backup/restore behavior require external operational checks.
