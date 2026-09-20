---
adr_number: "006"
status: aceito
created: 2026-09-20
supersedes: ""
superseded_by: ""
---
# ADR 006 — Contrato preliminar e conformidade antes da ingestão

## Contexto
M1 autorizado pelo usuário para formalizar eventos/identidade antes do núcleo durável M3.
Brainstorm v0.2 é contexto amplo; ADR-003/005 propõem garantias que precisam de contrato.

## Alternativas Consideradas
- Implementar ingestão persistente já: anteciparia M3 e a decisão de retenção/infra.
- Apenas Markdown: não provaria estrutura, tipagem ou cenários negativos.
- Contrato versionado com oráculo sintético: valida regras de integração e mantém
  limites explícitos de persistência e operação.

## Decisão
Adotar protocolo 0.1.0, JSON Schema 2020-12 e OpenAPI 3.1. Catálogo limitado a 14 fatos
operacionais, dinheiro decimal textual BRL, UUIDv4 e horários com milissegundos/fuso.
Concessões exatas de escopo e tenant da credencial, hash do token aleatório e segregação
de leitura/escrita. Modelo local de referência para replay/identidade; rotas públicas
somente leitura para documentos. A API de ingestão continua indisponível no M1.

## Consequências
Artefatos e fixtures reproduzíveis, proteção contra contratos ambíguos e nenhum ACK
falso. A restrição inicial exige novas versões para outros eventos/moedas. Testes
sintéticos não demonstram durabilidade, controle concorrente, RLS ou cadastro real;
essas provas permanecem obrigatórias no M3. ADRs 003/005 continuam propostas globais,
com decisões de wire format específicas consolidadas aqui para o M1.
