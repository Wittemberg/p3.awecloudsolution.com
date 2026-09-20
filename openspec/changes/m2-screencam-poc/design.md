# Design

## Context

Ver proposal.md. M1 está publicado; o servidor Ubuntu não é o Mint do teste.
O usuário ainda preparará esse equipamento. NVR informado: AITEK SIGMA-N210;
firmware a confirmar e acesso dependente de VPN ainda não configurada.
Recursos do servidor são compartilhados (4 GiB RAM); não armazenar vídeo contínuo ali.

## Goals / Non-Goals

**Goals:** kit reproduzível para qualificar X11 → H.264 → RTSP → NVR; falhas observáveis,
configuração persistente e evidências separadas por ambiente.

**Non-Goals:** backend de ingestão, UI de auditoria, retenção produtiva e implementação
de servidor ONVIF. ONVIF/WS-Discovery serão avaliados como compatibilidade, sem presumir
que MediaMTX transforma RTSP em câmera ONVIF. Windows e Wayland exigem outra captura.

## Decisions

- Captura X11 no usuário da sessão, com FFmpeg e região explícita. Evitar container
  privilegiado, `xhost +` e execução root para acessar a tela. Distribuição MediaMTX
  em container; laboratório isolado da stack p3. Integrar stack Portainer somente
  após conhecer a topologia de rede e fixar imagem/configuração verificadas.
- H.264/libx264 e RTSP/TCP como baseline de interoperabilidade; hardware encoder é
  alternativa posterior ao benchmark. Perfil inicial de ensaio: 1280×720, 10 FPS,
  GOP de 2 segundos. Ajustar à região real sem ultrapassar limites da tela.
- Supervisor com configuração em arquivo privado, validação antes de iniciar,
  tentativas 2/5/10/20/30/60 segundos com jitter e parada limpa dos subprocessos.
  Recomeçar backoff somente após período saudável; erro permanente exige correção.
- VPN entre servidor e Mint proposta (Tailscale candidato). NVR preferencialmente
  na LAN do Mint. VPN administra; medir vídeo na LAN e pela VPN separadamente.
  Não anunciar sub-redes nem instalar VPN sem conhecer endpoints e conta.
- Autorização por caminho: publicador separado de leitor; configuração sensível
  fora do Git, logs sem URLs autenticadas. RTSP sem TLS restrito à LAN isolada/VPN.
- Laboratório usa conteúdo sintético e receptor descartável. Arquivos gravados por
  FFmpeg comprovam transporte/decodificação, não compatibilidade com NVR real.
- Relatório inclui média/p95/pico de CPU/RAM e latência quando houver amostras
  suficientes, método, versão, duração, FPS/bitrate e gaps. Ensaiar 30 minutos estáveis,
  três interrupções de 30 segundos e restart do serviço; metas de aceitação de consumo
  dependem do hardware e serão propostas antes da campanha, sem inventar SLA.
- Relógio visual sintético e identificador de sequência permitem comparar origem,
  exibição e gravação. Medir sincronismo dos relógios; se não confiável, reportar
  incerteza. Histórico exige exportação/reprodução após parar a fonte.

## Risks / Trade-offs

- [Capacidades do SIGMA-N210 não verificadas] → registrar firmware e consultar documentação antes
  de escolher adapter; teste de RTSP manual separado de descoberta.
- [Tela sensível] → conteúdo exclusivamente sintético; região não é mascaramento
  dinâmico. Nenhuma autorização para capturar dados reais nesta PoC.
- [VPN com relay] → medir rota e latência, não atribuir seu custo ao encoder.
- [Sem Mint/NVR] → preparar kit e testes; manter gate de hardware aberto.
- [Versões externas] → verificar fontes oficiais e fixar versões/digests na implementação.

## Migration Plan

Adicionar componentes de PoC independentes, executar laboratório, preparar Mint/VPN,
validar LAN/NVR e consolidar relatório. Nenhuma migração PostgreSQL ou contrato M1.
Reversão: parar captura, remover apenas serviços/stack da PoC, revogar suas credenciais
e remover rotas específicas criadas; preservar gravações necessárias ao relatório
até a retenção de teste acordada. Não desmontar stacks compartilhadas.

## External prerequisites

Mint instalado com sessão X11, usuário de teste, acesso por chave/VPN, região de teste;
NVR identificado e autorizado com canal/espaço reservados. São bloqueios dos testes
correspondentes, não impedem implementar e verificar o kit localmente.
