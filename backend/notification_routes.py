from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.dependencies import get_session, require_role
from backend.models import NotificationConfig, Usuario
from backend.schemas import NotificationConfigSchema
from datetime import datetime, timezone

notification_router = APIRouter(prefix='/notifications', tags=['notifications'])


def _channel_diagnostics(config: NotificationConfig) -> dict:
    email_reasons: list[str] = []
    telegram_reasons: list[str] = []
    teams_reasons: list[str] = []

    # Email checks
    if not config.smtp_enabled:
        email_reasons.append("smtp_enabled=false")
    if not config.smtp_username:
        email_reasons.append("smtp_username vazio")
    if not config.smtp_password:
        email_reasons.append("smtp_password vazio")
    if not (config.smtp_server or config.email_provider in {"gmail", "outlook"}):
        email_reasons.append("smtp_server não definido e provider desconhecido")

    # Telegram checks
    if not config.telegram_enabled:
        telegram_reasons.append("telegram_enabled=false")
    if not config.telegram_token:
        telegram_reasons.append("telegram_token vazio")
    if not config.telegram_chat_id:
        telegram_reasons.append("telegram_chat_id vazio")

    # Teams checks
    if not config.teams_enabled:
        teams_reasons.append("teams_enabled=false")
    if not config.teams_webhook:
        teams_reasons.append("teams_webhook vazio")

    return {
        "email": {
            "enabled": bool(config.smtp_enabled),
            "ready": len(email_reasons) == 0,
            "provider": config.email_provider,
            "server": config.smtp_server,
            "port": config.smtp_port,
            "ssl": bool(config.smtp_ssl),
            "reasons": email_reasons,
        },
        "telegram": {
            "enabled": bool(config.telegram_enabled),
            "ready": len(telegram_reasons) == 0,
            "reasons": telegram_reasons,
        },
        "teams": {
            "enabled": bool(config.teams_enabled),
            "ready": len(teams_reasons) == 0,
            "reasons": teams_reasons,
        },
    }


def get_or_create_config(session: Session) -> NotificationConfig:
    """Busca a config existente ou cria uma padrão"""
    config = session.query(NotificationConfig).first()
    if not config:
        config = NotificationConfig()
        session.add(config)
        session.commit()
        session.refresh(config)
    return config


@notification_router.get('/config')
async def get_config(
    usuario: Usuario = Depends(require_role(["admin"])),
    session: Session = Depends(get_session)
):
    config = get_or_create_config(session)
    return {
        "email_provider": config.email_provider,
        "smtp_server": config.smtp_server,
        "smtp_port": config.smtp_port,
        "smtp_ssl": config.smtp_ssl,
        "smtp_username": config.smtp_username,
        "smtp_password": config.smtp_password,
        "smtp_enabled": config.smtp_enabled,
        "telegram_token": config.telegram_token,
        "telegram_chat_id": config.telegram_chat_id,
        "telegram_enabled": config.telegram_enabled,
        "teams_webhook": config.teams_webhook,
        "teams_enabled": config.teams_enabled,
        "trigger_critical": config.trigger_critical,
        "trigger_high": config.trigger_high,
        "trigger_medium": config.trigger_medium,
        "atualizado_em": config.atualizado_em,
    }


@notification_router.put('/config')
async def save_config(
    dados: NotificationConfigSchema,
    usuario: Usuario = Depends(require_role(["admin"])),
    session: Session = Depends(get_session)
):
    config = get_or_create_config(session)

    config.email_provider = dados.email_provider
    config.smtp_server = dados.smtp_server
    config.smtp_port = dados.smtp_port
    config.smtp_ssl = dados.smtp_ssl
    config.smtp_username = dados.smtp_username
    config.smtp_password = dados.smtp_password
    config.smtp_enabled = dados.smtp_enabled
    config.telegram_token = dados.telegram_token
    config.telegram_chat_id = dados.telegram_chat_id
    config.telegram_enabled = dados.telegram_enabled
    config.teams_webhook = dados.teams_webhook
    config.teams_enabled = dados.teams_enabled
    config.trigger_critical = dados.trigger_critical
    config.trigger_high = dados.trigger_high
    config.trigger_medium = dados.trigger_medium
    config.atualizado_em = datetime.now(timezone.utc)

    session.commit()
    return {"mensagem": "Configurações salvas com sucesso"}


@notification_router.get('/diagnostics')
async def diagnostics(
    usuario: Usuario = Depends(require_role(["admin"])),
    session: Session = Depends(get_session)
):
    config = get_or_create_config(session)
    channels = _channel_diagnostics(config)

    trigger_config = {
        "critical": bool(config.trigger_critical),
        "high": bool(config.trigger_high),
        "medium": bool(config.trigger_medium),
    }

    return {
        "summary": {
            "atualizado_em": config.atualizado_em,
            "any_channel_enabled": any([
                channels["email"]["enabled"],
                channels["telegram"]["enabled"],
                channels["teams"]["enabled"],
            ]),
            "any_channel_ready": any([
                channels["email"]["ready"],
                channels["telegram"]["ready"],
                channels["teams"]["ready"],
            ]),
        },
        "triggers": trigger_config,
        "channels": channels,
        "notes": [
            "Severidades enviadas dependem de triggers (critical/high/medium).",
            "No sniffer atual os eventos são gravados com severidade 'alta'.",
            "Se trigger_high=false, alertas do sniffer não serão enviados.",
        ],
    }


@notification_router.post('/test/email')
async def test_email(
    usuario: Usuario = Depends(require_role(["admin"])),
    session: Session = Depends(get_session)
):
    config = get_or_create_config(session)

    if not config.smtp_enabled:
        raise HTTPException(status_code=400, detail="Email não está ativado")

    providers = {
        "gmail":   {"server": "smtp.gmail.com", "port": 587},
        "outlook": {"server": "smtp.office365.com", "port": 587},
    }
    provider = providers.get(config.email_provider, providers["gmail"])

    try:
        import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText("Teste de notificação do AEGIS IDS/IPS")
        msg["Subject"] = "AEGIS — Teste de Email"
        msg["From"]    = config.smtp_username
        msg["To"]      = config.smtp_username

        with smtplib.SMTP(provider["server"], provider["port"]) as server:
            server.starttls()
            server.login(config.smtp_username, config.smtp_password)
            server.send_message(msg)

        return {"mensagem": "Email de teste enviado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar email: {str(e)}")


@notification_router.post('/test/telegram')
async def test_telegram(
    usuario: Usuario = Depends(require_role(["admin"])),
    session: Session = Depends(get_session)
):
    config = get_or_create_config(session)

    if not config.telegram_enabled:
        raise HTTPException(status_code=400, detail="Telegram não está ativado")
    if not config.telegram_token or not config.telegram_chat_id:
        raise HTTPException(status_code=400, detail="Configurações do Telegram incompletas")

    try:
        import httpx # pyright: ignore[reportMissingImports]
        url = f"https://api.telegram.org/bot{config.telegram_token}/sendMessage"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={
                "chat_id": config.telegram_chat_id,
                "text":    "AEGIS IDS/IPS — Teste de notificação Telegram"
            })
        if response.status_code != 200:
            detalhe = response.text
            raise HTTPException(
                status_code=500,
                detail=f"Erro Telegram ({response.status_code}): {detalhe}"
            )
        return {"mensagem": "Mensagem Telegram enviada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


@notification_router.post('/test/teams')
async def test_teams(
    usuario: Usuario = Depends(require_role(["admin"])),
    session: Session = Depends(get_session)
):
    config = get_or_create_config(session)

    if not config.teams_enabled:
        raise HTTPException(status_code=400, detail="Teams não está ativado")
    if not config.teams_webhook:
        raise HTTPException(status_code=400, detail="Webhook do Teams não configurado")

    try:
        import httpx # pyright: ignore[reportMissingImports]
        async with httpx.AsyncClient() as client:
            response = await client.post(config.teams_webhook, json={
                "text": "AEGIS IDS/IPS — Teste de notificação Microsoft Teams"
            })
        if response.status_code not in [200, 202]:
            raise HTTPException(status_code=500, detail="Erro ao enviar mensagem Teams")
        return {"mensagem": "Mensagem Teams enviada com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")