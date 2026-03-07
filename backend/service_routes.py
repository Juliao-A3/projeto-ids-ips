from fastapi import APIRouter, Depends
from backend.dependencies import get_session, verificar_token, require_role
from backend.models import IpsBloqueados, LogEvento, Status, Usuario

service_router = APIRouter(prefix='/service', tags=['stats'])

@service_router.get('/stats')
async def get_stats(
    usuario: Usuario = Depends(require_role(["admin", "analista", "operador"])),
    session = Depends(get_session)
):
    alerts_count = session.query(LogEvento).filter(
        LogEvento.status.in_([Status.PENDENTE, Status.MITIGADO])).count()
    bloqueio_count = session.query(IpsBloqueados).count()
    throughput_mbps = 0.0
    
    from datetime import datetime, timedelta, timezone
    cinco_minutos_atras = datetime.now(timezone.utc) - timedelta(minutes=5)
    atividade_recente = session.query(LogEvento).filter(
        LogEvento.timestamp >= cinco_minutos_atras
    ).count()
    
    sistema_ativo = atividade_recente > 0
    
    return {
        "alertas": alerts_count,
        "bloqueios": bloqueio_count,
        "throughput_mbps": throughput_mbps,
        "sistema_ativo": sistema_ativo
    }


@service_router.get('/system/metrics')
async def system_metrics(
    usuario: Usuario = Depends(require_role(["admin", "analista", "operador"]))
):
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=1, percpu=False)
        mem_info = psutil.virtual_memory()
        mem = mem_info.percent
        network_gbps = 1.0
        
        return {
            "cpu_load": float(round(cpu, 2)),
            "memory": float(round(mem, 2)),
            "network_gbps": float(round(network_gbps, 2))
        }
    except Exception as e:
        return {"cpu_load": 0.0, "memory": 0.0, "network_gbps": 0.0}


@service_router.get('/start')
async def start_service():
    return {"mensagem": "Serviço de monitoramento iniciado"}

@service_router.get('/stop')
async def stop_service():
    return {"mensagem": "Serviço de monitoramento parado"}