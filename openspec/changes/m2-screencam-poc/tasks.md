# Tasks

## 1. Preparação e limites

- [x] 1.1 Documentar inventário Mint/NVR, topologia privada proposta e roteiro de ensaio; verificar que campos desconhecidos e fontes estão explícitos. Evidência: docs/screencam-m2.md.
- [x] 1.2 Fixar versões de FFmpeg/MediaMTX e imagens usadas após consultar fontes oficiais; verificar binários e configurações no container. Evidência: Dockerfile.lab, screencam_lab.py e relatório p3-video-lab-82f63814 (FFmpeg 7.1.5 / MediaMTX 1.12.3).

## 2. Kit de captura

- [x] 2.1 Implementar configuração persistente de região e preflight X11, com rejeição de Wayland/configuração inválida; testar sem iniciar captura em erros. Evidência: 33 testes novos de configuração/preflight; build total 116 testes aprovado. Probes X11 simulados na suíte; validação Mint permanece em 4.x.
- [x] 2.2 Implementar captura H.264 e supervisor com backoff, parada limpa e health de progresso; testar falhas, recuperação e ausência de segredos nos logs. Evidência: testes unitários/processos e ensaio p3-video-lab-82f63814.
- [ ] 2.3 Preparar serviço de usuário e instruções Mint; verificar configuração após restart e limites de privilégio no laboratório, depois no Mint.

## 3. Transporte e laboratório

- [x] 3.1 Criar ambiente Docker isolado com MediaMTX autenticado por caminho, sem porta pública; verificar publicação/leitura autorizadas e rejeição de acesso indevido. Evidência: matriz HTTP/RTSP 401 no ensaio p3-video-lab-82f63814.
- [x] 3.2 Exercitar fonte sintética X11, decodificação, interrupções e retomada; registrar tempos e evidências de frames sem atribuir resultado ao NVR. Evidência: dois ensaios aprovados, p3-video-lab-b68a0697 e p3-video-lab-82f63814; campanha Mint/NVR com três interrupções permanece em 4.2.
- [x] 3.3 Implementar coleta e relatório de CPU/RAM/FPS/bitrate/latência/gaps; verificar amostras e unidades com ensaio reproduzível. Evidência: p3-video-lab-7674123b, marcador visual validado, amostras CPU/RSS e pacotes RTSP; docs/screencam-lab-evidence.json. Ensaio curto, não benchmark de Mint.
- [x] 3.4 Preparar stack de PoC compatível com Portainer, configuração privada e reversão; validar sintaxe e só implantar após definir endpoint/rede. Evidência: stack.yml aprovado por docker stack config, secret e rollback no runbook. Implantação permanece condicionada a 4.1.

## 4. Qualificação real

- [ ] 4.1 Preparar acesso privado autorizado ao Mint e SIGMA-N210; verificar conectividade e restrição das portas, registrar firmware e sessão gráfica.
- [ ] 4.2 Executar captura no Mint por 30 minutos, três interrupções e restart; registrar consumo, legibilidade, latência e reconexão com critérios de consumo definidos antes do ensaio.
- [ ] 4.3 Configurar canal reservado no NVR e demonstrar gravação e histórico após parar a fonte; registrar janela pedida/retornada, drift e lacunas.
- [ ] 4.4 Verificar RTSP, ONVIF e descoberta separadamente no firmware real; registrar suportado, não suportado ou inconclusivo e decisão de compatibilidade.

## 5. Entrega

- [x] 5.1 Executar testes/lint/build e OpenSpec strict; revisar regressões dos contratos M1. Evidência: 140 testes, Ruff e artifact drift aprovados; OpenSpec strict 3/3. Diff desde 734d671 sem alteração em app/contrato M1 ou seu oráculo/testes.
- [x] 5.2 Consolidar evidências, atualizar estado/roadmap, fazer commit/push e verificar CI aplicável. Evidência: commits 3c07b01/acab67b enviados, runs 35486910033/35487103922 com test/publish/deploy SUCCESS. Evidências de hardware continuam pendentes em 4.x; esta entrega cobre o kit/laboratório.
- [ ] 5.3 Somente após qualificação real, sincronizar specs e arquivar M2; verificar ausência de tarefas pendentes e preservar cenários consolidados.

Bloqueio externo de 2.3/4.x: Mint ainda será preparado; acesso ao NVR depende do
usuário e da VPN. Firmware identificado nas fotos fornecidas, com reconferência
pendente no equipamento; inventário em docs/screencam-m2.md. Kit/laboratório local concluídos; serviço validado
sintaticamente, mas restart e sessão gráfica reais aguardam a máquina.
Não arquivar M2 nem marcar a qualificação real concluída com evidências sintéticas.
