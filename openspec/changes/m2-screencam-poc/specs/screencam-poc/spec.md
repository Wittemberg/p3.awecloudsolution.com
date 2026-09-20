# ScreenCam PoC

## Purpose

Qualificar captura de tela e vídeo histórico para auditoria, com diagnóstico de falhas
e evidências mensuráveis no Linux Mint e no NVR selecionados para a prova.

## ADDED Requirements

### Requirement: Explicit capture boundary
The capture tool SHALL require an explicit authorized screen region and configuration,
produce H.264 over RTSP, and reject invalid configuration before starting capture.

#### Scenario: Capture a synthetic region on Mint
- **WHEN** an operator selects an X11 region displaying synthetic content
- **THEN** the receiving client displays that region with readable test markers
- **AND** the report identifies display session, dimensions, FPS and encoder settings

#### Scenario: Unsupported session or invalid region
- **WHEN** the session is Wayland or the requested region is missing or invalid
- **THEN** capture does not start and a diagnostic identifies the corrective action
- **AND** the tool does not silently capture the whole desktop

### Requirement: Private access to video
The PoC SHALL restrict publishing and reading to authorized peers and SHALL keep
credentials and captured media outside version control and diagnostic output.

#### Scenario: Unauthorized reader or publisher
- **WHEN** an unauthenticated peer tries to read or publish a protected path
- **THEN** the server rejects access

#### Scenario: Remote administration
- **WHEN** the Mint machine is accessed remotely
- **THEN** access uses an authorized private network path without public RTSP exposure

### Requirement: Recovery and observable health
The capture service SHALL recover from transient transport failures with bounded
backoff, survive process restart with persisted configuration, and report stalled
video separately from configuration and display failures.

#### Scenario: Transport outage
- **WHEN** the RTSP server becomes unavailable and later returns
- **THEN** the service retries without a busy loop and resumes video automatically
- **AND** the report records outage and recovery timestamps and any recording gap

#### Scenario: Configuration survives restart
- **WHEN** the service restarts
- **THEN** it reloads the configured region and target without changing capture scope

### Requirement: Real NVR recording and retrieval
M2 qualification SHALL demonstrate recording and historical retrieval on a real NVR
fed by a real Linux Mint capture, with model, firmware, timestamps and compatibility
recorded separately for RTSP, ONVIF and discovery.

#### Scenario: Retrieve after capture ends
- **WHEN** a marked synthetic sequence has been recorded and the publisher is stopped
- **THEN** the operator retrieves a historical interval containing the expected markers
- **AND** records requested versus actual start/end time, drift and retrieval method

#### Scenario: Missing interval or unsupported capability
- **WHEN** an interval is unavailable or a protocol feature is unsupported
- **THEN** the result identifies that limitation explicitly without treating live playback as history

### Requirement: Measured qualification
The qualification report SHALL record CPU, RAM, FPS, bitrate, dropped frames,
latency, stability duration and reconnection behavior with workload and measurement
method, distinguishing laboratory evidence from real hardware evidence.

#### Scenario: Hardware is not available
- **WHEN** only synthetic container tests are executable
- **THEN** those results are labeled laboratory evidence and M2 remains incomplete

#### Scenario: Hardware test completes
- **WHEN** the real capture and NVR test campaign ends
- **THEN** measured results and limitations support a recorded compatibility decision
- **AND** unmeasured fields remain explicitly inconclusive rather than inferred successes
