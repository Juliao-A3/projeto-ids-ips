# Exemplos Práticos - Sistema de Relatórios e Notificações

## 📌 Índice
1. [Exemplos com cURL](#-exemplos-com-curl)
2. [Exemplos em Python](#-exemplos-em-python)
3. [Exemplos em TypeScript/React](#-exemplos-em-typescriptreact)
4. [Casos de Uso](#-casos-de-uso)

---

## 🔌 Exemplos com cURL

### 1️⃣ Obter Resumo de Alertas (24h)

```bash
curl -X GET "http://localhost:8000/reports/summary?period=24h&severity=all" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

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

### 2️⃣ Listar Últimos 20 Incidentes "Altos"

```bash
curl -X GET "http://localhost:8000/reports/incidents?period=7d&severity=alta&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3️⃣ Obter Volume de Ataques por Hora

```bash
curl -X GET "http://localhost:8000/reports/attack-volume?period=24h" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o attack-volume.json
```

**Resposta:**
```json
[
  {"time": "00:00", "attacks": 12},
  {"time": "01:00", "attacks": 8},
  {"time": "02:00", "attacks": 15},
  {"time": "03:00", "attacks": 3}
]
```

### 4️⃣ Gerar e Baixar PDF (Relatório Detalhado)

```bash
curl -X GET "http://localhost:8000/reports/export/pdf?period=24h&severity=all&tipo=detalhado&limite=500" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o "/tmp/aegis-report-detalhado-24h.pdf"
```

### 5️⃣ Gerar PDF Resumido (Últimos 7 dias, apenas CRÍTICOS)

```bash
curl -X GET "http://localhost:8000/reports/export/pdf?period=7d&severity=critica&tipo=resumido&limite=100" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o "/tmp/aegis-report-criticos.pdf"
```

### 6️⃣ Obter Configuração de Notificações

```bash
curl -X GET "http://localhost:8000/notifications/config" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Resposta (com credenciais mascaradas):**
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

### 7️⃣ Configurar Email (Gmail com App Password)

```bash
curl -X PUT "http://localhost:8000/notifications/config" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email_provider": "gmail",
    "smtp_username": "alerts@gmail.com",
    "smtp_password": "xxxx xxxx xxxx xxxx",
    "smtp_enabled": true,
    "telegram_enabled": false,
    "teams_enabled": false,
    "trigger_critical": true,
    "trigger_high": true,
    "trigger_medium": false
  }'
```

### 8️⃣ Configurar Telegram

```bash
curl -X PUT "http://localhost:8000/notifications/config" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_token": "123456:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh",
    "telegram_chat_id": "987654321",
    "telegram_enabled": true,
    "trigger_critical": true,
    "trigger_high": true,
    "trigger_medium": false
  }'
```

### 9️⃣ Obter Diagnóstico de Canais

```bash
curl -X GET "http://localhost:8000/notifications/diagnostics" \
  -H "Authorization: Bearer YOUR_TOKEN"
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
  "notes": [...]
}
```

### 🔟 Testar Envio de Email

```bash
curl -X POST "http://localhost:8000/notifications/test/email" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Resposta:**
```json
{"mensagem": "Email de teste enviado com sucesso"}
```

### 1️⏸️ 1️ Testar Telegram

```bash
curl -X POST "http://localhost:8000/notifications/test/telegram" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 1️⏸️ 2️ Testar Teams

```bash
curl -X POST "http://localhost:8000/notifications/test/teams" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🐍 Exemplos em Python

### Setup Inicial

```python
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"
TOKEN = "seu_token_aqui"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def make_request(method, endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro: {e}")
        return None
```

### 1. Gerar Relatório PDF Programaticamente

```python
def download_pdf_report(period="24h", severity="all", tipo="detalhado"):
    """
    Downloaded relatório PDF
    
    Args:
        period: "24h", "7d", "30d"
        severity: "all", "critica", "alta", "media", "baixa"
        tipo: "detalhado", "resumido"
    """
    url = f"{BASE_URL}/reports/export/pdf"
    params = {
        "period": period,
        "severity": severity,
        "tipo": tipo,
        "limite": 500 if tipo == "detalhado" else 100
    }
    
    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            stream=True
        )
        response.raise_for_status()
        
        # Salvar PDF
        filename = f"aegis-report-{tipo}-{period}.pdf"
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✓ PDF salvo: {filename}")
        return filename
    except Exception as e:
        print(f"✗ Erro ao gerar PDF: {e}")
        return None

# Uso
download_pdf_report(period="24h", severity="critica", tipo="resumido")
```

### 2. Obter Métricas de Segurança

```python
def get_security_metrics(period="24h"):
    """
    Obtém resumo de métricas de segurança
    """
    data = make_request("GET", f"/reports/summary?period={period}")
    
    if data:
        print(f"\n{'='*50}")
        print(f"MÉTRICAS DE SEGURANÇA - {period.upper()}")
        print(f"{'='*50}")
        print(f"Total de Eventos:      {data['total_eventos']:,}")
        print(f"Críticos:              {data['criticos']}")
        print(f"Altos:                 {data['altos']}")
        print(f"Médios:                {data['medios']}")
        print(f"Bloqueados:            {data['bloqueados']}")
        print(f"IPs Bloqueados:        {data['total_ips_bloqueados']}")
        print(f"{'='*50}\n")
        return data
    return None

# Uso
metrics = get_security_metrics("24h")
```

### 3. Gerar Relatório Automático Diário

```python
import schedule
import time
from datetime import datetime

def generate_daily_report():
    """Gera e baixa relatório diário de forma automática"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    print(f"\n[{timestamp}] Gerando relatório diário...")
    
    # Gerar PDF
    pdf_file = download_pdf_report(
        period="24h",
        severity="all",
        tipo="detalhado"
    )
    
    # Obter métricas
    metrics = get_security_metrics("24h")
    
    if pdf_file and metrics:
        print(f"[{timestamp}] ✓ Relatório gerado com sucesso!")
    else:
        print(f"[{timestamp}] ✗ Erro ao gerar relatório")

# Agendar para 8h da manhã
schedule.every().day.at("08:00").do(generate_daily_report)

# Loop infinito
while True:
    schedule.run_pending()
    time.sleep(60)
```

### 4. Configurar Notificações por Email

```python
def setup_email_notifications(email, app_password):
    """
    Configura notificações por email (Gmail com 2FA)
    
    Args:
        email: seu.email@gmail.com
        app_password: 16 caracteres gerados no Gmail
    """
    config = {
        "email_provider": "gmail",
        "smtp_username": email,
        "smtp_password": app_password,
        "smtp_enabled": True,
        "telegram_enabled": False,
        "teams_enabled": False,
        "trigger_critical": True,
        "trigger_high": True,
        "trigger_medium": False
    }
    
    result = make_request("PUT", "/notifications/config", config)
    
    if result:
        print("✓ Configuração de email atualizada")
        
        # Testar
        test_result = make_request("POST", "/notifications/test/email")
        if test_result:
            print("✓ Email de teste enviado com sucesso!")
        else:
            print("✗ Erro ao testar email")
    else:
        print("✗ Erro ao atualizar configuração")

# Uso
setup_email_notifications(
    "alerts@gmail.com",
    "xxxx xxxx xxxx xxxx"
)
```

### 5. Configurar Notificações via Telegram

```python
def setup_telegram_notifications(token, chat_id):
    """
    Configura notificações via Telegram Bot
    
    Args:
        token: Token do bot (ex: 123456:ABC...)
        chat_id: ID do chat (ex: 987654321)
    """
    config = {
        "telegram_token": token,
        "telegram_chat_id": chat_id,
        "telegram_enabled": True,
        "trigger_critical": True,
        "trigger_high": True,
        "trigger_medium": False
    }
    
    result = make_request("PUT", "/notifications/config", config)
    
    if result:
        print("✓ Configuração de Telegram atualizada")
        
        # Testar
        test_result = make_request("POST", "/notifications/test/telegram")
        if test_result:
            print("✓ Mensagem de teste enviada ao Telegram!")
        else:
            print("✗ Erro ao testar Telegram")
    else:
        print("✗ Erro ao atualizar configuração")

# Uso
setup_telegram_notifications(
    "123456:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh",
    "987654321"
)
```

### 6. Verificar Status de Notificações

```python
def check_notification_status():
    """
    Verifica o status de todos os canais de notificação
    """
    data = make_request("GET", "/notifications/diagnostics")
    
    if not data:
        print("✗ Erro ao obter diagnóstico")
        return
    
    print("\n" + "="*60)
    print("STATUS DE CANAIS DE NOTIFICAÇÃO")
    print("="*60)
    
    # Summary
    summary = data.get("summary", {})
    print(f"\nÚltima Atualização: {summary.get('atualizado_em')}")
    print(f"Qualquer canal ativado? {summary.get('any_channel_enabled')}")
    print(f"Qualquer canal pronto? {summary.get('any_channel_ready')}")
    
    # Triggers
    triggers = data.get("triggers", {})
    print(f"\nTRIGGERS:")
    print(f"  Crítica: {triggers.get('critical')}")
    print(f"  Alta:    {triggers.get('high')}")
    print(f"  Média:   {triggers.get('medium')}")
    
    # Canais
    channels = data.get("channels", {})
    for canal, info in channels.items():
        status = "✓ PRONTO" if info['ready'] else "✗ NÃO PRONTO"
        print(f"\n{canal.upper()} {status}")
        print(f"  Ativado: {info['enabled']}")
        if info['reasons']:
            print(f"  Razões:")
            for reason in info['reasons']:
                print(f"    - {reason}")
    
    print("\n" + "="*60 + "\n")

# Uso
check_notification_status()
```

### 7. Listar Incidentes Recentes

```python
def list_recent_incidents(period="24h", limit=10):
    """
    Lista incidentes recentes com filtros
    """
    endpoint = f"/reports/incidents?period={period}&severity=all&limit={limit}"
    data = make_request("GET", endpoint)
    
    if not data:
        print("✗ Erro ao obter incidentes")
        return
    
    print(f"\n{'='*80}")
    print(f"INCIDENTES RECENTES - {period.upper()} ({len(data)} resultados)")
    print(f"{'='*80}")
    print(f"{'Hora':<10} {'Origem':<15} {'Destino':<15} {'Protocolo':<8} {'Sev':<7} {'Status':<10}")
    print("-" * 80)
    
    for incident in data:
        ts = incident['timestamp'].split('T')[1][:8] if incident['timestamp'] else "-"
        print(f"{ts:<10} {incident['origem']:<15} {incident['destino']:<15} "
              f"{incident['protocolo']:<8} {incident['severidade']:<7} {incident['status']:<10}")
    
    print(f"{'='*80}\n")

# Uso
list_recent_incidents("24h", limit=20)
```

---

## 📱 Exemplos em TypeScript/React

### 1. Hook Customizado para Relatórios

```typescript
import { useState, useEffect } from 'react';
import { api } from '@/services/api';

interface ReportMetrics {
  total_eventos: number;
  criticos: number;
  altos: number;
  medios: number;
  bloqueados: number;
  total_ips_bloqueados: number;
}

export function useReportMetrics(period: string) {
  const [metrics, setMetrics] = useState<ReportMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMetrics();
  }, [period]);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/reports/summary?period=${period}`);
      setMetrics(response.data);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar métricas');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return { metrics, loading, error, refetch: fetchMetrics };
}
```

**Uso em componente:**
```tsx
export function DashboardMetrics() {
  const { metrics, loading, error } = useReportMetrics('24h');

  if (loading) return <div>Carregando...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  return (
    <div>
      <h3>Total de Eventos: {metrics?.total_eventos}</h3>
      <h3>Críticos: {metrics?.criticos}</h3>
      <h3>Altos: {metrics?.altos}</h3>
    </div>
  );
}
```

### 2. Componente de Download de Relatório

```typescript
import { useState } from 'react';
import { Download } from 'lucide-react';
import { api } from '@/services/api';

interface PDFGeneratorProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export function PDFReportGenerator({ onSuccess, onError }: PDFGeneratorProps) {
  const [loading, setLoading] = useState(false);
  const [period, setPeriod] = useState<'24h' | '7d' | '30d'>('24h');
  const [tipo, setTipo] = useState<'detalhado' | 'resumido'>('detalhado');
  const [severity, setSeverity] = useState('all');

  const handleGeneratePDF = async () => {
    try {
      setLoading(true);
      
      const limite = tipo === 'detalhado' ? 500 : 100;
      const response = await api.get(
        `/reports/export/pdf?period=${period}&severity=${severity}&tipo=${tipo}&limite=${limite}`,
        { responseType: 'blob' }
      );

      // Criar e fazer download do arquivo
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `aegis-report-${tipo}-${period}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      onSuccess?.();
    } catch (error) {
      const message = 'Erro ao gerar PDF';
      onError?.(message);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>Gerar Relatório</h2>
      
      <label>
        Período:
        <select value={period} onChange={(e) => setPeriod(e.target.value as any)}>
          <option value="24h">Últimas 24h</option>
          <option value="7d">Últimos 7 dias</option>
          <option value="30d">Últimos 30 dias</option>
        </select>
      </label>

      <label>
        Tipo:
        <select value={tipo} onChange={(e) => setTipo(e.target.value as any)}>
          <option value="detalhado">Detalhado (até 500)</option>
          <option value="resumido">Resumido (até 100)</option>
        </select>
      </label>

      <label>
        Severidade:
        <select value={severity} onChange={(e) => setSeverity(e.target.value)}>
          <option value="all">Todas</option>
          <option value="critica">Crítica</option>
          <option value="alta">Alta</option>
          <option value="media">Média</option>
        </select>
      </label>

      <button onClick={handleGeneratePDF} disabled={loading}>
        <Download size={16} />
        {loading ? 'Gerando...' : 'Gerar PDF'}
      </button>
    </div>
  );
}
```

### 3. Verificador de Status de Notificações

```typescript
import { useState, useEffect } from 'react';
import { CheckCircle, AlertCircle } from 'lucide-react';
import { api } from '@/services/api';

interface ChannelStatus {
  email: {
    enabled: boolean;
    ready: boolean;
    reasons: string[];
  };
  telegram: {
    enabled: boolean;
    ready: boolean;
    reasons: string[];
  };
  teams: {
    enabled: boolean;
    ready: boolean;
    reasons: string[];
  };
}

export function NotificationStatusChecker() {
  const [status, setStatus] = useState<ChannelStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 30000); // Atualizar a cada 30s
    return () => clearInterval(interval);
  }, []);

  const checkStatus = async () => {
    try {
      const response = await api.get('/notifications/diagnostics');
      setStatus(response.data.channels);
    } catch (error) {
      console.error('Erro ao verificar status:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Verificando status...</div>;

  return (
    <div style={{ padding: '20px' }}>
      <h2>Status de Canais de Notificação</h2>
      
      {['email', 'telegram', 'teams'].map((canal) => {
        const data = status?.[canal as keyof ChannelStatus];
        if (!data) return null;

        return (
          <div key={canal} style={{ marginBottom: '15px', padding: '10px', border: '1px solid #ddd' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              {data.ready ? (
                <CheckCircle color="green" size={20} />
              ) : (
                <AlertCircle color="red" size={20} />
              )}
              <span style={{ textTransform: 'capitalize', fontWeight: 'bold' }}>
                {canal}
              </span>
              <span style={{ fontSize: '12px', color: '#666' }}>
                {data.enabled ? '(Ativado)' : '(Desativado)'}
              </span>
              <span style={{ marginLeft: 'auto', fontWeight: 'bold' }}>
                {data.ready ? 'Pronto ✓' : 'Não pronto ✗'}
              </span>
            </div>
            
            {data.reasons.length > 0 && (
              <div style={{ marginTop: '8px', fontSize: '12px', color: '#d32f2f' }}>
                <strong>Problemas:</strong>
                <ul>
                  {data.reasons.map((reason, idx) => (
                    <li key={idx}>{reason}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        );
      })}

      <button onClick={checkStatus} style={{ marginTop: '10px' }}>
        Atualizar Status
      </button>
    </div>
  );
}
```

---

## 🎯 Casos de Uso

### Caso 1: Auditoria Diária

```python
def daily_audit():
    """
    Executar a cada manhã para auditoria
    """
    # Gerar relatório dos últimos 24h
    pdf = download_pdf_report("24h", "all", "detalhado")
    
    # Obter métricas
    metrics = get_security_metrics("24h")
    
    # Verificar status
    check_notification_status()
    
    # Se críticos > 10, enviar alerta adicional
    if metrics and metrics['criticos'] > 10:
        print("⚠️ ALERTA: Muitos eventos críticos detectados!")
```

### Caso 2: Relatório Semanal Automático

```python
import schedule
from email.mime.base import MIMEBase
from email import encoders

def send_weekly_report():
    """
    Aos segundos-feira, enviar relatório da semana por email
    """
    pdf_file = download_pdf_report("7d", "all", "detalhado")
    
    # Carregar email de configuração
    config = make_request("GET", "/notifications/config")
    
    # Enviar via email
    # (usar biblioteca como smtplib para anexar arquivo)
    print(f"✓ Relatório semanal enviado: {pdf_file}")

schedule.every().monday.at("09:00").do(send_weekly_report)
```

### Caso 3: Integração com Slack

```python
def alert_on_critical_events():
    """
    Se houver eventos críticos, enviar alerta ao Slack
    """
    metrics = get_security_metrics("1h")  # Últimas 1h
    
    if metrics['criticos'] > 0:
        message = f"""
        ⚠️ ALERTA CRÍTICA DETECTADA!
        
        - Eventos Críticos: {metrics['criticos']}
        - Altos: {metrics['altos']}
        - Bloqueados: {metrics['bloqueados']}
        
        Acesse: http://localhost:5173/reports
        """
        
        # Enviar para Slack webhook
        requests.post('YOUR_SLACK_WEBHOOK', json={
            "text": message
        })
```

### Caso 4: Verificação de Saúde (Health Check)

```python
def health_check():
    """
    Verifique se todos os canais estão funcionando
    """
    try:
        make_request("POST", "/notifications/test/email")
        make_request("POST", "/notifications/test/telegram")
        make_request("POST", "/notifications/test/teams")
        
        return {
            "status": "ok",
            "message": "Todos os canais estão funcionando"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Executar como endpoint de health check
# GET /health →  health_check()
```

---

## 📊 Script Completo de Setup

```python
#!/usr/bin/env python3
"""
Script de setup completo de notificações e relatórios
"""

import requests
import sys
from getpass import getpass

BASE_URL = "http://localhost:8000"

def setup_notifications():
    print("\n" + "="*60)
    print("CONFIGURAR SISTEMA DE NOTIFICAÇÕES")
    print("="*60)
    
    token = getpass("Token JWT: ")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Email
    print("\n[1/3] Configurar Email")
    use_email = input("Usar Email? (s/n): ").lower() == 's'
    
    if use_email:
        email = input("Email (Gmail): ")
        app_pass = getpass("App Password (16 char): ")
        
        config = {
            "email_provider": "gmail",
            "smtp_username": email,
            "smtp_password": app_pass,
            "smtp_enabled": True,
            "trigger_critical": True,
            "trigger_high": True,
            "trigger_medium": False
        }
        
        response = requests.put(
            f"{BASE_URL}/notifications/config",
            json=config,
            headers=headers
        )
        print("✓ Email configurado" if response.ok else "✗ Erro ao configurar email")
    
    # Telegram
    print("\n[2/3] Configurar Telegram")
    use_telegram = input("Usar Telegram? (s/n): ").lower() == 's'
    
    if use_telegram:
        token_telegram = input("Bot Token (ex: 123456:ABC...): ")
        chat_id = input("Chat ID: ")
        
        config = {
            "telegram_token": token_telegram,
            "telegram_chat_id": chat_id,
            "telegram_enabled": True
        }
        
        response = requests.put(
            f"{BASE_URL}/notifications/config",
            json=config,
            headers=headers
        )
        print("✓ Telegram configurado" if response.ok else "✗ Erro ao configurar Telegram")
    
    # Verificar status
    print("\n[3/3] Verificar Status")
    response = requests.get(
        f"{BASE_URL}/notifications/diagnostics",
        headers=headers
    )
    
    if response.ok:
        data = response.json()
        print("\n✓ Sistema pronto!" if data['summary']['any_channel_ready'] else "\n✗ Alguns canais com problemas")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        setup_notifications()
    except KeyboardInterrupt:
        print("\n\nCancelado pelo utilizador")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Erro: {e}")
        sys.exit(1)
```

---

## ✅ Checklist de Implementação

- [ ] Email configurado e testado
- [ ] Telegram configurado e testado
- [ ] Teams (opcional) configurado e testado
- [ ] Triggers definidos (crítica, alta, média)
- [ ] Diagnóstico OK para todos os canais
- [ ] Primeira notificação de teste recebida
- [ ] Relatório PDF gerado com sucesso
- [ ] Agendar relatórios automáticos
- [ ] Documentar credenciais em local seguro

