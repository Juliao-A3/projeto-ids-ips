from datetime import datetime, timezone
from sqlalchemy import JSON, create_engine, Column, String, Integer, Boolean, Float, Enum, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship


import os
from sqlalchemy import create_engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

db_path = os.path.join(BASE_DIR, "database", "banco.db")
db_path = os.path.abspath(db_path)

engine = create_engine(f"sqlite:///{db_path}")

Base = declarative_base()

class UserRole(str, PyEnum):
    ADMIN = "admin"
    ANALISTA = "analista"
    OPERADOR = "operador"

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nome = Column("nome", String)
    email = Column("email", String, nullable=False, unique=True)
    senha_hash = Column("senha", String, nullable=False)
    role = Column(Enum(UserRole, name="user_roles"), nullable=False)
    avatar_url = Column(String)
    ativo = Column("ativo", Boolean, default=False)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, nome, email, senha_hash, role, ativo):
        self.nome = nome
        self.email = email
        self.senha_hash = senha_hash
        self.role = role
        self.ativo = ativo

#Tabela: logs_eventos (Histórico de Tráfego)
   
class Status(str, PyEnum):
    PENDENTE = "pendente"
    MITIGADO = "mitigado"
    IGNORADO = "ignorado"

class Severidade(str, PyEnum):
    CRITICA = "critica"
    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"

class LogEvento(Base):
    __tablename__ = 'log_eventos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    src_ip = Column('ip_origem', String(45), nullable=False)
    dest_ip = Column('ip_destino', String(45))
    src_port = Column('porta_origem', Integer)
    dest_port = Column('porta_destino', Integer)
    protocolo = Column(String(20))
    assinatura = Column('regras', String)
    severidade = Column(Enum(Severidade, name='severidade'))
    status = Column(Enum(Status, name='status'), default=Status.PENDENTE) #status do evento, se ele ja foi mitigado, ignorado ou ainda esta pendente de analise
    #RELACIONAMENTOS 1 para muitos com as tabelas de AnaliseIA e Alerta
    analises = relationship("AnaliseIA", backref="evento", cascade="all, delete")
    alertas = relationship("Alerta", backref="evento", cascade="all, delete")

    def __init__(self, src_ip, dest_ip, src_port, dest_port, protocolo, assinatura=None, severidade=None, status=Status.PENDENTE):
        self.src_ip = src_ip
        self.dest_ip = dest_ip
        self.src_port = src_port
        self.dest_port = dest_port
        self.protocolo = protocolo
        self.assinatura = assinatura
        self.severidade = severidade
        self.status = status
        self.timestamp = datetime.now(timezone.utc)
        self.analises = []
        self.alertas = []

class Alerta(Base):
    __tablename__ = 'alertas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    evento_id = Column(Integer, ForeignKey('log_eventos.id'), nullable=False)
    ip_origem = Column(String(45), nullable=False)
    ip_destino = Column(String(45), nullable=False)
    protocolo = Column(String(20))
    porta_de_comunicacao = Column(Integer)
    criado_em = Column(DateTime(timezone=True), default=lambda: datetime.now(datetime.timezone.utc))   

    def __init__(self, evento_id, ip_origem, ip_destino, protocolo, porta_de_comunicacao):
        self.evento_id = evento_id
        self.criado_em = datetime.now(timezone.utc)
        self.ip_origem = ip_origem
        self.ip_destino = ip_destino
        self.protocolo = protocolo
        self.porta_de_comunicacao = porta_de_comunicacao

#ai_score: Float (O nível de anomalia detectado pela sua IA, de 0 a 1)

class AnaliseIA(Base):
    __tablename__ = 'analises_ia'

    id = Column(Integer, primary_key=True, autoincrement=True)
    evento_id = Column(Integer, ForeignKey('log_eventos.id'), nullable=False)   
    score = Column(Float)
    classificacao = Column(String)  #ex: "Port Scan", "DDoS", "Brute Force", etc. 
    confianca = Column(Float)
    detalhes = Column(JSON)     # features usadas, SHAP values, etc.
    analisado_em = Column(DateTime(timezone=True))

    def __init__(self, evento_id, score, classificacao, confianca, detalhes, analisado_em):
        self.evento_id = evento_id
        self.score = score
        self.classificacao = classificacao
        self.confianca = confianca
        self.detalhes = detalhes
        self.analisado_em = analisado_em

class IpsBloqueados(Base):
    __tablename__ = 'ips_bloqueados'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bloqueado_por = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    alert_id = Column(Integer, ForeignKey('alertas.id'), nullable=False) # para saber qual alerta gerou o bloqueio
    ip_bloqueado = Column(String(45), nullable=False, unique=True)
    motivo = Column(String)
    bloqueado_em = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __init__(self, bloqueado_por, ip_bloqueado, motivo, bloqueado_em):
        self.bloqueado_por = bloqueado_por
        self.ip_bloqueado = ip_bloqueado
        self.motivo = motivo
        self.bloqueado_em = bloqueado_em

class NotificationConfig(Base):
    __tablename__ = "notification_config"
    
    id = Column(Integer, primary_key=True, autoincrement=True)

    email_provider      = Column(String, default="gmail")
    smtp_server = Column(String, nullable=True)
    smtp_port = Column(Integer, default=587)
    smtp_ssl = Column(Boolean, default=True)
    smtp_username = Column(String, nullable=True)
    smtp_password = Column(String, nullable=True)
    smtp_enabled = Column(Boolean, default=False)
    
    telegram_token = Column(String, nullable=True)
    telegram_chat_id = Column(String, nullable=True)
    telegram_enabled = Column(Boolean, default=False)
    
    # Aqui é para  Microsoft Teams
    teams_webhook = Column(String, nullable=True)
    teams_enabled = Column(Boolean, default=False)
    
    trigger_critical = Column(Boolean, default=True)
    trigger_high = Column(Boolean, default=True)
    trigger_medium = Column(Boolean, default=False)
    atualizado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(
    self,        
    email_provider="gmail", 
    smtp_server=None,
    smtp_port=587,
    smtp_ssl=True,
    smtp_username=None,
    smtp_password=None,
    smtp_enabled=False,
    telegram_token=None,
    telegram_chat_id=None,
    telegram_enabled=False,
    teams_webhook=None,
    teams_enabled=False,
    trigger_critical=True,
    trigger_high=True,
    trigger_medium=False,
):
        
        self.smtp_server = smtp_server
        self.email_provider = email_provider
        self.smtp_port = smtp_port
        self.smtp_ssl = smtp_ssl
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.smtp_enabled = smtp_enabled
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.telegram_enabled = telegram_enabled
        self.teams_webhook = teams_webhook
        self.teams_enabled = teams_enabled
        self.trigger_critical = trigger_critical
        self.trigger_high = trigger_high
        self.trigger_medium = trigger_medium
        self.atualizado_em = datetime.now(timezone.utc)

class NetworkConfig(Base):
    __tablename__ = "network_config"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    capture_interface   = Column(String, default="eth0")
    promiscuous_mode    = Column(Boolean, default=True)
    bpf_filter          = Column(String, default="")
    whitelist           = Column(String, default="192.168.1.0/24, 10.0.0.0/8, 127.0.0.1")
    atualizado_em       = Column(DateTime, default=lambda: datetime.now(timezone.utc))

Base.metadata.create_all(engine)

#Executa a criacao dos metadados do seu banco de seu banco (criar efetivamente o banco de dados)
