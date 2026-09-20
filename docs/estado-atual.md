# Estado atual — P3

M0 e M1 concluídos. Mudança ativa: `m2-screencam-poc` (implementação; 6/16 tarefas).
Histórico: `openspec/changes/archive/`; requisitos em `openspec/specs/`.
Marco em andamento: M2 — PoC ScreenCam em Linux Mint e NVR reais.

## M1 entregue

Event Protocol 0.1.0, catálogo de 14 tipos, JSON Schema Draft 2020-12, OpenAPI 3.1,
exemplos, verificador local e política executável sintética de identidade/replay.
[Protocolo](contracts/event-protocol-0.1.0.md), [identidade](contracts/integration-identity.md),
[ADR-006](adrs/006-contrato-m1.md).

Rotas públicas somente leitura: `/api/contracts/0.1.0/{document}` para
`event.schema.json`, `openapi.json`, `catalog.json` e `examples.json`.
Oráculo em scripts/event_conformance.py; não é backend produtivo.
POST de ingestão continua 404; persistência/outbox/credenciais reais são M3.

## Evidências

83 testes passaram: schema/OpenAPI, 14 tipos, payloads inválidos, grants compostos,
tenant forjado, leituras cruzadas, expiração/revogação/rotação, duplicidade/conflito,
CLI sem ecoar dados, rotas estáticas e regressões do bootstrap/deploy.
Ruff, artifact drift, Docker build, OpenSpec strict e smoke local aprovados.
Transitivas fixadas em constraints.txt. Um warning Starlette/AnyIO conhecido.

[Run 35484533521](https://github.com/Wittemberg/p3.awecloudsolution.com/actions/runs/35484533521):
test/publish/deploy SUCCESS, disparado por push em main.
Revisão pública comprovada: `e8944f40a654febb21c0aa64f8d9a233c17d71bb`.
Health OK por HTTPS válido e quatro documentos públicos comparados por igualdade
JSON com o repositório. O commit posterior de encerramento é documental, com skip ci;
a revisão documental pode ser posterior à imagem implantada.

## Infraestrutura e limites

Portainer EE 2.45.1; stack p3 ID 3, primary ID 1, registry GHCR ID 1. Webhook e
GitHub production/PORTAINER_STACK_WEBHOOK configurados, DEPLOY_ENABLED=true.
Tokens fora do Git; URL secreta em .local/portainer-stack-webhook (600).
Container local permanece em 127.0.0.1:18003. Sem alterações em PostgreSQL/dados reais.
Testes sintéticos não demonstram durabilidade, concorrência, RLS ou eficácia comercial.
Sem UAT/carga/hardware/NVR. Contrato 0.1.0 congelado após entrega; mudanças incompatíveis
exigem versão nova, fixtures e migração do integrador.

## Próximo trabalho

M2: inventário/runbook em [ScreenCam](screencam-m2.md). Configuração privada e preflight
em scripts/screencam_config.py; supervisor em scripts/screencam_capture.py e serviço
de usuário preparados. 48 testes novos, 131 totais aprovados no Docker; Ruff e
contratos sem divergência. Probes X11 simulados; supervisor testado com subprocessos
reais sintéticos. Unidade systemd passou em `systemd-analyze --user verify`, sem
instalação/ativação. Laboratório Xvfb/FFmpeg/MediaMTX em containers passou: frames
decodificados antes/depois de interrupção, retomada observada em 4,515 s e matriz
de negação de acesso aprovada. [Evidência sanitizada](screencam-lab-evidence.json).
OpenSpec strict: 3 itens aprovados. Recursos temporários removidos pelo executor.
Próximo: coleta de métricas, stack de PoC e ensaio de serviço no Mint.
O kit M2 não foi ativado na máquina real e não conclui a qualificação NVR.

O usuário ainda preparará o Linux Mint (versão, X11/Wayland, CPU/RAM a confirmar).
NVR disponível: AITEK SIGMA-N210, firmware a confirmar; ambos dependem de VPN para
acesso remoto. VPN ainda não instalada/configurada. Kit e laboratório podem avançar.
Tarefas canônicas em `openspec/changes/m2-screencam-poc/tasks.md`. Validar captura,
consumo, reconexão e recuperação histórica com dados sintéticos e política de acesso.
Não iniciar coleta de clientes antes de retenção e permissões definidas.
