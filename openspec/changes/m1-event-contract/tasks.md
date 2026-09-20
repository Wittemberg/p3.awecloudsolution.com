## 1. Protocol
- [x] 1.1 Deliver versioned catalog, schema, OpenAPI and 14 examples; independently validate documents and examples.
- [x] 1.2 Document identity, time, money, offline/retry and compatibility; review against PRD US01/US04 and ADRs.
## 2. Executable conformance
- [x] 2.1 Implement safe local checker and reference identity/replay model; test invalid payloads, forged scope, expiry, revocation, duplicate/conflict and cross-tenant reads.
- [x] 2.2 Serve versioned read-only documents; test route responses and continued absence of ingestion.
- [x] 2.3 Pin validation dependencies and run lint, artifact drift and complete Docker test suite.
## 3. Delivery
- [ ] 3.1 Validate OpenSpec strictly and publish commit; verify Actions test/publish/deploy and live revision/contracts.
- [ ] 3.2 Record evidence/limits, update roadmap/state and archive with consolidated spec validation.
