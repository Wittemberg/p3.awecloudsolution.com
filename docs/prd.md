---
prd_number: "001"
status: rascunho
priority: alta
created: 2026-09-19
depends_on: []
references: [brainstorm-plataforma-v0.3.md, trd.md, roadmap.md]
---
# PRD 001 — Visão global da plataforma P3

## 1. Contexto

Auditores do varejo precisam relacionar fatos de checkout, vídeo físico, tela e
contexto. Hoje há um brainstorm e uma base de instalação; não há fluxos operacionais
entregues. Este PRD é global conforme o manual harness; cenários implementáveis
pertencem a cada mudança OpenSpec. Arquitetura em [TRD](trd.md).

## 2. Solução proposta

Reunir fatos numa timeline auditável, priorizar alertas explicáveis, permitir revisão
humana e oferecer análise assistida opcional. ERP informa fatos; plataforma aplica
regras. Uma ocorrência não prova fraude. O auditor deve distinguir ausência de
evidência, falha técnica e conclusão inconclusiva.

Fora do primeiro piloto: visão computacional, self-checkout, SDK em todas as linguagens,
integração exclusiva StarTwo, compatibilidade binária Nextop e decisões punitivas
pela IA. MCP/Hermes entram após regras e auditoria manual funcionarem.

## 3. Funcionalidades

### US01 — Receber fatos confiáveis
Como integrador, quero transmitir eventos e recuperar atrasados para manter a sequência.
**Rules:** preservar identidade/origem e cancelamentos antes/depois da conclusão.
**Edge cases:** repetição não duplica efeito; mesmo ID com conteúdo diferente informa
conflito; reconexão não reescreve horário original *(premissas de protocolo)*.

### US02 — Investigar timeline e evidências
Como auditor, quero eventos, câmera física e ScreenCam associados para compreender o caso.
**Rules:** mostrar origem, horário e qualidade da correlação; acesso limitado às lojas autorizadas.
**Edge cases:** vídeo expirado ou relógio incerto aparece explicitamente; não fabricar evidência.

### US03 — Triar e concluir ocorrências
Como supervisor, quero fatores explicáveis e histórico de decisões para priorizar revisão.
**Rules:** conclusão humana com justificativa; preservar versão de regra e feedback.
**Edge cases:** fechamento concorrente informa conflito; reabertura guarda histórico
*(premissa — confirme ou corrija)*.

### US04 — Administrar acesso e operação
Como administrador, quero delimitar usuários, lojas e integrações para proteger informações.
**Rules:** papéis e acessos auditados; integração não recebe privilégio administrativo.
**Edge cases:** revogação impede novas consultas; falha de autorização não expõe existência
em outro tenant *(premissa — confirme ou corrija)*.

### US05 — Analisar com Hermes
Como auditor, quero síntese referenciada para acelerar investigação.
**Rules:** ferramentas de domínio com autorização, sem SQL arbitrário; fatos não podem
ser criados pela IA; revisão humana permanece necessária.
**Edge cases:** indisponibilidade mantém trabalho manual; conteúdo de evidência é dado,
não instrução; resposta sem suporte é marcada como não comprovada.

## 4. Fluxo de negócio

Fato → regra → alerta → triagem → ocorrência → revisão → conclusão humana.
Vídeo ausente não implica descarte automático; auditor pode concluir inconclusivo.

## 5. Critérios de aceite

| Critério | Razão | Verificação futura |
|---|---|---|
| Replay não duplica ocorrência | confiança no histórico | reenvio e restart em integração |
| Tenant A não consulta B | segregação de clientes | matriz negativa com dois tenants |
| Regra expõe fatores e versão | explicabilidade | auditor reconstrói cálculo |
| Vídeo ausente tem estado claro | impedir conclusão falsa | UAT com clip expirado |
| Sem Hermes, ingestão e revisão continuam | continuidade operacional | falha induzida |

Métricas: tempo de investigação e precisão de triagem têm baseline a levantar pelo
dono de produto no início do piloto, antes de pactuar metas. Proposta de sucesso:
redução do tempo mediano sem piorar qualidade da revisão; mínimo e prazo quantitativos
precisam ser acordados antes do UAT. Não há alegação de perdas financeiras reduzidas.

## 6. Marcos de produto

1. Histórico confiável (US01/US04): integrador demonstra replay e isolamento.
2. Auditoria contextualizada (US02/US03): auditor revisa evidência e conclui caso.
3. Assistência fundamentada (US05): síntese cita evidências e suporta falha de IA.

Todos aguardam implementação e aceite. Aprovador proposto: Wittemberg com auditor do piloto.
Tarefas de execução somente no OpenSpec; ordenação técnica no roadmap.

## 7. Riscos e dependências

Acesso ao PDV/NVR, taxonomia validada com integrador e política de retenção condicionam
piloto. Dados sintéticos servem ao bootstrap, não demonstram eficácia comercial.
Benchmark Nextop é fonte secundária no brainstorm: manual original não foi fornecido
nesta sessão, portanto suas afirmações não foram revalidadas contra o documento original.

## 8. Referências

[Brainstorm](brainstorm-plataforma-v0.3.md), [TRD](trd.md), [roadmap](roadmap.md).

## 9. Registro de decisões

2026-09-19: preservar independência de ERP, evidência contextualizada e auditoria humana
conforme v0.2. Premissas novas permanecem rascunho; bootstrap não aprova todo o produto.
