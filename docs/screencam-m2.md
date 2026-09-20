# ScreenCam M2 — preparação e ensaio

Estado: implementação em andamento, sem qualificação real. Tarefas canônicas:
`openspec/changes/m2-screencam-poc/tasks.md`.

## Inventário em 2026-09-20

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

Implementação disponível, ainda aguardando ensaio com FFmpeg/MediaMTX real:

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
