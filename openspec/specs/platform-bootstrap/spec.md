# platform-bootstrap Specification

## Purpose
Provide a verifiable operational foundation for P3, with honest availability status,
traceable project decisions and automated image delivery to the managed Swarm stack.

## Requirements

### Requirement: Local bootstrap exposes honest operational status
The system SHALL expose a local home page, hello endpoint and health endpoint without database or AI credentials.

#### Scenario: Local installation succeeds
- **WHEN** the operator builds and starts the local container
- **THEN** `/`, `/api/hello` and `/api/health` respond successfully
- **AND** the page states that business functionality is not available yet

#### Scenario: Release identity is inspected
- **WHEN** the operator requests health
- **THEN** the response contains the running revision and bootstrap stage

### Requirement: Delivery preparation preserves existing infrastructure
The project SHALL provide a Swarm stack definition and a guarded GHCR publication workflow without changing existing services.

#### Scenario: Deployment credentials are absent
- **WHEN** deployment is not enabled
- **THEN** CI can test and publish without calling Portainer
- **AND** documentation identifies the missing Portainer edition and credential requirements

#### Scenario: Deployment is enabled
- **WHEN** the configured webhook accepts a release request
- **THEN** the workflow checks the public health revision against that release before reporting success

### Requirement: Project decisions are traceable
The project SHALL preserve the original brainstorm, harness revision and distinct product, architecture, operational and change documentation.

#### Scenario: Another contributor resumes work
- **WHEN** they read AGENTS and the current state
- **THEN** they can identify the active change, executed checks and external blockers
