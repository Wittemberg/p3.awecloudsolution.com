# Estado atual — P3

M0 e M1 concluídos. Mudança ativa: `m2-screencam-poc` (12/16 tarefas; fechamento em revisão).
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
M1 sem UAT/carga; ensaio de hardware M2 relatado abaixo. Contrato 0.1.0 congelado após entrega; mudanças incompatíveis
exigem versão nova, fixtures e migração do integrador.

## M2 — qualificação e revisão de fechamento

Kit X11/FFmpeg, supervisor, configuração privada, laboratório isolado e template
Portainer preparados. O template da stack ScreenCam não foi implantado.
Última entrega publicada registrada: `acab67b212e996b498d53bab450393239faaf71b`,
run 35487103922 test/publish/deploy SUCCESS e revisão conferida no health HTTPS.
Esta revisão não verificou novamente o deploy público.

Ensaio real concluído no Linux Mint 21 + AiTek SIGMA-N210: 95,5 min contínuos,
57.470 frames a 10.00 FPS, três encerramentos com retomada automática e backoff exponencial,
RTSP Custom1/H.264 Baseline com repeat-headers=1 e dump_extra.
Canal D01 (câmera IP física) e D02 (ScreenCam do Linux Mint) operando simultaneamente.
Histórico de gravação extraído do NVR via protocolo Sofia NetIP (opcodes 1440/1424) e decodificado
com sucesso pelo FFmpeg. Relatório e evidências detalhadas em docs/screencam-m2.md e
docs/screencam-nvr-retrieval-evidence.json. Skill de operação registrada em .agents/skills/nvr-aitek-sigma/.

A mudança OpenSpec m2-screencam-poc foi finalizada (16/16 tarefas), main spec sincronizada em
openspec/specs/screencam-poc/spec.md e arquivada em openspec/changes/archive/2026-10-08-m2-screencam-poc/.

Verificação local: build de testes aprovado (pytest 140/140, Ruff e checagem de contratos estritos).
Próximo trabalho: M3 — Ingestão durável de eventos, outbox, persistência PostgreSQL e correlação com metadados de CFTV.
Credenciais e mídia privadas em `.local/`, nunca versionadas.

