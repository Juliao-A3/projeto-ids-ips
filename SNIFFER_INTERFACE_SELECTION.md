# Guia: Seleção de Interface de Captura

## Problema
Você não conseguia ver qual interface de rede o sniffer estava a usar para capturar pacotes.

## Solução

Agora existem dois endpoints para ajudar:

### 1. **Ver Interfaces Disponíveis** 
```bash
curl http://localhost:8000/sniffer/interfaces
```

Exemplo de resposta:
```json
{
  "monitored_interfaces": ["eth0", "eth1", "wlan0"],
  "count": 3,
  "status": "active"
}
```

### 2. **Ver Interface Selecionada Atualmente**
```bash
curl http://localhost:8000/sniffer/selected-interface
```

Quando o sniffer **NÃO** está a correr:
```json
{
  "running": false,
  "selected_interface": null,
  "message": "Sniffer não está a correr"
}
```

Quando o sniffer **ESTÁ** a correr:
```json
{
  "running": true,
  "selected_interface": "eth1",
  "forced": false,
  "all_interfaces": ["eth0", "eth1", "wlan0"],
  "message": "Capturando em: eth1"
}
```

## Como Forçar uma Interface Específica

Se quer garantir que o sniffer captura sempre na mesma interface:

1. **Editar arquivo `.env.sniffer`:**
   ```
   SNIFFER_FORCE_INTERFACE=eth1
   ```
   
   Substitua `eth1` pela interface que quer (pode ser `eth0`, `wlan0`, etc.)

2. **Reiniciar containers:**
   ```bash
   docker compose -f docker-compose.sniffer.yml up -d
   ```

3. **Verificar se foi aplicado:**
   ```bash
   curl http://localhost:8000/sniffer/selected-interface
   ```
   
   Verá `"forced": true` na resposta.

## Entender as Interfaces

- **eth0, eth1, eth2...** = Interfaces Ethernet (cabos de rede)
- **wlan0, wlan1...** = Interfaces WiFi
- **br-xxxxxxx** = Bridges de Docker (ignorar para captura de rede fisica)
- **docker0** = Interface interna do Docker (ignorar)

## Recomendação

Use a interface que está ligada à **rede física que quer monitorar**:
- Para monitorar o tráfego WAN → use a interface ligada ao modem/gateway
- Para monitorar o tráfego LAN → use a interface ligada ao switch/router
- Para monitorar o tráfego WiFi → use a interface wlan

## Verificação Rápida

```bash
# Ver qual interface tem IP (ativa)
ip addr show

# Ver qual interface está UP
ip link show

# Testar captura manual em eth1
sudo tcpdump -i eth1 -c 10
```
