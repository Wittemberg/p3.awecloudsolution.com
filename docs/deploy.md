# Guia de GHCR, Portainer e GitHub Actions

Verificado em 2026-09-19. O bootstrap pode rodar localmente já; o deploy público
precisa de registry, stack gerenciada e webhook configurados. Não cole tokens no Git,
no chat ou em arquivos versionados. SSH de Git e autenticação GHCR são independentes.

## Estado realizado

Stack `p3` (ID 3), ambiente `primary` (ID 1), registry GHCR autenticado existente
(ID 1) reutilizado. Webhook habilitado; URL disponível somente no arquivo local
`.local/portainer-stack-webhook` (600, fora do Git). HTTPS e revisão pública validados.
Falta cadastrar secret/variável no GitHub e provar promoção automática de uma nova imagem.
A tentativa com o token fornecido retornou HTTP 403: identidade lucaslyrab-rgb sem
administração do repositório. Usar credencial de Wittemberg ou conta autorizada;
aumentar escopos de um token não concede acesso que sua conta não possui.
Os passos 3–5 abaixo permanecem como procedimento de reprodução; não recriar os recursos.

## 1. Edição atual e acesso

O usuário atualizou o servidor de CE para **EE**. Inspeção confirmou a imagem
`portainer/portainer-ee` e a API pública informou versão **2.45.1**. O caminho de
stack webhook planejado pode prosseguir após conferir licença e acesso autenticado.
[Fonte do requisito de edição: webhooks de stack](https://docs.portainer.io/user/docker/stacks/webhooks).

Para automação, gerar um access token no perfil do usuário administrativo do Portainer.
Guardar o valor em arquivo local fora do Git com permissão 600 e informar somente
seu caminho. Não enviar senha/token no chat. Esse token permite configurar a stack;
o workflow usará apenas a URL secreta do webhook. Revogar o token de preparação
quando não for mais necessário. DEPLOY_ENABLED continua desabilitado até a validação.

## 2. Publicação no GitHub Actions

O workflow `.github/workflows/delivery.yml` testa PRs e main. Em main, publica:
`ghcr.io/wittemberg/p3.awecloudsolution.com:sha-<commit-completo>` e `:main`.
Usa `GITHUB_TOKEN` fornecido automaticamente pelo Actions com `packages: write` e
`contents: read`. Não criar PAT de escrita nem cadastrar manualmente GITHUB_TOKEN.
Em Settings → Actions → General, permitir execução do workflow e actions necessárias;
políticas da organização não podem bloquear a permissão de publicação.
O pacote é associado ao repositório pelo workflow e label OCI do Dockerfile.
[Fonte: autenticação GHCR](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry).

## 3. Criar token de leitura para o Portainer

1. Entrar no GitHub como **Wittemberg** (o login do registry é username, não email).
2. Avatar → Settings → Developer settings → Personal access tokens → Tokens (classic).
3. Generate new token (classic); nome `portainer-p3-ghcr-read`; definir expiração e
   lembrete de rotação compatível com a operação.
4. Selecionar somente `read:packages` para pull. Não usar `write:packages` ou
   `delete:packages` neste consumidor. Se houver SSO organizacional, autorizar o token.
5. Gerar, guardar em cofre e inserir diretamente no Portainer. Não usar chave SSH
   como senha do registry. Token fine-grained não substitui o classic nesse fluxo documentado.
6. Na página do pacote, conferir acesso do usuário e vínculo/permissões do repositório.
   Para pacote privado, a identidade do token precisa ter leitura; token não cria acesso.
7. Rotação: emitir novo token, atualizar registry, testar pull e depois revogar antigo.

## 4. Cadastrar Registry no Portainer

1. Abrir https://wit-portainer.awecloudsolution.com e autenticar como administrador.
2. Registries → Add registry → Custom registry.
3. Name: `GHCR Wittemberg`; Registry URL: `ghcr.io` (sem caminho da imagem).
4. Ativar Authentication; Username: `Wittemberg`; Password: PAT classic de leitura.
5. Salvar; disponibilizar o registry ao ambiente Swarm e às equipes autorizadas
   conforme os controles da edição instalada. Validar pull do pacote privado na stack.
6. Se falhar: conferir expiração, acesso ao pacote, escopo e associação ao ambiente;
   não tornar a imagem pública apenas para esconder problema de autenticação.
[Fonte: registry customizado](https://docs.portainer.io/admin/registries/add/custom).

## 5. Criar a stack gerenciada

Depois de um build/publicação bem-sucedido:

1. Selecionar ambiente Swarm → Stacks → Add stack; nome `p3`.
2. Usar Web editor e colar `deploy/stack.yml`, mantendo imagem GHCR e rede externa `interna`.
   O editor facilita o fluxo de webhook documentado; alterações futuras do YAML precisam
   ser sincronizadas no Portainer, pois o webhook atualiza imagem, não busca Git automaticamente.
3. Em Environment variables, criar `IMAGE_TAG=sha-<SHA-completo-publicado>`.
4. Garantir acesso ao registry privado cadastrado e executar Deploy the stack.
5. Conferir tarefa saudável, router `p3`, certificado válido e
   `https://p3.awecloudsolution.com/api/health`. `revision` deve ser o SHA escolhido.
6. Não publicar porta do app no host: Traefik chega pela overlay na porta 8000.
   Não adicionar PostgreSQL novo nem copiar senha do banco compartilhado.

## 6. Habilitar webhook e configurar o GitHub

Na edição compatível: Stacks → p3 → Editor → Webhooks → **Create a stack webhook**.
Copiar URL HTTPS como segredo. Esse endereço permite solicitar deploy; tratá-lo como token.

No repositório → Settings → Environments → New environment → `production`:
restringir branches a main; definir revisores somente se essa for a política desejada
(revisor obrigatório interrompe a atualização totalmente automática).
Em Environment secrets, cadastrar:

| Nome | Conteúdo |
|---|---|
| `PORTAINER_STACK_WEBHOOK` | URL completa copiada, sem query string |

Em Settings → Secrets and variables → Actions → Variables (nível **repositório**):

| Nome | Valor inicial / final |
|---|---|
| `DEPLOY_ENABLED` | `false` durante preparação; `true` após stack/registry/webhook validados |

A variável deve ser de repositório porque condiciona a criação do job. O token de
leitura do GHCR fica no Portainer, não é necessário como secret no Actions.

## 7. Provar atualização automática

1. Com stack saudável e secret cadastrado, colocar DEPLOY_ENABLED=true.
2. Fazer push de mudança autorizada em main, ou Actions → Test, publish and deploy → Run workflow.
3. Test deve passar; Publish envia ambas as tags; Deploy faz POST com
   `IMAGE_TAG=sha-<commit>` para substituir a variável de imagem da stack.
4. O script aguarda até cinco minutos pela revisão exata em `/api/health`; resposta
   de webhook isolada não aprova deploy. Se a edição instalada não aplicar variáveis
   conforme documentação, o teste de revision falha e a configuração deve ser corrigida.
5. Conferir Portainer: serviço p3_app 1/1, imagem/revision esperadas e logs sem erro.
6. Registrar URL do run, SHA/digest, horário e resultado. Esta prova ainda está pendente.

## 8. Rollback e diagnóstico

Anotar tag/digest anterior antes de promover. Em Portainer, alterar IMAGE_TAG para
`sha-<commit-anterior-validado>` e atualizar stack puxando a imagem; conferir revision.
Desativar DEPLOY_ENABLED durante investigação para impedir promoção concorrente.
Swarm também está configurado para rollback automático quando a tarefa falha no
monitoramento, mas falha de semântica exige rollback operacional. Não reescrever tags
SHA. Não apagar imagens anteriores enquanto forem candidatas a rollback.

401/403 GHCR: escopo/acesso/token. Imagem inexistente: validar Publish e nome minúsculo.
Webhook ausente: conferir edição. 404/502 público: conferir labels/overlay/porta/TLS.
Deploy sem mudança: verificar IMAGE_TAG e tasks; POST não garante convergência.
Timeout de POST: consultar stack antes de repetir; solicitação pode ter sido aceita.
Rollback de imagem não reverte schema; bootstrap não possui migrações.

## Fontes adicionais

[Publicação pelo Actions](https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images),
[labels Traefik Swarm](https://doc.traefik.io/traefik/reference/routing-configuration/other-providers/swarm/).
