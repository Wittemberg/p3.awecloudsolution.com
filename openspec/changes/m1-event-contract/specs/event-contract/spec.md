## Purpose
Enable ERP integrators to validate synthetic events and identity boundaries against a versioned contract before persistent ingestion is implemented.

## ADDED Requirements

### Requirement: Versioned event contract rejects ambiguous facts
The project SHALL publish protocol 0.1.0, an explicit initial catalog, JSON Schema and OpenAPI for future ingestion, with one synthetic example per supported event type.

#### Scenario: Valid event
- **WHEN** an integrator validates a supported event with required fields
- **THEN** the local checker accepts it and identifies protocol 0.1.0

#### Scenario: Invalid or ambiguous event
- **WHEN** an event contains unknown fields/types/version, a numeric monetary value, an invalid UUID or a timestamp without timezone
- **THEN** the checker rejects it without echoing the payload or credentials

#### Scenario: Server-owned fields
- **WHEN** an event supplies received_at or an inferred risk score
- **THEN** the input schema rejects the server-owned field

### Requirement: Identity determines permitted scope
The project SHALL specify bearer integration credentials whose server-owned tenant and exact organization/store/terminal/source grants govern ingestion and reads, and SHALL provide synthetic conformance tests for those rules.

#### Scenario: Forged tenant or location
- **WHEN** an authenticated fixture attempts another tenant or an ungranted location combination
- **THEN** the reference policy denies it before inspecting deduplication state

#### Scenario: Invalid credential
- **WHEN** a fixture credential is missing, wrong, expired or revoked
- **THEN** the reference policy returns the same unauthorized outcome

#### Scenario: Read another scope
- **WHEN** a fixture attempts to read an event outside its credential grants
- **THEN** the reference policy returns not found without revealing another tenant's event

### Requirement: Replay has explicit idempotency semantics
The contract SHALL define uniqueness by tenant and event_id, stable original receipt for exact retries, content conflict for changed facts, and persistent ACK requirements for the future ingestion service.

#### Scenario: Exact retry and conflicting reuse
- **WHEN** the same authorized fixture event is submitted twice and then modified with the same ID
- **THEN** the reference reports accepted, duplicate with original receipt, and conflict respectively

#### Scenario: Independent tenants
- **WHEN** two authorized tenants use the same event UUID
- **THEN** neither is treated as a duplicate of the other

### Requirement: Contract delivery does not pretend ingestion is live
The running service SHALL expose read-only versioned contract documents and SHALL leave business ingestion unavailable until its persistent implementation is delivered.

#### Scenario: Discover contract
- **WHEN** an integrator retrieves the versioned schema or OpenAPI
- **THEN** they receive valid machine-readable documents explicitly labeled as a contract for future ingestion

#### Scenario: Production does not acknowledge synthetic ingestion
- **WHEN** a caller posts to /api/v1/events on the current runtime
- **THEN** no event is accepted or stored
- **AND** documentation distinguishes reference conformance from durability, concurrency and end-to-end tenant isolation of a real backend
