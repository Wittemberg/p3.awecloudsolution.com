# Estado atual — P3

Atualizado: 2026-09-19. Mudança ativa: [bootstrap-platform](../openspec/changes/bootstrap-platform/).
Tarefas canônicas: [tasks.md](../openspec/changes/bootstrap-platform/tasks.md).

## Entregue localmente

Primeiro commit `4bcffdb` enviado a origin/main: SSH validado com chave existente
chavewit, sem exposição do conteúdo. Harness portátil fixado na revisão
`9dbc93d105de52d855f7e0cdd4671aa97c3c8352`. Brainstorm v0.2 preservado.
Novo brainstorm, PRD, TRD, cinco ADRs, viabilidade, roadmap, inventário e runbook criados.
Base FastAPI em container disponível somente em `http://127.0.0.1:18003`.
Produto de negócio ainda não implementado; documentos propostos não representam UAT.

## Evidências

- Docker build/test: 7 testes passaram (4 HTTP + 3 segurança/convergência do deploy).
  Um DeprecationWarning Starlette/AnyIO registrado; sem falha. Compose local executado; container saudável.
- `/`, `/api/hello`, `/api/health`: HTTP 200, health status ok, stage bootstrap.
- Compose e Swarm YAML aceitos pelos respectivos comandos Docker config.
- OpenSpec CLI 1.13.1 realmente executada em Node 22 container, telemetria desativada.
  init --tools codex --profile core gerou seis skills em `.agents/skills/` e config.
  `validate bootstrap-platform --strict`: válido.
- Harness: 23 fontes + bundles, 1719 arquivos fixados, zero erros; 10 testes passaram.
- SHA da action checkout v4.2.2 confirmado via git ls-remote.
- Imagem base fixada por digest e dependências resolvidas em constraints.txt.
- Verificação visual em navegador, carga, hardware/NVR, segurança integral e UAT não executados.

## Implantação pública verificada

Portainer EE 2.45.1 acessado com token fornecido por caminho local protegido.
Stack `p3` ID 3 criada pelo Portainer no ambiente `primary` ID 1; registry GHCR ID 1
já existente reutilizado. Webhook de stack habilitado e teste POST aceito.
Serviço `p3_app` executa a imagem publicada pelo Actions:
`ghcr.io/wittemberg/p3.awecloudsolution.com:sha-35f6d8263b33988048b2fa4601617f29fbf03815`
com digest `sha256:fb3a00bf43be736fea76104c229a300cf6f31fe5a4ccf13df001a8a9aee4ede0`.
HTTPS validado sem ignorar certificado: https://p3.awecloudsolution.com/api/health
retorna status ok e revision `35f6d8263b33988048b2fa4601617f29fbf03815`.
Na primeira consulta o certificado ainda estava em emissão; nova consulta passou.

URL secreta do webhook em `.local/portainer-stack-webhook`, permissão 600, diretório
700 e ignorado pelo Git. Nunca incluir conteúdo em documentação/logs.
O token administrativo Portainer não foi copiado ao projeto.

## Limites e próximo passo

Ainda faltam secret `PORTAINER_STACK_WEBHOOK` no environment `production` e variável
de repositório `DEPLOY_ENABLED=true` no GitHub. O token fornecido autentica como
`lucaslyrab-rgb`, com apenas leitura no repositório; criar environment retornou HTTP 403.
Nenhum secret/variável foi alterado. É necessário token de identidade com acesso
administrativo ao repositório. A chave SSH permite push, não configuração pela API.
Seguir [deploy.md](deploy.md), ou fornecer apenas o caminho local de uma credencial
GitHub com permissão suficiente. Depois executar o workflow e verificar **nova** revisão.
Teste do webhook com a mesma imagem prova acionamento, não a promoção de uma release nova.

Run de build/publicação já concluído: [35463803288](https://github.com/Wittemberg/p3.awecloudsolution.com/actions/runs/35463803288):
test SUCCESS, publish SUCCESS e deploy SKIPPED na configuração anterior.
Não arquivar até finalizar a prova de atualização automática. Sem alterações em
PostgreSQL, stacks existentes ou dados de clientes. Produto funcional segue no roadmap.
