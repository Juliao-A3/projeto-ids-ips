from fastapi import APIRouter, Depends

from backend.dependencies import get_session
from backend.models import IpsBloqueados, LogEvento, Status
from backend.schemas import StatsResponse

service_router = APIRouter(prefix='/service', tags=['stats'])

@service_router.get('/stats')
async def get_stats(dados: StatsResponse, session = Depends(get_session)):
    alerts_count = session.query(LogEvento).filter(
    LogEvento.status.in_([Status.PENDENTE, Status.MITIGADO])).count()
    bloqueio_count = session.query(IpsBloqueados).count()

    throughput_mbps = 0.0  # Vou substituir isso por um cálculo real baseado nos dados de rede
    stats = {
        "alertas": alerts_count,
        "bloqueios": bloqueio_count,
        "throughput_mbps": throughput_mbps
    }
    return stats

@service_router.get('/start')
async def start_service():
    # Aqui vamos poder iniciar o serviço de monitoramento
    return {"mensagem": "Serviço de monitoramento iniciado"}

@service_router.get('/stop')
async def stop_service():
    # Aqui vamos poder parar o serviço de monitoramento
    return {"mensagem": "Serviço de monitoramento parado"}