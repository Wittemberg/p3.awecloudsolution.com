# Inventário do servidor

Inspeção somente leitura em 2026-09-19; não é auditoria completa de segurança.

| Item | Observado |
|---|---|
| SO | Ubuntu 24.04.5 LTS |
| CPU / RAM / swap | 6 CPUs lógicas; 4 GiB RAM; 2 GiB swap |
| Disco raiz | 98 GiB total; 86 GiB disponíveis na inspeção |
| Docker | 29.8.1; Swarm ativo, um manager e um nó |
| Rede | overlay externa `interna` |
| Proxy | `traefik_traefik`, Traefik v3.5.3; web/websecure; letsencryptresolver |
| Portainer | `portainer_portainer`, atualizado pelo usuário para portainer-ee:latest; API informa 2.45.1; agente global |
| Painel | https://wit-portainer.awecloudsolution.com |
| Banco | `postgres_postgres`, PostgreSQL 14; volume postgres_data; sem porta publicada |
| pgAdmin | `pgadmin_pgadmin`, dpage/pgadmin4:latest |
| DNS P3 | resolução IPv4 para 177.136.234.234, nome canônico wit-servidor.awecloudsolution.com |
| Ferramentas host | Python 3.12.3; node/npm/gh/pip ausentes na inspeção |
| SSH GitHub | chave existente /root/.ssh/chavewit validada explicitamente |

Todos os serviços listados estavam 1/1. Portas ouvindo incluem 80/443, SSH 5822,
111, 2377 e 7946; escuta não prova acessibilidade externa. Revisar firewall de
Swarm/RPC por origem autorizada; regras não foram alteradas. Traefik estava em DEBUG.
Tags `latest` existentes reduzem reprodutibilidade: propor fixação por versão/digest
em manutenção própria. Backup, restore, monitoramento, criptografia de disco e política
de retenção existentes não foram comprovados. Não coletados ambientes de containers,
senhas, tokens ou conteúdo de chaves privadas.

O banco compartilhado será preservado. Propor banco/role exclusivos de P3 e rede
restrita em mudança futura. Bootstrap não se conecta ao PostgreSQL.

Atualização confirmada: imagem EE com digest
`sha256:0cd22f754ac52fcfceb362d5ce8f47ee23a5f6427484db17ebfaa4c8a00f7718`.
Status público não comprova licença ativa nem permissão administrativa.

P3 implantado: stack Portainer ID 3, ambiente primary ID 1, registry GHCR ID 1.
Serviço p3_app usa overlay interna e router TLS p3; PostgreSQL permanece intocado.
Webhook autenticado pela URL secreta testado; HTTPS público e revisão confirmados.
