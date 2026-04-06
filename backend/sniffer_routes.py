# backend/sniffer_routes.py
import asyncio
from datetime import datetime
import threading
import sys
import os
import shutil
import json
import ipaddress
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel

from dependencies import require_role, verificar_token_ws
from models import IpsBloqueados, LogEvento, Alerta, Severidade, Status, NetworkConfig
from sqlalchemy.orm import Session
from notification_service import notificar_alerta

# ── NFStream sniffer (nova API) ───────────────────────────────────────────────
from scapy_module.sniffer_realtime import iniciar as _sniffer_iniciar
from scapy_module.sniffer_realtime import parar   as _sniffer_parar
from scapy_module.sniffer_realtime import estado  as _sniffer_estado

PROJECT_PATH = Path(__file__).resolve().parent.parent

sniffer_router = APIRouter(prefix="/sniffer", tags=["Sniffer"])

# ── Whitelist IPs exactos ─────────────────────────────────────────────────────
_whitelist: set[str] = {'127.0.0.1'}

# ── Whitelist CIDR — ranges de fornecedores conhecidos e redes internas ───────
# Adiciona aqui qualquer range que não deva gerar alertas.
_whitelist_cidr: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = []

_CIDR_DEFAULTS = [
    # Loopback / link-local / multicast
    '127.0.0.0/8',
    '169.254.0.0/16',
    '224.0.0.0/4',
    'ff00::/8',
    'fe80::/10',
    '224.0.0.251',
    '239.255.255.250',
    '255.255.255.255',
    '192.168.100.76',
    # Google (GCP + serviços)
    '8.8.8.0/24',
    '8.8.4.0/24',
    '142.250.0.0/15',
    '142.251.0.0/16',
    '172.217.0.0/16',
    '34.0.0.0/9',
    '35.184.0.0/13',
    # Microsoft / Azure
    '13.64.0.0/11',
    '13.96.0.0/13',
    '13.104.0.0/14',
    '20.0.0.0/8',
    '40.64.0.0/10',
    # GitHub
    '140.82.112.0/20',
    '192.30.252.0/22',
    '185.199.108.0/22',
    # Cloudflare
    '1.1.1.0/24',
    '1.0.0.0/24',
    '104.16.0.0/13',
    '104.24.0.0/14',
]

for _cidr in _CIDR_DEFAULTS:
    try:
        _whitelist_cidr.append(ipaddress.ip_network(_cidr, strict=False))
    except ValueError:
        pass


def _ip_em_whitelist(ip: str) -> bool:
    """Verifica IP exacto e ranges CIDR."""
    if ip in _whitelist:
        return True
    try:
        addr = ipaddress.ip_address(ip)
        return any(addr in net for net in _whitelist_cidr)
    except ValueError:
        return False

# ── Estado global ────────────────────────────────────────────────────────────
_ws_clients:      list = []
_session_factory                  = None

# ── Event loop dedicado ───────────────────────────────────────────────────────
_loop: Optional[asyncio.AbstractEventLoop] = None

def _get_loop():
    global _loop
    if _loop is None or _loop.is_closed():
        _loop = asyncio.new_event_loop()
        threading.Thread(target=_loop.run_forever, daemon=True).start()
    return _loop

# ── Schemas ───────────────────────────────────────────────────────────────────
class SnifferStartSchema(BaseModel):
    interface: Optional[str] = None
    filtro:    Optional[str] = None
    bloquear:  bool = True

class WhitelistSchema(BaseModel):
    ip: str

class ModeloAtivoSchema(BaseModel):
    nome: str

# ── Broadcast WebSocket ───────────────────────────────────────────────────────
async def _broadcast_pacote(pkt_info: dict):
    mortos = []
    for ws in _ws_clients:
        try:
            await ws.send_json(pkt_info)
        except Exception:
            mortos.append(ws)
    for ws in mortos:
        if ws in _ws_clients:
            _ws_clients.remove(ws)

# ── Callback do NFStream ──────────────────────────────────────────────────────
async def _callback_fluxo(alerta: dict):
    """
    Chamado pelo sniffer_realtime.py para cada fluxo classificado.
    'alerta' tem as chaves: src_ip, dst_ip, src_port, dst_port,
    protocol, app, label, confidence, is_attack, flow_duration_s,
    total_bytes, total_packets.
    """
    # ── Filtro whitelist (IP exacto + ranges CIDR) ────────────────────────
    if _ip_em_whitelist(alerta.get("src_ip", "")) or \
       _ip_em_whitelist(alerta.get("dst_ip", "")):
        return

    # Normalizar para o formato que o frontend e o banco esperam
    pkt_info = {
        **alerta,
        'tipo':      'ataque' if alerta.get('is_attack') else 'normal',
        'protocolo': _proto_name(alerta.get('protocol', 0)),
        'confianca': round(alerta.get('confidence', 0) * 100, 1),
    }

    # ── Guardar no banco se for ataque ────────────────────────────────────
    if pkt_info['tipo'] == 'ataque' and _session_factory:
        try:
            session: Session = next(_session_factory())

            assinatura = (
                "RF_"
                + pkt_info.get('label', 'ATAQUE')
                  .upper().replace(' ', '_').replace('-', '_')
            )

            evento = LogEvento(
                src_ip     = pkt_info.get('src_ip',   'desconhecido'),
                dest_ip    = pkt_info.get('dst_ip',   'desconhecido'),
                src_port   = pkt_info.get('src_port',  0),
                dest_port  = pkt_info.get('dst_port',  0),
                protocolo  = pkt_info.get('protocolo', 'OUTRO'),
                assinatura = assinatura,
                severidade = Severidade.ALTA,
                status     = Status.PENDENTE,
            )
            session.add(evento)
            session.flush()

            alerta_db = Alerta(
                evento_id            = evento.id,
                ip_origem            = pkt_info.get('src_ip',  'desconhecido'),
                ip_destino           = pkt_info.get('dst_ip',  'desconhecido'),
                protocolo            = pkt_info.get('protocolo', 'OUTRO'),
                porta_de_comunicacao = pkt_info.get('dst_port', 0),
            )
            session.add(alerta_db)
            session.commit()

            asyncio.run_coroutine_threadsafe(
                notificar_alerta(evento, session),
                _get_loop()
            )

        except Exception as e:
            print(f"❌ Erro ao guardar no banco: {e}")
        finally:
            session.close()

    # ── Enviar para clientes WebSocket ────────────────────────────────────
    await _broadcast_pacote(pkt_info)


def _proto_name(proto_int: int) -> str:
    return {6: 'TCP', 17: 'UDP', 1: 'ICMP'}.get(int(proto_int), 'OUTRO')

# ── Helper — lê config de rede do banco ──────────────────────────────────────
def _ler_network_config():
    if not _session_factory:
        return None
    try:
        session = next(_session_factory())
        config  = session.query(NetworkConfig).first()
        session.close()
        return config
    except Exception as e:
        print(f"⚠ Erro ao ler config de rede: {e}")
        return None

# ── ROTAS ─────────────────────────────────────────────────────────────────────

@sniffer_router.post("/start")
async def start_sniffer(
    dados:   SnifferStartSchema,
    usuario = Depends(require_role(["admin"]))
):
    est = _sniffer_estado()
    if est.get('rodando'):
        raise HTTPException(status_code=400, detail="Sniffer já está a correr.")

    if sys.platform.startswith("linux") and os.geteuid() != 0:
        raise HTTPException(
            status_code=403,
            detail=(
                "Permissão insuficiente para captura de pacotes no Linux. "
                "Execute com sudo ou conceda CAP_NET_RAW e CAP_NET_ADMIN ao Python do .venv."
            ),
        )

    net_config      = _ler_network_config()
    interface_final = dados.interface

    if net_config:
        if not interface_final and net_config.capture_interface:
            interface_final = net_config.capture_interface
        # Carregar whitelist da BD
        if net_config.whitelist:
            for ip in net_config.whitelist.split(','):
                ip = ip.strip()
                if ip:
                    _whitelist.add(ip)

    _whitelist.add('127.0.0.1')

    loop = _get_loop()
    _sniffer_iniciar(
        interface = interface_final or 'enp0s3',
        callback  = _callback_fluxo,
        loop      = loop,
    )

    return {
        "message":   "Sniffer iniciado",
        "interface": interface_final or "enp0s3",
    }


@sniffer_router.post("/stop")
async def stop_sniffer(
    usuario = Depends(require_role(["admin"]))
):
    est = _sniffer_estado()
    if not est.get('rodando'):
        raise HTTPException(status_code=400, detail="Sniffer não está a correr.")
    _sniffer_parar()
    return {"message": "Sniffer parado com sucesso"}


@sniffer_router.post("/reboot")
async def reboot_sniffer(
    dados:   SnifferStartSchema,
    usuario = Depends(require_role(["admin"]))
):
    est = _sniffer_estado()
    if est.get('rodando'):
        _sniffer_parar()
        import time; time.sleep(2)
    return await start_sniffer(dados, usuario)


@sniffer_router.get("/status")
async def get_status(
    usuario = Depends(require_role(["admin", "analista", "operador"]))
):
    est   = _sniffer_estado()
    total = est.get('fluxos_processados', 0)
    ataques = est.get('ataques_detetados', 0)

    return {
        "running":            est.get('rodando', False),
        "interface":          est.get('interface', ''),
        "contador":           total,
        "anomalias":          ataques,
        "bloqueios":          0,          # NFStream não bloqueia directamente
        "taxa_anomalia":      round(ataques / total * 100, 2) if total > 0 else 0,
        "uptime_s":           est.get('uptime_s', 0),
        "whitelist":          list(_whitelist),
        "ips_bloqueados":     [],
        "stats":              {},
        "interface_ativas":   [est.get('interface', '')],
        "interface_inativas": [],
        "portas_tcp":         {},
        "portas_udp":         {},
        "ultimos_pacotes":    [],
        "contagem_ips":       {},
    }


@sniffer_router.post("/whitelist/add")
async def add_whitelist(
    dados:   WhitelistSchema,
    usuario = Depends(require_role(["admin"]))
):
    _whitelist.add(dados.ip)
    return {"message": f"IP {dados.ip} adicionado à whitelist"}


@sniffer_router.post("/whitelist/remove")
async def remove_whitelist(
    dados:   WhitelistSchema,
    usuario = Depends(require_role(["admin"]))
):
    _whitelist.discard(dados.ip)
    return {"message": f"IP {dados.ip} removido da whitelist"}


# ── WebSocket ─────────────────────────────────────────────────────────────────
@sniffer_router.websocket("/ws")
async def sniffer_ws(websocket: WebSocket, token: str = ""):
    if not _session_factory:
        await websocket.close(code=1008)
        return

    session = next(_session_factory())
    usuario = verificar_token_ws(token, session)
    if not usuario:
        await websocket.close(code=1008)
        session.close()
        return

    await websocket.accept()
    _ws_clients.append(websocket)

    try:
        est = _sniffer_estado()
        await websocket.send_json({
            "tipo":      "status",
            "running":   est.get('rodando', False),
            "contador":  est.get('fluxos_processados', 0),
            "anomalias": est.get('ataques_detetados', 0),
        })

        while True:
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        if websocket in _ws_clients:
            _ws_clients.remove(websocket)
    finally:
        session.close()


# ── Activar modelo ────────────────────────────────────────────────────────────
@sniffer_router.post("/modelo/ativar")
async def ativar_modelo(
    dados:   ModeloAtivoSchema,
    usuario = Depends(require_role(["admin"]))
):
    modelo_path = PROJECT_PATH / "models" / dados.nome
    if not modelo_path.exists():
        raise HTTPException(status_code=404, detail="Modelo não encontrado.")

    shutil.copy(modelo_path, PROJECT_PATH / "models" / "best_model.pkl")

    ref_path = PROJECT_PATH / "models" / "modelo_ativo.json"
    with open(ref_path, 'w') as f:
        json.dump({
            "nome":       dados.nome,
            "ativado_em": datetime.now().isoformat()
        }, f)

    return {
        "message":               f"Modelo {dados.nome} ativado com sucesso!",
        "modelo_ativo":          dados.nome,
        "arquivo_runtime":       "best_model.pkl",
        "usa_no_proximo_start":  True,
        "sniffer_em_execucao":   _sniffer_estado().get('rodando', False),
    }