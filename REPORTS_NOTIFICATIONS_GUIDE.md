# Sistema de Relatórios e Alertas por Email/Telegram - AEGIS

## 📋 Visão Geral

O AEGIS possui um sistema integrado de **relatórios técnicos em PDF** e **notificações em tempo real** via múltiplos canais (Email, Telegram, Teams).

---

## 1️⃣ SISTEMA DE RELATÓRIOS

### Localização dos Ficheiros
- **Backend**: `backend/reports_routes.py`, `backend/pdf_service.py`
- **Frontend**: `frontend/src/components/RelatorioManagement/`
- **Hooks**: `frontend/hooks/useReports.ts`

### Endpoints Disponíveis

#### 1. **GET `/reports/summary`**
Obtém resumo estatístico de alertas.

```python
GET /reports/summary?period=24h&severity=all
```

**Parâmetros:**
- `period`: `"24h"`, `"7d"`, `"30d"` 
- `severity`: `"all"`, `"critica"`, `"alta"`, `"media"`, `"baixa"`

**Resposta:**
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

#### 2. **GET `/reports/incidents`**
Lista incidentes recentess com limites.

```python
GET /reports/incidents?period=24h&severity=all&limit=10
```

**Resposta:**
```json
[
  {
    "id": 1,
    "timestamp": "2026-04-13T15:30:45.123456",
    "evento": "TCP SCAN DETECTADO",
    "origem": "192.168.1.100",
    "destino": "10.0.0.50",
    "protocolo": "TCP",
    "severidade": "alta",
    "status": "mitigado"
  }
]
```

#### 3. **GET `/reports/attack-volume`**
Gráfico de volume de ataques por hora.

```python
GET /reports/attack-volume?period=24h
```

**Resposta:**
```json
[
  {"time": "00:00", "attacks": 12},
  {"time": "01:00", "attacks": 8},
  {"time": "02:00", "attacks": 15}
]
```

#### 4. **GET `/reports/export/pdf` ⭐**
**Gera e baixa o PDF do relatório.**

```python
GET /reports/export/pdf?period=24h&severity=all&tipo=detalhado&limite=500
```

**Parâmetros:**
- `period`: `"24h"`, `"7d"`, `"30d"`
- `severity`: `"all"`, `"critica"`, `"alta"`, `"media"`, `"baixa"`
- `tipo`: `"detalhado"` (até 500 alertas) ou `"resumido"` (até 100 alertas)
- `limite`: Número máximo de alertas (respeitará o máximo do tipo)

**Limites por Tipo:**
```python
LIMITE_DETALHADO = 500  # Relatório com todos os detalhes
LIMITE_RESUMIDO = 100   # Versão comprimida
```

**Conteúdo do PDF:**
- ✅ Header com branding AEGIS
- ✅ Resumo executivo (métricas principais)
- ✅ Gráfico de volume de ataques
- ✅ Tabela detalhada de alertas
- ✅ Footer com numeração de páginas
- ✅ Aviso de truncagem (se alertas > limite)

### Modelo de Dados - Relatório

```python
# Dados inclusos no PDF
summary = {
    "total_eventos": int,           # Total de eventos no período
    "criticos": int,                # Quantidade crítica
    "altos": int,                   # Quantidade alta
    "medios": int,                  # Quantidade média
    "bloqueados": int,              # Eventos mitigados
    "total_ips_bloqueados": int,   # IPs únicos bloqueados
    "truncado": bool,               # Se foi limitado por máximo
    "total_real": int,              # Total real (sem limite)
    "limite_aplicado": int,         # Limite que foi aplicado
    "tipo_relatorio": str,          # "detalhado" ou "resumido"
}
```

### Configuração de Períodos

```python
def get_period_filter(period: str):
    agora = datetime.now(timezone.utc)
    if period == "24h":
        return agora - timedelta(hours=24)
    elif period == "7d":
        return agora - timedelta(days=7)
    elif period == "30d":
        return agora - timedelta(days=30)
    return agora - timedelta(hours=24)  # Default
```

### Geração de PDF - ReportLab

O PDF é gerado com **ReportLab** em `pdf_service.py`:

**Componentes Principais:**
1. **Paleta de Cores Corporativa:**
   ```python
   C_PRIMARY = #1A56DB (Azul principal)
   C_CRITICA = #DC2626 (Vermelho)
   C_ALTA = #D97706 (Laranja)
   C_MEDIA = #2563EB (Azul médio)
   C_SUCCESS = #16A34A (Verde)
   ```

2. **Renderização de Elementos:**
   - `draw_rounded_rect()` - Caixas arredondadas
   - `draw_severity_badge()` - Badges de severidade
   - `grafico_picos()` - Gráfico de volume (Matplotlib)
   - `draw_table_header()` - Cabeçalho de tabelas
   - `draw_log_row()` - Linhas de eventos
   - `draw_page_footer()` - Rodapé com numeração

3. **Características:**
   - ✅ Tamanho A4
   - ✅ Múltiplas páginas (conforme alertas)
   - ✅ Design responsivo
   - ✅ Gráficos integrados

### Fluxo de Acesso Frontend

1. **Componente `RelatorioManagement`:**
   - Filtros: Período, Severidade, Tipo (detalhado/resumido)
   - Botão "GERAR PDF"
   - Preview dos incidentes recentes
   - Métricas em cards

2. **Função `handleDownloadPDF`:**
   ```typescript
   const response = await api.get(
     `/reports/export/pdf?period=${period}&severity=${severity}&tipo=${reportType}&limite=${limiteAtual}`,
     { responseType: 'blob' }
   );
   // Download automático via <a> tag
   ```

3. **Hook `useReports`:**
   - Busca summary, incidents, volume
   - Gerencia loading e errors
   - Actualiza quando filtros mudam

---

## 2️⃣ SISTEMA DE NOTIFICAÇÕES

### Localização dos Ficheiros
- **Backend**: `backend/notification_service.py`, `backend/notification_routes.py`
- **Modelos**: `backend/models.py` → `NotificationConfig`
- **Schemas**: `backend/schemas.py` → `NotificationConfigSchema`
- **Frontend**: `frontend/src/components/NotificationsManagement/`
- **Hooks**: `frontend/hooks/useNotifications.ts`

### Arquitetura

```
┌─────────────────┐
│ LogEvento       │
│ (novo alerta)   │
└────────┬────────┘
         │
         v
┌─────────────────────────────┐
│ notificar_alerta()          │
│ (async)                     │
└────────┬────────────────────┘
         │
         ├─→ Email (SMTP) - Síncrono
         ├─→ Telegram Bot - Assíncrono
         └─→ Teams Webhook - Assíncrono
```

### Endpoints de Notificações

#### 1. **GET `/notifications/config`**
Obtém configuração atual de notificações.

```python
GET /notifications/config
```

**Resposta:**
```json
{
  "email_provider": "gmail",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_ssl": true,
  "smtp_username": "alerts@example.com",
  "smtp_password": "***",
  "smtp_enabled": true,
  "telegram_token": "123456:ABC...",
  "telegram_chat_id": "987654321",
  "telegram_enabled": true,
  "teams_webhook": "https://outlook.webhook.office.com/...",
  "teams_enabled": false,
  "trigger_critical": true,
  "trigger_high": true,
  "trigger_medium": false,
  "atualizado_em": "2026-04-13T15:30:45.123456"
}
```

#### 2. **PUT `/notifications/config`**
Atualiza configuração de notificações.

```python
PUT /notifications/config
Content-Type: application/json

{
  "smtp_enabled": true,
  "smtp_username": "alerts@company.com",
  "smtp_password": "secure_password",
  "telegram_enabled": true,
  "telegram_token": "123456:ABC...",
  "telegram_chat_id": "987654321",
  "trigger_critical": true,
  "trigger_high": true,
  "trigger_medium": false
}
```

**Resposta:**
```json
{"mensagem": "Configurações salvas com sucesso"}
```

#### 3. **GET `/notifications/diagnostics`**
Diagnóstico detalhado de canais.

```python
GET /notifications/diagnostics
```

**Resposta:**
```json
{
  "summary": {
    "atualizado_em": "2026-04-13T15:30:45.123456",
    "any_channel_enabled": true,
    "any_channel_ready": true
  },
  "triggers": {
    "critical": true,
    "high": true,
    "medium": false
  },
  "channels": {
    "email": {
      "enabled": true,
      "ready": true,
      "provider": "gmail",
      "server": "smtp.gmail.com",
      "port": 587,
      "ssl": true,
      "reasons": []
    },
    "telegram": {
      "enabled": true,
      "ready": true,
      "reasons": []
    },
    "teams": {
      "enabled": false,
      "ready": false,
      "reasons": ["teams_enabled=false", "teams_webhook vazio"]
    }
  },
  "notes": [
    "Severidades enviadas dependem de triggers",
    "No sniffer atual eventos são gravados com severidade 'alta'",
    "Se trigger_high=false, alertas do sniffer não serão enviados"
  ]
}
```

#### 4. **POST `/notifications/test/email`** ✉️
Testa envio de email.

#### 5. **POST `/notifications/test/telegram`**
Testa envio para Telegram.

#### 6. **POST `/notifications/test/teams`**
Testa envio para Teams.

### Modelo de Dados

```python
# backend/models.py
class NotificationConfig(Base):
    __tablename__ = "notification_config"
    
    # Email (SMTP)
    email_provider: str       # "gmail", "outlook", ou custom
    smtp_server: str          # Ex: smtp.gmail.com
    smtp_port: int            # Default 587 (STARTTLS) ou 465 (SSL)
    smtp_ssl: bool            # True para SSL, False para STARTTLS
    smtp_username: str        # Email do remetente
    smtp_password: str        # Senha ou app-specific password
    smtp_enabled: bool        # Ativa/desativa canal
    
    # Telegram
    telegram_token: str       # Bot token (ex: 123456:ABC...)
    telegram_chat_id: str     # Chat ID para enviar mensagens
    telegram_enabled: bool
    
    # Teams
    teams_webhook: str        # Webhook URL do Teams
    teams_enabled: bool
    
    # Triggers (filtros de severidade)
    trigger_critical: bool    # Envia alertas críticos
    trigger_high: bool        # Envia alertas altos
    trigger_medium: bool      # Envia alertas médios
    
    atualizado_em: datetime
```

### Fluxo de Notificações

#### 1. **Email SMTP**

**Função:** `enviar_email(config, evento)`

```python
# 1. Valida configuração
- Verifica se smtp_enabled = True
- Verifica credenciais (username/password)

# 2. Seleciona servidor
- Se "gmail" → smtp.gmail.com:587
- Se "outlook" → smtp.office365.com:587
- Se custom → usa smtp_server definido

# 3. Monta mensagem
msg["Subject"] = f"[AEGIS] Alerta {severidade} - {ip_origem}"
msg["From"] = smtp_username
msg.attach(corpo_email_em_texto)

# 4. Conecta e envia
- Usa SSL direto (porta 465) OU STARTTLS (porta 587)
- Fallback automático se falhar

# 5. Mensagem do email
AEGIS IDS/IPS - ALERTA DE SEGURANÇA

Severidade: ALTA
IP Origem: 192.168.1.100
IP Destino: 10.0.0.50
Protocolo: TCP
Porta: 443
Assinatura: TCP SCAN DETECTADO
Timestamp: 2026-04-13 15:30:45
Status: Pendente

Aceda ao painel AEGIS para mais detalhes.
```

**Providers Suportados:**
- ✅ Gmail
- ✅ Outlook 365
- ✅ Custom SMTP (definir servidor/porta)

**Configuração Gmail com 2FA:**
```
1. Ativa 2-Factor Authentication em Google Account
2. Gera "App Password" (16 caracteres)
3. Usa essa senha no campo "smtp_password"
Email: seu.email@gmail.com
Provider: gmail
Senha: xxxx xxxx xxxx xxxx (16 caracteres)
```

#### 2. **Telegram Bot**

**Função:** `enviar_telegram(config, evento)` (async)

```python
# 1. Valida configuração
- Verifica se telegram_enabled = True
- Verifica token e chat_id

# 2. Monta mensagem
AEGIS ALERTA

Severidade: ALTA
IP Origem: 192.168.1.100
IP Destino: 10.0.0.50
Protocolo: TCP
Porta: 443
Assinatura: TCP SCAN DETECTADO
Timestamp: 2026-04-13 15:30:45

# 3. Envia via Telegram Bot API
POST https://api.telegram.org/bot{TOKEN}/sendMessage
{
  "chat_id": "{CHAT_ID}",
  "text": "{MENSAGEM}"
}
```

**Configuração Telegram:**
```
1. Criar bot com @BotFather no Telegram
   /newbot → nome e username
   Recebe: token (123456:ABC...)

2. Obter chat_id:
   - Enviar mensagem para bot
   - Acessar: https://api.telegram.org/bot{TOKEN}/getUpdates
   - Cópia chat_id do resultado

3. Adicionar bot ao chat/grupo
4. Configurar no AEGIS
```

#### 3. **Microsoft Teams**

**Função:** `enviar_teams(config, evento)` (async)

```python
# 1. Valida configuração
- Verifica se teams_enabled = True
- Verifica webhook URL

# 2. Monta mensagem (usa corpo email)
AEGIS IDS/IPS - ALERTA DE SEGURANÇA
...

# 3. Envia via Webhook
POST https://outlook.webhook.office.com/webhookb2/...
{
  "text": "{MENSAGEM}"
}
```

**Configuração Teams:**
```
1. Abrir Teams → Canal desejado
2. Mais opções (...) → Conectores
3. Procurar "Webhook Incoming"
4. Configurar e copiar URL
5. Adicionar ao AEGIS
```

### Sistema de Triggers

```python
def deve_notificar(config, severidade):
    if severidade == "critica" and config.trigger_critical:
        return True
    if severidade == "alta" and config.trigger_high:
        return True
    if severidade == "media" and config.trigger_medium:
        return True
    return False
```

**Exemplo de Cenários:**
- ✅ trigger_critical=T, trigger_high=T, trigger_medium=F
  - Envia: Críticos, Altos
  - Bloqueia: Médios

- ✅ trigger_critical=T, trigger_high=F, trigger_medium=F
  - Envia: Apenas Críticos
  - Bloqueia: Altos, Médios

### Diagnóstico de Canais

A função `_channel_diagnostics()` identifica problemas:

```python
Email não está pronto se:
- smtp_enabled = false
- smtp_username vazio
- smtp_password vazio
- smtp_server não definido (e provider desconhecido)

Telegram não está pronto se:
- telegram_enabled = false
- telegram_token vazio
- telegram_chat_id vazio

Teams não está pronto se:
- teams_enabled = false
- teams_webhook vazio
```

---

## 3️⃣ FLUXO DE NOTIFICAÇÃO (Quando novo evento é detectado)

### Sequência de Eventos

```
1. LogEvento inserido na DB
   ↓
2. notificar_alerta() chamado (async)
   ↓
3. Obtém NotificationConfig
   ↓
4. Normaliza severidade do evento
   ↓
5. Verifica se deve enviar (triggers)
   ├─ Se NO → retorna
   └─ Se YES → continua
   ↓
6. Envia Email (SYNC)
   ├─ Conecta SMTP
   ├─ Autentica
   ├─ Envia mensagem
   └─ Fecha conexão
   ↓
7. Envia Telegram (ASYNC)
   ├─ Faz POST para Bot API
   └─ Retorna (sem esperar)
   ↓
8. Envia Teams (ASYNC)
   ├─ Faz POST para Webhook
   └─ Retorna (sem esperar)
```

### Integração com Sniffer

Quando o sniffer detecta um evento suspeito:

```python
# Em sniffer_routes.py ou similar
evento = LogEvento(
    src_ip="192.168.1.100",
    dest_ip="10.0.0.50",
    protocolo="TCP",
    dest_port=443,
    assinatura="TCP SCAN DETECTADO",
    severidade=Severidade.ALTA,  # ← Normalmente ALTA
    status=Status.PENDENTE
)
session.add(evento)
session.commit()

# Notifica automaticamente
await notificar_alerta(evento, session)
```

---

## 4️⃣ FRONTEND - Componentes de Notificações

### NotificationsManagement Component

**Localização:** `frontend/src/components/NotificationsManagement/index.tsx`

**Secções:**

1. **Email Configuration**
   - Toggle On/Off
   - Provider selector (Gmail, Outlook, Custom)
   - Server/Port settings
   - Username/Password
   - Botão "Test Email"

2. **Integrações Externas**
   - Telegram: Token + Chat ID
   - Teams: Webhook URL

3. **Trigger Settings**
   - Checkboxes: Critical, High, Medium

4. **Diagnostics**
   - Status de cada canal (Ready/Not Ready)
   - Razões de falha
   - Última actualização

### Hook useNotifications

```typescript
export function useNotifications() {
  const [config, setConfig] = useState<NotificationConfig>(defaultConfig);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [testing, setTesting] = useState("");

  // Carrega config
  // Salva alterações
  // Testa canais
  // Obtém diagnósticos
}
```

---

## 5️⃣ Guia de Configuração

### Passo 1: Gmail com 2FA

```
1. Gmail Account Settings
   - Security → 2-Step Verification (ON)
   - App passwords → Selecione "Mail" + "Windows Computer"
   - Gera password temporário (16 chars)

2. AEGIS Configuration
   - Email Provider: Gmail
   - SMTP Server: (auto-preenchido)
   - SMTP Port: 587
   - SSL: false (usa STARTTLS)
   - Username: seu.email@gmail.com
   - Password: xxxxxxxx xxxxxxxx (16 chars gerados)
   - Enable: ON
   - Click Test Email
```

### Passo 2: Telegram

```
1. Telegram BotFather
   - Chat @BotFather
   - /newbot
   - Nome: AEGIS Alerts
   - Username: aegis_alerts_bot (único)
   - Recebe token: 123456:ABC...

2. Obter Chat ID
   - Enviar mensagem ao bot
   - GET https://api.telegram.org/bot123456:ABC.../getUpdates
   - Copiar chat.id do JSON

3. AEGIS Configuration
   - Telegram Token: 123456:ABC...
   - Telegram Chat ID: 987654321
   - Enable: ON
   - Click Test Telegram
```

### Passo 3: Teams Webhook

```
1. Teams Channel
   - Clique em (...)
   - Connectors → Incoming Webhook
   - Configure + Copy URL

2. AEGIS Configuration
   - Teams Webhook: https://outlook.webhook.office.com/...
   - Enable: ON
   - Click Test Teams
```

---

## 6️⃣ Segurança

⚠️ **Importante:**

- ✅ Credenciais armazenadas em BD (NotificationConfig)
- ✅ **Nunca** exponha credenciais em logs ou respostas
- ✅ Use **App Passwords** (Google/Microsoft), não senha principal
- ✅ **Tokens de bot** são token de acesso — guardar com cuidado
- ✅ **Webhooks** devem ser restringidos por IP (se possível)
- ✅ Sempre usar HTTPS para webhooks

---

## 7️⃣ Troubleshooting

### Email não é enviado

```
1. Verifique diagnostics: GET /notifications/diagnostics
2. Valide credenciais SMTP
3. Verifique trigger (se medium, configure trigger_medium=true)
4. Teste manualmente: POST /notifications/test/email
5. Logs do servidor → [EMAIL] ...
```

### Telegram não funciona

```
1. Valide token com: https://api.telegram.org/bot{TOKEN}/getMe
2. Valide chat_id com: https://api.telegram.org/bot{TOKEN}/getUpdates
3. Verifique se bot está no chat (send mensagem ao bot primeiro)
4. Teste: POST /notifications/test/telegram
```

### Teams webhook inválido

```
1. Verifica URL é válida (comça com https://outlook.webhook.office.com)
2. Tenta POST manualmente com curl
3. Verifique permissões do canal
```

---

## 8️⃣ API Resumida

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/reports/summary` | Resumo de alertas |
| GET | `/reports/incidents` | Lista incidentes |
| GET | `/reports/attack-volume` | Volume por hora |
| GET | `/reports/export/pdf` | 📥 Download PDF |
| GET | `/notifications/config` | Config atual |
| PUT | `/notifications/config` | Actualiza config |
| GET | `/notifications/diagnostics` | Diagnóstico |
| POST | `/notifications/test/email` | Teste email |
| POST | `/notifications/test/telegram` | Teste Telegram |
| POST | `/notifications/test/teams` | Teste Teams |

---

## 9️⃣ Métricas e Estatísticas

**O que é rastreado nos relatórios:**
- Total de eventos por período
- Distribuição por severidade (crítica, alta, média, baixa)
- Eventos bloqueados vs pendentes
- IPs únicos bloqueados
- Volume de eventos por hora

**Alertas enviados:**
- Severidade do evento
- IP origem/destino
- Protocolo e porta
- Signature/Assinatura
- Timestamp
- Status (mitigado, pendente, ignorado)

---

## 🔟 Melhorias Futuras Sugeridas

- [ ] Exportar relatórios em Excel/CSV
- [ ] Agendar relatórios automáticos (diários, semanais)
- [ ] Enviar relatórios por email automaticamente
- [ ] Webhooks customizados (Slack, Discord, etc.)
- [ ] Template customizável para mensagens
- [ ] Rate limiting (não sobrecarregar canais)
- [ ] Arquivo histórico de notificações enviadas
- [ ] Dashboard em tempo real de notificações
- [ ] Retry automático com backoff exponencial
- [ ] Criptografia de credenciais na BD

