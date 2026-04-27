# 🚀 PLANO DE DEPLOYMENT CLOUD - RENDER + VERCEL + SNIFFER LOCAL

## Visão Geral da Arquitetura

```mermaid
flowchart LR
    Internet((Internet)) --> CDN[CDN Vercel]
    CDN --> WEB["🌐 Frontend Vercel<br/>(React/Vite SPA)"]
    
    Internet --> Render["☁️ Backend Render<br/>(FastAPI + PostgreSQL)"]
    WEB -->|API Calls HTTPS| Render
    
    LocalPC["🖥️ PC/VM LOCAL<br/>(Este PC)"] -->|SSH/Tunnel| Sniffer["🔍 Sniffer Local<br/>(Docker - Captura Tráfego)"]
    Sniffer -->|REST API HTTPS| Render
    
    Sniffer -->|Monitora| ETH0["eth0<br/>(Interface 1)"]
    Sniffer -->|Monitora| ETH1["eth1<br/>(Interface 2)"]
    Sniffer -->|Monitora| ETH2["eth2<br/>(Interface N)"]
    
    Render --> DB[(PostgreSQL<br/>Gerenciado)]
```

## 📋 Checklist de Deployment

### FASE 1: Preparar Backend para Render ✅

- [ ] **1.1** Verificar `render.yaml` está correto
- [ ] **1.2** Confirmar `requirements.txt` do backend
- [ ] **1.3** Revisar `backend/config.py` para suportar URLs dinâmicas
- [ ] **1.4** Testar localmente com `docker-compose.yml`

**Arquivos a revisar:**
```
backend/config.py          # CORS, FRONTEND_ORIGINS, etc
backend/requirements.txt   # Dependências
render.yaml               # Configuração de deployment
```

### FASE 2: Deploy Backend no Render 🟢

**Passo 1: Login no Render**
```
https://dashboard.render.com
```

**Passo 2: Criar Blueprint**
- New → Blueprint
- Conectar repositório GitHub
- Confirmar `render.yaml`

**Passo 3: Variáveis de Ambiente no Render**
```yaml
DATABASE_URL=postgres://...  # Auto-injetada
SECRET_KEY=seu_secret_aleatorio_gerado
CORS_ALLOW_ORIGIN_REGEX=.*vercel.app  # Para Vercel
FRONTEND_ORIGINS=*.vercel.app
SENSOR_API_TOKEN=seu_token_super_seguro  # Para sniffer autenticar
ENVIRONMENT=production
```

**Passo 4: Verificar Deploy**
```bash
# Após deploy, teste:
curl https://seu-backend.onrender.com/docs
```

**Resultado esperado:**
- URL: `https://seu-backend.onrender.com`
- PostgreSQL: gerenciado pelo Render
- Database migrations: `alembic upgrade head` rodado automaticamente

---

### FASE 3: Preparar Frontend para Vercel ✅

- [ ] **3.1** Revisar `frontend/` (React/Vite)
- [ ] **3.2** Confirmar `.env.production` com `VITE_API_URL`
- [ ] **3.3** Testar build local: `npm run build`
- [ ] **3.4** Commit e push para GitHub

**Arquivos críticos:**
```
frontend/vite.config.ts          # Build config
frontend/.env.production         # API URL produção
frontend/src/api/config.ts       # Cliente HTTP
```

### FASE 4: Deploy Frontend no Vercel 🟢

**Passo 1: Login no Vercel**
```
https://vercel.com/dashboard
```

**Passo 2: Import GitHub Project**
- Add New → Project
- Selecionar repositório
- Root Directory: `frontend`

**Passo 3: Variáveis de Ambiente**
```
VITE_API_URL=https://seu-backend.onrender.com
```

**Passo 4: Deploy**
- Vercel deteta `vite.config.ts` automaticamente
- Build: `npm run build`
- Output: `.vite/dist`

**Resultado esperado:**
- URL: `https://seu-projeto.vercel.app`
- Acesso automático ao backend Render via CORS

---

### FASE 5: Configurar Sniffer Local 🔍

- [ ] **5.1** Criar arquivo `.env.sniffer` neste PC
- [ ] **5.2** Configurar interfaces a monitorar
- [ ] **5.3** Testar conexão com backend cloud
- [ ] **5.4** Validar que **todas as interfaces aparecem na cloud**

#### 5.1 Criar `.env.sniffer`

```bash
# /home/jgd/projeto-ids-ips/.env.sniffer

# Backend Cloud
BACKEND_URL=https://seu-backend.onrender.com
SENSOR_API_TOKEN=seu_token_super_seguro

# Interfaces a monitorar (todas do PC)
INTERFACES=eth0,eth1,eth2,wlan0
ZONE_MAP=eth0:wan,eth1:lan,eth2:lan,wlan0:wlan

# Configuração do sniffer
SENSOR_NAME=Sniffer-Local-PC-$(hostname)
SENSOR_ZONE=mixed
IDS_THRESHOLD=0.7
IPS_MIN_CONFIDENCE=0.8
LOG_LEVEL=INFO
```

#### 5.2 Criar Docker Compose para Sniffer Local

**Arquivo: `docker-compose.sniffer.yml`**

```yaml
version: '3.8'

services:
  sniffer:
    build:
      context: ./
      dockerfile: ./docker-backend/Dockerfile
    container_name: ids-ips-sniffer-local
    
    # CRÍTICO: Capturar tráfego real
    network_mode: host
    cap_add:
      - NET_ADMIN
      - NET_RAW
      - SYS_PTRACE
    
    env_file: .env.sniffer
    
    environment:
      SENSOR_MODE=sniffer
      BACKEND_URL=${BACKEND_URL}
      SENSOR_API_TOKEN=${SENSOR_API_TOKEN}
      INTERFACES=${INTERFACES}
      ZONE_MAP=${ZONE_MAP}
      SENSOR_NAME=${SENSOR_NAME}
    
    volumes:
      - ./backend:/app/backend
      - ./sniffer:/app/sniffer
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
    
    restart: always
    
    sysctls:
      - net.core.rmem_max=134217728
      - net.core.wmem_max=134217728
      - net.ipv4.ip_forward=1
    
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "10"
```

#### 5.3 Iniciar Sniffer Local

```bash
# Terminal no PC local
cd /home/jgd/projeto-ids-ips

# Criar .env.sniffer
cp .env.sniffer.example .env.sniffer
nano .env.sniffer  # Editar com seus valores

# Iniciar sniffer
docker compose -f docker-compose.sniffer.yml up -d

# Verificar status
docker compose -f docker-compose.sniffer.yml logs -f sniffer
```

#### 5.4 Validar Conexão com Cloud

```bash
# Dentro do container sniffer
docker exec ids-ips-sniffer-local curl -H "Authorization: Bearer seu_token_super_seguro" \
  https://seu-backend.onrender.com/sniffer/status

# Resposta esperada:
# {
#   "status": "running",
#   "sensor_name": "Sniffer-Local-PC-host",
#   "interfaces": ["eth0", "eth1", "eth2", "wlan0"],
#   "zone_map": {...},
#   "packets_captured": 45230,
#   "last_alert": "2026-04-27T14:32:10Z"
# }
```

---

### FASE 6: Configurar Endpoints de Integração Sniffer-Backend

O sniffer deve enviar dados continuamente:

#### 6.1 POST `/sniffer/events` - Enviar Eventos

```bash
curl -X POST https://seu-backend.onrender.com/sniffer/events \
  -H "Authorization: Bearer seu_token_super_seguro" \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_name": "Sniffer-Local-PC-host",
    "interface": "eth0",
    "zone": "wan",
    "event_type": "alert",
    "alert_type": "port_scan",
    "source_ip": "192.168.1.100",
    "dest_ip": "8.8.8.8",
    "confidence": 0.95,
    "timestamp": "2026-04-27T14:32:10Z",
    "details": {...}
  }'
```

#### 6.2 GET `/sniffer/status` - Status em Tempo Real

```bash
curl -H "Authorization: Bearer seu_token_super_seguro" \
  https://seu-backend.onrender.com/sniffer/status
```

#### 6.3 GET `/dashboard/interfaces` - Listar Interfaces da Cloud

```bash
curl -H "Authorization: Bearer seu_token_super_seguro" \
  https://seu-backend.onrender.com/dashboard/interfaces

# Resposta:
# {
#   "sensors": [
#     {
#       "sensor_name": "Sniffer-Local-PC-host",
#       "interfaces": [
#         {"name": "eth0", "zone": "wan", "packets": 45230, "alerts": 12},
#         {"name": "eth1", "zone": "lan", "packets": 8932, "alerts": 2},
#         ...
#       ]
#     }
#   ]
# }
```

---

### FASE 7: Validar Tudo Online 🟢

- [ ] **7.1** Frontend Vercel acarrega
- [ ] **7.2** Login funciona (backend Render responde)
- [ ] **7.3** Sniffer conecta e envia eventos
- [ ] **7.4** Dashboard mostra interfaces do PC local
- [ ] **7.5** Alertas aparecem em tempo real na cloud

#### Checklists de Validação

**Frontend (Vercel):**
```bash
# 1. Acesse https://seu-projeto.vercel.app
# 2. Abra DevTools (F12)
# 3. Verifique Network → veja requisições para seu-backend.onrender.com
# 4. Login e explore dashboard
```

**Backend (Render):**
```bash
# 1. Acesse https://seu-backend.onrender.com/docs
# 2. Teste endpoints com Swagger UI
# 3. Verifique PostgreSQL está rodando
# 4. Veja logs de deploy em https://dashboard.render.com
```

**Sniffer Local:**
```bash
# 1. Verifique container rodando
docker compose -f docker-compose.sniffer.yml ps

# 2. Veja logs
docker compose -f docker-compose.sniffer.yml logs -f sniffer | grep "connected\|error\|interface"

# 3. Confirme interfaces sendo monitoradas
docker exec ids-ips-sniffer-local ip link show

# 4. Teste envio de eventos manualmente
curl -X POST https://seu-backend.onrender.com/sniffer/events \
  -H "Authorization: Bearer seu_token_super_seguro" \
  -H "Content-Type: application/json" \
  -d '{"sensor_name":"test","interface":"eth0",...}'
```

---

## 📊 URLs de Acesso Finais

| Serviço        | URL                                      | Notas                        |
|---|---|---|
| **Frontend**   | `https://seu-projeto.vercel.app`       | Acesso público              |
| **Backend API** | `https://seu-backend.onrender.com`     | HTTPS + Auth token          |
| **API Docs**   | `https://seu-backend.onrender.com/docs` | Swagger UI                  |
| **Sniffer**    | Local (Docker) - não exposto             | Envia dados para backend    |

---

## 🔐 Segurança - Essencial

1. **HTTPS em tudo** ✅ (Vercel + Render já fornecem)
2. **SENSOR_API_TOKEN** - Bearer token fortíssimo
3. **CORS** configurado corretamente no backend
4. **Firewall local** - sniffer não precisa ser exposto
5. **Rate limiting** - adicionar no backend para `/sniffer/events`

---

## 🛠️ Próximos Passos

1. **Agora:** Revisar este plano e ajustar URLs/tokens
2. **Depois:** Copiar `.env.sniffer.example` → `.env.sniffer`
3. **Deploy Backend:** Push para GitHub → Render detecta `render.yaml`
4. **Deploy Frontend:** Conectar Vercel ao repositório
5. **Iniciar Sniffer:** `docker-compose -f docker-compose.sniffer.yml up -d`
6. **Monitorar:** Dashboard da cloud mostrando interfaces local em tempo real

---

## 📞 Referência Rápida

```bash
# Verificar status completo
./check_deployment_status.sh

# Limpar e reiniciar tudo localmente
docker compose -f docker-compose.sniffer.yml down -v
docker compose -f docker-compose.sniffer.yml up -d

# Ver logs em tempo real
docker compose -f docker-compose.sniffer.yml logs -f sniffer

# Entrar no container
docker exec -it ids-ips-sniffer-local bash
```

---

## ⚠️ Troubleshooting

### Sniffer não conecta ao backend

```bash
# Testar conectividade
curl -v https://seu-backend.onrender.com/health

# Verificar token
echo "seu_token_super_seguro"

# Teste de auth
curl -H "Authorization: Bearer seu_token_super_seguro" \
  https://seu-backend.onrender.com/sniffer/status
```

### Interfaces não aparecem no dashboard

- Verificar `INTERFACES` no `.env.sniffer`
- Confirmar sniffer está enviando `/sniffer/events`
- Ver logs do backend no Render

### CORS error no frontend

- Backend em `/api` não retorna header `Access-Control-Allow-Origin`
- Revisar `CORS_ALLOW_ORIGIN_REGEX` no Render env
- Deve incluir `*.vercel.app`

---

**Status:** 🔴 Ainda não deployado  
**Última atualização:** 2026-04-27  
**Ambiente alvo:** Render (Backend) + Vercel (Frontend) + Local (Sniffer)
