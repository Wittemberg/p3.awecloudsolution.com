# Estado atual — P3

Bootstrap concluído; aguardando início da próxima mudança do roadmap.
Histórico e tarefas: [bootstrap-platform](../openspec/changes/archive/2026-09-20-bootstrap-platform/tasks.md).
Requisitos entregues: `openspec/specs/platform-bootstrap/spec.md`.

## Entrega

Harness portátil revisão `9dbc93d105de52d855f7e0cdd4671aa97c3c8352`.
Brainstorm original preservado, revisão v0.3, PRD, TRD, cinco ADRs, viabilidade,
roadmap, inventário e runbook versionados. Aplicação é bootstrap operacional;
funcionalidades de negócio ainda não implementadas.

## Infraestrutura e automação validadas

Portainer EE 2.45.1; stack p3 ID 3 no ambiente primary ID 1; registry GHCR ID 1
existente reutilizado. Webhook de stack habilitado. Secret GitHub
PORTAINER_STACK_WEBHOOK cadastrado no environment production; variável de repositório
DEPLOY_ENABLED=true. Credencial GitHub atual possui administração; HTTP 403 anterior resolvido.

[Run 35483369209](https://github.com/Wittemberg/p3.awecloudsolution.com/actions/runs/35483369209):
test SUCCESS, publish SUCCESS, deploy SUCCESS. Disparado por workflow_dispatch em main.
O mesmo workflow está configurado para push em main.

Revisão pública comprovada: `4fe6648e860f5459dcadfda8f9c1d3958dc5e1bb`.
Imagem `ghcr.io/wittemberg/p3.awecloudsolution.com:sha-4fe6648e860f5459dcadfda8f9c1d3958dc5e1bb`.
Digest `sha256:4821119f2d22f8da9cbeff4a204b48aaa71da69293882ae9deb18c3808e2b326`.
HTTPS sem ignorar certificado: https://p3.awecloudsolution.com/api/health retornou
status ok e revisão exata. Swarm executou nova tarefa e encerrou a anterior.

## Evidências e limites

7 testes de aplicação/deploy passaram; Compose/Swarm config e OpenSpec strict válidos.
Harness: 1719 arquivos fixados, zero erros, 10 testes passaram. Imagem base fixada por
digest, transitivas em constraints.txt. Um DeprecationWarning Starlette/AnyIO conhecido.

URL secreta em `.local/portainer-stack-webhook`, permissão 600, diretório 700 e ignorado
pelo Git. Tokens administrativos não copiados ao projeto ou logs. PostgreSQL e demais
stacks preservados. Container de desenvolvimento permanece em 127.0.0.1:18003.

Sem UAT, validação visual em navegador, carga, hardware/NVR ou auditoria integral de
segurança do produto. Não confundir bootstrap disponível com plataforma comercial pronta.
Próxima mudança: M1 do roadmap — contratos de eventos, identidade e isolamento.
Documentação de encerramento usa skip ci; SHA documental pode superar a revisão em produção.
