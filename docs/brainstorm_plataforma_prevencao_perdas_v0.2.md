# Plataforma Aberta de Prevenção de Perdas no Varejo

## Brainstorm consolidado, requisitos, arquitetura, benchmark, hipóteses e pendências

**Documento de trabalho:** v0.2\
**Data:** 16/09/2026\
**Status:** Engenharia de requisitos / definição conceitual\
**Nome do produto:** ainda não definido\
**Nome provisório usado em alguns brainstorms:** WR Loss

------------------------------------------------------------------------

# 0. Objetivo deste documento

Este documento consolida, em detalhe, as ideias discutidas até aqui para
a criação de uma plataforma própria de prevenção de perdas no varejo.

Ele deve funcionar simultaneamente como:

-   memória técnica do projeto;
-   registro das decisões já tomadas;
-   catálogo de hipóteses;
-   base para especificações futuras;
-   backlog de questões em aberto;
-   documento de onboarding para novos colaboradores;
-   base para agentes de desenvolvimento;
-   referência para criação posterior de ADRs, OpenAPI, schemas, MCP,
    Skills e roadmap.

O documento também incorpora as conclusões obtidas pela análise do
**Sistema Cash - Manual de Integração via Biblioteca Dinâmica - Versão
1.3**, de 23/03/2022.

É fundamental distinguir neste documento:

-   **fato documentado no manual Nextop**;
-   **inferência arquitetural**;
-   **decisão do nosso projeto**;
-   **ideia futura ainda não aprovada**.

------------------------------------------------------------------------

# 1. Visão geral

Queremos construir uma **plataforma aberta de inteligência para
prevenção de perdas**, inicialmente orientada ao varejo e especialmente
a supermercados, mas arquitetada para evoluir para outros segmentos.

O sistema deverá correlacionar:

``` text
EVENTOS DO ERP/PDV
        +
CONTEXTO OPERACIONAL
        +
CÂMERA FÍSICA
        +
TELA DO PDV
        +
TELEMETRIA
        +
HISTÓRICO
        +
REGRAS
        +
ANÁLISE COMPORTAMENTAL
        +
INTELIGÊNCIA ARTIFICIAL
```

O resultado deve ser uma plataforma capaz de transformar eventos
operacionais em uma **timeline auditável**, localizar evidências
relacionadas e priorizar situações que merecem análise humana.

------------------------------------------------------------------------

# 2. O que o produto NÃO será

O produto não será:

-   uma integração exclusiva para StarTwo;
-   um plugin específico para um único ERP;
-   uma integração com a Nextop;
-   um clone literal do CASH;
-   somente uma câmera virtual;
-   somente um sistema de CFTV;
-   somente um dashboard;
-   somente um detector por IA;
-   somente um sistema de alertas.

A ScreenCam, o Hermes, o MCP e os conectores de ERP são componentes de
uma plataforma maior.

------------------------------------------------------------------------

# 3. Princípio de independência

A plataforma deverá ser independente de:

## 3.1 ERP

Exemplos:

-   StarTwo;
-   Consinco;
-   Linx;
-   TOTVS;
-   Arius;
-   ERP próprio;
-   qualquer outro sistema capaz de integrar com nosso contrato.

## 3.2 CFTV

Não devemos depender de um único fabricante.

Devemos priorizar:

-   RTSP;
-   ONVIF;
-   integrações documentadas com DVR/NVR/VMS;
-   adapters específicos apenas quando agregarem valor.

## 3.3 Inteligência artificial

O Hermes Agent será o motor/orquestrador de IA adotado, mas a plataforma
não deve ficar acoplada a um único modelo de linguagem ou provider.

## 3.4 Infraestrutura

O desenho deve permitir implantação:

-   cloud;
-   on-premises;
-   híbrida;
-   edge + cloud.

------------------------------------------------------------------------

# 4. Contexto StarTwo e SuperTop

A StarTwo é a fornecedora do ERP/PDV utilizado pelo SuperTop.

O usuário deste projeto atua como parceiro comercial da StarTwo e presta
serviços de cloud para sistemas StarTwo.

Os PDVs StarTwo observados utilizam **Linux Mint**.

O SuperTop ainda não possui integração Nextop no cenário discutido.

O manual Nextop foi obtido como material técnico de referência.

**Decisão:** o conhecimento obtido nesse contexto não deve produzir
acoplamento StarTwo no núcleo da plataforma.

Uma integração StarTwo poderá existir futuramente apenas como um
adapter/conector entre muitos.

------------------------------------------------------------------------

# 5. Benchmark Nextop

A Nextop foi escolhida como um dos benchmarks por possuir uma solução
madura de prevenção de perdas.

Foram discutidos como referências funcionais:

-   CASH;
-   Enterprise;
-   Top Ocorrências;
-   SET;
-   Supervisor Remoto;
-   RECEBE;
-   alertas inteligentes;
-   Smart Cart;
-   aplicações de visão computacional/self-checkout.

O objetivo não é reproduzir esses produtos, mas compreender o domínio.

------------------------------------------------------------------------

# 6. Objetivo da engenharia competitiva

O estudo da Nextop deve responder perguntas como:

-   quais acontecimentos do PDV são considerados relevantes?
-   quais campos acompanham esses acontecimentos?
-   quais eventos possuem maior valor para auditoria?
-   quais informações de contexto são necessárias?
-   como a solução diferencia venda, operação financeira e evento
    operacional?
-   como um autorizador é representado?
-   como pagamentos mistos são representados?
-   como balança e telemetria entram no modelo?
-   como uma ocorrência pode ser correlacionada com vídeo?
-   quais decisões maduras podemos incorporar de forma independente?

Fluxo desejado:

``` text
BENCHMARK / MANUAL
        |
        v
CONHECIMENTO DO DOMÍNIO
        |
        v
REQUISITOS
        |
        v
MODELO CANÔNICO PRÓPRIO
        |
        v
ARQUITETURA PRÓPRIA
        |
        v
PROTOCOLO / API / SDK PRÓPRIOS
        |
        v
PRODUTO PRÓPRIO
```

------------------------------------------------------------------------

# 7. Limites da análise

Não é objetivo:

-   copiar código;
-   reproduzir interface visual;
-   contornar proteção;
-   obter segredos;
-   reproduzir marca;
-   depender de protocolo proprietário;
-   implementar uma biblioteca binariamente compatível com a Nextop.

O que interessa é o conhecimento de domínio exposto pelo contrato de
integração.

------------------------------------------------------------------------

# 8. Manual Nextop analisado

Documento:

``` text
Sistema Cash
Manual de Integração via Biblioteca Dinâmica
Versão 1.3
23/03/2022
13 páginas
```

Histórico relevante:

``` text
1.0 - versão inicial
1.1 - tamanhos máximos dos campos alfanuméricos
1.2 - liberação manual de item
1.3 - identificação de itens pesados no estabelecimento
```

Esse histórico demonstra que o contrato evoluiu para acomodar novos
casos de prevenção de perdas.

**Lição para nosso projeto:** nosso Event Protocol deve ser extensível e
versionado.

------------------------------------------------------------------------

# 9. Arquitetura Nextop comprovada pelo manual

O manual documenta:

``` text
PDV / ERP
   |
   | chamadas de funções
   v
libcash.dll     Windows
libCash.so      Linux
   |
   | UDP
   | porta padrão 8090
   v
SERVIDOR CASH
```

Inicialização:

``` c
TOPCASH_Inicializacao(
    char* servidor,
    int porta,
    int caixa
)
```

Parâmetros:

-   IP do servidor CASH;
-   porta UDP;
-   número do caixa.

Finalização:

``` c
TOPCASH_Finalizacao()
```

------------------------------------------------------------------------

# 10. O que o manual NÃO documenta

Não devemos preencher essas lacunas com suposições.

Permanecem desconhecidos:

-   formato dos datagramas UDP;
-   cabeçalho;
-   magic bytes;
-   encoding;
-   serialização;
-   checksum;
-   ACK;
-   retry;
-   sequenciamento;
-   fragmentação;
-   criptografia;
-   autenticação;
-   buffer offline;
-   store-and-forward;
-   deduplicação;
-   timestamp transmitido;
-   identificação explícita da loja;
-   persistência no servidor;
-   arquitetura interna do CASH;
-   associação com câmeras;
-   recuperação de vídeo;
-   arquitetura do NVR/VMS;
-   geração interna de alertas;
-   geração de ocorrências;
-   integração CASH ↔ Enterprise.

Portanto, o manual nos dá uma visão muito boa do **contrato PDV →
CASH**, mas não do CASH inteiro.

------------------------------------------------------------------------

# 11. Insight principal obtido do manual

O CASH trata o PDV como um **gerador de eventos operacionais em tempo
real**.

Não são enviados apenas dados de uma venda concluída.

São comunicadas ações à medida que acontecem:

``` text
ABERTURA CAIXA
ITEM
ITEM
CONSULTA
DESCONTO
AUTORIZADOR
CANCELAMENTO
SUBTOTAL
PAGAMENTO
GAVETA
TROCO
FECHAMENTO
```

Além disso existe telemetria periódica de balança.

Isso confirma que nosso produto deve ser **event-driven**.

------------------------------------------------------------------------

# 12. Princípio "ERP informa fatos"

O ERP não deve implementar nossa lógica de prevenção de perdas.

O ERP informa:

``` text
O QUE aconteceu
QUANDO aconteceu
ONDE aconteceu
QUEM participou
QUAL objeto foi afetado
QUAL valor estava envolvido
```

A nossa plataforma decide:

``` text
se existe regra
se existe anomalia
se merece score
se gera alerta
se gera ocorrência
quais evidências recuperar
se Hermes deve analisar
```

------------------------------------------------------------------------

# 13. Catálogo Nextop - ciclo do caixa

## 13.1 Abertura de caixa

``` c
TOPCASH_AberturaCaixa(
    codigo_operador,
    nome_operador,
    valor_caixa
)
```

Conhecimento extraído:

-   operador;
-   identificação;
-   fundo disponível;
-   início de sessão financeira.

Nosso evento:

``` text
cash_session.opened
```

Campos desejados:

``` text
session_id
operator
opening_amount
occurred_at
store_id
terminal_id
```

------------------------------------------------------------------------

## 13.2 Fechamento de caixa

``` text
TOPCASH_FechamentoCaixa
```

Nosso evento:

``` text
cash_session.closed
```

Além do valor informado pelo ERP, futuramente poderemos calcular:

``` text
expected_cash
reported_cash
difference
```

------------------------------------------------------------------------

## 13.3 Fundo de caixa

``` text
TOPCASH_FundoCaixa
```

Nosso evento:

``` text
cash.supplied
```

Possíveis fatores futuros:

-   frequência;
-   valor;
-   horário;
-   operador;
-   supervisor;
-   diferença contra comportamento histórico.

------------------------------------------------------------------------

## 13.4 Sangria

``` text
TOPCASH_SangriaCaixa
```

Nosso evento:

``` text
cash.withdrawn
```

A sangria deve ser tratada como evento financeiro relevante de primeira
classe.

------------------------------------------------------------------------

# 14. Tipo de caixa

Nextop diferencia:

``` text
1  Caixa Normal
2  Caixa Rápido
3  Caixa Preferencial
4  Caixa de Recebimentos
5  Caixa de Drogaria
6  Caixa de Consulta de Preços
99 Personalizado
```

Lição:

> Não devemos comparar indiscriminadamente o comportamento de todos os
> terminais.

Nosso terminal deverá possuir classificação.

Exemplo:

``` json
{
  "terminal_id": "04",
  "terminal_type": "FAST_CHECKOUT"
}
```

Isso deve influenciar baselines.

------------------------------------------------------------------------

# 15. Operações não comerciais

O CASH possui `TOPCASH_TipoOperacao`.

Tipos documentados:

-   recebimento;
-   pagamento de fatura;
-   recarga/crédito;
-   pagamento de contas;
-   pagamento de benefício;
-   vale-presente;
-   bilhete de transporte;
-   personalizado.

Isso demonstra que nosso conceito de transação não pode ser sinônimo de
venda.

Modelo:

``` text
TRANSACTION
    |
    +-- SALE
    +-- RECEIPT
    +-- BILL_PAYMENT
    +-- RECHARGE
    +-- BENEFIT
    +-- GIFT_CARD
    +-- TRANSPORT
    +-- CUSTOM
```

------------------------------------------------------------------------

# 16. Eventos operacionais do terminal

Nextop possui `TOPCASH_EventoPdv`.

Eventos documentados:

-   Leitura X;
-   Redução Z;
-   Ligamento;
-   Desligamento;
-   Reinício;
-   Substituição de Papel;
-   Personalizado.

Nossa família deverá prever:

``` text
terminal.started
terminal.stopped
terminal.restarted
terminal.paper_changed
terminal.fiscal_x_read
terminal.fiscal_z_reduction
terminal.custom
```

Isso é importante porque o contexto técnico pode ajudar a interpretar
eventos posteriores.

------------------------------------------------------------------------

# 17. Ciclo da transação

O manual evidencia um ciclo:

``` text
transaction.started
       |
       +-- item
       +-- item
       +-- consulta
       +-- desconto
       +-- autorização
       |
       v
transaction.subtotal
       |
       v
payment
       |
       v
change
       |
       v
transaction.completed
```

Esse ciclo deverá ser reconstruível integralmente no Timeline Engine.

------------------------------------------------------------------------

# 18. Abertura de cupom

Nextop:

``` text
TOPCASH_AberturaCupom
```

Nosso evento:

``` text
transaction.started
```

Precisamos possuir `transaction_id` globalmente inequívoco dentro do
tenant.

------------------------------------------------------------------------

# 19. Fechamento de cupom

Nextop:

``` text
TOPCASH_FechamentoCupom
```

Nosso evento:

``` text
transaction.completed
```

Campos adicionais desejáveis:

``` text
gross_total
discount_total
surcharge_total
net_total
item_count
payment_count
```

Nem todos são exigidos pelo manual; são evolução nossa.

------------------------------------------------------------------------

# 20. Dois tipos de cancelamento

O manual diferencia claramente:

## Antes da finalização

``` text
TOPCASH_CancelamentoVenda
```

## Depois da finalização

``` text
TOPCASH_CancelamentoCupom
```

Essa diferença deve ser preservada.

Sugestão:

``` text
transaction.cancelled_before_completion
transaction.voided_after_completion
```

Essa distinção é relevante para o Risk Engine.

------------------------------------------------------------------------

# 21. Desconto no cupom

Nextop envia:

-   cupom;
-   operador;
-   percentual;
-   valor.

Nosso modelo deve preservar simultaneamente:

``` text
percentage
amount
```

Evento:

``` text
transaction.discount_applied
```

------------------------------------------------------------------------

# 22. Acréscimo no cupom

Evento:

``` text
transaction.surcharge_applied
```

Mesma filosofia do desconto.

------------------------------------------------------------------------

# 23. Cliente

Nextop possui identificação de cliente com CPF/CNPJ e nome.

Nosso modelo deverá considerar privacidade e minimização.

Possíveis campos:

``` text
customer.id
customer.document_hash
customer.type
```

**Pendência:** decidir quando dados pessoais completos são realmente
necessários.

------------------------------------------------------------------------

# 24. Vendedor

Entidade separada do operador.

Isso é importante para operações em que:

``` text
OPERADOR DO CAIXA != VENDEDOR
```

Nosso modelo deve permitir ambos.

------------------------------------------------------------------------

# 25. Autorizador

Nextop possui chamada específica para identificar autorizador da
operação seguinte.

Isso sugere associação contextual por ordem das chamadas.

Nossa arquitetura deve melhorar esse ponto, criando vínculo explícito:

``` json
{
  "authorization": {
    "authorization_id": "...",
    "authorized_by": {
      "id": "12"
    }
  }
}
```

Assim não dependemos de ordem implícita.

------------------------------------------------------------------------

# 26. Inclusão de item

A função Nextop inclui:

-   código;
-   descrição;
-   quantidade;
-   unidade;
-   valor unitário;
-   valor total;
-   digitado;
-   pesado.

Dois campos são particularmente valiosos:

``` text
digitado
pesado
```

`digitado` diferencia:

``` text
scanner
versus
entrada manual
```

`pesado` identifica item pesado no estabelecimento.

Esses são excelentes sinais analíticos.

------------------------------------------------------------------------

# 27. Método de captura do item

Nosso modelo deve ser mais expressivo:

``` text
capture_method:
    BARCODE_SCAN
    MANUAL_ENTRY
    SCALE
    PLU
    RFID
    VISION
    OTHER
```

O manual só comprova scanner versus digitado e flag de pesagem. As
demais opções são extensões futuras nossas.

------------------------------------------------------------------------

# 28. Produto pesado

Exemplo de contexto de risco:

``` text
produto de alto valor
+
pesado no estabelecimento
+
entrada manual
+
cancelamento posterior
+
mesmo operador recorrente
```

Nenhum desses sinais isoladamente implica fraude.

A combinação pode justificar análise.

------------------------------------------------------------------------

# 29. Cancelamento de item

Nextop envia:

-   código;
-   descrição;
-   quantidade;
-   unidade;
-   valor unitário;
-   valor total.

Limitação observada:

> não existe identificador explícito da linha do cupom no método
> documentado.

Nosso protocolo deverá possuir:

``` text
line_id
item_sequence
```

Isso evita ambiguidade quando o mesmo produto aparece várias vezes.

------------------------------------------------------------------------

# 30. Consulta de item/preço

Nextop trata consulta como evento.

Nosso evento:

``` text
item.queried
```

Isso permite analisar sequências como:

``` text
CONSULTA
   |
ENTRADA MANUAL
   |
INCLUSÃO
   |
CANCELAMENTO
```

A plataforma deve analisar **sequências**, não somente eventos isolados.

------------------------------------------------------------------------

# 31. Desconto por item

Evento:

``` text
item.discount_applied
```

Devemos usar nomes inequívocos para:

``` text
discount_amount
discount_percentage
original_unit_price
resulting_unit_price
```

O manual possui nomenclatura de parâmetro potencialmente ambígua; não
devemos reproduzi-la.

------------------------------------------------------------------------

# 32. Acréscimo por item

Evento:

``` text
item.surcharge_applied
```

Mesmo princípio.

------------------------------------------------------------------------

# 33. Departamento do produto

Nextop permite informar departamento após inclusão do item.

Isso valida a importância de contexto de categoria.

Nosso modelo poderá evoluir para:

``` text
department
category
subcategory
brand
risk_class
```

Exemplo:

``` text
AÇOUGUE
  -> CARNES
      -> BOVINOS
```

Baselines poderão ser diferentes por departamento.

------------------------------------------------------------------------

# 34. Item não cadastrado

Nextop possui:

``` text
TOPCASH_ItemNaoCadastrado
```

Nosso evento:

``` text
item.unknown
```

Esse evento pode ser um sinal operacional importante.

------------------------------------------------------------------------

# 35. Liberação manual SmartCart

A versão 1.2 adicionou evento de liberação manual.

Nosso modelo deverá prever:

``` text
item.manual_release
```

A principal lição não é copiar SmartCart, mas manter o protocolo
extensível para novos tipos de checkout e sensores.

------------------------------------------------------------------------

# 36. Subtotal

Nextop registra explicitamente o comando de subtotal.

Nosso evento:

``` text
transaction.subtotal_requested
```

Ações intermediárias do operador possuem valor analítico mesmo sem
alterar o resultado fiscal.

------------------------------------------------------------------------

# 37. Pagamentos

Nextop exige uma chamada por forma de pagamento.

Isso confirma que uma transação deve suportar N pagamentos:

``` text
TRANSACTION
   |
   +-- payment #1
   +-- payment #2
   +-- payment #3
```

Nosso evento:

``` text
payment.registered
```

Formas modernas devem ser extensíveis:

``` text
CASH
PIX
CREDIT_CARD
DEBIT_CARD
STORE_CARD
VOUCHER
CHECK
GIFT_CARD
OTHER
```

------------------------------------------------------------------------

# 38. Troco

Nextop trata troco como evento próprio.

Nosso evento:

``` text
change.registered
```

Devemos registrar o fato, não apenas derivá-lo matematicamente.

------------------------------------------------------------------------

# 39. Abertura da gaveta

Nextop exige evento sempre que a gaveta abrir.

Nosso evento:

``` text
cash.drawer_opened
```

Regra futura possível:

``` text
gaveta aberta
AND
nenhum pagamento em dinheiro próximo
AND
nenhuma sangria
AND
nenhum fundo
```

Isso gera candidato para análise.

------------------------------------------------------------------------

# 40. Telemetria da balança

A função `TOPCASH_PesoBalanca` deve ser executada repetidamente a cada
segundo.

Essa é uma das descobertas mais importantes.

Ela demonstra que a solução recebe não apenas eventos discretos, mas
também **telemetria contínua**.

Portanto devemos separar:

``` text
EVENTS
versus
TELEMETRY
```

------------------------------------------------------------------------

# 41. Event Bus + Telemetry Bus

Arquitetura proposta:

``` text
                    INGESTION
                        |
          +-------------+-------------+
          |                           |
          v                           v
     EVENT INGEST                TELEMETRY INGEST
          |                           |
          v                           v
      EVENT BUS                 TELEMETRY BUS
          |                           |
          +-------------+-------------+
                        |
                        v
                 TIMELINE ENGINE
```

Telemetrias futuras possíveis:

-   peso da balança;
-   estado da gaveta;
-   sensores;
-   SmartCart;
-   self-checkout;
-   presença;
-   fila;
-   dispositivos IoT.

------------------------------------------------------------------------

# 42. Ausência de timestamp no contrato Nextop

As funções documentadas não recebem timestamp.

Não sabemos se:

-   a biblioteca adiciona timestamp;
-   o servidor adiciona timestamp;
-   o protocolo não transmite timestamp.

Nossa arquitetura deve ser explícita.

Campos:

``` text
occurred_at
received_at
```

Exemplo:

``` json
{
  "occurred_at": "2026-09-16T09:42:26.382-03:00",
  "received_at": "2026-09-16T09:42:26.421-03:00"
}
```

Isso permite medir ingest latency.

------------------------------------------------------------------------

# 43. Event ID

O contrato documentado não expõe um ID único do evento.

Nossa API deve exigir:

``` text
event_id
```

Benefícios:

-   idempotência;
-   deduplicação;
-   retry;
-   replay;
-   auditoria;
-   event sourcing;
-   diagnóstico.

ULID/UUID será decidido posteriormente.

------------------------------------------------------------------------

# 44. Loja e tenant explícitos

A inicialização Nextop documentada recebe servidor, porta e caixa, mas
não loja.

Nossa arquitetura não deve depender de configuração implícita.

Identificadores mínimos:

``` text
tenant_id
organization_id
store_id
terminal_id
```

------------------------------------------------------------------------

# 45. Vínculos explícitos

Nosso modelo deverá evitar contexto dependente apenas de ordem.

Identificadores possíveis:

``` text
event_id
session_id
transaction_id
line_id
authorization_id
payment_id
occurrence_id
causation_id
correlation_id
```

------------------------------------------------------------------------

# 46. Modelo Canônico de Evento v0.1 - proposta

``` json
{
  "schema_version": "1.0",

  "event_id": "01K5...",
  "event_type": "item.cancelled",

  "occurred_at": "2026-09-16T09:42:26.382-03:00",
  "received_at": "2026-09-16T09:42:26.421-03:00",

  "tenant_id": "tenant-x",
  "organization_id": "org-x",
  "store_id": "007",
  "terminal_id": "004",

  "session_id": "sess-8293",
  "transaction_id": "sale-183923",
  "line_id": "004",

  "operator": {
    "id": "35",
    "name": "OPERADOR"
  },

  "authorization": {
    "required": true,
    "authorized_by": {
      "id": "12"
    }
  },

  "product": {
    "sku": "9382",
    "ean": "7891234567890",
    "description": "PICANHA KG",
    "department": "ACOUGUE",
    "unit": "KG"
  },

  "quantity": 1.420,
  "unit_price": 79.90,
  "total": 113.46,

  "capture": {
    "method": "MANUAL_ENTRY",
    "weighed_in_store": true
  }
}
```

**Status:** proposta; não congelado.

------------------------------------------------------------------------

# 47. Taxonomia v0.1 revisada

``` text
terminal.*
    started
    stopped
    restarted
    paper_changed
    fiscal_x_read
    fiscal_z_reduction
    custom

cash_session.*
    opened
    closed

cash.*
    supplied
    withdrawn
    drawer_opened

transaction.*
    started
    subtotal_requested
    completed
    cancelled_before_completion
    voided_after_completion
    discount_applied
    surcharge_applied

transaction.operation.*
    receipt
    bill_payment
    recharge
    benefit
    gift_card
    transport
    custom

item.*
    added
    cancelled
    queried
    discount_applied
    surcharge_applied
    unknown
    manual_release

customer.*
    identified

seller.*
    identified

authorization.*
    granted

payment.*
    registered

change.*
    registered

telemetry.scale.*
    weight
```

------------------------------------------------------------------------

# 48. API-first

A principal interface de integração será uma API pública.

Conceito:

``` http
POST /api/v1/events
```

Software houses não devem ser obrigadas a utilizar biblioteca binária.

------------------------------------------------------------------------

# 49. SDKs

A API será o contrato.

SDKs serão conveniência.

Planejados:

-   Python;
-   .NET;
-   Java;
-   Node.js;
-   Go.

Avaliar:

-   C;
-   C++;
-   Delphi.

Princípio:

> SDK não pode ser o único modo de integrar.

------------------------------------------------------------------------

# 50. Agent/Connector no PDV

Em alguns cenários um agent local poderá ser útil.

Responsabilidades possíveis:

``` text
POS CONNECTOR
EVENT BUFFER
RETRY
HEALTH
SCREENCAM
```

O agent não deverá executar LLM.

------------------------------------------------------------------------

# 51. Offline / Store-and-forward

Mesmo não documentado no manual Nextop, consideramos necessário para
nosso produto.

Cenário:

``` text
PDV
 |
 | internet indisponível
 v
LOCAL BUFFER
 |
 | conexão retorna
 v
REPLAY
 |
 v
PLATFORM
```

Requisitos:

-   fila persistente;
-   idempotência;
-   retry exponencial;
-   limite de armazenamento;
-   métricas de backlog;
-   ordenação quando necessária.

------------------------------------------------------------------------

# 52. REST, streaming e MCP têm papéis diferentes

``` text
REST
 -> integração operacional comum

SDK
 -> ergonomia para software houses

STREAMING
 -> alto volume / grandes redes

WEBHOOK
 -> plataforma notificando sistemas externos

MCP
 -> agentes e IA
```

Não usar MCP como substituto do Event API do PDV.

------------------------------------------------------------------------

# 53. Webhooks

Eventos de saída possíveis:

``` text
alert.created
occurrence.created
occurrence.updated
occurrence.closed
```

Exemplo:

``` json
{
  "type": "occurrence.created",
  "occurrence_id": "occ_928392",
  "risk_score": 87,
  "store": "007",
  "terminal": "004"
}
```

------------------------------------------------------------------------

# 54. Event Streaming

Tecnologia ainda não definida.

Candidatos:

-   NATS;
-   Kafka;
-   RabbitMQ;
-   outros.

Critérios futuros:

-   simplicidade operacional;
-   throughput;
-   replay;
-   ordering;
-   multi-tenancy;
-   observabilidade;
-   custo;
-   integração com stack escolhida.

------------------------------------------------------------------------

# 55. Video Engine

Objetivo:

``` text
                   VIDEO ENGINE
                        |
       +----------------+----------------+
       |                |                |
       v                v                v
   CAMERA IP          NVR/VMS         SCREENCAM
```

Funções desejadas:

-   cadastro;
-   descoberta;
-   health;
-   snapshot;
-   live;
-   recuperação histórica;
-   clips;
-   associação com PDV;
-   associação com ocorrência.

------------------------------------------------------------------------

# 56. RTSP e ONVIF

Priorizar padrões abertos.

RTSP:

-   transporte do stream.

ONVIF:

-   descoberta;
-   identificação;
-   profiles;
-   integração com ecossistema CFTV.

Adapters proprietários poderão existir quando necessários.

------------------------------------------------------------------------

# 57. ScreenCam

A ideia inicial era criar uma câmera IP virtual cuja imagem fosse a tela
do computador.

Após o brainstorm, ScreenCam passa a ser um componente estratégico da
plataforma.

``` text
TELA PDV
   |
   v
CAPTURE
   |
   v
ENCODE
   |
   v
RTSP / ONVIF
   |
   v
NVR / VIDEO ENGINE
```

------------------------------------------------------------------------

# 58. ScreenCam - requisitos

-   Linux;
-   Windows;
-   prioridade PoC Linux Mint;
-   tela inteira;
-   monitor;
-   janela;
-   região;
-   H.264 inicialmente;
-   avaliar H.265;
-   RTSP;
-   ONVIF;
-   WS-Discovery;
-   main stream;
-   substream;
-   baixo CPU;
-   baixa RAM;
-   baixa latência;
-   reinício automático;
-   execução como serviço;
-   métricas de health.

------------------------------------------------------------------------

# 59. PoC ScreenCam Linux Mint

Primeira arquitetura:

``` text
X11
 |
 v
FFmpeg x11grab
 |
 v
H.264
 |
 v
MediaMTX
 |
 v
RTSP
 |
 +--> VLC
 |
 +--> NVR
```

MediaMTX é candidato de PoC, não decisão definitiva.

------------------------------------------------------------------------

# 60. ScreenCam como câmera adicional

Uma instalação poderá ter:

``` text
PDV 04
 |
 +-- CAMERA CHECKOUT 04
 |
 +-- SCREENCAM PDV 04
```

Assim a mesma ocorrência poderá mostrar:

-   cliente;
-   operador;
-   mercadoria;
-   tela;
-   mensagens do ERP;
-   ação executada.

------------------------------------------------------------------------

# 61. Overlay opcional

Ideia futura:

``` text
+---------------------------------------+
| LOJA 07 | PDV 04 | OPERADOR 35       |
| 16/09/2026 09:42:26                  |
+---------------------------------------+
|                                       |
|              TELA PDV                 |
|                                       |
+---------------------------------------+
| ITEM CANCELADO                        |
| PICANHA KG - R$ 183,40                |
+---------------------------------------+
```

Vantagem:

-   evidência contextual já gravada.

Desvantagens a avaliar:

-   poluição visual;
-   duplicação de dados;
-   privacidade;
-   risco de overlay incorreto.

------------------------------------------------------------------------

# 62. Timeline Engine

Este deve ser um dos componentes centrais.

Exemplo:

``` text
09:42:11 ITEM ADDED
09:42:18 QUANTITY CHANGED
09:42:26 ITEM CANCELLED
09:42:31 DRAWER OPENED
```

Associado a:

``` text
PHYSICAL CAMERA
09:42:06 ---------------- 09:42:46

SCREENCAM
09:42:06 ---------------- 09:42:46

SCALE
09:42:06 ---------------- 09:42:46
```

------------------------------------------------------------------------

# 63. Event Time versus Ingest Time

Devemos manter ambos.

``` text
occurred_at = momento no PDV
received_at = momento no backend
```

Possível campo adicional:

``` text
processed_at
```

Isso permitirá:

-   medir latência;
-   detectar relógio incorreto;
-   replay;
-   reconstrução de timeline.

------------------------------------------------------------------------

# 64. Sincronização de relógio

Requisito crítico.

Precisamos especificar:

-   NTP;
-   timezone;
-   offset;
-   drift;
-   relógio de câmera;
-   relógio do NVR;
-   relógio do PDV;
-   relógio do agent;
-   relógio do backend.

Métrica:

``` text
clock_drift_ms
```

------------------------------------------------------------------------

# 65. Clips de ocorrência

Configuração possível:

``` text
PRE_ROLL  = 10s
POST_ROLL = 20s
```

Evento:

``` text
09:42:26
```

Clip:

``` text
09:42:16 -> 09:42:46
```

Janela deverá ser configurável por regra/tipo de evento.

------------------------------------------------------------------------

# 66. Rule Engine

IA não deve substituir regras determinísticas.

Fluxo:

``` text
EVENT
 |
 v
RULE ENGINE
 |
 v
RISK FACTORS
 |
 v
RISK ENGINE
```

Exemplo:

``` text
cancelamento > R$ 100             +20
frequência > 3x baseline          +25
mesmo autorizador recorrente      +20
horário atípico                   +10
```

------------------------------------------------------------------------

# 67. Regras devem ser explicáveis

Não queremos:

``` text
SCORE = 87
```

Queremos:

``` text
SCORE = 87

+25 frequência anormal
+20 valor elevado
+20 autorizador recorrente
+12 horário atípico
+10 sequência incomum
```

------------------------------------------------------------------------

# 68. Regras por sequência

Exemplo:

``` text
item.queried
   |
item.added manual
   |
transaction.subtotal
   |
item.cancelled
   |
cash.drawer_opened
```

Uma sequência pode ser mais significativa que um evento isolado.

Precisamos estudar:

-   CEP;
-   state machines;
-   temporal rules;
-   sliding windows.

------------------------------------------------------------------------

# 69. Baselines

Comparações possíveis:

``` text
operador
versus
mesma função

terminal
versus
mesmo tipo de terminal

loja
versus
rede

produto
versus
departamento

horário
versus
mesma faixa histórica
```

------------------------------------------------------------------------

# 70. Risk Engine

Responsabilidades:

-   agregar fatores;
-   calcular score;
-   manter explicabilidade;
-   versionar modelo;
-   permitir thresholds por tenant;
-   registrar por que um score foi atribuído.

------------------------------------------------------------------------

# 71. Evento, alerta, ocorrência e fraude

São conceitos diferentes.

``` text
EVENTO
  |
  v
REGRA
  |
  v
ALERTA
  |
  v
TRIAGEM
  |
  v
OCORRÊNCIA
```

Uma ocorrência não significa automaticamente fraude.

------------------------------------------------------------------------

# 72. Workflow de ocorrência

Sugestão:

``` text
DETECTED
   |
TRIAGE
   |
IN_REVIEW
   |
   +--> CONFIRMED
   +--> DISMISSED
   +--> INCONCLUSIVE
   |
CLOSED
```

Terminologia final ainda será definida.

------------------------------------------------------------------------

# 73. Dados da ocorrência

-   occurrence_id;
-   tenant;
-   loja;
-   PDV;
-   eventos;
-   score;
-   fatores;
-   regras;
-   operador;
-   autorizador;
-   produto;
-   transaction_id;
-   clips;
-   snapshots;
-   ScreenCam;
-   notas;
-   responsável;
-   status;
-   classificação;
-   conclusão;
-   histórico.

------------------------------------------------------------------------

# 74. Feedback humano

O auditor deve poder informar:

``` text
procedente
improcedente
inconclusivo
```

E eventualmente motivo.

Esse feedback poderá alimentar:

-   ajuste de regras;
-   thresholds;
-   analytics;
-   datasets futuros;
-   avaliação do Hermes.

------------------------------------------------------------------------

# 75. Hermes Agent

Decisão:

> Hermes Agent será o motor/orquestrador de IA da plataforma.

Hermes ficará no backend/cloud.

Não nos PDVs.

------------------------------------------------------------------------

# 76. Responsabilidades do Hermes

-   investigar ocorrências;
-   buscar evidências;
-   correlacionar histórico;
-   comparar baselines;
-   resumir timeline;
-   explicar fatores;
-   auxiliar auditor;
-   produzir relatório;
-   sugerir próximos pontos de investigação.

Não deverá:

-   criar fatos operacionais;
-   substituir Event Bus;
-   ser dependência para gravação;
-   ser dependência para Rule Engine;
-   acusar automaticamente pessoas de fraude.

------------------------------------------------------------------------

# 77. Falha do Hermes

Com Hermes indisponível:

``` text
ingest           OK
events           OK
telemetry        OK
video            OK
rules            OK
risk             OK
occurrences      OK
manual audit     OK
AI analysis      OFFLINE
```

Fila de análise:

``` text
PENDING AI
   |
Hermes returns
   |
process backlog
```

------------------------------------------------------------------------

# 78. Provider/modelo

Hermes será a camada de orquestração.

O provider poderá ser substituível.

Possibilidades futuras:

-   modelos cloud;
-   modelos locais;
-   modelos especializados;
-   visão;
-   multimodal.

------------------------------------------------------------------------

# 79. MCP Server próprio

A plataforma terá um MCP Server oficial.

``` text
                    PLATFORM MCP
                        |
       +----------------+----------------+
       |                |                |
       v                v                v
     HERMES         CLIENT AI       OTHER AGENTS
```

Hermes será o primeiro consumidor.

------------------------------------------------------------------------

# 80. MCP não acessará banco diretamente

Preferência:

``` text
Hermes
 |
 v
DOMAIN TOOL
 |
 v
SERVICE
 |
 v
DATABASE
```

Evitar:

``` text
Hermes -> SQL arbitrário
```

Benefícios:

-   segurança;
-   autorização;
-   multi-tenancy;
-   auditabilidade;
-   estabilidade de contrato.

------------------------------------------------------------------------

# 81. MCP tools - eventos

``` text
search_events
get_event
get_event_sequence
get_transaction_timeline
```

------------------------------------------------------------------------

# 82. MCP tools - transações

``` text
search_transactions
get_transaction
get_transaction_items
get_transaction_payments
```

------------------------------------------------------------------------

# 83. MCP tools - ocorrências

``` text
search_occurrences
get_occurrence
create_occurrence
classify_occurrence
add_occurrence_note
close_occurrence
```

Ações de escrita deverão ter permissões mais restritas.

------------------------------------------------------------------------

# 84. MCP tools - análise

``` text
get_operator_statistics
get_terminal_statistics
get_store_statistics
get_product_history
compare_operator_baseline
compare_terminal_baseline
get_risk_factors
```

------------------------------------------------------------------------

# 85. MCP tools - vídeo

``` text
get_video_clip
get_screen_clip
get_camera_snapshot
```

------------------------------------------------------------------------

# 86. MCP tools - telemetria

``` text
get_scale_timeline
get_telemetry_window
```

------------------------------------------------------------------------

# 87. Skills Hermes

Estrutura imaginada:

``` text
skills/
|
+-- loss-prevention/
+-- pos-auditing/
+-- cancellation-analysis/
+-- cash-withdrawal-analysis/
+-- operator-behavior/
+-- supervisor-analysis/
+-- video-auditing/
+-- retail-fraud-patterns/
+-- occurrence-report/
```

O conhecimento do domínio deve ser progressivamente extraído do código e
organizado em Skills quando apropriado.

------------------------------------------------------------------------

# 88. Exemplo de análise Hermes

Entrada:

``` text
ITEM CANCELLED
Loja 07
PDV 04
Operador 35
R$ 183,40
Risk Score 75
```

Hermes:

``` text
get_occurrence
get_transaction_timeline
get_operator_statistics
compare_operator_baseline
get_product_history
get_video_clip
get_screen_clip
get_scale_timeline
```

Saída desejada:

``` text
O operador apresenta frequência de cancelamentos
3,2x superior ao baseline comparável.

14 de 17 cancelamentos acima de determinado valor
foram associados ao mesmo autorizador.

Timeline:
09:42:11 item registrado
09:42:18 quantidade alterada
09:42:26 cancelamento
09:42:31 gaveta aberta

Há vídeo físico e ScreenCam disponíveis.

Revisão humana recomendada.
```

------------------------------------------------------------------------

# 89. Análise comportamental

O sistema deverá analisar tendências, não apenas incidentes.

Exemplo:

``` text
OPERADOR 35

Cancelamentos:             17
Baseline:                   4

Valor cancelado:       R$ 847
Baseline:              R$ 192

Autorizações por #12:      14

Horário dominante:    18-20h
```

Isso pode alimentar regras e Hermes.

------------------------------------------------------------------------

# 90. Visão computacional

Não é prioridade inicial.

Possibilidades futuras:

-   item passando sem leitura;
-   produto não registrado;
-   troca de etiqueta;
-   divergência visual;
-   self-checkout;
-   comportamento físico;
-   gaveta;
-   carrinho;
-   produto visual versus SKU registrado.

Estratégia:

``` text
PRIMEIRO
eventos estruturados
+
regras
+
timeline
+
vídeo
+
Hermes

DEPOIS
computer vision
```

------------------------------------------------------------------------

# 91. Multi-tenant

Hierarquia possível:

``` text
TENANT
 |
 +-- ORGANIZATION
      |
      +-- NETWORK
           |
           +-- STORE
                |
                +-- DEPARTMENT
                +-- TERMINAL
                +-- CAMERA
```

Modelo final ainda será refinado.

------------------------------------------------------------------------

# 92. RBAC

Perfis possíveis:

-   platform admin;
-   tenant admin;
-   manager;
-   auditor;
-   supervisor;
-   technician;
-   integration/API;
-   read-only;
-   custom.

------------------------------------------------------------------------

# 93. LGPD e privacidade

Precisamos tratar formalmente:

-   imagens de clientes;
-   imagens de funcionários;
-   identificação de operadores;
-   CPF/CNPJ;
-   retenção;
-   minimização;
-   acesso;
-   exportação;
-   logs;
-   evidências;
-   base legal;
-   políticas por tenant.

Não assumir que todo dado disponível no ERP deve ser enviado.

------------------------------------------------------------------------

# 94. Segurança

Requisitos:

-   TLS;
-   autenticação;
-   autorização;
-   secrets management;
-   rotação;
-   tenant isolation;
-   audit log;
-   rate limits;
-   assinatura/verificação quando aplicável;
-   proteção de evidências;
-   trilha de ações do Hermes;
-   trilha de ações humanas.

------------------------------------------------------------------------

# 95. Observabilidade

Desde a PoC devemos coletar:

``` text
event ingest latency
event rate
duplicate rate
retry count
offline backlog
clock drift
video latency
video bitrate
ScreenCam CPU
ScreenCam RAM
MCP latency
Hermes latency
AI cost
rule hit rate
false positive feedback
```

------------------------------------------------------------------------

# 96. Arquitetura consolidada

``` text
                           CLIENTES / ERP
                                |
             +------------------+------------------+
             |                  |                  |
             v                  v                  v
            REST               SDK              STREAM
             |                  |                  |
             +------------------+------------------+
                                |
                                v
                       INTEGRATION GATEWAY
                                |
                    +-----------+-----------+
                    |                       |
                    v                       v
               EVENT INGEST          TELEMETRY INGEST
                    |                       |
                    v                       v
                EVENT BUS              TELEMETRY BUS
                    |                       |
                    +-----------+-----------+
                                |
                                v
                         TIMELINE ENGINE
                                |
        +-----------------------+-----------------------+
        |                       |                       |
        v                       v                       v
   RULE ENGINE             VIDEO ENGINE            ANALYTICS
        |                       |                       |
        v                       |                       |
   RISK ENGINE                  |                       |
        |                       |                       |
        +-----------------------+-----------------------+
                                |
                                v
                           OCCURRENCES
                                |
                    +-----------+-----------+
                    |                       |
                    v                       v
                  MCP                    AUDIT WEB
                    |
                    v
               HERMES AGENT
```

------------------------------------------------------------------------

# 97. Componentes conceituais

``` text
platform/
|
+-- integration-gateway/
|   +-- rest-api/
|   +-- sdk/
|   +-- webhooks/
|   +-- streaming/
|
+-- event-ingest/
+-- telemetry-ingest/
+-- event-bus/
+-- telemetry-bus/
+-- event-store/
+-- telemetry-store/
+-- timeline-service/
|
+-- rule-engine/
+-- risk-engine/
+-- occurrence-service/
|
+-- video-engine/
|   +-- rtsp/
|   +-- onvif/
|   +-- nvr-adapters/
|   +-- screencam/
|
+-- ai/
|   +-- hermes/
|   +-- mcp-server/
|   +-- skills/
|
+-- audit-web/
+-- analytics/
+-- admin/
+-- auth/
+-- observability/
```

------------------------------------------------------------------------

# 98. PoC - filosofia

Não devemos começar tentando construir o produto inteiro.

A PoC deve provar os riscos técnicos fundamentais:

1.  captura de tela;
2.  vídeo;
3.  ingest de evento;
4.  sincronismo;
5.  timeline;
6.  regra;
7.  ocorrência;
8.  MCP;
9.  Hermes.

------------------------------------------------------------------------

# 99. PoC Fase 1 - ScreenCam

``` text
Linux Mint
   |
   v
FFmpeg
   |
   v
MediaMTX
   |
   v
RTSP
   |
   +--> VLC
   +--> NVR REAL
```

Medir:

-   CPU;
-   RAM;
-   FPS;
-   bitrate;
-   qualidade;
-   latência;
-   estabilidade.

------------------------------------------------------------------------

# 100. PoC Fase 2 - Event API

Criar:

``` text
POST /events
```

E um simulador de PDV.

Não depender de StarTwo.

Simular:

``` text
open session
start transaction
add item
cancel item
subtotal
payment
drawer
complete
```

------------------------------------------------------------------------

# 101. PoC Fase 3 - Timeline

Associar:

``` text
event
+
physical camera
+
ScreenCam
```

Criar visualização simples.

------------------------------------------------------------------------

# 102. PoC Fase 4 - Rule Engine

Regras mínimas.

Exemplos:

``` text
cancelamento > X
gaveta sem evento financeiro
cancelamentos repetidos
mesmo autorizador
```

------------------------------------------------------------------------

# 103. PoC Fase 5 - MCP + Hermes

Criar poucas tools:

``` text
get_occurrence
get_transaction_timeline
get_operator_statistics
get_video_clip
get_screen_clip
```

Hermes deve investigar uma ocorrência usando apenas MCP.

------------------------------------------------------------------------

# 104. PoC Fase 6 - telemetria

Simular balança:

``` text
1 amostra/segundo
```

Correlacionar com item e vídeo.

------------------------------------------------------------------------

# 105. Métricas da PoC - eventos

-   p50/p95/p99 ingest latency;
-   events/sec;
-   duplicidade;
-   perda;
-   retry;
-   backlog;
-   replay;
-   ordering.

------------------------------------------------------------------------

# 106. Métricas da PoC - vídeo

-   CPU;
-   RAM;
-   bitrate;
-   FPS;
-   latency;
-   dropped frames;
-   reconnection;
-   clip retrieval time.

------------------------------------------------------------------------

# 107. Métricas da PoC - timeline

-   clock drift;
-   correlação evento/vídeo;
-   diferença `occurred_at`/`received_at`;
-   precisão do clip.

------------------------------------------------------------------------

# 108. Métricas da PoC - Hermes

-   duração da análise;
-   número de tools;
-   tokens/custo;
-   taxa de falhas;
-   utilidade avaliada pelo auditor;
-   evidências citadas;
-   backlog.

------------------------------------------------------------------------

# 109. Matriz Nextop -\> aprendizado -\> nossa decisão

  -----------------------------------------------------------------------
  Elemento documentado    Conhecimento extraído   Nossa decisão inicial
  ----------------------- ----------------------- -----------------------
  DLL/SO                  software houses         API pública + SDK
                          precisam de interface   opcional
                          simples                 

  UDP 8090                eventos enviados em     ingest orientado a
                          tempo real              eventos

  número do caixa         terminal é entidade     `terminal_id` explícito
                          central                 

  abertura/fechamento     sessão de caixa importa `cash_session.*`

  fundo/sangria           movimentação financeira `cash.*`
                          importa                 

  tipo de caixa           baseline depende do     `terminal_type`
                          terminal                

  tipo operação           nem toda transação é    transaction type
                          venda                   

  eventos PDV             contexto técnico        `terminal.*`
                          importa                 

  abertura cupom          ciclo precisa ser       `transaction.started`
                          reconstruído            

  cancelamento            semânticas distintas    dois eventos diferentes
  antes/depois                                    

  desconto/acréscimo      valor e percentual      payload explícito
                          importam                

  cliente/vendedor        papéis distintos        entidades distintas

  autorizador             autorização é contexto  vínculo explícito
                          de risco                

  item digitado           método de captura       `capture.method`
                          importa                 

  item pesado             contexto da balança     `weighed_in_store`
                          importa                 

  cancelamento item       item é evento auditável `item.cancelled`

  consulta item           ações intermediárias    `item.queried`
                          importam                

  departamento            baseline por categoria  product taxonomy

  item desconhecido       falhas de cadastro      `item.unknown`
                          importam                

  manual release          protocolo deve evoluir  schemas versionados

  subtotal                comandos intermediários timeline completa
                          importam                

  pagamentos múltiplos    1:N pagamentos          payment entity

  troco                   fato deve ser           `change.registered`
                          registrado              

  gaveta                  evento físico           `cash.drawer_opened`
                          importante              

  peso 1 Hz               existe telemetria       Telemetry Bus
                          contínua                

  sem timestamp explícito contrato moderno deve   `occurred_at`
                          carregar tempo          

  sem event ID explícito  retry precisa de        `event_id`
                          identidade              

  sem line ID explícito   cancelamento pode ser   `line_id`
                          ambíguo                 
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 110. Perguntas ainda sem resposta sobre Nextop/CASH

-   como os datagramas são estruturados?
-   existe ACK?
-   existe retry?
-   existe buffer?
-   como funciona offline?
-   como a loja é identificada?
-   como o timestamp é definido?
-   como os eventos são persistidos?
-   como o CASH associa caixa e câmera?
-   existe mapa PDV ↔ câmera?
-   como o vídeo é consultado?
-   quais NVRs/VMS são suportados?
-   como relógios são sincronizados?
-   como alertas são criados?
-   como ocorrências são criadas?
-   quais regras existem?
-   existe score?
-   como funciona auditoria?
-   como Enterprise consome CASH?
-   como o vídeo da tela é tratado, se houver?
-   como SmartCart interage além dos eventos documentados?

Essas perguntas não impedem o desenho inicial do nosso produto.

------------------------------------------------------------------------

# 111. Decisões já tomadas

-   produto ERP-agnostic;
-   API-first;
-   SDKs opcionais;
-   MCP como interface de IA;
-   Hermes Agent como AI Engine;
-   Hermes fora do PDV;
-   ScreenCam como componente;
-   Linux Mint como plataforma prioritária da primeira PoC ScreenCam;
-   eventos e vídeo desacoplados, unidos pela timeline;
-   regras determinísticas antes da IA;
-   IA não é dependência funcional;
-   multi-tenant desde a arquitetura;
-   protocolo próprio;
-   benchmark Nextop usado como conhecimento, não como integração.

------------------------------------------------------------------------

# 112. Decisões ainda abertas

## Backend

-   linguagem;
-   framework;
-   arquitetura de serviços.

## Banco

-   PostgreSQL;
-   Timescale;
-   ClickHouse;
-   combinação;
-   outro.

## Bus

-   NATS;
-   Kafka;
-   RabbitMQ;
-   outro.

## Vídeo

-   MediaMTX definitivo ou PoC;
-   armazenamento;
-   retenção;
-   NVR adapters;
-   object storage.

## Infra

-   Docker/Portainer;
-   Kubernetes;
-   híbrido.

## IA

-   provider inicial;
-   modelo inicial;
-   multimodal;
-   vision model.

## Comercial

-   nome;
-   licenciamento;
-   pricing;
-   SaaS/on-prem;
-   canais;
-   certificação de ERP.

------------------------------------------------------------------------

# 113. Pendências críticas

## P0 - Protocolo de eventos

Transformar o modelo canônico em especificação formal.

Entregáveis futuros:

``` text
event-protocol.md
event-schema.json
openapi.yaml
```

## P0 - Taxonomia

Revisar e congelar primeira versão.

## P0 - Timestamp/sincronismo

Definir política.

## P0 - Idempotência/offline

Definir store-and-forward.

## P1 - ScreenCam PoC

Validar em Linux Mint + NVR real.

## P1 - Timeline

Provar correlação evento ↔ vídeo.

## P1 - Rule Engine

Definir modelo inicial.

## P1 - MCP/Hermes

Provar investigação end-to-end.

------------------------------------------------------------------------

# 114. Roadmap macro

``` text
FASE 0
Pesquisa / benchmark / requisitos
        |
        v
FASE 1
Event Protocol + OpenAPI
        |
        v
FASE 2
ScreenCam PoC
        |
        v
FASE 3
Event Core + Telemetry
        |
        v
FASE 4
Timeline + Video
        |
        v
FASE 5
Rules + Risk + Occurrences
        |
        v
FASE 6
MCP + Hermes
        |
        v
FASE 7
SDKs + ERP adapters
        |
        v
FASE 8
Escala + segurança + produto
        |
        v
FUTURO
Computer Vision / Self-checkout / automações
```

------------------------------------------------------------------------

# 115. Possível estratégia de integração comercial

Software houses poderão escolher:

``` text
OPÇÃO A
Integrar diretamente REST API

OPÇÃO B
Usar SDK oficial

OPÇÃO C
Instalar Connector/Agent

OPÇÃO D
Streaming para grandes redes
```

Certificações futuras:

``` text
Certified Integration
- ERP A
- ERP B
- ERP C
```

------------------------------------------------------------------------

# 116. Diferenciais que podem emergir

Ainda não são promessas comerciais fechadas, mas o brainstorm aponta
diferenciais potenciais:

-   protocolo aberto;
-   ERP-agnostic;
-   ScreenCam;
-   câmera física + tela sincronizadas;
-   event timeline;
-   telemetria;
-   Risk Engine explicável;
-   Hermes via MCP;
-   integração com agentes externos;
-   APIs modernas;
-   buffer offline;
-   multi-tenant;
-   implantação cloud/on-prem;
-   análise por sequência;
-   feedback humano.

------------------------------------------------------------------------

# 117. Norte de produto

A unidade fundamental do sistema não é a câmera.

Também não é o cupom.

É a **ocorrência contextualizada no tempo**.

Ela poderá reunir:

``` text
EVENTOS
+
TRANSAÇÃO
+
OPERADOR
+
AUTORIZADOR
+
PRODUTO
+
PAGAMENTO
+
TELEMETRIA
+
CÂMERA FÍSICA
+
SCREENCAM
+
REGRAS
+
HISTÓRICO
+
ANÁLISE HERMES
```

------------------------------------------------------------------------

# 118. Visão final consolidada

``` text
                       QUALQUER ERP / PDV
                              |
               +--------------+--------------+
               |              |              |
              REST           SDK           STREAM
               |              |              |
               +--------------+--------------+
                              |
                              v
                      INTEGRATION GATEWAY
                              |
                   +----------+----------+
                   |                     |
                   v                     v
               EVENTS               TELEMETRY
                   |                     |
                   +----------+----------+
                              |
                              v
                         TIMELINE
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
       RULES                VIDEO             ANALYTICS
          |                   |                   |
          v          +--------+--------+          |
        RISK          |                 |          |
          |           v                 v          |
          |       PHYSICAL CAM       SCREENCAM     |
          |           |                 |          |
          +-----------+--------+--------+----------+
                              |
                              v
                         OCCURRENCES
                              |
                    +---------+---------+
                    |                   |
                    v                   v
                  AUDIT                MCP
                                        |
                                        v
                                   HERMES AGENT
                                        |
                                        v
                                ASSISTED ANALYSIS
```

------------------------------------------------------------------------

# 119. Próximos documentos derivados

Este brainstorm não deve virar uma especificação monolítica para sempre.

À medida que o projeto amadurecer, devemos separar:

``` text
/docs

00-brainstorm.md
01-product-vision.md
02-domain-model.md
03-event-protocol.md
04-event-catalog.md
05-telemetry-protocol.md
06-openapi.md
07-video-architecture.md
08-screencam.md
09-timeline-engine.md
10-rule-engine.md
11-risk-engine.md
12-occurrences.md
13-mcp.md
14-hermes.md
15-security.md
16-multitenancy.md
17-observability.md
18-poc-plan.md
19-roadmap.md
20-nextop-benchmark.md

/adrs
ADR-001-api-first.md
ADR-002-hermes-ai-engine.md
ADR-003-mcp-domain-tools.md
ADR-004-event-time.md
ADR-005-screencam.md
...
```

------------------------------------------------------------------------

# 120. Regra para evolução deste documento

Toda nova informação deve ser marcada mentalmente ou formalmente como
uma destas categorias:

``` text
FACT
    comprovado por fonte/manual/teste

INFERENCE
    conclusão plausível ainda não comprovada

DECISION
    escolha arquitetural nossa

IDEA
    possibilidade ainda em avaliação

PENDING
    pergunta ou decisão em aberto
```

Isso evita que inferências antigas se transformem acidentalmente em
"fatos" durante o desenvolvimento.

------------------------------------------------------------------------

# 121. Status atual do projeto

## Concluído conceitualmente

-   visão geral;
-   independência de ERP;
-   API-first;
-   Hermes;
-   MCP;
-   ScreenCam;
-   importância da timeline;
-   separação regras/IA;
-   estudo do contrato Nextop;
-   catálogo inicial de eventos;
-   telemetria reconhecida como domínio próprio.

## Próximo marco recomendado

Formalizar:

1.  **Domain Model v0.1**
2.  **Event Catalog v0.1**
3.  **Canonical Event Envelope v0.1**
4.  **Telemetry Envelope v0.1**
5.  **OpenAPI v0.1**
6.  **PoC ScreenCam**
7.  **PoC end-to-end evento → timeline → vídeo → regra → ocorrência →
    MCP → Hermes**

------------------------------------------------------------------------

# 122. Resumo executivo

A análise do manual Nextop alterou o projeto de forma importante.

Antes, a ideia poderia ser percebida principalmente como:

``` text
TELA DO PDV -> CÂMERA VIRTUAL -> NVR
```

Agora o projeto está definido de forma muito mais ampla:

``` text
PDV
 |
 +--> EVENTOS
 |
 +--> TELEMETRIA
 |
 +--> SCREENCAM

CFTV
 |
 +--> CÂMERA FÍSICA

                |
                v
             TIMELINE
                |
                v
              RULES
                |
                v
               RISK
                |
                v
           OCCURRENCES
                |
                v
               MCP
                |
                v
             HERMES
                |
                v
         AUDITORIA HUMANA
```

O manual Nextop mostrou que uma solução madura valoriza eventos
detalhados e contínuos do checkout. Nossa proposta evolui esse conceito
com identidade explícita, timestamps, idempotência, protocolo aberto,
telemetria separada, timeline, ScreenCam, Risk Engine explicável, MCP e
Hermes.

Esse é, até o momento, o norte técnico consolidado do projeto.
