## Context
Only bootstrap routes exist. PRD US01/US04 and ADR-003/005 define intent; see proposal.
M1 supplies executable contracts; M3 owns durable ingest/outbox and real credentials.

## Goals / Non-Goals
Deliver machine-readable 0.1.0 and negative conformance checks. No database changes,
real credential provisioning, production ingestion, event processing or historical video.

## Decisions
- JSON Schema Draft 2020-12 as wire source of truth; generate documents from a small
  deterministic builder, CI checks drift. OpenAPI 3.1 embeds the same schema definitions.
  Prefer explicit JSON types over framework coercion. Runtime only serves static JSON.
- Initial catalog covers cash sessions, cash movements/drawer, transaction start/subtotal/
  completion/both cancellations, items added/cancelled, payment and change (14 types).
  Remaining v0.2 taxonomy reserved, rejected until specified. No generic arbitrary payload.
- UUIDv4 event identity; timezone-aware millisecond timestamps, decimal strings with fixed
  scale, additionalProperties=false. Source session UUID and sequence support diagnosis,
  not global ordering. Exact parsed JSON equality ignores key order but not changed facts.
- Credential tenant and exact tuple grants authoritative; integration identity remains
  stable across rotation. Bearer token ≥256 random bits, stored hash only, expiry/revocation.
  Local reference uses explicitly synthetic in-memory fixtures; never imported by runtime.
- Reference outcomes model 201/200/401/403/404/409/422; JSON transport has 400/413.
  They are conformance observations, not actual production HTTP routes. Future success
  requires event+outbox commit; untested persistence cannot be inferred from reference tests.
- Versioned read-only routes under /api/contracts/0.1.0; do not replace runtime /openapi.json.
  Business OpenAPI has no production server URL and labels operations planned for M3.

## Risks / Trade-offs
[Reference mistaken for production] → explicit labels, no serving write routes, regression test.
[Schema diverges from examples/OpenAPI] → independent validator and artifact drift tests.
[Store/terminal grant cartesian product] → exact tuples, negative combinations tested.
[Replay semantics interpreted as exactly-once] → state retention/atomicity required in M3;
only deterministic equality policy proven here. No changes to shared PostgreSQL.

## Migration Plan
New public contract version only; no existing ERP clients or stored events. Rollback image
removes read-only routes without data migration. Freeze 0.1.0 after this change; incompatible
wire or validation changes require a new explicit protocol version and adapter migration.
