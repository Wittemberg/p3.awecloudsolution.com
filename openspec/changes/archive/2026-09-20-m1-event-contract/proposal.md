# M1 — Contrato de eventos e identidade

## Why
Integradores precisam de um contrato inequívoco antes de enviar eventos de PDV.
O brainstorm ainda mistura nomes, números monetários e identidade informada pelo cliente.

## What Changes
- Publicar Event Protocol 0.1.0, catálogo inicial, JSON Schema e OpenAPI 3.1.
- Definir credenciais, escopos tenant/loja/terminal/origem, rotação e revogação.
- Entregar verificador local e modelo de conformidade para testar payload, autorização,
  deduplicação e conflitos com fixtures sintéticas.
- Disponibilizar contratos em rotas somente leitura e verificar estabilidade em CI.
- Manter POST de ingestão ausente no runtime: durabilidade, outbox e provisionamento
  persistente de credenciais pertencem ao M3. OpenAPI de ingestão é contrato futuro explícito.

## Capabilities
### New Capabilities
- `event-contract`: protocolo versionado e conformidade local de eventos e identidades.
### Modified Capabilities
Nenhuma; endpoints de bootstrap e comportamento de disponibilidade são preservados.

## Impact
Arquivos de contrato, documentação, CLI local, testes e rotas estáticas de contrato.
Dependências de validação somente no ambiente de testes/ferramentas. Sem migração,
credenciais reais de integração, alterações de banco ou dados de clientes.
Autorização de executar M1 segue o pedido do usuário e o manual §4.3; o planejamento
precede a implementação sem criar um novo portão de aprovação para o trabalho autorizado.
