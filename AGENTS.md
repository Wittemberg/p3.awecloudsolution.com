<!-- harness-skills:start -->
## Biblioteca de desenvolvimento de Wittemberg

Leia [.harness/AGENTS.md](.harness/AGENTS.md) para selecionar skills e padrões aplicáveis à tarefa. Os caminhos desse documento são relativos à pasta `.harness/`.

Preserve as decisões e instruções deste projeto. Use a biblioteca sob demanda, sem carregar todos os snapshots ou ativar ferramentas externas automaticamente.
<!-- harness-skills:end -->

## Projeto P3

Leia `docs/estado-atual.md` e a mudança ativa antes de implementar.
Siga `.harness/docs/manual.md`. Uma mudança OpenSpec por vez.
PRD global em `docs/prd.md`; arquitetura em `docs/trd.md` e `docs/adrs/`.
Tarefas canônicas em `openspec/changes/`; não criar pipeline SDD paralelo.
Teste: `docker build --target test -t p3-test .`.
Local: `docker compose up -d --build`; smoke em `127.0.0.1:18003`.
Nunca versionar segredos, URLs secretas de webhook ou dados reais de clientes.
Não alterar stacks existentes nem migrar PostgreSQL compartilhado incidentalmente.
Premissas propostas não são aprovação de produto. Não declarar deploy por HTTP 2xx do webhook.
