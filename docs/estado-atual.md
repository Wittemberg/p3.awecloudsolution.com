# Estado atual — P3

Mudança ativa: [m1-event-contract](../openspec/changes/m1-event-contract/tasks.md).
M0 arquivado; infraestrutura e deploy automático funcionais.

## M1 entregue localmente

Event Protocol 0.1.0, catálogo de 14 tipos, JSON Schema Draft 2020-12, OpenAPI 3.1 e
exemplos sintéticos. [Protocolo](contracts/event-protocol-0.1.0.md),
[identidade](contracts/integration-identity.md), [ADR-006](adrs/006-contrato-m1.md).
Rotas somente leitura em /api/contracts/0.1.0/{document}.
Oráculo de conformidade em scripts/event_conformance.py; não é backend produtivo.
POST de ingestão continua 404; persistência, outbox e credenciais reais pertencem ao M3.

## Evidências

83 testes locais passaram, incluindo schema/OpenAPI, 14 tipos, erros, isolamento,
rotação/revogação, replay, conflito e regressão HTTP/deploy. Ruff e drift de artefatos
passaram. Transitivas fixadas em constraints.txt. Warning Starlette/AnyIO conhecido.
Validação final OpenSpec, CI/deploy e revisão pública M1 ainda em execução.

## Infraestrutura preservada

Portainer EE 2.45.1; stack p3 ID 3, primary ID 1, registry GHCR ID 1. Webhook e
GitHub production/PORTAINER_STACK_WEBHOOK configurados, DEPLOY_ENABLED=true.
Tokens fora do Git; URL secreta em .local/portainer-stack-webhook (600).
Baseline M0 implantada: revisão 4fe6648, run 35483369209.
Nenhuma alteração em PostgreSQL ou credenciais de clientes. Sem UAT/carga/hardware.

## Continuação

Concluir tarefas de entrega M1 e arquivar somente com evidência remota.
Depois M2: ScreenCam em Linux Mint e NVR reais; é necessário identificar equipamento
e disponibilidade. Não iniciar coleta real sem política de acesso e retenção.
