---
adr_number: "001"
status: aceito
created: 2026-09-19
supersedes: ""
superseded_by: ""
---
# ADR 001 — Swarm, Portainer e GHCR

## Contexto
Usuário exige stack Portainer no Swarm existente e distribuição GHCR.

## Alternativas Consideradas
Swarm existente reduz mudança operacional; Kubernetes aumentaria escopo; Compose apenas atende desenvolvimento.

## Decisão
Usar Docker/Swarm e Portainer para produção, GHCR para imagem e Actions para build. Webhook de stack só será habilitado com edição compatível e acesso autenticado.

## Consequências
CE observado impede concluir o caminho BE agora. Não há autorização implícita para contratar licença ou substituir Portainer. Manter bootstrap local e guia concreto.
