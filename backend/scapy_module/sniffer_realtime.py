"""
sniffer_realtime.py  ·  AEGIS – Captura de tráfego com NFStream
----------------------------------------------------------------
Substitui a captura packet-by-packet do Scapy por captura ao nível
de FLUXO com NFStream. Vantagens:

  • Features completas CIC-IDS 2018 (incl. Init Fwd/Bwd Win Byts)
  • Sem reconstrução manual de estatísticas por pacote
  • Compatível com a mesma interface callback/WebSocket já existente
  • Funciona em Linux com permissões CAP_NET_RAW

Timeouts usados:
  idle_timeout   = 15 s  → fluxo sem actividade expira em 15 s
  active_timeout = 60 s  → fluxo activo expira ao fim de 60 s

Uso standalone (teste):
  python sniffer_realtime.py --interface enp0s3
"""

from __future__ import annotations

import sys
import os
import time
import logging
import asyncio
import argparse
import threading
from typing import Callable, Optional

# ── Path setup para imports locais ────────────────────────────────────────
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from nfstream import NFStreamer                        # pip install nfstream
from backend.scapy_module.extractor import extrair_features_nfstream
from backend.scapy_module.predictor  import prever_fluxo

# ── Logging ───────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] SNIFFER | %(message)s',
)
logger = logging.getLogger(__name__)

# ── Estado global ─────────────────────────────────────────────────────────
_rodando:    bool               = False
_interface:  str                = ''
_callback:   Optional[Callable] = None
_loop:       Optional[asyncio.AbstractEventLoop] = None
_thread:     Optional[threading.Thread]          = None
_stop_event: threading.Event    = threading.Event()

# Estatísticas da sessão
_stats = {
    'fluxos_processados': 0,
    'ataques_detetados':  0,
    'inicio':             0.0,
}


# ── API pública ───────────────────────────────────────────────────────────

def iniciar(
    interface: str,
    callback:  Optional[Callable] = None,
    loop:      Optional[asyncio.AbstractEventLoop] = None,
) -> None:
    """
    Inicia a captura NFStream em background.
    Chamado pelo sniffer_routes.py quando o utilizador clica "Iniciar".
    """
    global _rodando, _interface, _callback, _loop, _thread

    if _rodando:
        logger.warning("Sniffer já está activo — ignora novo pedido de início.")
        return

    _interface = interface
    _callback  = callback
    _loop      = loop

    _stop_event.clear()
    _stats['fluxos_processados'] = 0
    _stats['ataques_detetados']  = 0
    _stats['inicio']             = time.time()

    _rodando = True
    _thread  = threading.Thread(
        target   = _captura_loop,
        args     = (interface,),
        daemon   = True,
        name     = 'aegis-nfstream',
    )
    _thread.start()
    logger.info(f"✅ Captura NFStream iniciada em '{interface}'")


def parar() -> None:
    """
    Sinaliza paragem do sniffer.
    O loop termina ao processar o próximo fluxo expirado (≤ idle_timeout s).
    """
    global _rodando
    _rodando = False
    _stop_event.set()
    dur = round(time.time() - _stats['inicio'], 1) if _stats['inicio'] else 0
    logger.info(
        f"🛑 Sniffer parado | "
        f"duração={dur}s | "
        f"fluxos={_stats['fluxos_processados']} | "
        f"ataques={_stats['ataques_detetados']}"
    )


def estado() -> dict:
    """Devolve estado actual para polling do frontend."""
    return {
        'rodando':            _rodando,
        'interface':          _interface,
        'fluxos_processados': _stats['fluxos_processados'],
        'ataques_detetados':  _stats['ataques_detetados'],
        'uptime_s':           round(time.time() - _stats['inicio'], 1) if _stats['inicio'] else 0,
    }


# ── Loop interno ──────────────────────────────────────────────────────────

def _captura_loop(interface: str) -> None:
    """
    Corre numa thread dedicada.
    NFStreamer emite fluxos completos quando estes expiram — exactamente
    o formato em que o CIC-IDS 2018 foi gerado.
    """
    global _rodando

    try:
        streamer = NFStreamer(
            source             = interface,
            statistical_analysis = True,   # activa stats de pacotes e IAT
            idle_timeout       = 5,        # expira fluxo após 5 s sem pacotes
            active_timeout     = 20,        # expira fluxo activo após 20 s
            accounting_mode    = 3,         # contabiliza headers IP+TCP
            n_dissections      = 20,        # DPI para app_name (opcional)
        )

        logger.info("NFStreamer a aguardar fluxos...")

        for flow in streamer:
            # ── Verificação de paragem entre fluxos ───────────────────────
            if not _rodando or _stop_event.is_set():
                logger.info("Stop recebido — a sair do loop NFStream.")
                break

            _processar_fluxo(flow)

    except PermissionError:
        logger.error(
            "❌ Permissão negada ao abrir a interface. "
            "Executa: sudo setcap cap_net_raw,cap_net_admin=eip $(which python3)"
        )
    except Exception as exc:
        logger.error(f"Erro no loop NFStream: {exc}", exc_info=True)
    finally:
        _rodando = False
        logger.info("Thread NFStream terminada.")



# Limiar mínimo de confiança para classificar como ataque.
# Abaixo deste valor o fluxo é tratado como Benign (evita falsos positivos).
CONFIDENCE_THRESHOLD: float = float(os.getenv("AEGIS_ATTACK_THRESHOLD", "0.46"))


def _processar_fluxo(flow) -> None:
    """Extrai features, corre o modelo e notifica via callback."""
    _stats['fluxos_processados'] += 1

    # 1 — Extracção de features CIC-IDS 2018
    features = extrair_features_nfstream(flow)
    if features is None:
        return

    # 2 — Predição pelo Random Forest
    resultado = prever_fluxo(features)
    if resultado is None:
        return

    label      = resultado.get('label',      'Benign')
    confidence = resultado.get('confidence',  0.0)

    # 3 — Limiar de confiança: abaixo de CONFIDENCE_THRESHOLD → Benign
    if label.lower() != 'benign' and confidence < CONFIDENCE_THRESHOLD:
        logger.debug(
            f"⚪ Falso positivo suprimido: {label} ({confidence:.1%}) "
            f"< limiar {CONFIDENCE_THRESHOLD:.0%}"
        )
        label     = 'Benign'
        confidence = confidence   # mantém o valor real para o alerta

    is_attack = label.lower() != 'benign'

    if is_attack:
        _stats['ataques_detetados'] += 1

    # 3 — Construção do alerta
    alerta = {
        'src_ip'    : features.get('_src_ip',   '?'),
        'dst_ip'    : features.get('_dst_ip',   '?'),
        'src_port'  : int(features.get('_src_port', 0)),
        'dst_port'  : int(features.get('_dst_port', 0)),
        'protocol'  : int(features.get('_protocol',  0)),
        'app'       : features.get('_app', 'Unknown'),
        'label'     : label,
        'confidence': round(float(confidence), 4),
        'is_attack' : is_attack,
        # Métricas do fluxo úteis para o dashboard
        'flow_duration_s' : round(flow.bidirectional_duration_ms / 1000.0, 3),
        'total_bytes'     : int(flow.bidirectional_bytes),
        'total_packets'   : int(flow.bidirectional_packets),
    }

    # Log compacto
    icone = '🚨' if is_attack else '✅'
    logger.info(
        f"{icone} {alerta['src_ip']}:{alerta['src_port']} → "
        f"{alerta['dst_ip']}:{alerta['dst_port']} | "
        f"{label} ({confidence:.1%}) | "
        f"{alerta['flow_duration_s']}s | {alerta['total_bytes']} B"
    )

    # 4 — Envio assíncrono ao WebSocket
    if _callback and _loop and not _loop.is_closed():
        asyncio.run_coroutine_threadsafe(_callback(alerta), _loop)


# ── Entrada standalone ────────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AEGIS NFStream sniffer (teste standalone)')
    parser.add_argument('--interface', '-i', default='enp0s3', help='Interface de rede')
    args = parser.parse_args()

    print(f"\n🔍 AEGIS NFStream Sniffer — interface: {args.interface}")
    print("Ctrl+C para parar\n")

    # Callback de teste: imprime no terminal
    async def _print_alerta(alerta: dict) -> None:
        print(f"  → {alerta}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        iniciar(interface=args.interface, callback=_print_alerta, loop=loop)
        loop.run_forever()
    except KeyboardInterrupt:
        print("\n⏹  A parar...")
        parar()
    finally:
        loop.close()