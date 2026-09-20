# Identidade de integração — contrato M1

Escopo: credencial máquina-a-máquina do ERP/conector; login de pessoas/OIDC é outro
contrato. M1 entrega política e provas sintéticas, não cadastro produtivo de identidades.

## Registro autoritativo futuro

Servidor persiste credential_id, integration_id estável, tenant_id, grants exatos
(organization_id, store_id, terminal_id, source_id), permissions (events:write e/ou
events:read), token_hash, expires_at e revoked_at/estado. Identificadores do registro
vêm de provisionamento administrativo, nunca do payload. Default deny: grant vazio,
permissão ausente ou combinação não cadastrada nega acesso.

`source_id` representa stream lógico do conector; registro garante pertencimento à
loja/terminal/organização do tenant. Não usar listas independentes de lojas e terminais:
a combinação store-2/pos-1 pode ser indevida mesmo se cada ID existir em algum grant.
Payload declara tenant somente para detectar erro de roteamento; identidade autenticada
é a autoridade. Leituras também filtram tenant/grant e não revelam registros alheios.

## Emissão, armazenamento e rotação planejados

Gerar segredo opaco com pelo menos 256 bits de entropia via CSPRNG e entregá-lo uma vez
por canal seguro. Nunca embutir token em URL; TLS obrigatório. Persistir somente hash
SHA-256 do token aleatório de alta entropia e comparar em tempo constante. Essa política
não serve para senhas humanas, que exigem KDF próprio. Armazenar token no edge em secret
ou arquivo 600, limitar leitura ao serviço; não incluir em eventos, prints ou telemetria.

Expiração obrigatória; proposta operacional de 90 dias a validar antes do piloto.
Rotação emite credential_id novo com integration_id/tenant/grants preservados; permitir
sobreposição curta explicitamente configurada (proposta: até 24 h), testar a nova e
revogar a antiga. Eventos retidos usam o token novo sem mudar event_id/payload.
Revogação invalida também consultas/retries imediatamente após propagação definida
no M3; cache não pode ignorar revogação indefinidamente. Auditar emissão, escopo, uso,
revogação e operador administrativo, sem guardar o segredo.

## Garantias verificadas no M1 e limites

O modelo local recebe registros sintéticos explicitamente e testa hash incorreto,
credencial ausente/expirada/revogada, escopo forjado, tenant cruzado, grants compostos,
permissões separadas e rotação com idempotência. Não expõe endpoints HTTP, não cria
usuários de teste em produção e não depende do token administrativo do Portainer/GitHub.

Persistência de credenciais, rate limits, auditoria real, integridade de cadastros,
RLS e concorrência entre requisições serão implementados/testados no M3. Isolamento
no oráculo prova política; não prova isolamento de um banco ainda inexistente.
