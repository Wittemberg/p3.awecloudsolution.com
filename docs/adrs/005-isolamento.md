---
adr_number: "005"
status: proposto
created: 2026-09-19
supersedes: ""
superseded_by: ""
---
# ADR 005 — Isolamento multi-tenant e evidências

## Contexto
Eventos, imagens e pessoas têm sensibilidades distintas e pertencem a clientes separados.

## Alternativas Consideradas
Banco por tenant isola melhor mas aumenta operação; tabelas compartilhadas com RLS exigem testes e controles rigorosos.

## Decisão
Propor tenant derivado de identidade, FKs compostas, RLS e políticas em serviços. Evidências com checksum, auditoria de acesso e links temporários; retenção por política validada.

## Consequências
Mais testes de autorização e gerenciamento de chaves. CPF/hash e vídeo permanecem dados sensíveis; não alegar anonimização por hash. Proibir coleta real antes de política e acesso aprovados.
