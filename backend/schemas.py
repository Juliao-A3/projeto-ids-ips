from pydantic import BaseModel
from typing import Optional

class UsuarioSchema(BaseModel):
    email: str
    nome: str
    senha: str
    role: str = "admin"
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
class LoginSchema(BaseModel):
    email: str
    senha: str

    class Config:
        from_attributes = True            

class RefreshTokenSchema(BaseModel):
    refresh_token: str        

class NotificationConfigSchema(BaseModel):
    email_provider:     str             = "gmail"
    smtp_server:        Optional[str]   = None
    smtp_port:          int             = 587
    smtp_ssl:           bool            = True
    smtp_username:      Optional[str]   = None
    smtp_password:      Optional[str]   = None
    smtp_enabled:       bool            = False
    telegram_token:     Optional[str]   = None
    telegram_chat_id:   Optional[str]   = None
    telegram_enabled:   bool            = False
    teams_webhook:      Optional[str]   = None
    teams_enabled:      bool            = False
    trigger_critical:   bool            = True
    trigger_high:       bool            = True
    trigger_medium:     bool            = False

    class Config:
        from_attributes = True    