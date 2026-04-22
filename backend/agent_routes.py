import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from backend.database import get_db
from backend.models import Alerta, IpsBloqueados

router = APIRouter(prefix="/api/agent", tags=["Agente"])

AGENT_SECRET = os.getenv("AGENT_SECRET", "token_secreto_aqui")


# ─── Schema do alerta enviado pelo agente ────────────────────────────
class AlertaAgente(BaseModel):
    ip_origem: str
    ip_destino: Optional[str] = ""
    tipo_ataque: str
    confianca: float
    interface: str
    protocolo: Optional[str] = ""
    porta_destino: Optional[int] = 0
    bloqueado: bool = True


def verificar_token(x_agent_token: str = Header(...)):
    """Valida o token do agente."""
    if x_agent_token != AGENT_SECRET:
        raise HTTPException(status_code=401, detail="Token de agente inválido")
    return x_agent_token


# ─── Endpoint principal ──────────────────────────────────────────────
@router.post("/alerta")
async def receber_alerta_agente(
    alerta: AlertaAgente,
    db: Session = Depends(get_db),
    token: str = Depends(verificar_token)
):
    novo_alerta = Alerta(
        ip_origem=alerta.ip_origem,
        tipo_ataque=alerta.tipo_ataque,
        confianca=alerta.confianca,
        bloqueado=alerta.bloqueado,
    )
    db.add(novo_alerta)
    db.commit()
    return {"status": "ok"}


# ─── Health check do agente ──────────────────────────────────────────
@router.get("/ping")
async def ping(token: str = Depends(verificar_token)):
    """O agente usa isto para verificar se a cloud está acessível."""
    return {"status": "online", "timestamp": datetime.utcnow().isoformat()}
