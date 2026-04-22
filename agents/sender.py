import os
import httpx
import asyncio
import logging

logger = logging.getLogger("aegis.sender")

CLOUD_URL = os.getenv("CLOUD_URL", "https://projeto-ids-ips.onrender.com/")
AGENT_TOKEN = os.getenv("AGENT_TOKEN", "")
TIMEOUT = 10  # segundos


async def enviar_alerta(alerta: dict):
    """
    Envia um alerta de ataque detetado para a API cloud.

    alerta = {
        "ip_origem": "192.168.10.20",
        "ip_destino": "192.168.10.10",
        "tipo_ataque": "DoS",
        "confianca": 0.97,
        "interface": "eth0",
        "protocolo": "TCP",
        "porta_destino": 80,
        "bloqueado": True
    }
    """
    url = f"{CLOUD_URL}/api/agent/alerta"
    headers = {
        "X-Agent-Token": AGENT_TOKEN,
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(url, json=alerta, headers=headers)
            if response.status_code == 200:
                logger.info(f"[SENDER] Alerta enviado: {alerta['tipo_ataque']} ({alerta['ip_origem']})")
            else:
                logger.warning(f"[SENDER] Resposta inesperada: {response.status_code} - {response.text}")
    except httpx.ConnectError:
        logger.error(f"[SENDER] Sem conexão com a cloud: {url}")
    except httpx.TimeoutException:
        logger.error(f"[SENDER] Timeout ao enviar alerta para {url}")
    except Exception as e:
        logger.error(f"[SENDER] Erro inesperado: {e}")


def enviar_alerta_sync(alerta: dict):
    """Wrapper síncrono para chamar do sniffer (thread não-async)."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(enviar_alerta(alerta), loop)
        else:
            asyncio.run(enviar_alerta(alerta))
    except Exception as e:
        logger.error(f"[SENDER] Erro ao agendar envio: {e}")
