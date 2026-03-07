from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.dependencies import get_session, require_role
from backend.models import LogEvento, Alerta, IpsBloqueados, Status, Severidade, Usuario
from datetime import datetime, timezone, timedelta
from fastapi.responses import StreamingResponse
from backend.pdf_service import gerar_pdf
from backend.dependencies import get_session, require_role, verificar_token_query

reports_router = APIRouter(prefix='/reports', tags=['reports'])


def get_period_filter(period: str):
    agora = datetime.now(timezone.utc)
    if period == "24h":
        return agora - timedelta(hours=24)
    elif period == "7d":
        return agora - timedelta(days=7)
    elif period == "30d":
        return agora - timedelta(days=30)
    return agora - timedelta(hours=24)


@reports_router.get('/summary')
async def get_summary(
    period: str = "24h",
    severity: str = "all",
    usuario: Usuario = Depends(require_role(["admin", "analista", "operador"])),
    session: Session = Depends(get_session)
):
    desde = get_period_filter(period)

    query = session.query(LogEvento).filter(LogEvento.timestamp >= desde)

    if severity != "all":
        query = query.filter(LogEvento.severidade == severity)

    total_eventos    = query.count()
    criticos         = query.filter(LogEvento.severidade == Severidade.CRITICA).count()
    altos            = query.filter(LogEvento.severidade == Severidade.ALTA).count()
    medios           = query.filter(LogEvento.severidade == Severidade.MEDIA).count()
    bloqueados       = query.filter(LogEvento.status == Status.MITIGADO).count()
    total_bloqueados = session.query(IpsBloqueados).count()

    return {
        "total_eventos":    total_eventos,
        "criticos":         criticos,
        "altos":            altos,
        "medios":           medios,
        "bloqueados":       bloqueados,
        "total_ips_bloqueados": total_bloqueados,
    }


@reports_router.get('/incidents')
async def get_incidents(
    period: str = "24h",
    severity: str = "all",
    limit: int = 10,
    usuario: Usuario = Depends(require_role(["admin", "analista", "operador"])),
    session: Session = Depends(get_session)
):
    desde = get_period_filter(period)

    query = session.query(LogEvento).filter(LogEvento.timestamp >= desde)

    if severity != "all":
        query = query.filter(LogEvento.severidade == severity)

    logs = query.order_by(LogEvento.timestamp.desc()).limit(limit).all()

    return [
        {
            "id":         l.id,
            "timestamp":  l.timestamp.isoformat() if l.timestamp else None,
            "evento":     l.assinatura or "Evento desconhecido",
            "origem":     l.src_ip,
            "destino":    l.dest_ip,
            "protocolo":  l.protocolo,
            "severidade": l.severidade.value if l.severidade else None,
            "status":     l.status.value if l.status else None,
        }
        for l in logs
    ]


@reports_router.get('/attack-volume')
async def get_attack_volume(
    period: str = "24h",
    usuario: Usuario = Depends(require_role(["admin", "analista", "operador"])),
    session: Session = Depends(get_session)
):
    desde = get_period_filter(period)

    logs = session.query(LogEvento).filter(
        LogEvento.timestamp >= desde
    ).order_by(LogEvento.timestamp).all()

    # agrupa por hora
    volume = {}
    for log in logs:
        if log.timestamp:
            hora = log.timestamp.strftime("%H:%M")
            volume[hora] = volume.get(hora, 0) + 1

    return [{"time": k, "attacks": v} for k, v in sorted(volume.items())]

@reports_router.get('/export/pdf')
async def export_pdf(
    period: str = "24h",
    severity: str = "all",
    usuario: Usuario = Depends(require_role(["admin", "analista", "operador"])),
    session: Session = Depends(get_session)
    ):
    desde = get_period_filter(period)
    query = session.query(LogEvento).filter(LogEvento.timestamp >= desde)

    if severity != "all":
        query = query.filter(LogEvento.severidade == severity)

    logs = query.order_by(LogEvento.timestamp.desc()).all()

    # summary
    total    = len(logs)
    criticos = sum(1 for l in logs if l.severidade == Severidade.CRITICA)
    altos    = sum(1 for l in logs if l.severidade == Severidade.ALTA)
    medios   = sum(1 for l in logs if l.severidade == Severidade.MEDIA)
    bloqueados = sum(1 for l in logs if l.status == Status.MITIGADO)
    total_ips  = session.query(IpsBloqueados).count()

    summary = {
        "total_eventos": total,
        "criticos":      criticos,
        "altos":         altos,
        "medios":        medios,
        "bloqueados":    bloqueados,
        "total_ips_bloqueados": total_ips,
    }

    period_label = {"24h": "Últimas 24 Horas", "7d": "Últimos 7 Dias", "30d": "Últimos 30 Dias"}.get(period, period)
    pdf_buf = gerar_pdf(logs, summary, period_label)

    return StreamingResponse(
        pdf_buf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=aegis-report-{period}.pdf",
            "Access-Control-Allow-Origin": "http://localhost:5173",
            "Access-Control-Allow-Credentials": "true",
        }
    )