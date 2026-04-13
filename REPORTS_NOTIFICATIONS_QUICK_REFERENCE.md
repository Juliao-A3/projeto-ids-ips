# Referência Rápida - Relatórios e Notificações

## 🚀 Início Rápido (5 min)

### Setup Email (Gmail)
```bash
# 1. Ativar 2FA no Google Account (security.google.com)
# 2. Gerar "App Password" (16 caracteres)
# 3. CURL:

curl -X PUT "http://localhost:8000/notifications/config" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email_provider": "gmail",
    "smtp_username": "seu.email@gmail.com",
    "smtp_password": "xxxx xxxx xxxx xxxx",
    "smtp_enabled": true,
    "trigger_critical": true,
    "trigger_high": true,
    "trigger_medium": false
  }'

# 4. Testar
curl -X POST "http://localhost:8000/notifications/test/email" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Setup Telegram
```bash
# 1. Chat @BotFather → /newbot → criador bot
# 2. Enviar mensagem ao bot
# 3. GET https://api.telegram.org/bot{TOKEN}/getUpdates → copiar chat.id
# 4. CURL:

curl -X PUT "http://localhost:8000/notifications/config" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_token": "123456:ABC...",
    "telegram_chat_id": "987654321",
    "telegram_enabled": true
  }'

# 5. Testar
curl -X POST "http://localhost:8000/notifications/test/telegram" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Gerar Relatório PDF
```bash
# Download de relatório PDF (24h, detalhado)
curl -X GET "http://localhost:8000/reports/export/pdf?period=24h&severity=all&tipo=detalhado&limite=500" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o aegis-report.pdf
```

---

## 📍 Endpoints Principais

| Endpoint | Método | Descrição | Parâmetros |
|----------|--------|-----------|-----------|
| `/reports/summary` | GET | Resumo de alertas | period, severity |
| `/reports/incidents` | GET | Lista incidentes | period, severity, limit |
| `/reports/attack-volume` | GET | Volume por hora | period |
| `/reports/export/pdf` ⭐ | GET | Download PDF | period, severity, tipo, limite |
| `/notifications/config` | GET | Config atual | - |
| `/notifications/config` | PUT | Atualizar config | (body: JSON) |
| `/notifications/diagnostics` | GET | Status canais | - |
| `/notifications/test/email` | POST | Teste email | - |
| `/notifications/test/telegram` | POST | Teste telegram | - |
| `/notifications/test/teams` | POST | Teste teams | - |

---

## 🔧 Parâmetros de Filtros

### Period
- `24h` - Últimas 24 horas
- `7d` - Últimos 7 dias
- `30d` - Últimos 30 dias

### Severity
- `all` - Todas as severidades
- `critica` - Apenas crítica
- `alta` - Apenas alta
- `media` - Apenas média
- `baixa` - Apenas baixa

### Tipo de Relatório
- `detalhado` - Até 500 alertas (completo)
- `resumido` - Até 100 alertas (comprimido)

---

## 💾 Estrutura de Resposta - GET /reports/summary

```json
{
  "total_eventos": 245,
  "criticos": 5,
  "altos": 32,
  "medios": 208,
  "bloqueados": 15,
  "total_ips_bloqueados": 8
}
```

---

## 💾 Estrutura de Resposta - GET /notifications/config

```json
{
  "email_provider": "gmail",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_ssl": true,
  "smtp_username": "alerts@company.com",
  "smtp_password": "***",
  "smtp_enabled": true,
  "telegram_token": "***",
  "telegram_chat_id": "***",
  "telegram_enabled": true,
  "teams_webhook": "***",
  "teams_enabled": false,
  "trigger_critical": true,
  "trigger_high": true,
  "trigger_medium": false,
  "atualizado_em": "2026-04-13T15:30:45.123456"
}
```

---

## 📧 Configuração - Email

```json
{
  "email_provider": "gmail|outlook|custom",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_ssl": false,
  "smtp_username": "seu.email@gmail.com",
  "smtp_password": "app_password_16_caracteres",
  "smtp_enabled": true
}
```

**Providers Pré-configurados:**
- Gmail: `smtp.gmail.com:587`
- Outlook: `smtp.office365.com:587`
- Custom: Definir servidor/porta

---

## 📱 Configuração - Telegram

```json
{
  "telegram_token": "123456:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh",
  "telegram_chat_id": "987654321",
  "telegram_enabled": true
}
```

**Como obter:**
1. @BotFather → `/newbot`
2. Recebe token
3. Enviar mensagem ao bot
4. GET `https://api.telegram.org/bot{TOKEN}/getUpdates`
5. Copiar `chat.id`

---

## 🤝 Configuração - Teams

```json
{
  "teams_webhook": "https://outlook.webhook.office.com/webhookb2/...",
  "teams_enabled": true
}
```

**Como obter:**
1. Teams → Canal desejado
2. Mais opções (...) → Conectores
3. Procurar "Webhook Incoming"
4. Configurar e copiar URL

---

## ⚙️ Triggers (Filtros de Severidade)

```json
{
  "trigger_critical": true,   // Envia críticos?
  "trigger_high": true,       // Envia altos?
  "trigger_medium": false     // Envia médios?
}
```

**Exemplo:** Com valores acima, são enviados:
- ✅ Alertas CRÍTICA
- ✅ Alertas ALTA
- ❌ Alertas MÉDIA (bloqueado)

---

## 🔍 Diagnóstico - GET /notifications/diagnostics

### Campo "ready"
- ✅ `true` - Canal pronto para enviar
- ❌ `false` - Canal com problemas

### Campo "reasons"
Lista de problemas encontrados:
- `"smtp_enabled=false"` - Canal desativado
- `"smtp_username vazio"` - Falta email
- `"smtp_password vazio"` - Falta senha
- etc.

---

## 🐍 Python - Use Rápido

```python
import requests

BASE = "http://localhost:8000"
TOKEN = "seu_jwt_token"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Obter métricas
metrics = requests.get(f"{BASE}/reports/summary?period=24h", headers=HEADERS).json()
print(metrics)

# Configurar email
config = {
    "email_provider": "gmail",
    "smtp_username": "seu@gmail.com",
    "smtp_password": "app_password",
    "smtp_enabled": True,
    "trigger_critical": True,
    "trigger_high": True
}
requests.put(f"{BASE}/notifications/config", json=config, headers=HEADERS)

# Testar email
requests.post(f"{BASE}/notifications/test/email", headers=HEADERS)

# Download PDF
response = requests.get(
    f"{BASE}/reports/export/pdf?period=24h&tipo=detalhado",
    headers=HEADERS,
    stream=True
)
with open("report.pdf", "wb") as f:
    f.write(response.content)
```

---

## 🔐 Permissões Necessárias

| Endpoint | Permissão Necessária |
|----------|---------------------|
| `/reports/*` | `"admin"`, `"analista"` ou `"operador"` |
| `/notifications/config` (GET) | `"admin"` |
| `/notifications/config` (PUT) | `"admin"` |
| `/notifications/test/*` | `"admin"` |
| `/notifications/diagnostics` | `"admin"` |

---

## ⚠️ Erros Comuns

### ❌ Email não é enviado
```
Solução:
1. Verifique GET /notifications/diagnostics
2. Valide email em debug de provider (Gmail: "Less Secure App Access")
3. Teste com curl: POST /notifications/test/email
4. Verifique logs: [EMAIL] ...
```

### ❌ Telegram não funciona
```
Solução:
1. Confirme token: https://api.telegram.org/bot{TOKEN}/getMe
2. Confirme chat_id: https://api.telegram.org/bot{TOKEN}/getUpdates
3. Verifique se bot está no chat
4. Teste com curl: POST /notifications/test/telegram
```

### ❌ PDF não gera
```
Solução:
1. Verifique se há alertas no período
2. Teste GET /reports/incidents
3. Aumentar limite?
4. Verificar se matplotlib está instalado
5. Logs: [PDF] ...
```

### ❌ Notificações não chegam
```
Solução:
1. Verifique GET /notifications/diagnostics (ready=true?)
2. Verifique triggers: trigger_high, trigger_critical, etc
3. Severidade do evento é >= trigger?
4. Teste com POST /notifications/test/{canal}
5. Verifique logs do backend
```

---

## 📊 Limites

| Item | Limite |
|------|--------|
| Alertas (Detalhado) | 500 por PDF |
| Alertas (Resumido) | 100 por PDF |
| Timeout SMTP | 20 segundos |
| Período máximo | 30 dias |
| Incidentes por lista | 10-100 (configurável) |

---

## 🎯 Fluxo típico de configuração

```
1. Setup Email
   ↓
2. Teste email (POST /notifications/test/email)
   ↓
3. Setup Telegram (opcional)
   ↓
4. Teste telegram (POST /notifications/test/telegram)
   ↓
5. Configure triggers (critical, high, medium)
   ↓
6. Valide diagnostics (GET /notifications/diagnostics)
   ↓
7. Pronto! Sistema enviará alertas automaticamente
```

---

## 📁 Arquivos Importantes

| Ficheiro | Descrição |
|----------|-----------|
| `backend/reports_routes.py` | Endpoints de relatórios |
| `backend/notification_routes.py` | Endpoints de notificações |
| `backend/notification_service.py` | Lógica de envio |
| `backend/pdf_service.py` | Geração de PDFs |
| `backend/models.py` | NotificationConfig model |
| `frontend/src/components/RelatorioManagement/` | UI de relatórios |
| `frontend/src/components/NotificationsManagement/` | UI de notificações |

---

## 📚 Documentação Completa

Consulte os arquivos:
- 📖 `REPORTS_NOTIFICATIONS_GUIDE.md` - Documentação técnica
- 📖 `REPORTS_NOTIFICATIONS_EXAMPLES.md` - Exemplos de código
- 📖 `REPORTS_NOTIFICATIONS_ARCHITECTURE.md` - Diagramas e fluxogramas

---

## 💡 Dicas Úteis

- ✅ Use `period=24h` para relatórios rápidos
- ✅ Use `tipo=resumido` para menos dados
- ✅ Teste canais antes de configurar triggers
- ✅ Verifique diagnostics regularmente
- ✅ Use app passwords para Gmail (não senha principal)
- ✅ Guarde tokens do Telegram com segurança
- ✅ Configure apenas os canais que vai usar
- ✅ Inicie com `trigger_critical=true`, depois adicione outros

---

## 🆘 Suporte Rápido

**Problema**: API retorna 401
**Solução**: Verificar JWT token (Bearer valid?)

**Problema**: 403 Forbidden
**Solução**: Verificar role (admin, analista, operador?)

**Problema**: 404 Not Found
**Solução**: Verificar endpoint URL (typos?)

**Problema**: 500 Internal Server Error
**Solução**: Verificar logs do backend (stderr/stdout)

**Problema**: Timeout
**Solução**: SMTP lento? Telegram API down? Teams webhook inválida?

---

## 🔗 URLs Úteis

```
Django Settings: http://localhost:8000/docs
API Docs: http://localhost:8000/swagger
API Redoc: http://localhost:8000/redoc
Frontend: http://localhost:5173/reports
```

---

**Última atualização:** 13 de Abril de 2026
**Versão AEGIS:** 4.0.2

