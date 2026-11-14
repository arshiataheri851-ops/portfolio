# ERYNDEX — Portfolio Index

This index mirrors the projects currently listed on the public ERYNDEX website. Descriptions below are concise summaries, not customer references.

**Important:** The portfolio includes demonstrators, reference implementations, concepts, and MVPs. Do not describe these as customer deployments unless separately verified and approved.

| # | Project | Current description / scope | Public status |
|---:|---|---|---|
| 1 | [FarsiPulse](https://farsipulse.onrender.com) | Persian sentiment intelligence API; Persian text normalization, batch processing, transformer inference, and reproducible evaluation. [Source](https://github.com/arshiataheri851-ops/arshiataheri851-ops/tree/feat/product-websites-farsipulse-atlasrag-relayforge/projects/persian-sentiment-api) | Dedicated public website |
| 2 | [AtlasRAG](https://atlasrag-6eab.onrender.com) | Tenant-isolated document retrieval with PostgreSQL full-text search, citations, authenticated APIs, and retrieval evaluation. [Source](https://github.com/arshiataheri851-ops/arshiataheri851-ops/tree/feat/product-websites-farsipulse-atlasrag-relayforge/projects/production-rag-service) | Dedicated public website |
| 3 | [RelayForge](https://relayforge-rcpo.onrender.com) | Webhook delivery engine with idempotent ingestion, HMAC-SHA256 signatures, bounded retries, leases, and dead-letter handling. [Source](https://github.com/arshiataheri851-ops/arshiataheri851-ops/tree/feat/product-websites-farsipulse-atlasrag-relayforge/projects/webhook-reliability-platform) | Dedicated public website |
| 4 | ML Model Serving Platform | Versioned scikit-learn model artifact, reproducible training, held-out evaluation, and a validated FastAPI inference endpoint. [Source](https://github.com/arshiataheri851-ops/arshiataheri851-ops/tree/main/projects/ml-model-serving-platform) | Source and documentation |
| 5 | Grounded Document Retrieval API | Source-aware retrieval baseline using TF-IDF, cosine similarity, local documents, and FastAPI; generated answers are not claimed. [Source](https://github.com/arshiataheri851-ops/arshiataheri851-ops/tree/main/projects/grounded-document-retrieval) | Source and documentation |
| 6 | Market Intelligence & Risk Analytics | Educational OHLCV pipeline with validation, moving averages, daily-change monitoring, and CSV reporting using synthetic data. [Source](https://github.com/arshiataheri851-ops/arshiataheri851-ops/tree/main/projects/market-intelligence-risk-engine) | Educational demonstrator |
| 7 | Workflow Orchestration Engine | Dependency-aware DAG runner with cycle detection, topological execution, retries, and per-step outcomes. [Source](https://github.com/arshiataheri851-ops/arshiataheri851-ops/tree/main/projects/workflow-orchestration-engine) | Source and documentation |
| 8 | ML Feature Store | SQLite-backed feature store with typed schemas, versioned entity values, batch lookup, and TTL freshness metadata. [Source](https://github.com/arshiataheri851-ops/arshiataheri851-ops/tree/main/projects/ml-feature-store) | Source and documentation |
| 9 | Intelligent Recommendation Platform | FastAPI recommendation service with interaction history, weighted feedback, cold-start fallback, and explainable ranking. [Source](https://github.com/arshiataheri851-ops/arshiataheri851-ops/tree/main/projects/intelligent-recommendation-platform) | Source and documentation |
| 10 | STRIDE — Sportswear & Equipment Store | Responsive storefront concept with product search, filters, sorting, wishlist, shopping bag, and clearly labelled demo checkout. [Source](https://github.com/arshiataheri851-ops/arshiataheri851-ops/tree/main/projects/stride-store) | Storefront concept |
| 11 | Agent Workflow Orchestrator | Approval-aware workflow control plane with DAG validation, task states, bounded retries, SQLite persistence, and audit trail. [Source](https://github.com/arshiataheri851-ops/arshiataheri851-ops/tree/main/projects/agent-workflow-orchestrator) | Source and documentation |
| 12 | Event Stream Processing Platform | Event-ingestion reference with schema validation, idempotent writes, dead-letter queue, and deterministic window aggregation. [Source](https://github.com/arshiataheri851-ops/arshiataheri851-ops/tree/main/projects/event-stream-processing-platform) | Source and documentation |
| 13 | LLM Gateway Control Plane | Provider-agnostic LLM gateway with routing policies, spend ceilings, bounded retries, and a labelled local mock mode. [Source](https://github.com/arshiataheri851-ops/arshiataheri851-ops/tree/main/projects/llm-gateway-control-plane) | Source and documentation |
| 14 | RoutePilot — Fleet & Delivery Operations | Fleet and delivery workflow MVP with FastAPI, SQLite, status tracking, proof-of-delivery metadata, and simulated vehicle positions. [Source](https://github.com/arshiataheri851-ops/arshiataheri851-ops/tree/main/projects/routepilot) | MVP / demonstrator |
| 15 | SignalDesk — Service Operations Intelligence | Service-desk MVP for ticket creation, assignment, priority and SLA-risk filters, status changes, and audit history. [Source](https://github.com/arshiataheri851-ops/arshiataheri851-ops/tree/main/projects/signaldesk) | MVP / demonstrator |
| 16 | ERYNDEX — Bilingual Company Website | Responsive English/Persian B2B company website with service pages, project case studies, and a contact interface. [Source](https://github.com/arshiataheri851-ops/arshiataheri851-ops/tree/main/projects/eryndex-company-website) | Company website |

## Live-site note

The company homepage currently identifies FarsiPulse, AtlasRAG, and RelayForge as the three projects with dedicated public product websites. Availability can change; verify each site before describing it as operational.

## Portfolio maintenance checklist

- Keep each project title and description aligned with its source repository.
- Label synthetic data, mock providers, demo checkout, simulated positions, and other non-production behavior clearly.
- Link to a project website only when the destination is reachable.
- Link to source code and documentation.
- Add customer attribution or performance results only with evidence and publication permission.
