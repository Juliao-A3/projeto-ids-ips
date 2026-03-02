from fastapi import APIRouter, Depends, HTTPException
from backend.dependencies import get_session
from backend.models import Alerta, LogEvento
from backend.schemas import LogEventoSchema


monitor_router = APIRouter(prefix='/monitor', tags=['monitoramento'])

@monitor_router.post('/salvar_alerta', status_code=201)
async def salvar_alerta(log_evento: LogEventoSchema, session = Depends(get_session)):
    try:
        event_log = LogEvento(
            src_ip=log_evento.src_ip,
            dest_ip=log_evento.dest_ip,
            src_port=log_evento.src_port,
            dest_port=log_evento.dest_port,
            protocolo=log_evento.protocolo,
            assinatura=log_evento.assinatura,
            severidade=log_evento.severidade,
            status=log_evento.status
        )
        session.add(event_log)
        session.flush()  # Gera o ID sem commitar

        alerta = Alerta(
            evento_id=event_log.id,
            ip_origem=log_evento.src_ip,
            ip_destino=log_evento.dest_ip,
            protocolo=log_evento.protocolo,
            porta_de_comunicacao=log_evento.dest_port
        )
        session.add(alerta)
        session.commit()
        
        return {"id": alerta.id, "mensagem": "Alerta salvo com sucesso"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))