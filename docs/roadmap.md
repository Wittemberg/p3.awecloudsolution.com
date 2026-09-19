# Roadmap por evidências

Sem datas comerciais assumidas. Este documento ordena marcos; tarefas ficam somente
na mudança OpenSpec ativa. Não iniciar a seguinte até concluir ou delimitar a anterior.

| Marco | Entrega / dependência | Critério de passagem |
|---|---|---|
| M0 — Fundação | bootstrap-platform, documentos, Git, CI e preparação deploy | testes locais; specs válidas; pendências externas explícitas |
| M1 — Contrato e identidade | catálogo, OpenAPI, JSON Schema, credencial de integração | contratos válidos/inválidos, tenant forjado e conflito de ID testados |
| M2 — Prova ScreenCam | Linux Mint real, FFmpeg/MediaMTX candidatos e NVR | gravação, reconexão, busca histórica, CPU/RAM/latência medidos |
| M3 — Núcleo durável | ingestão, outbox, replay e telemetria separada | NFR01–03 com restart e indisponibilidade |
| M4 — Timeline e vídeo | M2/M3, mapeamento temporal e clips | janela correta, drift e ausência visíveis em UAT |
| M5 — Regras e ocorrências | fatores/versionamento, workflow, feedback | auditor reconstrói regra e conclui caso com trilha |
| M6 — MCP/Hermes | autorização e ferramentas limitadas | evidências citadas, teste de prompt injection, custo e fallback |
| M7 — Piloto e produto | adapter ERP, restore, carga, operação e treinamento | aceite do piloto + revisão de segurança/capacidade |

Visão computacional, multi-região e SDKs adicionais são oportunidades posteriores.
Segurança, testes, privacidade e observabilidade atravessam todos os marcos; não são
adiados para uma fase final. Nenhum marco de negócio está entregue pelo Hello World.
