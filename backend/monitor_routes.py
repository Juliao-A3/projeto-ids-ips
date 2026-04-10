from fastapi import APIRouter, Depends, HTTPException
from backend.dependencies import get_session, require_role
from backend.models import Alerta, LogEvento, Usuario
from backend.models import Severidade
from backend.schemas import LogEventoSchema
from backend.notification_service import notificar_alerta

monitor_router = APIRouter(prefix='/monitor', tags=['monitoramento'])


def _normalizar_severidade(valor):
    if valor is None:
        return Severidade.ALTA
    if isinstance(valor, Severidade):
        return valor
    texto = str(valor).strip().lower()

    if any(token in texto for token in ["ddos", "dos", "infilteration", "infiltration", "critica"]):
        return Severidade.CRITICA
    if any(token in texto for token in ["bruteforce", "brute force", "ssh", "ftp", "bot", "alta"]):
        return Severidade.ALTA
    if any(token in texto for token in ["scan", "probe", "suspected", "suspicious", "media"]):
        return Severidade.MEDIA
    if "baixa" in texto:
        return Severidade.BAIXA

    mapa = {
        "critica": Severidade.CRITICA,
        "alta": Severidade.ALTA,
        "media": Severidade.MEDIA,
        "baixa": Severidade.BAIXA,
    }
    return mapa.get(texto, Severidade.ALTA)

@monitor_router.post('/salvar_alerta', status_code=201)
async def salvar_alerta(
    log_evento: LogEventoSchema,
    usuario: Usuario = Depends(require_role(["admin"])),
    session = Depends(get_session)
):
    try:
        event_log = LogEvento(
            src_ip=log_evento.src_ip,
            dest_ip=log_evento.dest_ip,
            src_port=log_evento.src_port,
            dest_port=log_evento.dest_port,
            protocolo=log_evento.protocolo,
            assinatura=log_evento.assinatura,
            severidade=_normalizar_severidade(log_evento.severidade),
            status=log_evento.status
        )
        session.add(event_log)
        session.flush()

        alerta = Alerta(
            evento_id=event_log.id,
            ip_origem=log_evento.src_ip,
            ip_destino=log_evento.dest_ip,
            protocolo=log_evento.protocolo,
            porta_de_comunicacao=log_evento.dest_port
        )
        session.add(alerta)
        session.commit()

        # envia notificações automaticamente
        await notificar_alerta(event_log, session)

        return {"id": alerta.id, "mensagem": "Alerta salvo com sucesso"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@monitor_router.get('/logs')
async def listar_logs(
    limit: int = 20,
    usuario: Usuario = Depends(require_role(["admin", "analista", "operador"])),
    session = Depends(get_session)
):
    logs = session.query(LogEvento).order_by(LogEvento.id.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "timestamp": l.timestamp.isoformat() if l.timestamp else None,
            "src_ip": l.src_ip,
            "dest_ip": l.dest_ip,
            "protocolo": l.protocolo,
            "severidade": l.severidade,
            "status": l.status
        }
        for l in logs
    ]