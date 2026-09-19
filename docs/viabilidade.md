# Termo de abertura e estudo de viabilidade

Data: 2026-09-19. Status: rascunho de planejamento; autorização para bootstrap e documentação.
Patrocinador: Wittemberg. Produto: P3 (nome comercial ainda não aprovado).

## Objetivo e resultado

Criar plataforma independente de ERP para reduzir tempo de investigação de perdas
com timeline e evidências, preservando decisão humana. Nesta entrega: repositório,
base local verificável, plano técnico e operacional, pipeline e guia de implantação.
O produto comercial completo será entregue por mudanças futuras do roadmap.

## Viabilidade técnica

Favorável para bootstrap e provas sintéticas no host existente. Condicionada para
piloto: testar clocks, buffer offline, isolamento, captura Linux Mint, compatibilidade
NVR e obtenção de evidências históricas. Um host de 4 GiB não está dimensionado para
reter vídeo de múltiplas lojas nem hospedar inferência pesada. Vídeo inicialmente
permanece no NVR/edge, com clips selecionados conforme política validada.

## Viabilidade financeira

Não comprovada sem orçamento e volumes. Modelo de custo mensal: infraestrutura +
armazenamento/backup + tráfego de vídeo + suporte/operação + licença Portainer BE
(se escolhida) + consumo de modelos. Dimensionar vídeo por bitrate × duração × câmeras
× retenção, incluindo cópias de segurança. Medir tokens/análise e análises/dia antes
de contratar IA. Receita, preço, margem e prazo de retorno precisam de dados do
patrocinador; não há estimativa inventada nem contratação autorizada neste documento.

## Viabilidade operacional

Exige responsáveis por instalação de PDV, cadastro de câmera, triagem, incidentes,
restauração e revisão de acesso. Propor Wittemberg como dono de infraestrutura e
representante do piloto como aprovador de negócio; nomes precisam de confirmação.
Treinamento: auditor executa ocorrência sintética, registra conclusão e reconhece
vídeo indisponível; operador pratica rollback e restauração antes de entrada real.

## Riscos e decisões de passagem

| Risco | Mitigação | Gate / responsável proposto |
|---|---|---|
| Evidência dessincronizada | medir drift e sinalizar incerteza | PoC / integrador |
| Dados expostos entre clientes | testes negativos de isolamento | piloto / engenharia |
| Falha do host | backup externo e restore ensaiado | produção / operações |
| Custos de vídeo/IA | limites e medição por tenant | contratação / patrocinador |
| Alarmes excessivos | calibração e feedback com auditor | UAT / dono do produto |
| CE sem webhook de stack | decisão explícita BE ou alternativa | deploy / patrocinador |

Sucesso desta abertura não significa viabilidade comercial aprovada. Cada marco
exige evidência conforme qualidade-operacao.md; escopo muda por OpenSpec e ADR quando durável.
