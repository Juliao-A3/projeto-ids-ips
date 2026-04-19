# Baseline de Regras - WAN, LAN e WLAN

Este baseline e um ponto de partida para producao. Ajuste apos 7-14 dias com base em falso positivo e trafego real.

## Politica por zona

| Zona | Objetivo principal | Acao padrao |
|---|---|---|
| WAN | Bloquear ameacas vindas da Internet | Bloqueio mais agressivo |
| LAN | Conter movimento lateral interno | Alertar primeiro, bloquear reincidencia |
| WLAN | Controlar risco de BYOD/convidados | Alertar e bloquear por comportamento persistente |

## Regras iniciais recomendadas

| Zona | Evento | Limiar inicial | Janela | Acao |
|---|---|---|---|---|
| WAN | Port scan (SYN sem ACK) | >= 20 destinos | 60s | Bloquear IP origem |
| WAN | SYN flood | >= 100 SYN e ACK baixo | 30s | Bloquear IP origem |
| WAN | Brute force SSH/FTP | >= 8 tentativas | 120s | Bloquear IP origem |
| WAN | HTTP flood | >= 200 req/min por IP | 60s | Bloquear IP origem |
| LAN | Varredura interna | >= 30 destinos | 120s | Alerta critico |
| LAN | Brute force interno | >= 10 tentativas | 180s | Alerta alto + bloquear na reincidencia |
| LAN | Beaconing suspeito | conexoes periodicas para C2 | 10m | Alerta alto |
| WLAN | Recon em clientes | >= 15 destinos | 90s | Alerta alto |
| WLAN | Ataque por dispositivo convidado | >= 2 eventos graves | 120s | Isolar dispositivo (bloqueio) |
| WLAN | Exfiltracao anomala | volume acima do baseline | 10m | Alerta critico |

## Parametros operacionais no sistema

Use estes valores no ambiente para comecar:

- `IPS_ATTACK_WINDOW_SECONDS=120`
- `IPS_MIN_BLOCK_CONFIDENCE=0.85`
- `ATTACK_MIN_CONFIDENCE=0.82`
- `INFILTRATION_MIN_CONFIDENCE=0.90`
- `LOCAL_NOISE_MIN_CONFIDENCE=0.93`

Ajuste sugerido por zona:

- WAN: reduzir `IPS_MIN_BLOCK_CONFIDENCE` para 0.80-0.85 se quiser resposta mais rapida.
- LAN: manter 0.85-0.90 para evitar bloqueio de servicos internos legitimos.
- WLAN: manter 0.85 e usar whitelist de infraestrutura (controladora, DHCP, DNS).

## Whitelist minima recomendada

- Gateway/firewall interno
- Servidores DNS e DHCP internos
- Controladora WLAN e APs
- Endpoints de monitoramento conhecidos (SIEM, backup, atualizacao)

## Politica de severidade

| Severidade | Criterio | Acao |
|---|---|---|
| Critica | DDoS, brute force intenso, exfiltracao clara | Bloqueio automatico + notificacao imediata |
| Alta | Recon persistente, malware suspeito | Alerta imediato + bloqueio por reincidencia |
| Media | Comportamento anomalo sem confirmacao | Alertar e observar |
| Baixa | Ruido ou desvio pequeno | Somente log |

## Runbook rapido de operacao

1. Primeira semana: modo alerta predominante, sem bloqueio automatico em LAN/WLAN.
2. Segunda semana: ativar bloqueio automatico em WAN e em casos criticos de LAN/WLAN.
3. Toda semana: revisar top IPs bloqueados e ajustar whitelist/threshold.
4. Todo incidente critico: registrar causa raiz e atualizar esta baseline.
