# Brainstorm — Plataforma P3 v0.3

**Lente:** especificação de projeto de desenvolvimento. **Sessão:** 2026-09-19.
Retomada integral da v0.2 (seções 0–122), preservada como fonte histórica.
Documentação e bootstrap autorizados pelo pedido do usuário; propostas de produto
abaixo não equivalem a homologação de implementação futura.

## Problema

Auditar perdas exige reunir fatos dispersos do PDV, contexto e vídeo. A unidade de
valor é uma ocorrência contextualizada, revisável por uma pessoa, sem inferir fraude
apenas de um cancelamento, score ou resposta de IA.

## Requisitos de negócio

Auditor consulta sequência, evidências e lacunas; supervisor triage e conclui com
justificativa; administrador delimita lojas e acesso; integrador envia fatos sem
implementar regras do produto. ERP independente, regras explicáveis, feedback humano
e operação sem IA permanecem decisões da v0.2. SuperTop é contexto potencial de
piloto, não compromisso confirmado de acesso a equipamento ou dados.

## Requisitos técnicos

Para auditoria confiável: identidade de evento, persistência antes de confirmação,
replay idempotente e relógios explicitamente qualificados. Para integração aberta:
contrato próprio versionado. Para evidência: mapeamento temporal terminal/câmera,
disponibilidade e integridade dos clips. Para segregação comercial: tenant derivado
da credencial. Para operação simples: propor monólito modular e PostgreSQL,
extraindo processos somente com medição que justifique custo operacional.

## Não-funcionais

| Dimensão | Proposta / restrição | Estado |
|---|---|---|
| Volume | Piloto sintético antes de capacidade contratual; metas no TRD | Inferido |
| Resposta | Confirmação exige durabilidade; processamento posterior assíncrono | Inferido |
| Acesso | Papéis auditor, supervisor, administrador e integração separados | Inferido |
| Dados | Minimizar identidade pessoal e conteúdo capturado; validar retenção antes de piloto real | Inferido |
| Falhas | Offline no conector; IA indisponível não interrompe ingestão | Decidido na v0.2 |
| Integrações | ERP/NVR reais ainda precisam de prova de compatibilidade | Inferido |
| Hospedagem | Docker Swarm/Portainer neste servidor | Decidido pelo usuário |
| Operação | Wittemberg como responsável inicial, a confirmar | Inferido |
| Orçamento/prazo | Não fornecidos; viabilidade condicionada, sem preço ou data prometidos | Pendente de informação |

## Estados

| Item | Estado | Fonte/Premissa | Data |
|---|---|---|---|
| API-first, Hermes backend, MCP, ScreenCam | Decidido | v0.2 §111 | 2026-09-19 |
| Docker, GHCR, Actions e domínio | Decidido | pedido atual | 2026-09-19 |
| Swarm único nó, 4 GiB RAM, PostgreSQL 14 | Verificado | inspeção local; infraestrutura.md | 2026-09-19 |
| Stack webhook requer BE; instalação é CE | Verificado | documentação Portainer e imagem instalada | 2026-09-19 |
| FastAPI e monólito modular | Inferido | reduzir complexidade inicial; ADR-002 proposto | 2026-09-19 |
| Piloto e limiares de qualidade | Inferido | TRD e plano de QA; precisam de validação | 2026-09-19 |

## Divergências e correções propostas

1. `transaction.subtotal` (§17/68) diverge de `transaction.subtotal_requested`
   (§36/47): adotar o segundo no catálogo inicial; exemplo de timeline não cria tipo.
2. `quantity changed` aparece em timeline, mas não no catálogo: especificar antes
   de permitir; desconhecidos devem ser rejeitados, não interpretados silenciosamente.
3. §46 chama envelope v0.1 com `schema_version: 1.0`: usar versão preliminar coerente;
   só congelar 1.0 após testes de contrato. `received_at` pertence ao servidor.
4. Números monetários binários podem perder precisão: propor decimal textual com
   moeda explícita; quantidade e peso também têm escala/unidade definidas.
5. `tenant_id` recebido não autoriza acesso: identidade autenticada governa tenant
   e escopo de loja; rejeitar divergência, incluindo consultas e MCP.
6. `received_at - occurred_at` inclui clock drift e offline: não chamar essa diferença
   de latência da API. Medir duração HTTP separadamente e preservar offset estimado.
7. Event-driven não exige todos os componentes como microserviços nem event sourcing
   completo. Separar eventos/telemetria logicamente antes de impor dois brokers.
8. RTSP não garante descoberta ONVIF nem histórico no NVR. Validar gravação, busca,
   reconexão, X11/Wayland e consumo no hardware real; não prometer compatibilidade universal.
9. Hash simples de CPF pode ser enumerado: preferir não coletar; pseudonimização
   precisa de chave/contexto e política. Hash não torna vídeo ou pessoas anônimos.
10. Captura de tela pode revelar pagamentos e dados pessoais: definir regiões,
    mascaramento e permissões antes da coleta, não apenas na exportação.
11. Único nó não entrega alta disponibilidade. Limitar o ambiente a preparação/piloto
    até backup, restauração e capacidade medidos. Não atualizar o PostgreSQL compartilhado.
12. Webhook de stack BE conflita com CE observado. Propor BE ou selecionar alternativa
    CE com novo design; não trocar silenciosamente por webhook de serviço/API administrativa.

## Alternativas descartadas

| Alternativa | Motivo / trade-off |
|---|---|
| Microserviços + Kafka já no bootstrap | Custo de RAM/operação sem volume medido; reavaliar por carga |
| LLM no PDV ou no caminho de gravação | Viola independência operacional da IA |
| Copiar boilerplate com LangChain | Dependência antecipada e licença sem declaração; base mínima própria |
| Kubernetes | Contraria escolha atual de Swarm e adiciona operação |
| Confundir score com culpa | Viola revisão humana e qualidade da evidência |

## Pendências

Solicitar definição de lojas/PDVs, operadores simultâneos, volume, retenção e orçamento
antes do dimensionamento produtivo. Validar acesso ao Linux Mint e modelos de NVR
antes de ScreenCam. Confirmar responsável de privacidade, política de acesso e
retenção antes de dados reais. Confirmar BE/alternativa CE e credencial de gestão
antes de criar stack via Portainer. A ausência dessas respostas não bloqueia esta
base técnica nem os documentos em rascunho; bloqueia alegações de produção pronta.
