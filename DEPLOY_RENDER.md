# Deploy no Render

Este repositório já contém `render.yaml` com:
- PostgreSQL gerenciado
- Backend FastAPI
- Frontend estático
- `alembic upgrade head` no start do backend

## Arquitetura para ambiente atrás de firewall

Este projeto deve ser dividido em dois planos:

- **Plano interno (atrás da firewall):** sensores IDS/IPS para borda (WAN), LAN e WLAN, com captura de tráfego, bloqueio local e coleta de eventos.
- **Plano público na nuvem:** backend de gestão, banco PostgreSQL e frontend web.

Fluxo recomendado:

```mermaid
flowchart LR
   INTERNET((Internet)) --> WAN_FW[Firewall/Gateway (WAN)]
   WAN_FW --> CORE[Rede interna]
   CORE --> LAN_SW[Switch LAN]
   CORE --> WLAN_CTRL[Controlador/AP WLAN]

   WAN_FW --> SENSOR_WAN[Sensor WAN/Borda]
   LAN_SW --> SENSOR_LAN[Sensor LAN]
   WLAN_CTRL --> SENSOR_WLAN[Sensor WLAN]

   SENSOR_WAN -->|Eventos, alertas e métricas| API[Backend FastAPI público]
   SENSOR_LAN -->|Eventos, alertas e métricas| API
   SENSOR_WLAN -->|Eventos, alertas e métricas| API

   API --> DB[(PostgreSQL)]
   WEB[Frontend web] --> API
```

## Estratégia de sensores

- **Opção A (recomendada):** 3 sensores lógicos (WAN, LAN e WLAN), cada um com política própria.
- **Opção B:** 1 host com múltiplas interfaces monitorando WAN, LAN e WLAN.

Regras práticas:

- WAN: foco em tráfego de entrada, scanning, brute force e flood externos.
- LAN: foco em movimento lateral, varredura interna e propagação de malware.
- WLAN: foco em BYOD, convidados, APs e tráfego leste-oeste sem fio.

Matriz operacional inicial:

- Consulte `SECURITY_BASELINE_WAN_LAN_WLAN.md` para limiares e ações de bloqueio por zona.

Configuração no sistema:

- Defina `SENSOR_ZONE` no sensor (`wan`, `lan` ou `wlan`).
- Para ajuste fino, use variáveis por zona como `IPS_WAN_THRESHOLD`, `IPS_LAN_MIN_BLOCK_CONFIDENCE` e `IPS_WLAN_ATTACK_WINDOW_SECONDS`.
- A rota `GET /sniffer/status` passa a mostrar `sensor_zone`, `ips_threshold`, `ips_min_confidence` e `ips_attack_window_s` ativos.

Monitoramento simultâneo WAN + LAN:

- O `POST /sniffer/start` agora aceita múltiplas interfaces no mesmo processo.
- Exemplo de payload para monitorar os dois lados ao mesmo tempo:

```json
{
   "interfaces": ["eth0", "eth1"],
   "zone_map": {
      "eth0": "wan",
      "eth1": "lan"
   }
}
```

- `GET /sniffer/status` retorna `interfaces` e `zone_map` para validação operacional.

## Passos

1. Suba este repositório no GitHub.
2. No Render, escolha **New +** -> **Blueprint**.
3. Selecione o repositório.
4. Confirme a criação dos recursos.
5. Após o provisionamento, verifique as variáveis de ambiente:
   - `DATABASE_URL` será injetada pelo Postgres do Render
   - `SECRET_KEY` será gerada automaticamente
   - `CORS_ALLOW_ORIGIN_REGEX` já aceita domínios `*.onrender.com`
   - `VITE_API_URL` aponta para a URL pública do backend (ex.: `https://aegis-backend.onrender.com`)

## Observações

- O backend executa `alembic upgrade head` antes de iniciar o Uvicorn.
- Os sensores IDS/IPS não devem ficar no Render; eles precisam rodar na infraestrutura de rede (gateway, switch espelhado, TAP ou host com acesso ao tráfego interno).
- Se você usar um domínio próprio no frontend, ajuste `CORS_ALLOW_ORIGIN_REGEX` ou `FRONTEND_ORIGINS` no backend.
- Para usar email de recuperação de senha, configure `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER` e `SMTP_PASS`.
- Se o sniffer IDS/IPS precisar capturar tráfego real, o backend precisa rodar em um ambiente com permissões de rede adequadas. Em PaaS comum isso pode ser limitado.
