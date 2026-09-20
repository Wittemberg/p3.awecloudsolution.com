# Event Protocol 0.1.0 — M1

Status: contrato inicial implementado e testável localmente. **A API de ingestão não
está disponível em produção.** A implementação persistente será M3. PRD US01/US04;
[ADR-006](../adrs/006-contrato-m1.md); [identidade](integration-identity.md).

## Artefatos e fonte de verdade

- [JSON Schema](../../app/contracts/v0_1_0/event.schema.json), Draft 2020-12.
- [OpenAPI](../../app/contracts/v0_1_0/openapi.json), 3.1.0; servidor example.invalid
  deliberado, operações marcadas planned-m3; não confundir com /openapi.json do runtime.
- [Catálogo](../../app/contracts/v0_1_0/catalog.json) e [14 exemplos sintéticos](../../app/contracts/v0_1_0/examples.json).
- Gerador determinístico: `scripts/build_contracts.py`; `--check` acusa divergência.

Distribuição pública somente leitura:
`https://p3.awecloudsolution.com/api/contracts/0.1.0/{document}`,
onde document é event.schema.json, openapi.json, catalog.json ou examples.json.
O schema é normativo para estrutura/tipos; regras de identidade e replay abaixo são
normativas para comportamento. O gerador mantém os artefatos sincronizados, não
substitui documentação de semântica nem constitui serviço de ingestão.

## Envelope e identidade

| Campo | Regra |
|---|---|
| schema_version | literal 0.1.0; API /v1 é namespace futuro de transporte, não versão do evento |
| event_id | UUIDv4 canônico minúsculo, gerado uma vez na origem |
| event_type | um dos 14 tipos definidos abaixo |
| occurred_at | calendário válido; RFC3339 com milissegundos e Z ou offset explícito |
| tenant_id | assertiva a conferir contra tenant da credencial; não concede autorização |
| organization_id/store_id/terminal_id/source_id | combinação exata concedida à integração |
| source_session_id | UUIDv4 da sessão de sequenciamento do conector; muda quando o contador reinicia |
| source_sequence | inteiro de 0 a 2^53−1, monotônico na sessão; não é chave de deduplicação |
| session_id | identificador de sessão de caixa; diferente de sessão do conector |
| transaction_id | obrigatório para todos os tipos fora de cash/cash_session; opcional nos demais |
| payload | objeto específico do tipo, sem campos adicionais |

Identificadores de domínio: 1–64 caracteres ASCII, começando por letra/número,
continuando com letras/números, ponto, underscore, dois-pontos ou hífen. São opacos;
identificadores de transação/linha/pagamento/sessão devem ser inequívocos no escopo
(tenant, source_id), não reutilizados arbitrariamente. Cadastro hierárquico real e
integridade referencial serão conferidos no backend M3.

Toda chave desconhecida é erro, inclusive dentro do payload. `received_at`, risco,
score e inferências não são enviados pelo PDV. Dados pessoais nominais/documentos,
cartão e credenciais estão excluídos; operator_id é pseudônimo opaco definido pelo
integrador. Isso não equivale a anonimização. Não há extensões livres em 0.1.0.

## Catálogo inicial

Todos os campos listados são obrigatórios; consultar schema para enumerações e limites.
Os exemplos são independentes, não um demonstrativo contábil de uma venda completa.

| Tipo | Payload e significado |
|---|---|
| cash_session.opened | operator_id, opening_amount, currency; início de caixa |
| cash_session.closed | operator_id, reported_amount, currency; valor informado no fechamento |
| cash.supplied | movement_id, operator_id, amount, currency; suprimento |
| cash.withdrawn | movement_id, operator_id, amount, currency; sangria |
| cash.drawer_opened | operator_id, reason; fato de abertura, motivo pode ser UNKNOWN |
| transaction.started | operator_id, transaction_type=SALE; início de venda |
| transaction.subtotal_requested | amount, currency; pedido intermediário de subtotal |
| transaction.completed | net_total, currency, item_count, payment_count; conclusão |
| transaction.cancelled_before_completion | reason_code, operator_id; cancelamento da venda ainda aberta |
| transaction.voided_after_completion | reason_code, operator_id, authorization_id, authorized_by; anulação pós-conclusão autorizada |
| item.added | line_id, sku, quantity, unit, unit_price, total, currency, capture_method, weighed_in_store |
| item.cancelled | line_id, sku, quantity, unit, total, currency, reason_code, operator_id |
| payment.registered | payment_id, method, amount, currency; um evento por pagamento |
| change.registered | amount, currency; fato de troco informado |

`line_id` identifica a linha, não apenas o SKU. Cancelamento de item pode informar
quantidade parcial; coerência contra a quantidade original exige a projeção M3.
`total` e valores de fechamento são fatos informados pelo ERP, não calculados aqui;
regras não devem confundir divergência aritmética com payload estruturalmente inválido.
Regras de estado (venda já concluída, linha inexistente, soma de pagamentos) exigem
histórico e permanecem fora do verificador estrutural M1.

### Reservados, ainda rejeitados

Demais terminal.*, descontos/acréscimos de transação/item, item.queried/unknown/manual_release,
customer.identified, seller.identified, authorization.granted, operações não comerciais,
telemetria e extensões customizadas do brainstorm não estão aceitos nesta versão.
`transaction.subtotal` foi descartado em favor de `transaction.subtotal_requested`.
`item.quantity_changed` não existe no catálogo inicial. Negócio amplo continua no PRD;
a restrição da primeira versão não remove capacidades futuras do roadmap.

## Dinheiro, quantidade e tempo

Dinheiro: string decimal não negativa, exatamente duas casas, até 12 dígitos inteiros,
sem separador de milhar, expoente ou zero inicial excedente; somente BRL nesta versão.
Exemplos: "0.00", "113.46"; número JSON 113.46 é inválido. Quantidade: string positiva,
exatamente três casas, até 9 dígitos inteiros, com unidade UN/KG/L/M. Cancelamentos usam
quantidade positiva e tipo explícito; não representam estorno por número negativo.
Arredondamento comercial, impostos e fechamento pertencem ao ERP e regras futuras.

received_at é UTC atribuído pelo backend após recepção, retornado como recibo após
commit. occurred_at e offset originais são preservados; não ajustar fato durante replay.
Clock drift não é duração HTTP. O verificador aceita eventos antigos/futuros estruturalmente
válidos: limites de drift/quarentena serão política do piloto, nunca descarte silencioso.
Sincronizar NTP em PDV/edge/backend e registrar qualidade do relógio em telemetria futura.
Leap seconds não são aceitos por este perfil; precisão é fixa em milissegundos.

## Transporte e resultados planejados para M3

Um evento por POST /api/v1/events; HTTPS e Authorization: Bearer obrigatório.
application/json UTF-8; limite 65.536 bytes, inclusive espaços; sem JSON comprimido
nesta versão. Chaves JSON duplicadas, NaN/Infinity e conteúdo malformado são 400.
Credencial verificada antes de consultar qualquer estado de idempotência; autorização
depende do escopo completo. Payload válido não constitui autorização.

| Status | Código/comportamento |
|---|---|
| 201 | evento+outbox persistidos atomicamente; recibo accepted |
| 200 | reenvio exato; recibo duplicate com received_at original |
| 400 | INVALID_JSON |
| 401 | UNAUTHORIZED (ausente, inválida, expirada ou revogada; resposta indistinguível) |
| 403 | FORBIDDEN (tenant/escopo/permissão não concedidos) |
| 404 | NOT_FOUND em consulta fora de escopo ou inexistente |
| 409 | EVENT_CONFLICT (mesma identidade, outro conteúdo) |
| 413 / 415 | PAYLOAD_TOO_LARGE / UNSUPPORTED_MEDIA_TYPE |
| 422 | INVALID_EVENT (versão/tipo/campo/valor inválido) |
| 429 / 503 | RATE_LIMITED / UNAVAILABLE; reenviar preservando identidade |

Erros devolvem somente code, sem payload, nomes de pessoas, tokens ou valores rejeitados.
M1 testa os resultados de política no modelo local; limites de rede, rate limiting e
transações persistentes ainda não são serviços operacionais. POST real continua 404.

## Idempotência e replay offline

Unicidade: (tenant autenticado, event_id). IDs iguais em tenants distintos são independentes.
Repetição compara todo evento validado; ordem das chaves e espaços não alteram fatos.
Números inteiros matematicamente iguais são equivalentes. Strings são exatas: mudar
representação de timestamp/offset, fonte, sequência, payload ou qualquer vínculo mantendo
event_id é conflito. Rotacionar credencial da mesma integração/grants não muda a identidade.
Erro 409 exige diagnóstico e quarentena; nunca gerar ID novo automaticamente para contorná-lo.

Conector futuro grava localmente o envelope antes de tentar envio, conserva ID/tempo/
sequência no retry e só remove pendência após recibo de sucesso. Backoff exponencial
com jitter, teto de 60 s; respeitar Retry-After em 429. Timeout/503 mantém pendência;
401/403 requer corrigir credencial; 400/409/413/415/422 segue para diagnóstico sem loop.
Fila cheia não pode descartar silenciosamente: alertar e aplicar a política operacional
pactuada no piloto. Eventos atrasados/fora de ordem não devem ser rejeitados só pela
sequência; a timeline pode ser incompleta e completada posteriormente.

No M3, unicidade e efeito precisam ser atômicos sob concorrência, ACK após commit de
evento+outbox; deduplicação deve sobreviver a restart. Manter marcador de identidade
pelo menos durante toda janela de replay acordada; expiração não pode recriar efeitos.
Janela numérica e retenção do piloto são requisito de entrada para M3, não uma garantia
inventada no M1. O ReferenceLedger é volátil, apenas um oráculo de teste.

## Verificação e evolução

```sh
docker build --target test -t p3-test .
docker run --rm p3-test python scripts/build_contracts.py --check
```

Para validar um arquivo sintético no host: Python 3.12/venv,
`pip install -c constraints.txt -r requirements-dev.txt`, depois
`python -m scripts.event_conformance /caminho/evento.json`.
Saída 0/valid=true ou 1/code sem ecoar dados. Extraia um objeto de examples.json para
obter um arquivo individual. Em container, montar apenas arquivo sintético em /tmp/event.json
e chamar o mesmo módulo; não inserir credenciais reais no verificador.

Após conclusão, 0.1.0 permanece estável. Novo campo obrigatório, enum, regra restritiva
ou tipo suportado exige nova versão explícita, novas fixtures, migração e anúncio ao
integrador; não mudar silenciosamente schema congelado. Contrato não garante toda a
segurança/persistência do futuro serviço: testes M3 precisam provar isso no backend real.

Fontes técnicas consultadas: [JSON Schema/Pydantic](https://docs.pydantic.dev/latest/concepts/json_schema/),
[OpenAPI 3.1](https://spec.openapis.org/oas/v3.1.0.html),
[jsonschema validation](https://python-jsonschema.readthedocs.io/en/stable/validate/).
