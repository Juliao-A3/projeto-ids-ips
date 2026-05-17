# Arquitetura e Fluxogramas - Relatórios e Notificações

## 📐 Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React/TypeScript)              │
├─────────────────┬──────────────────┬────────────────────────────┤
│ RelatorioManag. │ Notifications    │ DashboardMetrics           │
│  - PDF Download │ Management       │  - Summary cards           │
│  - Filters      │  - Config Form   │  - Metics charts           │
│  - Preview      │  - Diagnostics   │  - Attack volume           │
└────────┬────────┴────────┬─────────┴────────────┬───────────────┘
         │ HTTP            │ HTTP               │ HTTP
         │ REST            │ REST               │ REST
         v                 v                    v
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI/Python)                      │
├──────────────────┬──────────────────┬─────────────────────────┤
│ reports_routes   │ notification_    │ Other services         │
│ .py              │ routes.py        │                        │
│                  │                  │                        │
│ GET /reports/    │ GET /notif/      │                        │
│  - summary       │  - config        │                        │
│  - incidents     │  - diagnostics   │                        │
│  - attack-volume │ PUT /notif/      │                        │
│  - export/pdf    │  - config        │                        │
│                  │ POST /notif/     │                        │
│                  │  - test/email    │                        │
│                  │  - test/telegram │                        │
│                  │  - test/teams    │                        │
└────────┬─────────┴────────┬─────────┴─────────────┬──────────────┘
         │                  │                       │
         v                  v                       v
┌──────────────────┬───────────────────┬──────────────────────────┐
│ pdf_service.py   │notification_      │ models.py                │
│                  │ service.py        │ schemas.py               │
│ - gerar_pdf()    │                   │                          │
│ - gráficos       │ - enviar_email()  │ - LogEvento              │
│ - layout design  │ - enviar_telegram │ - NotificationConfig     │
│ - tabelas        │ - enviar_teams()  │ - IpsBloqueados         │
│                  │ - notificar_      │                          │
│                  │   alerta()        │                          │
└────────┬─────────┴────────┬──────────┴─────────────┬────────────┘
         │                  │                       │
         v                  v                       v
┌──────────────────┬───────────────────┬──────────────────────────┐
│ ReportLab PDF    │ SMTP / HTTP Async │ Database                 │
│ Gen.             │ Clients           │ (SQLAlchemy/Alembic)     │
│                  │                   │                          │
│ - Canvas         │ - smtplib (email) │ - notification_config    │
│ - Colors         │ - httpx (telegram)│ - log_evento             │
│ - Shapes         │ - httpx (teams)   │ - ips_bloqueados         │
└────────┬─────────┴────────┬──────────┴─────────────┬────────────┘
         │                  │                       │
         v                  v                       v
    ┌──────────┐    ┌─────────────┐      ┌──────────────┐
    │ PDF File │    │Email Server │      │ PostgreSQL   │
    │ (Download)    │ SMTP        │      │ Database     │
    └──────────┘    │             │      └──────────────┘
                    │ Telegram    │
                    │ Bot API     │
                    │             │
                    │ Teams       │
                    │ Webhook     │
                    └─────────────┘
```

---

## 🔄 Fluxo de Geração de Relatório PDF

```
┌─── Frontend (React) ───┐
│  Página de Relatórios  │
│  - Seleciona período   │
│  - Seleciona severidade│
│  - Seleciona tipo      │
│  - Clica "Gerar PDF"   │
└───────────┬────────────┘
            │
            │ GET /reports/export/pdf?period=24h&severity=all&tipo=detalhado&limite=500
            │
            v
┌── Backend (FastAPI) ───────┐
│ export_pdf() endpoint       │
│ 1. Valida parâmetros       │
│ 2. Calcula período         │
└───────────┬────────────────┘
            │
            │ Query Database
            │
            v
┌── SQLAlchemy ORM ──────────┐
│ SELECT LogEvento WHERE     │
│  - timestamp >= desde      │
│  - severidade = filter     │
│ ORDER BY timestamp DESC    │
│ LIMIT limite_final         │
└───────────┬────────────────┘
            │
            │ Retorna [log1, log2, ...]
            │
            v
┌── Backend (FastAPI) ───────┐
│ 3. Calcula estatísticas    │
│    - total_eventos         │
│    - criticos, altos, etc  │
│    - bloqueados            │
│ 4. Chama gerar_pdf()       │
└───────────┬────────────────┘
            │
            │ (logs, summary, period_label, tipo)
            │
            v
┌── pdf_service.py ──────────┐
│ gerar_pdf()                │
│ ├─ Canvas A4              │
│ ├─ Page 1:                │
│ │  ├─ Header AEGIS        │
│ │  ├─ Report ID           │
│ │  ├─ Summary metrics     │
│ │  ├─ Attack volume graph │
│ │  └─ Page footer         │
│ ├─ Pages 2+:              │
│ │  ├─ Table header        │
│ │  ├─ Log rows (6-por-pág)│
│ │  └─ Page footer         │
│ └─ BytesIO buffer         │
└───────────┬────────────────┘
            │
            │ PDF bytes buffer
            │
            v
┌── Backend (FastAPI) ───────┐
│ 5. Retorna PDF como stream │
│    - Content-Type: pdf     │
│    - Attachment filename   │
└───────────┬────────────────┘
            │
            │ HTTP 200 + PDF blob
            │
            v
┌─── Frontend (React) ───┐
│ 5. Blob recebido       │
│ 6. Criar <a> tag       │
│ 7. Trigger download    │
│ 8. Cleanup             │
└───────────┬────────────┘
            │
            v
    ┌────────────────┐
    │ PDF Salvo no   │
    │ downloads/     │
    │ aegis-report-  │
    │ {tipo}-{period}│
    │ .pdf           │
    └────────────────┘
```

---

## 🚨 Fluxo de Notificação de Alerta

```
┌─────────────────────────────┐
│ Sniffer detecta evento      │
│ Ex: TCP SCAN               │
│ Severidade: ALTA           │
└──────────┬──────────────────┘
           │
           │ Cria LogEvento
           │
           v
┌──────────────────────────────┐
│ session.add(evento)          │
│ session.commit()             │
└──────────┬───────────────────┘
           │
           │ await notificar_alerta(evento, session)
           │
           v
┌──────────────────────────────────┐
│ notification_service.py          │
│ 1. get_config(session)           │
│    ↓ NotificationConfig DB       │
│ 2. normalizar_severidade(evento) │
│    ↓ ALTA (verificado)           │
│ 3. deve_notificar(config, "alta")│
│    ├─ trigger_high = True?       │
│    └─ SIM! → continua            │
└──────────┬───────────────────────┘
           │
           ├──────────────────┬──────────────┬──────────────┐
           │                  │              │              │
           v                  v              v              v
    ┌──EMAIL────┐     ┌──TELEGRAM────┐ ┌──TEAMS────┐  (Sync)
    │(Síncrono) │     │ (Async)      │ │(Async)   │
    └─────┬─────┘     └──────┬───────┘ └────┬─────┘
          │                  │              │
          │                  │ (Async tasks)│
          │                  │ (não bloqueia)
          │                  │              │
    ┌─────v──────────┐       │       ┌──────v───┐
    │ enviar_email() │       │       │teams...()│
    │                │       │       └──────────┘
    │ 1. Valida:     │       │
    │  - enabled?    │       │
    │  - credentials?│       │
    │ 2. Provider:   │       │
    │  - Gmail       │       │
    │  - Outlook     │       │
    │  - Custom      │       │
    │ 3. Monta msg   │       │
    │ 4. SMTP auth   │       │
    └─────┬──────────┘   ┌───v──────────────┐
          │               │enviar_telegram()│
          │               │                 │
          │               │ 1. Valida token │
          │               │ 2. POST /send   │
          │               │ 3. Retorna      │
          │               └─────────────────┘
          │
    ┌─────v────────────────┐
    │ Conecta SMTP Server  │
    │  - smtp.gmail.com:587│
    │  - ou custom         │
    │ Autentica            │
    │ Envia mensagem       │
    │ Fecha conexão        │
    └─────┬────────────────┘
          │
    ┌─────v────────────────┐
    │✓ Email Enviado!      │
    │ Logs: [EMAIL] ...    │
    └──────────────────────┘
```

---

## 📊 Estrutura de Dados do Relatório

```
┌─ NotificationConfig (DB)
│  ├─ email_provider: "gmail"
│  ├─ smtp_server: "smtp.gmail.com"
│  ├─ smtp_port: 587
│  ├─ smtp_ssl: true
│  ├─ smtp_username: "alerts@company.com"
│  ├─ smtp_password: "***"
│  ├─ smtp_enabled: true
│  ├─ telegram_token: "123456:ABC..."
│  ├─ telegram_chat_id: "987654321"
│  ├─ telegram_enabled: true
│  ├─ teams_webhook: "https://outlook.webhook.office.com/..."
│  ├─ teams_enabled: false
│  ├─ trigger_critical: true
│  ├─ trigger_high: true
│  └─ trigger_medium: false

┌─ LogEvento (DB)
│  ├─ id: int
│  ├─ timestamp: datetime
│  ├─ src_ip: "192.168.1.100"
│  ├─ dest_ip: "10.0.0.50"
│  ├─ protocolo: "TCP"
│  ├─ dest_port: 443
│  ├─ assinatura: "TCP SCAN DETECTADO"
│  ├─ severidade: Enum(CRITICA/ALTA/MEDIA/BAIXA)
│  ├─ status: Enum(MITIGADO/PENDENTE/IGNORADO)
│  └─ payload: JSON (opcional)

┌─ IpsBloqueados (DB)
│  ├─ id: int
│  ├─ ip: "192.168.1.100"
│  ├─ razao: "Número de alertas"
│  └─ timestamp: datetime

┌─ Summary (JSON da API)
│  ├─ total_eventos: 245
│  ├─ criticos: 5
│  ├─ altos: 32
│  ├─ medios: 208
│  ├─ bloqueados: 15
│  ├─ total_ips_bloqueados: 8
│  ├─ truncado: false
│  ├─ total_real: 245
│  ├─ limite_aplicado: 500
│  └─ tipo_relatorio: "detalhado"
```

---

## 🎨 Layout do PDF

```
┌────────────────────────────────────────────────────┐
│                  AEGIS v4.0.2                      │
│            RELATÓRIO TÉCNICO DE SEGURANÇA          │
│                                                    │
│ REPORT ID: #IDS-2026-04-13-X11                    │
│ Gerado: 13 de Abril, 2026 -- 15:30:45             │
├────────────────────────────────────────────────────┤
│ PERÍODO: Últimas 24 Horas                          │
│ TIPO: Detalhado (127 alertas de 500 mostrados)    │
├────────────────────────────────────────────────────┤
│ RESUMO EXECUTIVO                                   │
│ ┌──────────────────────────────────────────────┐  │
│ │ Total de Eventos:        245                 │  │
│ │ ├─ Crítica:              5       [██░░░░░░]  │  │
│ │ ├─ Alta:                 32      [███░░░░░]  │  │
│ │ ├─ Média:                208     [██████░░]  │  │
│ │ └─ Baixa:                0       [░░░░░░░░]  │  │
│ │                                              │  │
│ │ Eventos Bloqueados:      15      [█████░░░]  │  │
│ │ IPs Bloqueados:          8                   │  │
│ └──────────────────────────────────────────────┘  │
├────────────────────────────────────────────────────┤
│ GRÁFICO: VOLUME DE ATAQUES                        │
│ │                                                 │
│ │     ██  ██                                       │
│ │  ██ ██  ██     ██                               │
│ │  ██ ██  ██  ██ ██  ██                           │
│ │  ██ ██  ██  ██ ██  ██       ██  ██              │
│ │  ──────────────────────────────────────────     │
│ │  00 02 04 06 08 10 12 14 16 18 20 22            │
│ │            (Horas)                              │
│                                                   │
├────────────────────────────────────────────────────┤
│ EVENTOS REGISTADOS                                │
│ ┌─────┬────────┬─────────┬────────┬──────┬──────┐ │
│ │Hora │ Origem │ Destino │Protoc.│Sever.│Ação  │ │
│ ├─────┼────────┼─────────┼────────┼──────┼──────┤ │
│ │15:30│192.168 │ 10.0.0.5│ TCP   │ALTA  │BLOQUE│ │
│ │15:45│  1.100 │   50    │        │      │ADO   │ │
│ ├─────┼────────┼─────────┼────────┼──────┼──────┤ │
│ │15:31│172.16. │ 8.8.8.8 │ UDP   │MEDIA │ALERTA│ │
│ │45   │  0.254 │         │        │      │      │ │
│ ├─────┼────────┼─────────┼────────┼──────┼──────┤ │
│ │...  │   ...  │  ...    │ ...   │ ...  │ ...  │ │
│ └─────┴────────┴─────────┴────────┴──────┴──────┘ │
│                                                    │
├────────────────────────────────────────────────────┤
│  Pág. 01 de 02                  AEGIS v4.0.2      │
│ Gerado automaticamente pelo Sistema IDS/IPS IA     │
└────────────────────────────────────────────────────┘
```

---

## 🔐 Fluxo de Segurança de Credenciais

```
Frontend (React
    │
    ├─ User insere: email@gmail.com
    ├─ User insere: app_password
    │
    v
PUT /notifications/config
{
  "smtp_username": "email@gmail.com",
  "smtp_password": "xxxx xxxx xxxx xxxx"
}
    │
    v
Backend API
    │
    ├─ Valida schema (pydantic)
    ├─ Autentica user (JWT)
    ├─ Autoriza role (admin)
    │
    v
NotificationConfigSchema
    │
    ├─ Email validation
    ├─ Password não é revelado em logs
    │
    v
Database (PostgreSQL)
    │
    ├─ NotificationConfig.smtp_password = ***
    │  (Guardado em plaintext na DB - considere encryption)
    │
    v
Em tempo de envio:
    │
    ├─ Carrega credenciais da DB
    ├─ Conecta ao SMTP (credentials in memory)
    ├─ Limpa memory após envio
    │
    v
✓ Email enviado com sucesso
```

---

## ⚡ Performance e Escalabilidade

### Relatórios
- **Limite de alertas**: 500 (detalhado) / 100 (resumido)
- **Geração PDF**: ~2-5 segundos (com gráficos)
- **Tamanho PDF**: ~100-200 KB
- **Armazenamento**: Em BytesIO (não persiste)

### Notificações
- **Email**: Síncrono (timeout 20s)
- **Telegram**: Assíncrono (não bloqueia)
- **Teams**: Assíncrono (não bloqueia)
- **Retry**: Não implementado (considere adicionar)

### Otimizações Sugeridas
```python
# 1. Cache de relatórios
@cache.cached(timeout=300)  # 5 minutos
def get_summary(period, severity):
    # ...

# 2. Background tasks para emails
from celery import shared_task

@shared_task
def enviar_email_async(config_id, evento_id):
    # Envia email em background

# 3. Conexão SMTP reutilizável
class SMTPPool:
    def __init__(self, server, port, username, password):
        self.pool = []
    
    def get_connection(self):
        # Pool de conexões SMTP

# 4. Rate limiting
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@reports_router.get('/export/pdf')
@limiter.limit("10/minute")
def export_pdf(...):
    # Máximo 10 PDFs por minuto
```

---

## 🧪 Testes Recomendados

```python
# tests/test_reports.py
def test_get_summary():
    response = client.get("/reports/summary?period=24h")
    assert response.status_code == 200
    assert "total_eventos" in response.json()

def test_export_pdf():
    response = client.get("/reports/export/pdf?tipo=detalhado")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

# tests/test_notifications.py
def test_get_config():
    response = client.get("/notifications/config")
    assert response.status_code == 200

def test_save_config():
    config = {"smtp_enabled": True, ...}
    response = client.put("/notifications/config", json=config)
    assert response.status_code == 200

def test_email_notification():
    evento = LogEvento(...)
    result = enviar_email(config, evento)
    assert result == True

def test_notification_trigger():
    config.trigger_high = False
    resultado = deve_notificar(config, "alta")
    assert resultado == False
```

---

## 📋 Checklist de Verificação

- [ ] **Relatórios**
  - [ ] GET /reports/summary retorna dados corretos
  - [ ] GET /reports/export/pdf gera PDF válido
  - [ ] Filtros por período funcionam
  - [ ] Filtros por severidade funcionam
  - [ ] Truncagem funciona (limite respeitado)
  
- [ ] **Notificações**
  - [ ] Email SMTP conecta corretamente
  - [ ] Email é recebido com conteúdo correto
  - [ ] Telegram envia mensagens
  - [ ] Teams recebe webhooks
  - [ ] Triggers filtram corretamente
  - [ ] Diagnóstico identifica problemas
  
- [ ] **Segurança**
  - [ ] Credenciais não aparecem em logs
  - [ ] Apenas admins podem configurar
  - [ ] Validated input (schema validation)
  - [ ] CORS configurado corretamente
  
- [ ] **Performance**
  - [ ] PDF gerado em < 5 segundos
  - [ ] Email enviado em < 20 segundos
  - [ ] Notificação não bloqueia sniffer
  - [ ] Sem memory leaks em BytesIO

