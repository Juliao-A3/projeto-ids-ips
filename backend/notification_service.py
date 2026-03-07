import smtplib
import httpx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from backend.models import NotificationConfig, LogEvento, Severidade


def get_config(session: Session) -> NotificationConfig | None:
    return session.query(NotificationConfig).first()


def deve_notificar(config: NotificationConfig, severidade: str) -> bool:
    if severidade == Severidade.CRITICA.value and config.trigger_critical:
        return True
    if severidade == Severidade.ALTA.value and config.trigger_high:
        return True
    if severidade == Severidade.MEDIA.value and config.trigger_medium:
        return True
    return False


def montar_mensagem_email(evento: LogEvento) -> str:
    return f"""
    🚨 AEGIS IDS/IPS — ALERTA DE SEGURANÇA

    Severidade : {evento.severidade.value.upper()}
    IP Origem  : {evento.src_ip}
    IP Destino : {evento.dest_ip}
    Protocolo  : {evento.protocolo}
    Porta      : {evento.dest_port}
    Assinatura : {evento.assinatura or 'N/A'}
    Timestamp  : {evento.timestamp}
    Status     : {evento.status.value}

    Acede ao painel AEGIS para mais detalhes.
    """


def montar_mensagem_telegram(evento: LogEvento) -> str:
    return (
        f"🚨 *AEGIS ALERTA*\n\n"
        f"*Severidade:* {evento.severidade.value.upper()}\n"
        f"*IP Origem:* `{evento.src_ip}`\n"
        f"*IP Destino:* `{evento.dest_ip}`\n"
        f"*Protocolo:* {evento.protocolo}\n"
        f"*Porta:* {evento.dest_port}\n"
        f"*Assinatura:* {evento.assinatura or 'N/A'}\n"
        f"*Timestamp:* {evento.timestamp}"
    )


def enviar_email(config: NotificationConfig, evento: LogEvento):
    """Envia email de alerta"""
    print(f"[EMAIL] smtp_enabled: {config.smtp_enabled}")
    print(f"[EMAIL] smtp_username: {config.smtp_username}")
    print(f"[EMAIL] email_provider: {config.email_provider}")

    if not config.smtp_enabled or not config.smtp_username:
        print("[EMAIL] Abortado — não configurado")
        return

    providers = {
        "gmail":   "smtp.gmail.com",
        "outlook": "smtp.office365.com",
    }
    servidor = providers.get(config.email_provider, "smtp.gmail.com")

    try:
        msg = MIMEMultipart()
        msg["Subject"] = f"[AEGIS] Alerta {evento.severidade.value.upper()} — {evento.src_ip}"
        msg["From"]    = config.smtp_username
        msg["To"]      = config.smtp_username
        msg.attach(MIMEText(montar_mensagem_email(evento), "plain"))

        with smtplib.SMTP(servidor, 587) as server:
            server.starttls()
            server.login(config.smtp_username, config.smtp_password)
            server.send_message(msg)

        print(f"[AEGIS] Email enviado para {config.smtp_username}")
    except Exception as e:
        print(f"[AEGIS] Erro ao enviar email: {e}")


async def enviar_telegram(config: NotificationConfig, evento: LogEvento):
    """Envia mensagem Telegram"""
    if not config.telegram_enabled or not config.telegram_token:
        return

    try:
        url = f"https://api.telegram.org/bot{config.telegram_token}/sendMessage"
        async with httpx.AsyncClient() as client:
            await client.post(url, json={
                "chat_id":    config.telegram_chat_id,
                "text":       montar_mensagem_telegram(evento),
                "parse_mode": "Markdown"
            })
        print(f"[AEGIS] Telegram enviado")
    except Exception as e:
        print(f"[AEGIS] Erro ao enviar Telegram: {e}")


async def enviar_teams(config: NotificationConfig, evento: LogEvento):
    """Envia mensagem Teams"""
    if not config.teams_enabled or not config.teams_webhook:
        return

    try:
        async with httpx.AsyncClient() as client:
            await client.post(config.teams_webhook, json={
                "text": montar_mensagem_email(evento)
            })
        print(f"[AEGIS] Teams enviado")
    except Exception as e:
        print(f"[AEGIS] Erro ao enviar Teams: {e}")


async def notificar_alerta(evento: LogEvento, session: Session):
    config = get_config(session)

    if not config:
        return

    if not deve_notificar(config, evento.severidade.value):
        return

    # email (síncrono)
    enviar_email(config, evento)

    # telegram e teams (assíncrono)
    await enviar_telegram(config, evento)
    await enviar_teams(config, evento)