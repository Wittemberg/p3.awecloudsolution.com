## Context
Aplicação inexistente; v0.2 amplo; Swarm único nó; Portainer inicialmente CE, atualizado pelo usuário para EE 2.45.1.

## Goals / Non-Goals
Entregar base local e documentação; preparar CI/CD. Não implementar ingestão real,
login fictício, gravação de vídeo ou contratação de licença.

## Decisions
Base FastAPI mínima própria; runtime container; dependências diretas fixadas; usuário
não root. Stack usa rede interna e labels Swarm do Traefik. PostgreSQL permanece
intocado. Docs globais referenciadas pelo OpenSpec; snapshot harness portátil preservado.
Actions publica imagem de commit e só chama webhook se DEPLOY_ENABLED=true.
Valida revision servida, porque resposta de webhook não comprova rollout.

## Risks / Trade-offs
EE instalada e acesso administrativo verificado; stack e webhook criados/testados.
Ativação automática aguarda secret e variável GitHub; provar promoção de nova revisão. Único nó sem HA. Base fixada por digest e transitivas em constraints.txt; auditoria de dependências antes de produção.

## Migration Plan
Sem persistência de produto. Local: docker compose up/down. Produção futura: Portainer
cria stack pelo arquivo; rollback para IMAGE_TAG de commit anterior. Não migrar banco.

## Open Questions
Credencial API GitHub ou configuração manual dos secrets/variables; volumetria e NVR do piloto; retenção e orçamento.
