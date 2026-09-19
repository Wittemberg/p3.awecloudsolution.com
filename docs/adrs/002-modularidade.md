---
adr_number: "002"
status: proposto
created: 2026-09-19
supersedes: ""
superseded_by: ""
---
# ADR 002 — Monólito modular e PostgreSQL

## Contexto
Muitos domínios conceituais e host com 4 GiB, sem volume medido.

## Alternativas Consideradas
Microserviços isolam escala mas ampliam operação; monólito reduz custo inicial; broker específico pode ser extraído depois.

## Decisão
Propor FastAPI modular e PostgreSQL com outbox, separando worker quando surgir processamento assíncrono.

## Consequências
Menos serviços; exige limites claros entre módulos e disciplina transacional. Reavaliar com saturação medida, não com antecipação.
