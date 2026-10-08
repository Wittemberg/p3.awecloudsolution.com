# ScreenCam M2 — preparação e ensaio

Estado: kit implementado; recuperação histórica real demonstrada em 2026-10-08,
com critérios de qualificação ainda pendentes (seções 7 e 8). Tarefas canônicas:
`openspec/changes/m2-screencam-poc/tasks.md`.

## Inventário em 2026-09-20

Registro histórico de preparação. O inventário do ensaio de setembro está no
relatório de hardware ao final; pendências desta seção não representam o estado atual.

| Item | Evidência / pendência |
|---|---|
| Captura | Linux Mint ainda será preparado pelo usuário |
| SO, sessão, CPU/RAM, resolução | A confirmar na máquina; primeira PoC exige X11 |
| NVR | AiTek SIGMA-N210 confirmado pela etiqueta fotografada; entrada 10CH |
| Firmware fotografado | `V4.03.R11.C6380251.12201.040000.0000000` |
| Construção exibida | `2025-09-19 14:45:17` |
| Compressão na etiqueta | H.265; aceitação de H.264 ainda não verificada |
| Alimentação na etiqueta | DC 12 V, 3 A |
| Canal livre, disco, relógio e rede local | A confirmar no equipamento |
| Acesso | VPN a configurar; endereços/usuários ainda não fornecidos |
| Credenciais | Não recebidas para Mint/NVR; guardar fora do Git |
| Servidor P3 | Ubuntu compartilhado; não equivale ao Mint do teste |

Consulta ao [fabricante](https://aitekbrasil.com/) e à
[linha Sigma](https://aitekbrasil.com/linha-sigma/) em 2026-09-20 não localizou
documentação suficiente do SIGMA-N210. Não inferir protocolos, URLs de playback
ou credenciais padrão a partir de modelos parecidos.

Evidências locais fornecidas pelo usuário e conferidas visualmente: `/root/nvr-aitek-foto-1.jpg`
(tela Versão), `/root/nvr-aitek-foto-2.jpg` (etiqueta) e `/root/nvr-aitek.txt`
(transcrição coerente com as fotos). A tela também indica 10 canais de gravação.
São observações fotográficas, sem consulta remota ao equipamento. MAC, número de
série, QR code e código NAT permanecem nos originais locais e não são versionados.
O estado NAT conectado corresponde ao instante da foto, sem comprovar rota privada
ou disponibilidade atual. Os arquivos não fornecem IP LAN, portas ou credenciais.

Consequência para M2: testar primeiro se o canal aceita a fonte H.264/RTSP do kit.
A inscrição H.265 não comprova nem exclui H.264. Se houver rejeição, identificar
codec/perfil e modo de cadastro suportados antes de propor mudança do encoder;
não tratar falha de codec como falha da VPN. RTSP, ONVIF, descoberta e recuperação
histórica permanecem sem comprovação. A versão fotografada será reconferida no acesso,
sem propor atualização de firmware com base apenas no identificador.

## Topologia proposta

Mint (X11/FFmpeg) → MediaMTX em container na LAN de teste → canal reservado do NVR.
Servidor P3 → VPN → Mint e, por rota autorizada específica, administração do NVR.
Preferir vídeo dentro da LAN para separar custo do encoder de latência da internet.
Nenhuma porta RTSP deve ser publicada na internet. O endpoint Portainer que gerenciará
o container e a localização definitiva do MediaMTX dependem dessa topologia.

Tailscale é candidato, ainda não instalado. Acesso ao NVR pode exigir subnet router;
autorizar somente o IP/portas necessários, sem publicar toda a rede por conveniência.
Referências oficiais consultadas em 2026-09-20:
[Linux](https://tailscale.com/docs/install/linux),
[subnet router](https://tailscale.com/kb/1104/enable-ip-forwarding).

## Configuração e preflight disponíveis

Na máquina de teste, copiar `deploy/screencam/config.example.json` para arquivo
privado fora do Git (por exemplo `.local/screencam/config.json`), modo 600, pertencente
ao usuário da sessão. Substituir credenciais demonstrativas e ajustar região,
IP privado e porta. A região é obrigatória e suas dimensões devem ser pares.

Executar no usuário da sessão X11, com `DISPLAY`/autorização da sessão disponíveis:

```sh
python3 scripts/screencam_config.py .local/screencam/config.json
```

Esse comando **não captura nem transmite**. Verifica arquivo, sessão, geometria real
via `xdpyinfo`, dispositivo x11grab e encoder libx264. Retorna JSON com `ready` ou
diagnóstico seguro e código 2. Não executar `xhost +` para contornar falhas de acesso.
Uma sessão SSH deve preservar o contexto da sessão gráfica autorizada; definir
XDG_SESSION_TYPE manualmente não comprova que o desktop é X11.

Referência de captura: [FFmpeg x11grab](https://ffmpeg.org/ffmpeg-devices.html#x11grab),
consultada em 2026-09-20.

## Supervisor e serviço de usuário

Implementação disponível, com laboratório sintético e ensaio de hardware relatados:

```sh
python3 scripts/screencam_capture.py .local/screencam/config.json
```

Esse comando inicia captura após preflight. Usa H.264/yuv420p, RTSP/TCP, GOP de
2 segundos, alvo de 1500 kbit/s e teto configurado de 2000 kbit/s. O bitrate real
precisa ser medido. Não há áudio nem captura de cursor. Referências de
[progresso FFmpeg](https://ffmpeg.org/ffmpeg.html) e
[RTSP](https://ffmpeg.org/ffmpeg-protocols.html#rtsp), consultadas em 2026-09-20.

Eventos JSON: `starting`, `streaming`, `video_stalled`, `disconnected`, `retrying`,
`action_required`, `stopped`. Progresso de frames mede atividade do encoder, não
prova decodificação no cliente ou gravação no NVR. Sem primeiro frame em 15 segundos
ou avanço em 10 segundos, o processo é encerrado e a conexão é tentada novamente.
Backoff 2/5/10/20/30/60 segundos com jitter e teto de 60 segundos. Um período de
60 segundos com avanço reinicia a sequência. Falha de configuração/autenticação
exige correção; não fica repetindo credenciais inválidas.

SIGINT/SIGTERM encerra o filho; após 3 segundos sem sair, força encerramento.
Configuração é relida e validada antes de cada tentativa. Para mudança de região
durante operação, parar o serviço, editar e reiniciar explicitamente.

O FFmpeg recebe URL autenticada em argv. Ela não é impressa pelo supervisor, mas
pode ser visível a processos locais com permissão de inspeção. Usar máquina/usuário
de teste confiável e credencial restrita ao stream sintético; não compartilhar
saída de `ps`, diagnósticos brutos ou dumps. O serviço desabilita core dumps.

Instalação no Mint, **como usuário da sessão gráfica**, após configurar o destino:

```sh
install -d -m 700 ~/.local/lib/p3-screencam ~/.config/p3-screencam
install -d ~/.config/systemd/user
install -m 600 scripts/screencam_config.py scripts/screencam_capture.py ~/.local/lib/p3-screencam/
install -m 600 .local/screencam/config.json ~/.config/p3-screencam/config.json
install -m 644 deploy/screencam/p3-screencam.service ~/.config/systemd/user/
systemctl --user import-environment DISPLAY XAUTHORITY XDG_SESSION_TYPE
systemctl --user daemon-reload
systemctl --user enable --now p3-screencam.service
journalctl --user -u p3-screencam.service -n 30
```

Não habilitar antes de selecionar região sintética e credenciais próprias. O serviço
depende da sessão gráfica ativa; confirmar integração do desktop com
`graphical-session.target` no Mint real. Não habilitar linger para simular uma sessão
gráfica inexistente. Para parar e desabilitar: `systemctl --user disable --now p3-screencam.service`.
Erro com código 2 não reinicia automaticamente; corrigir a causa e usar
`systemctl --user restart p3-screencam.service`.

## Laboratório reproduzível

Construir e executar no servidor com Docker:

```sh
docker build -f deploy/screencam/Dockerfile.lab -t p3-screencam-lab .
python3 scripts/screencam_lab.py
```

O executor cria recursos exclusivos `p3-video-lab-*` e os remove no encerramento
normal, inclusive em falha de teste. Não publica portas nem conecta o display do
host. Relatório sanitizado fica em `.local/<run-id>/report.json`. Se o executor for
interrompido abruptamente, conferir os recursos desse run antes de repetir.

Base Python fixada por digest; pacotes diretos FFmpeg `7:7.1.5-0+deb13u1`, Xvfb
`2:21.1.16-1.3+deb13u4` e x11-utils `7.7+7`, consultados no repositório Debian
da imagem em 2026-09-20. Transitivas APT ainda vêm dos repositórios ativos; builds
futuros não são bit a bit reproduzíveis, e versões removidas exigirão revisão explícita.

MediaMTX `1.12.3`, digest
`sha256:3634a1eed1288b93e8d22ed74694eae96d483fcf676cac5d0c91830ad1b86b3d`.
Baseline de ensaio, não alegação de versão mais recente ou aprovação produtiva.
Fontes oficiais consultadas: [release](https://github.com/bluenviron/mediamtx/releases/tag/v1.12.3)
e [configuração dessa versão](https://github.com/bluenviron/mediamtx/blob/v1.12.3/mediamtx.yml).
Autenticação interna por caminho e TCP somente; HLS/RTMP/WebRTC/SRT/API desligados.

O laboratório verifica vídeo em movimento (hashes de frames decodificados), acesso
negado, parada/retomada do servidor RTSP e ausência de credenciais nos logs do
supervisor. Não demonstra gravação/histórico no NVR, qualidade visual de texto,
latência de um PDV real nem estabilidade de longa duração.

### Medição sintética

`screencam_metrics.py source` gera frames de teste em cinza com horário codificado em
48 bits, checksum e células invertidas. O relógio é gerado antes da apresentação por
ffplay. O receptor decodifica o marcador e mede geração → chegada decodificada no
mesmo relógio do host; isso inclui apresentação, captura, codificação, transporte,
decodificação e buffers. Não atribuir esse total apenas ao encoder ou à rede.
Marcadores corrompidos/ausentes são contados e reprovam o ensaio automático.

CPU: deltas utime+stime de `/proc/PID/stat` por tempo monotônico, normalizados para
um núcleo (100% = um núcleo). RSS em bytes, com amostragem a cada ~1 segundo.
PID/starttime precisa ser estável. Não é consumo total do Mint, do Xvfb ou do NVR.
FPS entregue: número de intervalos entre frames dividido pelo tempo observado.
Intervalos de chegada medem gaps do receptor, sem provar perda de gravação no NVR.
Bitrate: bytes dos pacotes de vídeo sobre intervalo de PTS, excluindo último pacote
e overhead da rede; janela separada de ~3 segundos. Percentil p95 por nearest-rank.
O ensaio curto serve para verificar instrumentação, não para homologar capacidade.

### Stack Portainer preparada

`deploy/screencam/stack.yml` passou em `docker stack config`. Ainda não implantada:
exige endpoint/nó aprovado, label `p3_screencam=true`, overlay privada externa
`p3_video_private`, rota privada até essa overlay e secret `p3_screencam_config_v1`.
A stack não publica portas, não usa a rede pública do Traefik e não cria VPN.
Sem uma rota/gateway autorizado, Mint/NVR externos não alcançarão o serviço.

Preparar cópia privada de `mediamtx.example.yml`, substituir senhas distintas e
criar o secret no endpoint escolhido pelo Portainer (Secrets → Add secret). Não
colar credenciais no editor de stack ou em variáveis GitHub. Subir o YAML com nome
exclusivo `p3-screencam` somente depois de verificar a rota privada e o nó de destino.
Não adicionar `ports:` para contornar ausência de VPN. O usuário do container é
10001; o secret é montado somente leitura para esse UID. Sem gravação local contínua.

Rollback operacional: parar captura e remover apenas a stack `p3-screencam`; revogar
credenciais e remover o secret após não haver consumidores. Preservar a stack `p3`
e demais serviços. Troca de secret exige novo nome versionado; nunca reutilizar um
secret antigo com conteúdo presumido. O template ainda não qualifica rede/hardware.

## Roteiro de qualificação real

1. Registrar inventário, versões, topologia, sincronismo dos relógios, canal reservado
   e espaço de gravação. Definir limites de CPU/RAM/latência antes do benchmark.
2. Apresentar somente conteúdo sintético com relógio e identificadores de sequência
   na região autorizada. Registrar resolução, FPS, bitrate/configuração e legibilidade.
3. Executar 30 minutos; coletar CPU/RAM com unidade e intervalo de amostragem,
   FPS entregue, bitrate, frames perdidos e latência observada. Separar LAN/VPN.
4. Interromper transporte por 30 segundos, três vezes, preservando o acesso administrativo.
   Registrar início/fim da falha, retomada automática e gaps no vídeo gravado.
5. Reiniciar o serviço de captura e verificar que configuração e região permanecem.
6. Parar a fonte e recuperar no NVR uma janela histórica com marcadores conhecidos.
   Registrar janela pedida/retornada, método, duração, drift, ausência/expiração e
   resultado de decodificação. Guardar mídia sintética em diretório privado, fora do Git.
7. Testar separadamente cadastro RTSP manual, ONVIF e descoberta. Descoberta que
   funciona na LAN não comprova descoberta pela VPN; registrar onde cada teste ocorreu.
8. Consolidar resultados, limitações e decisão de compatibilidade. NVR indisponível,
   live playback ou gravação em FFmpeg não substituem teste histórico no SIGMA-N210.

## Registro do ensaio

Cada execução deve conter ID/data/revisão, operador, ambiente (lab/real), equipamento,
firmware/versões, configuração sem credenciais, duração/amostras, método e unidade
de cada métrica, interrupções, janela de histórico, evidências privadas e conclusão.
Campos não medidos ficam `inconclusivo`; ausência de evidência nunca vira aprovação.
Definir prazo de exclusão das gravações sintéticas antes de iniciar a campanha.

## Relatório de Qualificação Real (Hardware Mint + NVR SIGMA-N210)

Relato de ensaio em hardware físico em 2026-09-22 / 2026-09-23 referente às Tasks
2.3, 4.1, 4.2, 4.3 e 4.4. A revisão de 2026-10-07 preserva as observações abaixo,
mas não confirma conclusão integral de 4.2/4.3: faltam evidências descritas na seção 7.

### 1. Inventário e Topologia Privada (Task 4.1)

- **Estação de captura:** Linux Mint 21 (Vanessa), X11 nativo em display `:0`, resolução 1024x768, IP privado `192.168.15.127`, usuário não-root `startwo`.
- **Gravador NVR:** AiTek SIGMA-N210 (10 canais digitais, placa Xiongmai/JFTech `NBD88X16S-KL-V3`), firmware `V4.03.R11.C6380251.12201.040000.0000000`, IP privado `192.168.15.110`.
- **Canais ativos no NVR:**
  - Canal D01: Câmera IP física em operação (`192.168.15.111`).
  - Canal D02: ScreenCam Linux Mint (`192.168.15.127:8554/screencam`).
- **Topologia de rede:** Túnel seguro WireGuard `wg0` (`10.10.1.0/24` para `192.168.15.0/24`), RTT médio 25-70 ms, 0% perda de pacotes. Nenhuma porta RTSP ou NVR exposta à internet.

### 2. Compatibilidade de Protocolo e Perfil (Task 4.4)

- **RTSP Custom1:** **Suportado e homologado**.
  - O cadastro manual via perfil `Custom1` no NVR permite preenchimento arbitrário dos paths RTSP.
  - Requisito mandatório de codec: H.264 Constrained Baseline Profile (nível 3.1) com repetição obrigatória de cabeçalhos SPS/PPS em cada keyframe (`-x264-params repeat-headers=1` e `-bsf:v dump_extra`). Sem repetição in-band, o decodificador de hardware do NVR rejeita os frames e apresenta tela preta.
  - Paths configurados: MainStream `/screencam`, SubStream (Extra Stream) `/video2` ou `/screencam`.
- **ONVIF:** **Não suportado pelo MediaMTX nativo** (MediaMTX 1.12.3 opera como servidor RTSP puro na porta 8554 e não implementa o daemon SOAP/WS-Discovery ONVIF).
- **Sofia / NetIP (Porta 34567):** **Suportado**. Utilizado para telemetria, conferência de canais, estado de disco e busca de histórico via `OPFileQuery` (opcode 1440).
- **Descoberta ONVIF/WS-Discovery no firmware:** **Inconclusiva**. Não há resultado
  separado de teste de descoberta na LAN/VPN. A ausência de servidor ONVIF no
  MediaMTX não demonstra ausência dessa capacidade no NVR.

### 3. Ensaio Contínuo e Consumo (Task 4.2)

- **Duração contínua inicial:** 95,5 minutos ininterruptos (57.470 frames gerados a 10,00 FPS estáveis).
- **Consumo de recursos no Mint (amostragem ps/top):**
  - `ffmpeg` (captura X11 e encoding H.264): 46,9% de 1 núcleo (~11% da CPU total da máquina), RSS de 83,9 MB.
  - `mediamtx` (servidor RTSP): 3,6% de CPU, RSS de 24,2 MB.
  - `screencam_capture.py` (supervisor): 0,1% de CPU, RSS de 13,0 MB.
  - **Total de memória residente:** ~121 MB.
- **Qualidade visual:** Exibição do desktop com terminal e janelas perfeitamente legíveis na tela do NVR (tanto no mosaico quanto em tela cheia).

### 4. Ensaio de Interrupção e Resiliência (Task 4.2)

Foram executadas 3 interrupções forçadas via SIGTERM no encoder, verificando o supervisor e o NVR:

1. **Interrupção 1:** Falha detectada pelo supervisor (`encoder_exit`); backoff de 1,95 s; novo encoder iniciado em 2,5 s; NVR reconectou a sessão RTSP em 14 s.
2. **Interrupção 2:** Falha detectada; backoff de 4,73 s; novo encoder iniciado em 5,2 s; NVR reconectou a sessão RTSP em 8 s.
3. **Interrupção 3:** Falha detectada; backoff de 9,02 s; novo encoder iniciado em 9,6 s; NVR reconectou a sessão RTSP em 7 s.

Todas as três tentativas recuperaram a transmissão automaticamente sem intervenção humana e sem travar o NVR.

### 5. Gravação em Disco e Recuperação Histórica (Task 4.3)

- **Espaço e Partição:** HD de 2 TB instalado (`/idea0`, 1.907.729 MB total); status OK.
- **Volume gravado durante o ensaio:** 3.122 MB (3,12 GB) gravados continuamente no canal D02.
- **Estrutura de arquivos históricos:** Blocos contínuos gravados em `/idea0/2026-09-22/002/` e `/idea0/2026-09-23/002/` com tag de gravação regular `[R]`.
- **Validação de consulta:** A consulta remota via protocolo NetIP (`OPFileQuery`, opcode 1440) retornou a lista completa de arquivos gravados no canal 1 (D02) cobrindo todos os intervalos do ensaio.

### 6. Serviço de Usuário Systemd (Task 2.3)

- Unidades `p3-mediamtx.service` e `p3-screencam.service` instaladas em `~/.config/systemd/user/` no Mint.
- Habilitadas com `systemctl --user enable --now`.
- Binários e scripts em modo 600 sob `~/.local/lib/p3-screencam/` e configuração privada em `~/.config/p3-screencam/config.json`.
- Processos gerenciados nativamente por cgroup de usuário com logging em journald.

### 7. Revisão das evidências de fechamento — 2026-10-07

Foram consultados este relatório, as tarefas/spec/design da mudança, os relatórios
sintéticos em `.local/p3-video-lab-*/report.json` e o inventário de arquivos em
`/root/guarderia-evidencias/nvr-audit-20260922/`. Este último contém preflight e
sondagens HTTP/HTTPS/rede, sem mídia de playback. Não foi localizado nesses caminhos
um trecho exportado do NVR nem registro de reprodução após parar o publicador.
Os números do ensaio acima são observações do relato anterior, não novas medições.

| Critério | Resultado da revisão |
|---|---|
| Histórico após parar a fonte | Pendente: OPFileQuery lista arquivos; não demonstra reprodução/exportação com os marcadores esperados |
| Janela pedida/retornada, drift e lacunas | Inconclusivos: faltam horários e comparação do trecho recuperado |
| Interrupção de transporte por 30 s, três vezes | Pendente: o relato registra SIGTERM no encoder, sem duração da indisponibilidade do transporte |
| Restart do serviço e região persistida no Mint | Pendente de registro antes/depois; há testes sintéticos e relato de instalação das unidades |
| CPU/RAM/FPS e estabilidade no Mint | Valores relatados acima; limites prévios de consumo não localizados |
| Bitrate, frames perdidos e latência no hardware | Inconclusivos: sem medição/método registrados; valores do laboratório não os substituem |
| RTSP e descoberta | RTSP relatado como funcional; descoberta permanece inconclusiva e separada de ONVIF no MediaMTX |

Para concluir 4.3, localizar a evidência existente ou executar o roteiro de histórico
com conteúdo sintético: registrar parada da fonte, janela solicitada e retornada,
marcadores recuperados, drift, gaps, método e resultado de reprodução/decodificação.
A recuperação posterior está na seção 8; a mídia permanece fora do Git. Para concluir
4.2, complementar os registros do ensaio
ou repetir os cenários faltantes, definindo critérios de consumo antes da medição.
M2 permanece ativo até esses critérios serem conferidos; sincronização e arquivamento
nesta revisão não foram realizados.

### 8. Recuperação histórica executada — 2026-10-08

O usuário confirmou que não havia extraído gravação e autorizou acesso ao NVR de
bancada. Consulta pela WireGuard: portas 80/554/34567 acessíveis; autenticação NetIP
aceita. Mint não respondeu nas portas 22/8554 testadas; isso não comprova parada
controlada da fonte nem estado atual do serviço.

OPFileQuery retornou 9 arquivos em 22/09 e 23 em 23/09 para o canal D02.
Um primeiro arquivo curto de 22/09 continha câmera física; foi excluído da evidência
ScreenCam. O número do canal sozinho não identifica sua fonte ao longo do tempo.

Foram recuperadas duas janelas posteriores por OPPlayBack, modo ByName, usando
Claim (1424), DownloadStart/DownloadStop (1420) e dados (1426). O formato de frames
e a implementação foram consultados no [cliente OpenIPC, revisão fixada](https://github.com/OpenIPC/python-dvr/tree/6ea861a1e99cab5922084a4a0eac6fe2d5b6120d).
Os cabeçalhos do NVR foram separados do H.264; fragmentos incompletos nas bordas
foram descartados, sem preencher frames ausentes.

| Janela pedida, relógio do NVR em 23/09 | Frames completos recuperados | Resultado |
|---|---|---|
| 00:01:00–00:01:15 | 00:01:01–aprox. 00:01:12,9; 120 frames / 12 s | Fundo de tela do desktop; sem marcadores |
| 09:01:00–09:01:15 | 09:01:01–aprox. 09:01:13,6; 127 frames / 12,7 s | Tela com vídeo pausado e diálogo legível; sem marcadores |

Ambos: H.264 Constrained Baseline, 1024×768, 10 FPS no cabeçalho do NVR.
FFmpeg decodificou os H.264 extraídos com `-xerror`, exit 0 e stderr vazio.
O primeiro frame de cada janela foi inspecionado. Um MP4 sem recodificação foi
verificado com ffprobe: 127 frames, 10 FPS e 12,7 s.

Tempos de keyframes têm precisão de segundos. O horário do último frame é estimado
pela contagem de frames após o último keyframe a 10 FPS; não mede drift entre Mint
e NVR. Nas janelas verificadas, keyframes aparecem a cada 2 s/20 frames. As perdas
nas bordas decorrem do recorte/extração e não demonstram gaps da gravação original.
Não foram localizados marcadores sintéticos; a tarefa 4.3 permanece parcialmente
atendida até demonstrar o cenário completo da spec.

[Evidência sanitizada](screencam-nvr-retrieval-evidence.json) contém hashes, contagens,
janelas e limitações. Mídia, consultas e scripts do procedimento ficam em
`.local/nvr-retrieval-20261007/`, modo privado, fora do Git. MP4:
`screencam-20260923-090101.mp4`. A pasta mantém o nome da data de início da revisão.

### 9. Verificações locais desta revisão

- Build Docker `--target test` aprovado, incluindo pytest, Ruff e verificação de
  divergência dos artefatos de contrato. Reexecução após interrupção reutilizou o cache.
- Unidade systemd aprovada por `systemd-analyze --user verify` fora do sandbox.
- OpenSpec 1.13.1: `validate --all --strict`, inicialmente 3/3; verificação final
  4/4 após aparecer uma spec consolidada local não versionada, preservada nesta
  revisão. Há aviso informativo de que o delta ADDED já existe nessa spec;
  reconciliar o estado de sincronização antes de arquivar, após os critérios reais.
- Laboratório `p3-video-lab-f0d21873` aprovado com o encoder atualizado: frames
  decodificados antes/depois de falha de transporte, retomada em 6,236 s, acesso
  indevido negado, 73 marcadores válidos, aproximadamente 10 FPS. Latência sintética
  geração→decodificação p95 779,361 ms; não equivale à latência do hardware.
  Relatório privado em `.local/p3-video-lab-f0d21873/report.json`; recursos removidos
  pelo executor. O ensaio valida transporte, não supre a campanha real pendente.
