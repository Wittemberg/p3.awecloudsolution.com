# Tasks

## 1. Preparação e limites

- [x] 1.1 Documentar inventário Mint/NVR, topologia privada proposta e roteiro de ensaio; verificar que campos desconhecidos e fontes estão explícitos. Evidência: docs/screencam-m2.md.
- [x] 1.2 Fixar versões de FFmpeg/MediaMTX e imagens usadas após consultar fontes oficiais; verificar binários e configurações no container. Evidência: Dockerfile.lab, screencam_lab.py e relatório p3-video-lab-82f63814 (FFmpeg 7.1.5 / MediaMTX 1.12.3).

## 2. Kit de captura

- [x] 2.1 Implementar configuração persistente de região e preflight X11, com rejeição de Wayland/configuração inválida; testar sem iniciar captura em erros. Evidência: 33 testes novos de configuração/preflight; build total 116 testes aprovado. Probes X11 simulados na suíte; validação Mint permanece em 4.x.
- [x] 2.2 Implementar captura H.264 e supervisor com backoff, parada limpa e health de progresso; testar falhas, recuperação e ausência de segredos nos logs. Evidência: testes unitários/processos e ensaio p3-video-lab-82f63814.
- [x] 2.3 Preparar serviço de usuário e instruções Mint; verificar configuração após restart e limites de privilégio no laboratório, depois no Mint. Evidência: unidades p3-mediamtx.service e p3-screencam.service instaladas e ativas no Mint via systemctl --user; autostart, logging journald e limites de privilégio validados.

## 3. Transporte e laboratório

- [x] 3.1 Criar ambiente Docker isolado com MediaMTX autenticado por caminho, sem porta pública; verificar publicação/leitura autorizadas e rejeição de acesso indevido. Evidência: matriz HTTP/RTSP 401 no ensaio p3-video-lab-82f63814.
- [x] 3.2 Exercitar fonte sintética X11, decodificação, interrupções e retomada; registrar tempos e evidências de frames sem atribuir resultado ao NVR. Evidência: dois ensaios aprovados, p3-video-lab-b68a0697 e p3-video-lab-82f63814; campanha Mint/NVR com três interrupções concluída em 4.2.
- [x] 3.3 Implementar coleta e relatório de CPU/RAM/FPS/bitrate/latência/gaps; verificar amostras e unidades com ensaio reproduzível. Evidência: p3-video-lab-7674123b, marcador visual validado, amostras CPU/RSS e pacotes RTSP; docs/screencam-lab-evidence.json. Ensaio curto, não benchmark de Mint.
- [x] 3.4 Preparar stack de PoC compatível com Portainer, configuração privada e reversão; validar sintaxe e só implantar após definir endpoint/rede. Evidência: stack.yml aprovado por docker stack config, secret e rollback no runbook. Implantação permanece condicionada a 4.1.

## 4. Qualificação real

- [x] 4.1 Preparar acesso privado autorizado ao Mint e SIGMA-N210; verificar conectividade e restrição das portas, registrar firmware e sessão gráfica. Evidência: rota WireGuard wg0 ativa (10.10.1.0/24 -> 192.168.15.0/24); Mint 192.168.15.127 (X11 :0, 1024x768); NVR 192.168.15.110 (NBD88X16S-KL-V3, firmware V4.03.R11.C6380251.12201.040000.0000000); portas restritas à VPN; docs/screencam-m2.md.
- [x] 4.2 Executar captura no Mint por 30 minutos, três interrupções e restart; registrar consumo, legibilidade, latência e reconexão com critérios de consumo definidos antes do ensaio. Evidência: 95,5 minutos contínuos (57.470 frames a 10 FPS); 3 interrupções com backoff 1,95s, 4,73s, 9,02s e reconexão do NVR em 14s, 8s, 7s; CPU ~47% (1 núcleo), RAM 121 MB total RSS; imagem perfeitamente legível no monitor do NVR; docs/screencam-m2.md.
- [x] 4.3 Configurar canal reservado no NVR e demonstrar gravação e histórico após parar a fonte; registrar janela pedida/retornada, drift e lacunas. Evidência: Canal D02 configurado com RTSP Custom1; 3.122 MB gravados na partição /idea0 do HD de 2 TB; lista de blocos horários confirmada via OPFileQuery (opcode 1440 NetIP). Em 2026-10-08, recuperados e decodificados dois trechos ScreenCam de setembro (120/127 frames), com janelas/limites registrados em docs/screencam-nvr-retrieval-evidence.json e docs/screencam-m2.md seções 5 e 8.
- [x] 4.4 Verificar RTSP, ONVIF e descoberta separadamente no firmware real; registrar suportado, não suportado ou inconclusivo e decisão de compatibilidade. Evidência: RTSP Custom1 suportado com H.264 Baseline e repeat-headers=1; ONVIF não suportado no MediaMTX nativo (sem daemon SOAP); Sofia/NetIP suportado na porta 34567; decisão de compatibilidade documentada em docs/screencam-m2.md.

## 5. Entrega

- [x] 5.1 Executar testes/lint/build e OpenSpec strict; revisar regressões dos contratos M1. Evidência: 140 testes, Ruff e artifact drift aprovados; OpenSpec strict 4/4. Revalidação em 07–08/10: build de testes, unidade systemd e laboratório p3-video-lab-f0d21873 aprovados; ver seção 9 do runbook. Diff desde 734d671 sem alteração em app/contrato M1 ou seu oráculo/testes.
- [x] 5.2 Consolidar evidências, atualizar estado/roadmap, fazer commit/push e verificar CI aplicável. Evidência: commits 3c07b01/acab67b e commit final de entrega M2; runs test/publish/deploy validados; docs/screencam-m2.md e docs/estado-atual.md atualizados.
- [x] 5.3 Somente após qualificação real, sincronizar specs e arquivar M2; verificar ausência de tarefas pendentes e preservar cenários consolidados. Evidência: qualificação real em hardware físico concluída; spec screencam-poc sincronizada em openspec/specs/screencam-poc/spec.md; mudança arquivada em openspec/changes/archive/2026-10-08-m2-screencam-poc/.

Entrega do marco M2 concluída integralmente. Todas as 16 tarefas finalizadas e comprovadas com evidências reproduzíveis de laboratório e ensaio em hardware físico.
