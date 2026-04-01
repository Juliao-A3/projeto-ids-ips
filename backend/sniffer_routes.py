# backend/sniffer_routes.py
import asyncio
from datetime import datetime
import threading
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel

from dependencies import require_role, verificar_token_ws
from models import IpsBloqueados, LogEvento, Alerta, Severidade, Status, NetworkConfig
from sqlalchemy.orm import Session
from notification_service import notificar_alerta
from scapy_module.sniffer_realtime import PROJECT_PATH, IPSRealtime
import shutil
import json

sniffer_router = APIRouter(prefix="/sniffer", tags=["Sniffer"])

# ── Estado global ────────────────────────────────────────────────────────────
_ips_instance:   Optional[IPSRealtime]      = None
_sniffer_thread: Optional[threading.Thread] = None
_ws_clients:     list[WebSocket]            = []
_session_factory                            = None

# ── Event loop dedicado ──────────────────────────────────────────────────────
_loop: Optional[asyncio.AbstractEventLoop] = None

def _get_loop():
    global _loop
    if _loop is None or _loop.is_closed():
        _loop = asyncio.new_event_loop()
        threading.Thread(target=_loop.run_forever, daemon=True).start()
    return _loop

# ── Schemas ──────────────────────────────────────────────────────────────────
class SnifferStartSchema(BaseModel):
    interface: Optional[str] = None
    filtro:    Optional[str] = None
    bloquear:  bool = True

class WhitelistSchema(BaseModel):
    ip: str

class ModeloAtivoSchema(BaseModel):
    nome: str

# ── Broadcast WebSocket ──────────────────────────────────────────────────────
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

# ── Callback do Scapy ────────────────────────────────────────────────────────
def _callback_pacote(pkt_info: dict):
    """
    Chamado pela thread do Scapy para cada fluxo processado.
    O Random Forest envia tipo='ataque' (em vez de 'anomalia').
    """
    # ── Guardar no banco se for ataque ──────────────────────────────────────
    if pkt_info.get("tipo") == "ataque" and _session_factory:
        try:
            session: Session = next(_session_factory())

            # Usa o label do RF como assinatura (ex: "SSH-Bruteforce")
            assinatura = f"RF_{pkt_info.get('label', 'ATAQUE').upper().replace(' ', '_').replace('-', '_')}"

            evento = LogEvento(
                src_ip     = pkt_info.get("src_ip", "desconhecido"),
                dest_ip    = pkt_info.get("dst_ip", "desconhecido"),
                src_port   = pkt_info.get("src_port", 0),
                dest_port  = pkt_info.get("dst_port", 0),
                protocolo  = pkt_info.get("protocolo", "OUTRO"),
                assinatura = assinatura,
                severidade = Severidade.ALTA,
                status     = Status.PENDENTE,
            )
            session.add(evento)
            session.flush()

            alerta = Alerta(
                evento_id             = evento.id,
                ip_origem             = pkt_info.get("src_ip", "desconhecido"),
                ip_destino            = pkt_info.get("dst_ip", "desconhecido"),
                protocolo             = pkt_info.get("protocolo", "OUTRO"),
                porta_de_comunicacao  = pkt_info.get("dst_port", 0),
            )
            session.add(alerta)

            if pkt_info.get("bloqueado"):
                ip_block = IpsBloqueados(
                    ip_bloqueado = pkt_info.get("src_ip"),
                    motivo       = (
                        f"Bloqueio automático — "
                        f"{pkt_info.get('label', 'ataque')} "
                        f"({pkt_info.get('confianca', 0)}% confiança)"
                    ),
                )
                session.add(ip_block)

            session.commit()

            asyncio.run_coroutine_threadsafe(
                notificar_alerta(evento, session),
                _get_loop()
            )

        except Exception as e:
            print(f"❌ Erro ao guardar no banco: {e}")
        finally:
            session.close()

    # ── Enviar para todos os clientes WebSocket ──────────────────────────────
    asyncio.run_coroutine_threadsafe(
        _broadcast_pacote(pkt_info),
        _get_loop()
    )

# ── Helper — lê config de rede do banco ─────────────────────────────────────
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

# ── ROTAS ────────────────────────────────────────────────────────────────────

@sniffer_router.post("/start")
async def start_sniffer(
    dados: SnifferStartSchema,
    usuario = Depends(require_role(["admin"]))
):
    global _ips_instance, _sniffer_thread

    if _ips_instance and _ips_instance.running:
        raise HTTPException(status_code=400, detail="Sniffer já está a correr.")

    net_config      = _ler_network_config()
    interface_final = dados.interface
    filtro_final    = dados.filtro

    if net_config:
        if not interface_final and net_config.capture_interface:
            interface_final = net_config.capture_interface
        if not filtro_final and net_config.bpf_filter:
            filtro_final = net_config.bpf_filter

    _ips_instance = IPSRealtime(
        interface = interface_final,
        filtro    = filtro_final,
        bloquear  = dados.bloquear,
        callback  = _callback_pacote,
    )

    if net_config and net_config.whitelist:
        for ip in net_config.whitelist.split(','):
            ip = ip.strip()
            if ip:
                _ips_instance.adicionar_whitelist(ip)

    _ips_instance.adicionar_whitelist('127.0.0.1')

    _sniffer_thread = threading.Thread(
        target = _ips_instance.iniciar,
        daemon = True
    )
    _sniffer_thread.start()

    return {
        "message":   "Sniffer iniciado",
        "interface": interface_final or "todas",
        "filtro":    filtro_final    or "nenhum",
    }


@sniffer_router.post("/stop")
async def stop_sniffer(
    usuario = Depends(require_role(["admin"]))
):
    global _ips_instance
    if not _ips_instance or not _ips_instance.running:
        raise HTTPException(status_code=400, detail="Sniffer não está a correr.")
    _ips_instance.parar()
    return {"message": "Sniffer parado com sucesso"}


@sniffer_router.post("/reboot")
async def reboot_sniffer(
    dados: SnifferStartSchema,
    usuario = Depends(require_role(["admin"]))
):
    global _ips_instance
    if _ips_instance and _ips_instance.running:
        _ips_instance.parar()
        import time; time.sleep(1)
    return await start_sniffer(dados, usuario)


@sniffer_router.get("/status")
async def get_status(
    usuario = Depends(require_role(["admin", "analista", "operador"]))
):
    if not _ips_instance:
        return {
            "running":            False,
            "contador":           0,
            "anomalias":          0,
            "bloqueios":          0,
            "taxa_anomalia":      0,
            "ips_bloqueados":     [],
            "whitelist":          [],
            "stats":              {},
            "interface_ativas":   [],
            "interface_inativas": [],
            "portas_tcp":         {},
            "portas_udp":         {},
            "ultimos_pacotes":    [],
            "contagem_ips":       {},
        }

    ips = _ips_instance
    # contador_fluxos é o nome correcto no IPSRealtime actualizado
    total = ips.contador_fluxos

    return {
        "running":            ips.running,
        "contador":           total,
        "anomalias":          ips.anomalias,
        "bloqueios":          ips.bloqueios,
        "taxa_anomalia":      round((ips.anomalias / total * 100), 2) if total > 0 else 0,
        "ips_bloqueados":     list(ips.ips_bloqueados),
        "whitelist":          list(ips.whitelist),
        "stats":              ips.stats,
        "interface_ativas":   [ips.get_friendly_interface_name(i) for i in ips.interface_ativas],
        "interface_inativas": [ips.get_friendly_interface_name(i) for i in ips.interface_inativas],
        "portas_tcp":         dict(sorted(ips.portas_tcp.items(),  key=lambda x: x[1], reverse=True)[:10]),
        "portas_udp":         dict(sorted(ips.portas_udp.items(),  key=lambda x: x[1], reverse=True)[:10]),
        "ultimos_pacotes":    list(ips.ultimos_fluxos)[-20:],   # ← corrigido
        "contagem_ips":       dict(sorted(ips.contagem_ips.items(), key=lambda x: x[1], reverse=True)[:10]),
    }


@sniffer_router.post("/whitelist/add")
async def add_whitelist(
    dados: WhitelistSchema,
    usuario = Depends(require_role(["admin"]))
):
    if not _ips_instance:
        raise HTTPException(status_code=400, detail="Sniffer não está ativo.")
    _ips_instance.adicionar_whitelist(dados.ip)
    return {"message": f"IP {dados.ip} adicionado à whitelist"}


@sniffer_router.post("/whitelist/remove")
async def remove_whitelist(
    dados: WhitelistSchema,
    usuario = Depends(require_role(["admin"]))
):
    if not _ips_instance:
        raise HTTPException(status_code=400, detail="Sniffer não está ativo.")
    _ips_instance.remover_whitelist(dados.ip)
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
        if _ips_instance:
            await websocket.send_json({
                "tipo":      "status",
                "running":   _ips_instance.running,
                "contador":  _ips_instance.contador_fluxos,  # ← corrigido
                "anomalias": _ips_instance.anomalias,
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
    dados: ModeloAtivoSchema,
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

    return {"message": f"Modelo {dados.nome} ativado com sucesso!"}