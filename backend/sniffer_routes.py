# backend/sniffer_routes.py
import asyncio
from datetime import datetime
import threading
import sys
import os
import shutil
import json
from collections import defaultdict, deque
from typing import Union
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from scapy_module.sniffer_realtime import processar_fluxo as _sniffer_processar
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel

from dependencies import require_role, verificar_token_ws
from models import IpsBloqueados, LogEvento, Alerta, Severidade, Status, NetworkConfig
from sqlalchemy.orm import Session
from notification_service import notificar_alerta
from whitelist import get_whitelist

# NFStream sniffer (nova API) 
from scapy_module.sniffer_realtime import iniciar as _sniffer_iniciar
from scapy_module.sniffer_realtime import parar   as _sniffer_parar
from scapy_module.sniffer_realtime import estado  as _sniffer_estado

PROJECT_PATH = Path(__file__).resolve().parent.parent

sniffer_router = APIRouter(prefix="/sniffer", tags=["Sniffer"])

# ── Obter instância global da whitelist 
_whitelist_manager = get_whitelist()

# ── Estado global
_ws_clients: list = []
_session_factory = None
_contagem_ips: defaultdict[str, int] = defaultdict(int)
_ultimos_pacotes: deque[dict] = deque(maxlen=50)
_stats_lock = threading.Lock()

# ── Event loop dedicado 
_loop: Optional[asyncio.AbstractEventLoop] = None

def _get_loop():
    global _loop
    if _loop is None or _loop.is_closed():
        _loop = asyncio.new_event_loop()
        threading.Thread(target=_loop.run_forever, daemon=True).start()
    return _loop

# ── Schemas 
class SnifferStartSchema(BaseModel):
    interface: Optional[str] = None
    filtro:    Optional[str] = None
    bloquear:  bool = True

class WhitelistSchema(BaseModel):
    ip: str

class ModeloAtivoSchema(BaseModel):
    nome: str

# ── Broadcast WebSocket 
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


async def _persistir_alerta_async(pkt_info: dict):
    """Persistencia e notificacao em segundo plano para nao atrasar os logs em tempo real."""
    if pkt_info.get('tipo') != 'ataque' or not _session_factory:
        return

    session: Optional[Session] = None
    try:
        session = next(_session_factory())

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
            severidade = _normalizar_severidade_alerta(True, pkt_info.get('label')),
            assinatura = assinatura,
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

        try:
            await notificar_alerta(evento, session)
        except Exception as notify_err:
            print(f"⚠ Erro ao enviar notificações: {notify_err}")

    except Exception as e:
        if session is not None:
            try:
                session.rollback()
            except Exception:
                pass
        print(f"❌ Erro ao guardar no banco: {e}")
    finally:
        if session is not None:
            session.close()

# ── Callback do NFStream 
async def _callback_fluxo(alerta: dict):
    """
    Chamado pelo sniffer_realtime.py para cada fluxo classificado.
    'alerta' tem as chaves: src_ip, dst_ip, src_port, dst_port,
    protocol, app, label, confidence, is_attack, flow_duration_s,
    total_bytes, total_packets.
    """
    try:
        if not isinstance(alerta, dict):
            return

        # Filtro whitelist apenas para tráfego totalmente interno/infra.
        # Se apenas uma ponta estiver na whitelist, mantém o log para o frontend.
        src_whitelisted = _whitelist_manager.is_ip_whitelisted(alerta.get("src_ip", ""))
        dst_whitelisted = _whitelist_manager.is_ip_whitelisted(alerta.get("dst_ip", ""))
        if src_whitelisted and dst_whitelisted:
            return

        # Normalizar para o formato que o frontend e o banco esperam
        pkt_info = {
            **alerta,
            'timestamp': datetime.now().isoformat(),
            'tipo':      'ataque' if alerta.get('is_attack') else 'normal',
            'protocolo': _proto_name(alerta.get('protocol', 0)),
            'confianca': round(alerta.get('confidence', 0) * 100, 1),
        }

        with _stats_lock:
            _ultimos_pacotes.appendleft(pkt_info)
            if pkt_info['tipo'] == 'ataque':
                src_ip = str(pkt_info.get('src_ip', '')).strip()
                if src_ip:
                    _contagem_ips[src_ip] += 1

        # Enviar para clientes WebSocket imediatamente para reduzir latencia visual.
        await _broadcast_pacote(pkt_info)

        # Persistencia/notificacao em segundo plano para nao bloquear o stream dos logs.
        if pkt_info['tipo'] == 'ataque':
            asyncio.create_task(_persistir_alerta_async(pkt_info))

    except Exception as e:
        print(f"[sniffer_routes] Erro no callback de fluxo: {e}")


def _proto_name(proto_int: int) -> str:
    try:
        proto_num = int(proto_int)
    except (TypeError, ValueError):
        return 'OUTRO'
    return {6: 'TCP', 17: 'UDP', 1: 'ICMP'}.get(proto_num, 'OUTRO')


def _normalizar_severidade_alerta(is_attack: bool, label: Optional[str]) -> Union[Severidade, None]:
    if not is_attack:
        return None

    label_norm = str(label or "").strip().lower()

    # Critica: ataques volumétricos/disruptivos.
    if any(token in label_norm for token in ["ddos", "dos", "infilteration", "infiltration"]):
        return Severidade.CRITICA

    # Alta: brute force e bot activity confirmada.
    if any(token in label_norm for token in ["bruteforce", "brute force", "ssh-", "ftp-", "bot"]):
        return Severidade.ALTA

    # Media: padrões suspeitos/sondagem.
    if any(token in label_norm for token in ["scan", "probe", "suspected", "suspicious"]):
        return Severidade.MEDIA

    # Fallback seguro para ataque desconhecido.
    return Severidade.ALTA

# Helper — lê config de rede do banco 
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

# ── ROTAS 

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
                    _whitelist_manager.add_exact_ip(ip)

    loop = _get_loop()
    interface_capture = interface_final or 'eth0'

    _sniffer_iniciar(
        interface = interface_capture,
        callback  = _callback_fluxo,
        loop      = loop,
    )

    with _stats_lock:
        _contagem_ips.clear()
        _ultimos_pacotes.clear()

    return {
        "message":   "Sniffer iniciado",
        "interface": interface_capture,
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
    with _stats_lock:
        contagem_ips = dict(_contagem_ips)
        ultimos_pacotes = list(_ultimos_pacotes)

    return {
        "running":            est.get('rodando', False),
        "interface":          est.get('interface', ''),
        "contador":           total,
        "anomalias":          ataques,
        "bloqueios":          0,          # NFStream não bloqueia directamente
        "taxa_anomalia":      round(ataques / total * 100, 2) if total > 0 else 0,
        "uptime_s":           est.get('uptime_s', 0),
        "whitelist":          list(_whitelist_manager.get_all_ips()),
        "ips_bloqueados":     [],
        "stats":              {},
        "interface_ativas":   [est.get('interface', '')],
        "interface_inativas": [],
        "portas_tcp":         {},
        "portas_udp":         {},
        "ultimos_pacotes":    ultimos_pacotes,
        "contagem_ips":       contagem_ips,
    }


@sniffer_router.post("/whitelist/add")
async def add_whitelist(
    dados:   WhitelistSchema,
    usuario = Depends(require_role(["admin"]))
):
    if _whitelist_manager.add_exact_ip(dados.ip):
        return {"message": f"IP {dados.ip} adicionado à whitelist"}
    else:
        raise HTTPException(status_code=400, detail=f"IP inválido: {dados.ip}")


@sniffer_router.post("/whitelist/remove")
async def remove_whitelist(
    dados:   WhitelistSchema,
    usuario = Depends(require_role(["admin"]))
):
    if _whitelist_manager.remove_exact_ip(dados.ip):
        return {"message": f"IP {dados.ip} removido da whitelist"}
    raise HTTPException(status_code=404, detail=f"IP {dados.ip} não está na whitelist")


# WebSocket 
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


# Activar modelo 
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
# endpoint que recebe os fluxos do cicflowmeter

from fastapi import Request
from fastapi.responses import JSONResponse

@sniffer_router.post("/flow-input")
async def receber_fluxo(request: Request):
    """
    O cicflowmeter faz POST aqui com o JSON de cada fluxo terminado.
    Classifica e transmite pelo WebSocket.
    """
    try:
        flow_dict = await request.json()
        dados = await _sniffer_processar(flow_dict)

        # Fallback de entrega: garante histórico de logs no /sniffer/status
        # mesmo quando o callback em tempo real falha.
        if isinstance(dados, dict):
            pkt_info = {
                **dados,
                "timestamp": datetime.now().isoformat(),
                "tipo": "ataque" if dados.get("is_attack") else "normal",
                "protocolo": _proto_name(dados.get("protocol", 0)),
                "confianca": round(float(dados.get("confidence", 0)) * 100, 1),
            }

            with _stats_lock:
                exists = any(
                    p.get("id") == pkt_info.get("id")
                    and p.get("src_ip") == pkt_info.get("src_ip")
                    and p.get("dst_ip") == pkt_info.get("dst_ip")
                    and p.get("dst_port") == pkt_info.get("dst_port")
                    for p in _ultimos_pacotes
                )
                if not exists:
                    _ultimos_pacotes.appendleft(pkt_info)
                    if pkt_info["tipo"] == "ataque":
                        src_ip = str(pkt_info.get("src_ip", "")).strip()
                        if src_ip:
                            _contagem_ips[src_ip] += 1

        return JSONResponse({"status": "ok"})
    except Exception as e:
        print(f"[sniffer_routes] Erro em /flow-input: {e}")
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)