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


def normalizar_severidade(evento: LogEvento) -> Severidade:
    if evento.severidade is None:
        evento.severidade = Severidade.ALTA
        return evento.severidade

    if isinstance(evento.severidade, Severidade):
        return evento.severidade

    texto = str(evento.severidade).strip().lower()
    mapa = {
        "critica": Severidade.CRITICA,
        "alta": Severidade.ALTA,
        "media": Severidade.MEDIA,
        "baixa": Severidade.BAIXA,
    }
    evento.severidade = mapa.get(texto, Severidade.ALTA)
    return evento.severidade


def montar_mensagem_email(evento: LogEvento) -> str:
    return f"""
    AEGIS IDS/IPS - ALERTA DE SEGURANCA

    Severidade: {evento.severidade.value.upper()}
    IP Origem: {evento.src_ip}
    IP Destino: {evento.dest_ip}
    Protocolo: {evento.protocolo}
    Porta: {evento.dest_port}
    Assinatura: {evento.assinatura or 'N/A'}
    Timestamp: {evento.timestamp}
    Status: {evento.status.value}

    Aceda ao painel AEGIS para mais detalhes.
    """


def montar_mensagem_telegram(evento: LogEvento) -> str:
    return (
        f"AEGIS ALERTA\n\n"
        f"Severidade: {evento.severidade.value.upper()}\n"
        f"IP Origem: {evento.src_ip}\n"
        f"IP Destino: {evento.dest_ip}\n"
        f"Protocolo: {evento.protocolo}\n"
        f"Porta: {evento.dest_port}\n"
        f"Assinatura: {evento.assinatura or 'N/A'}\n"
        f"Timestamp: {evento.timestamp}"
    )


def enviar_email(config: NotificationConfig, evento: LogEvento) -> bool:
    """Envia email de alerta"""
    print(f"[EMAIL] smtp_enabled: {config.smtp_enabled}")
    print(f"[EMAIL] smtp_username: {config.smtp_username}")
    print(f"[EMAIL] email_provider: {config.email_provider}")

    if not config.smtp_enabled:
        print("[EMAIL] Abortado — canal desativado")
        return False
    if not config.smtp_username:
        print("[EMAIL] Abortado — smtp_username vazio")
        return False
    if not config.smtp_password:
        print("[EMAIL] Abortado — smtp_password vazio")
        return False

    providers = {
        "gmail": ("smtp.gmail.com", 587),
        "outlook": ("smtp.office365.com", 587),
    }
    provider_server, provider_port = providers.get(config.email_provider, ("smtp.gmail.com", 587))
    servidor = config.smtp_server or provider_server
    porta = int(config.smtp_port or provider_port)

    msg = MIMEMultipart()
    msg["Subject"] = f"[AEGIS] Alerta {evento.severidade.value.upper()} - {evento.src_ip}"
    msg["From"] = config.smtp_username
    msg["To"] = config.smtp_username
    msg.attach(MIMEText(montar_mensagem_email(evento), "plain", "utf-8"))

    try:
        # Gmail/Office 365 normalmente usam STARTTLS em 587; SSL direto é mais comum em 465.
        usar_ssl_direto = bool(config.smtp_ssl) and porta == 465

        if usar_ssl_direto:
            with smtplib.SMTP_SSL(servidor, porta, timeout=20) as server:
                server.login(config.smtp_username, config.smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(servidor, porta, timeout=20) as server:
                server.ehlo()
                if porta != 465:
                    server.starttls()
                    server.ehlo()
                server.login(config.smtp_username, config.smtp_password)
                server.send_message(msg)

        print(f"[AEGIS] Email enviado para {config.smtp_username}")
        return True
    except Exception as e:
        # Fallback útil quando a configuração foi gravada com smtp_ssl=true mas porta 587.
        try:
            with smtplib.SMTP(servidor, 587, timeout=20) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(config.smtp_username, config.smtp_password)
                server.send_message(msg)
            print(f"[AEGIS] Email enviado para {config.smtp_username} (fallback STARTTLS)")
            return True
        except Exception as fallback_err:
            print(f"[AEGIS] Erro ao enviar email: {e}")
            print(f"[AEGIS] Fallback STARTTLS também falhou: {fallback_err}")
            return False


async def enviar_telegram(config: NotificationConfig, evento: LogEvento):
    """Envia mensagem Telegram"""
    if not config.telegram_enabled or not config.telegram_token or not config.telegram_chat_id:
        print("[TELEGRAM] Abortado — canal desativado ou configuração incompleta")
        return

    try:
        url = f"https://api.telegram.org/bot{config.telegram_token}/sendMessage"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={
                "chat_id":    config.telegram_chat_id,
                "text":       montar_mensagem_telegram(evento)
            })
            if response.status_code != 200:
                print(f"[AEGIS] Erro ao enviar Telegram ({response.status_code}): {response.text}")
                return
        print(f"[AEGIS] Telegram enviado")
    except Exception as e:
        print(f"[AEGIS] Erro ao enviar Telegram: {e}")


async def enviar_teams(config: NotificationConfig, evento: LogEvento):
    """Envia mensagem Teams"""
    if not config.teams_enabled or not config.teams_webhook:
        print("[TEAMS] Abortado — canal desativado ou webhook vazio")
        return

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(config.teams_webhook, json={
                "text": montar_mensagem_email(evento)
            })
            response.raise_for_status()
        print(f"[AEGIS] Teams enviado")
    except Exception as e:
        print(f"[AEGIS] Erro ao enviar Teams: {e}")


async def notificar_alerta(evento: LogEvento, session: Session):
    try:
        config = get_config(session)

        if not config:
            print("[NOTIFY] Sem configuração de notificações")
            return

        severidade = normalizar_severidade(evento)

        if not deve_notificar(config, severidade.value):
            print(f"[NOTIFY] Severidade '{severidade.value}' filtrada pelos triggers")
            return
    finally:
        try:
            session.close()
        except Exception:
            pass

    # email (síncrono)
    enviar_email(config, evento)

    # telegram e teams (assíncrono)
    await enviar_telegram(config, evento)
    await enviar_teams(config, evento)    