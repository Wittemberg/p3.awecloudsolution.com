# P3 — Plataforma de prevenção de perdas

Base inicial executável; funcionalidades de negócio ainda não implementadas.
Repositório: https://github.com/Wittemberg/p3.awecloudsolution.com

## Executar e verificar

```sh
docker build --target test -t p3-test .
docker compose up -d --build
curl --fail http://127.0.0.1:18003/api/health
curl --fail http://127.0.0.1:18003/api/hello
```

A página inicial está em http://127.0.0.1:18003/. Encerrar com `docker compose down`.
Alternativa Python 3.12: ambiente virtual, instalar com `pip install -c constraints.txt -r requirements-dev.txt`, executar
`python -m pytest -q` e `uvicorn app.main:app --host 127.0.0.1 --port 18003`.
Não há credenciais nem dependência de banco/LLM no bootstrap.

## Documentação

- [Estado e evidências](docs/estado-atual.md)
- [Novo brainstorm](docs/brainstorm-plataforma-v0.3.md)
- [PRD global](docs/prd.md), [TRD](docs/trd.md), [roadmap](docs/roadmap.md)
- [Abertura e viabilidade](docs/viabilidade.md)
- [Inventário do servidor](docs/infraestrutura.md)
- [Configuração GHCR, Portainer e Actions](docs/deploy.md)
- [QA, operação e rastreabilidade](docs/qualidade-operacao.md)

## Processo e origem

Harness portátil em `.harness/`, revisão `9dbc93d105de52d855f7e0cdd4671aa97c3c8352`.
Origem: https://github.com/Wittemberg/harness-skills. Preservados os avisos de terceiros.
Baseline corporativa: `.harness/standards/wittemberg/README.md`.
Base Python/FastAPI mínima própria: o boilerplate foi avaliado, mas não copiado,
pois traz LangChain/agente prematuro e licença não declarada. Hermes é etapa futura.
OpenSpec guarda requisitos/tarefas da mudança; PRD guarda visão global.

## Contratos M1

[Event Protocol 0.1.0](docs/contracts/event-protocol-0.1.0.md) e
[identidade de integração](docs/contracts/integration-identity.md).
Contratos públicos em `/api/contracts/0.1.0/event.schema.json` e
`/api/contracts/0.1.0/openapi.json`. A ingestão persistente continua no M3.
