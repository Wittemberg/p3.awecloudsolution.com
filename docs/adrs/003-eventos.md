---
adr_number: "003"
status: proposto
created: 2026-09-19
supersedes: ""
superseded_by: ""
---
# ADR 003 — Identidade, tempo e durabilidade

## Contexto
Offline, retry e múltiplas fontes exigem rastreabilidade; envelope original ainda é proposta.

## Alternativas Consideradas
Ordenação por chegada é simples mas perde semântica; event time preserva fato mas precisa qualificar clock.

## Decisão
UUID como identificador opaco; tenant + event_id único; conteúdo divergente gera conflito. occurred_at com timezone, received_at pelo servidor, sequência por origem e decimal textual para valores. ACK somente após commit durável.

## Consequências
Processamento at-least-once exige efeitos idempotentes. Replay preserva fato, gera projeções versionadas e não duplica ocorrência. Eventos tardios podem revisar projeção com histórico.
