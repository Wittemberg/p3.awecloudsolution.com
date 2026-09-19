# Qualidade, operação e rastreabilidade

## Cobertura do ciclo A–H

| Processo | Artefato canônico / gate |
|---|---|
| A Concepção | viabilidade.md; orçamento/piloto validados antes de compromisso comercial |
| B Requisitos | prd.md e mudança OpenSpec; cenários e fontes explícitos |
| C Arquitetura | trd.md + ADRs; schemas e migrações por mudança |
| D Construção | testes, Dockerfile, workflow; revisão do diff antes de push |
| E QA | matriz abaixo; UAT humano com evidências |
| F Deploy | deploy.md; SHA servido deve coincidir com release |
| G Operação | health, logs, backup/restore e rollback ensaiados |
| H Transversais | Git, ADR, riscos e estado-atual.md; tarefas no OpenSpec |

## Matriz de testes do produto (planejada)

| Requisito | Verificação / evidência exigida |
|---|---|
| US01/NFR02 | enviar, confirmar, reiniciar, reenviar; comparar conjunto de IDs e efeitos |
| US01/NFR01 | carga sustentada com p50/p95/p99, taxa de erro, CPU, RAM, backlog |
| US02 | câmera física + ScreenCam; drift conhecido, NVR offline e clip expirado |
| US03 | regras limítrofes, eventos tardios, concorrência e trilha de conclusão |
| US04/NFR03 | matriz de dois tenants em API, banco, exportação, clips e MCP |
| US05 | Hermes fora, timeout, injeção na evidência e resposta sem referência |
| NFR04 | restauração em ambiente isolado; registrar RPO/RTO medidos |
| NFR08 | teclado e viewport 360/768/1366/1920; zoom 100%; sem overflow |

Suíte atual cobre somente bootstrap. Não confundir teste unitário com teste de hardware,
segurança integral, carga ou UAT. Evidências realizadas ficam em estado-atual.md.

## Operação

Health do bootstrap prova HTTP disponível, não banco/vídeo/IA. Quando existirem,
separar liveness/readiness e estados degradados. Logs sem senhas, CPF ou URLs secretas;
limitar tamanho e retenção. Alertar por erros, backlog persistente, disco e certificados.
Responsável inicial proposto: Wittemberg; escala de atendimento a pactuar no piloto.

P0: perda de evento confirmado, vazamento entre tenants ou indisponibilidade crítica;
interromper rollout/coleta afetada, preservar evidência e mitigar. P1: funcionalidade
importante degradada com caminho operacional; P2: refinamento. Registrar causa,
responsável, correção, teste de regressão e homologação antes de encerrar defeito.

Backup: política a validar antes de usar PostgreSQL; propor cópia diária externa,
criptografada, retenção definida pelo responsável e restore periódico isolado. Vídeos
e banco têm políticas diferentes. Nenhum backup existente foi comprovado.

Deploy: serializar por ambiente, usar imagem identificada por SHA, monitorar health e
revision. Falha → manter/retornar imagem anterior conhecida; dados exigem plano próprio.
Treinamento/UAT: auditor executa caso procedente, improcedente, inconclusivo e evidência
ausente; integrador simula rede interrompida; operador ensaia rollback e restore.
Aceite precisa de responsável, data e resultado, não apenas checkbox automático.
