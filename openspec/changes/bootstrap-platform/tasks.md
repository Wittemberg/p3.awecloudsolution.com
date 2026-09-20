## 1. Context and design
- [x] 1.1 Read manual, baseline and original brainstorm; preserve sources.
- [x] 1.2 Inspect infrastructure and validate GitHub SSH by initial push.
- [x] 1.3 Record brainstorm, PRD, TRD, ADR, feasibility and roadmap.

## 2. Bootstrap and delivery preparation
- [x] 2.1 Implement local status application and meaningful bootstrap tests.
- [x] 2.2 Prepare Docker image, local Compose and Swarm stack definition.
- [x] 2.3 Prepare and check GHCR workflow and detailed credentials runbook.

## 3. Verification
- [x] 3.1 Run container tests and local endpoint smoke checks.
- [x] 3.2 Validate OpenSpec strictly and inspect generated Codex integration.
- [x] 3.3 Record limitations, commit and synchronize resulting files.

## 4. External deployment completion
- [x] 4.1 Obtain administrative access and verify webhook availability (EE 2.45.1; stack webhook created and invoked).
- [ ] 4.2 Finish GitHub configuration: stack 3, existing registry 1 and webhook are ready; register production secret and enable DEPLOY_ENABLED.
- [ ] 4.3 Verify GitHub Actions run and matching live revision; archive only after required scope is complete.
