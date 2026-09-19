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

## Limites e próximo passo

Portainer CE observado; stack webhook solicitado requer BE conforme fonte oficial
referenciada em [deploy.md](deploy.md). Não houve troca de edição, contratação,
criação de stack pública ou alteração de PostgreSQL/Traefik/serviços existentes.
Credencial administrativa Portainer, registry GHCR e secret de webhook não fornecidos.
Workflow preparado para publicar com GITHUB_TOKEN; deploy só com DEPLOY_ENABLED=true.
Execução remota de Actions e publicação precisam ser confirmadas após push.

Para continuar: resolver BE ou alternativa CE, seguir runbook de credenciais/stack,
verificar release pública por SHA. Não arquivar mudança antes das tarefas pendentes.
Depois, detalhar M1 no roadmap com contratos de domínio e cenários de isolamento.
