---
name: nvr-aitek-sigma
description: Conectar, qualificar e operar o NVR AiTek SIGMA-N210 (base Xiongmai/Sofia), incluindo topologia de rede privada, portas de controle, cadastro de stream ScreenCam via RTSP/ONVIF e recuperação de gravações históricas.
license: MIT
metadata:
  model: "AiTek SIGMA-N210 (10CH)"
  firmware_family: "Xiongmai (XM / Sofia / NetIP)"
  target_ports: [80, 554, 8899, 34567]
---

# Skill: Operação e Qualificação do NVR AiTek SIGMA-N210

Esta skill reúne o procedimento técnico, topologia e protocolos para integrar e qualificar o NVR **AiTek SIGMA-N210** na plataforma P3 (marco M2 — ScreenCam).

---

## 1. Identificação de Hardware e Firmware

* **Equipamento:** AiTek SIGMA-N210 (10 canais de gravação).
* **Firmware identificado:** `V4.03.R11.C6380251.12201.040000.0000000` (Construção: `2025-09-19 14:45:17`).
* **Origem da Plataforma:** Placa OEM **Xiongmai (XM / Sofia / NetIP / XMeye)**.
  * O padrão `V4.03.R11...` é característico do firmware XM.
  * O status NAT fotografo (`2:119.8.229.159...`) conecta-se à infraestrutura de nuvem XMeye/dvr163.
* **Compressão na etiqueta:** H.265. O suporte a H.264 nos canais digitais é o padrão dessa família de chips, mas deve ser comprovado no teste prático.

---

## 2. Topologia de Rede e Restrições de Segurança

1. **Isolamento Estrito:**
   * Nenhuma porta do NVR (nem HTTP, nem RTSP, nem NetIP) deve ser exposta publicamente na internet.
   * O tráfego entre o servidor P3 e o NVR deve transitar exclusivamente por VPN privada (OpenVPN `tun0`, WireGuard `wg0` ou Tailscale).
2. **Sub-rede Local:**
   * O NVR reside na LAN privada sob o IP `192.168.15.110`.
   * A rota do servidor para a sub-rede `192.168.15.0/24` é roteada pelo gateway do cliente VPN (ex.: roteador de borda TP-Link TL-ER605 em `10.8.0.10`).
3. **Segredos e Credenciais:**
   * Nunca versionar credenciais de acesso ao NVR no Git.
   * Guardar configurações locais em arquivos restritos (`mode 600`) dentro de `.local/`.

---

## 3. Mapeamento de Portas e Protocolos

| Porta | Protocolo | Função no Firmware XM / AiTek | Uso no P3 / ScreenCam |
|---|---|---|---|
| **34567 / TCP** | NetIP (Sofia) | Protocolo proprietário Xiongmai de gerenciamento, configuração e busca de vídeo (usado por CMS, VMS e app XMeye). | Descoberta, diagnóstico fino, consulta de status dos canais e busca de gravações por calendário. |
| **80 / TCP** | HTTP | Interface web administrativa (HTML/JS/ActiveX/H5). | Configuração manual do canal digital para receber o stream do MediaMTX. |
| **554 / TCP** | RTSP | Servidor de streaming ao vivo do NVR. | Extração de vídeo do NVR para a timeline do P3 (M4). Formatos típicos de URL: `rtsp://<user>:<pass>@<ip>:554/user=<user>_password=<pass>_channel=<ch>_stream=0.sdp` ou `rtsp://<user>:<pass>@<ip>:554/cam/realmonitor?channel=<ch>&subtype=0`. |
| **8899 / TCP** | ONVIF | Serviços padrão ONVIF (Device, Media, Imaging). | Descoberta automática e cadastro padronizado de canais. |

---

## 4. Roteiro de Qualificação do ScreenCam no NVR (Marco M2)

### Passo 1 — Sondagem e Verificação de Conectividade
A partir do ambiente autorizado com rota para `192.168.15.0/24`:
```bash
# Testar portas essenciais do NVR sem transferir dados sensíveis
nc -zv -w 3 192.168.15.110 80 554 8899 34567
```

### Passo 2 — Cadastro do Canal ScreenCam
1. Acessar a interface do NVR (via Web na porta 80 ou pelo monitor local).
2. Navegar em: **Configurações do Sistema → Canais Digitais / Gerenciamento de Câmeras**.
3. Selecionar um canal livre (ex.: Canal 10).
4. Adicionar dispositivo manualmente:
   * **Protocolo:** ONVIF ou RTSP Customizado.
   * **URL RTSP:** `rtsp://<usuario>:<senha>@<ip_privado_mediamtx>:8554/screencam`
   * **Transporte:** TCP preferencial.

### Passo 3 — Validação de Codec (H.264 vs H.265)
1. O supervisor ScreenCam emite H.264 baseline/main profile via FFmpeg (`libx264`, `yuv420p`).
2. Verificar no NVR se o preview e o status do canal ficam ativos:
   * Se o NVR conectar e exibir a tela normalmente: **compatibilidade H.264 comprovada**.
   * Se o NVR recusar por codec inválido: documentar no relatório M2 e avaliar transcodificação para H.265 (`libx265`).

### Passo 4 — Teste de Gravação e Busca Histórica (Tarefa 4.3)
1. Deixar o ScreenCam transmitindo por 30 minutos contínuos.
2. Interromper propositalmente o processo por 60 segundos e reiniciar.
3. No NVR, acessar **Reprodução / Playback**:
   * Verificar se a linha do tempo reflete a gravação do canal.
   * Confirmar se a lacuna de 60 segundos aparece corretamente identificada na linha de tempo do NVR sem travar o gravador.
   * Extrair um trecho de 1 minuto em formato MP4/AVI e verificar a legibilidade dos caracteres da tela capturada.
