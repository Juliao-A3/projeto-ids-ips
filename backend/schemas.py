from pydantic import BaseModel
from typing import Optional

class UsuarioSchema(BaseModel):
    email: str
    nome: str
    senha: str
    role: Optional[str] = "admin"
    ativo: Optional[bool] = True

    class Config:
        from_attributes = True

class StatsResponse(BaseModel):
    alerts: int
    blocked_ips: int
    throughput_mbps: float

class LogEventoSchema(BaseModel):
    src_ip: Optional[str]
    dest_ip: Optional[str]
    src_port: Optional[int]
    dest_port: Optional[int]
    protocolo: Optional[str]
    assinatura: Optional[str]
    severidade: Optional[str]
    status: Optional[str]

    class Config:
        from_attributes = True    