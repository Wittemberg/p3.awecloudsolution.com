# Bootstrap da plataforma P3

## Why
O projeto precisa de uma base executável e rastreável antes dos contratos de negócio.
Servidor existente exige convivência com Swarm, Portainer, Traefik e PostgreSQL.

## What Changes
- Preservar brainstorm original e registrar revisão, PRD, TRD, ADRs e roadmap.
- Criar aplicação mínima de disponibilidade, container e stack preparada.
- Testar localmente; configurar CI/publicação GHCR e deploy condicionado ao webhook.
- Registrar credenciais necessárias e diferenças CE/BE sem alterar serviços existentes.

## Capabilities
### New Capabilities
- `platform-bootstrap`: execução local e preparação verificável de entrega.

### Modified Capabilities
Nenhuma.

## Impact
Novos arquivos e container local. Sem migração de dados ou acesso ao PostgreSQL.
Webhook/stack gerenciada dependem de Portainer compatível e credencial ainda ausente.
