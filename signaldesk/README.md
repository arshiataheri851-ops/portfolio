# SignalDesk — Service Operations Intelligence Demonstrator

SignalDesk is a responsive, interactive front-end concept for service teams managing incoming requests and SLA commitments.

## Included
- Sample operations overview with queue metrics
- Searchable request queue
- Priority and SLA-risk filters
- Local-only assignment interaction
- Queue distribution visualization
- Transparent rule-based prioritization explanation

## Run
Open `index.html` in a modern browser. No build step or backend is required.

## Production architecture direction
A production version could integrate authenticated intake APIs, a ticketing database, event-driven SLA timers, role-based assignment, audit events and analytics. Any AI-assisted triage should be separately evaluated, explainable, permission-aware and subject to human review.

## Important scope
All records and metrics are illustrative. Interactions run only in the browser; assignment does not persist or contact a service. The score is a rule-based example, not an AI prediction. This is a portfolio concept, not a deployed customer system.

Built as an ERYNDEX portfolio project.