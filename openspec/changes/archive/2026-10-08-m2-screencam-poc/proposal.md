# Proposal

## Why

A timeline P3 depende de vídeo recuperável, mas RTSP disponível não comprova gravação
nem busca histórica em NVR. M2 deve testar essa cadeia no Linux Mint e hardware reais
antes de comprometer a arquitetura de evidências de M4.

## What Changes

- Preparar captura de região X11 com FFmpeg/H.264 e distribuição MediaMTX em Docker.
- Configuração explícita, diagnóstico, recuperação de conexão e acesso privado.
- Laboratório sintético reproduzível e roteiro de medição de CPU/RAM/FPS/bitrate/latência.
- Validar gravação, interrupção, reconexão e recuperação histórica no NVR real.
- Documentar compatibilidade RTSP, ONVIF e descoberta separadamente, com evidências.

## Capabilities

### New Capabilities

- `screencam-poc`: captura, transporte privado e qualificação da cadeia de vídeo.

### Modified Capabilities

Nenhuma. O contrato M1 e os endpoints atuais permanecem válidos.

## Impact

Novos scripts, testes, configuração Docker e runbook de ScreenCam. Sem migração de
banco, ingestão M3, inferência, dados de clientes ou alteração incidental de stacks.
O usuário informou em 2026-09-20 que ainda preparará o Mint. Acesso por VPN é proposto;
equipamento, sessão gráfica e NVR precisam ser identificados para validação real.
Laboratório não substitui o gate de hardware; Windows/H.265/main-substream e captura
por janela permanecem requisitos de evolução, fora da primeira PoC X11 por região.
