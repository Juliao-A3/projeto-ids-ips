import os
import httpx
import asyncio
import logging

logger = logging.getLogger("aegis.sender")

CLOUD_URL = os.getenv("CLOUD_URL", "https://projeto-ids-ips.onrender.com")
TIMEOUT = 10


async def enviar_fluxo(fluxo: dict):
    """
    Envia o fluxo classificado para o endpoint /sniffer/flow-input da cloud.
    O backend já trata de classificar, guardar e fazer WebSocket push.
    """
    url = f"{CLOUD_URL}/sniffer/flow-input"

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(url, json=fluxo)
            if response.status_code == 200:
                logger.info(f"[SENDER] Fluxo enviado: {fluxo.get('src_ip', '')} → {fluxo.get('Label', '')}")
            else:
                logger.warning(f"[SENDER] Resposta inesperada: {response.status_code} - {response.text}")
    except httpx.ConnectError:
        logger.error(f"[SENDER] Sem conexão com a cloud: {url}")
    except httpx.TimeoutException:
        logger.error(f"[SENDER] Timeout ao enviar para {url}")
    except Exception as e:
        logger.error(f"[SENDER] Erro inesperado: {e}")


def enviar_fluxo_sync(fluxo: dict):
    """Wrapper síncrono para chamar do sniffer (thread não-async)."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(enviar_fluxo(fluxo), loop)
        else:
            asyncio.run(enviar_fluxo(fluxo))
    except Exception as e:
        logger.error(f"[SENDER] Erro ao agendar envio: {e}")
