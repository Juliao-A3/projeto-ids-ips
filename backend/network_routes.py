from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.dependencies import get_session, require_role
from backend.models import IpsBloqueados, Usuario, NetworkConfig
from pydantic import BaseModel
import psutil
from datetime import datetime, timezone

network_router = APIRouter(prefix='/network', tags=['network'])


def get_or_create_config(session: Session) -> NetworkConfig:
    config = session.query(NetworkConfig).first()
    if not config:
        config = NetworkConfig()
        session.add(config)
        session.commit()
        session.refresh(config)
    return config


@network_router.get('/interfaces')
async def get_interfaces(
    usuario: Usuario = Depends(require_role(["admin", "analista", "operador"])),
):
    interfaces = []
    stats = psutil.net_if_stats()
    addrs = psutil.net_if_addrs()
    io    = psutil.net_io_counters(pernic=True)

    for name, stat in stats.items():
        addr_list = addrs.get(name, [])
        ip  = next((a.address for a in addr_list if a.family.name == 'AF_INET'), '-')
        mac = next((a.address for a in addr_list
                    if a.family.name in ('AF_PACKET', 'AF_LINK')), '-')
        nic_io = io.get(name)

        interfaces.append({
            "name":         name,
            "status":       "UP" if stat.isup else "DOWN",
            "speed":        f"{stat.speed} Mbps" if stat.speed else "N/A",
            "ip":           ip,
            "mac":          mac,
            "packets_sent": nic_io.packets_sent if nic_io else 0,
            "packets_recv": nic_io.packets_recv if nic_io else 0,
        })

    return interfaces


@network_router.get('/blocked-ips')
async def get_blocked_ips(
    usuario: Usuario = Depends(require_role(["admin"])),
    session: Session = Depends(get_session)
):
    ips = session.query(IpsBloqueados).order_by(IpsBloqueados.bloqueado_em.desc()).all()
    return [
        {
            "id":           ip.id,
            "ip_bloqueado": ip.ip_bloqueado,
            "motivo":       ip.motivo,
            "bloqueado_em": ip.bloqueado_em.isoformat() if ip.bloqueado_em else None,
        }
        for ip in ips
    ]


@network_router.delete('/blocked-ips/{ip_id}')
async def unblock_ip(
    ip_id: int,
    usuario: Usuario = Depends(require_role(["admin"])),
    session: Session = Depends(get_session)
):
    ip = session.query(IpsBloqueados).filter(IpsBloqueados.id == ip_id).first()
    if not ip:
        raise HTTPException(status_code=404, detail='IP não encontrado')
    session.delete(ip)
    session.commit()
    return {"message": f"IP {ip.ip_bloqueado} desbloqueado com sucesso"}


class NetworkConfigSchema(BaseModel):
    capture_interface: str  = "eth0"
    promiscuous_mode:  bool = True
    bpf_filter:        str  = ""
    whitelist:         str  = "192.168.1.0/24, 10.0.0.0/8, 127.0.0.1"

@network_router.get('/config')
async def get_config(
    usuario: Usuario = Depends(require_role(["admin", "analista", "operador"])),
    session: Session = Depends(get_session)
):
    config = get_or_create_config(session)
    return {
        "capture_interface": config.capture_interface,
        "promiscuous_mode":  config.promiscuous_mode,
        "bpf_filter":        config.bpf_filter,
        "whitelist":         config.whitelist,
    }

@network_router.put('/config')
async def save_config(
    data: NetworkConfigSchema,
    usuario: Usuario = Depends(require_role(["admin"])),
    session: Session = Depends(get_session)
):
    config = get_or_create_config(session)
    config.capture_interface = data.capture_interface
    config.promiscuous_mode  = data.promiscuous_mode
    config.bpf_filter        = data.bpf_filter
    config.whitelist         = data.whitelist
    config.atualizado_em     = datetime.now(timezone.utc)
    session.commit()
    return {"message": "Configuração salva com sucesso"}    
    