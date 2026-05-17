# 🎯 PLANO DE DEPLOYMENT - SUMÁRIO EXECUTIVO

## Situação Atual
- ✅ Código do backend e frontend pronto  
- ✅ Backend já está hospedado no Render
- ✅ Frontend já está hospedado na Vercel
- ✅ Docker compose configurado localmente
- ✅ Documentação de arquitetura existente
- ⏳ Falta ativar/validar o sniffer local e a integração com a cloud

## Objetivo Geral
```
Sniffer local (este PC) → Backend Online (Render) ← Frontend Online (Vercel)
     (captura)      (requisições HTTPS)         (acesso web)
```

## Arquitetura Final

```
┌─────────────────────────────────────────────────────────┐
│                   ☁️ NUVEM (ONLINE)                      │
│  ┌─────────────────────────────────────────────────┐    │
│  │ Frontend Vercel                                 │    │
│  │ https://projeto-ids-ips.vercel.app              │    │
│  │ (Acesso público, SPA React/Vite)               │    │
│  └────────────────────┬────────────────────────────┘    │
│                       │                                  │
│                  API HTTPS                              │
│      (CORS desde *.vercel.app)                          │
│                       │                                  │
│  ┌────────────────────▼────────────────────────────┐    │
│  │ Backend Render             ┌──────────────────┐ │    │
│  │ https://projeto-ids-ips.onrender.com           │ │    │
│  │ (FastAPI + Autenticação)   │ PostgreSQL      │ │    │
│  │                            │ Gerenciado      │ │    │
│  │ GET  /health               │                 │ │    │
│  │ POST /sniffer/events       │ (Alertas,      │ │    │
│  │ GET  /sniffer/status       │  Eventos,      │ │    │
│  │ GET  /dashboard/interfaces │  Métricas)     │ │    │
│  │ (Bearer Token obrigatório) └──────────────────┘ │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
         ▲           ▲           ▲
         │           │           │ HTTPS + Bearer Token
         │           │           │ (SENSOR_API_TOKEN)
         │           │           │
         │ Requisições continuadas (POST /sniffer/events)
         │ a cada 10-30 segundos
         │
┌────────┴──────────────────────────┐
│    🖥️ PC/VM LOCAL (Este PC)       │
│  ┌──────────────────────────────┐ │
│  │ Docker Sniffer               │ │
│  │ ┌──────────────────────────┐ │ │
│  │ │ Interface eth0 (WAN)     │ │ │
│  │ │ Interface eth1 (LAN)     │ │ │
│  │ │ Interface eth2 (LAN)     │ │ │
│  │ │ Interface wlan0 (WLAN)   │ │ │
│  │ └──────────────────────────┘ │ │
│  │ Captura → Analisa → Envia    │ │
│  │ para Backend Online          │ │
│  └──────────────────────────────┘ │
└────────────────────────────────────┘
```

---

## 📋 4 Etapas Principais

### 1️⃣ Backend no Render
- [x] Já hospedado e acessível
- [ ] Validar saúde e rotas
- **URL Final:** `https://projeto-ids-ips.onrender.com`

### 2️⃣ Frontend no Vercel
- [x] Já hospedado e acessível
- [ ] Validar carregamento e login
- **URL Final:** `https://projeto-ids-ips.vercel.app`

### 3️⃣ Sniffer Local (15 min)
- [ ] Copiar `.env.sniffer.example` → `.env.sniffer`
- [ ] Editar com URL do backend + token
- [ ] Configurar interfaces (eth0, eth1, etc)
- [ ] Rodar: `docker compose -f docker-compose.sniffer.yml up -d`
- **Status:** Container rodando localmente

### 4️⃣ Validar (5 min)
- [ ] Frontend carrega e faz login
- [ ] Dashboard mostra interfaces do PC
- [ ] Sniffer está "connected" no backend
- [ ] Alertas chegando em tempo real

---

## 🔑 Valores Críticos

| Item | Valor | Onde Usar |
|---|---|---|
| **BACKEND_URL** | `https://projeto-ids-ips.onrender.com` | `.env.sniffer`, `frontend/.env.production` |
| **SENSOR_API_TOKEN** | `rnd_NI58G0zUFnPDd88wjSYPfCnCBfZO` | `.env.sniffer`, Render env vars |
| **FRONTEND_ORIGINS** | `*.vercel.app` | `backend/config.py`, Render env vars |
| **VITE_API_URL** | Backend URL | `frontend/.env.production` |

---

## ✅ Pré-requisitos Atendidos?

- [ ] Código limpo em GitHub (`main` branch)
- [ ] `render.yaml` existe e válido
- [ ] `docker-compose.sniffer.yml` existe
- [ ] `.env.sniffer.example` existe
- [ ] `backend/requirements.txt` tem todas dependências
- [ ] `frontend/vite.config.ts` está OK
- [ ] Contas criadas: GitHub, Render, Vercel

---

## 🚀 Comandos Rápidos

```bash
# ===== FASE 1: Backend =====
# Ir para Render Dashboard, conectar GitHub, deixar deploy automático

# ===== FASE 2: Frontend =====
# Ir para Vercel Dashboard, import project, deixar deploy automático

# ===== FASE 3: Sniffer Local =====
cp .env.sniffer.example .env.sniffer
nano .env.sniffer  # Editar Backend URL + Token + Interfaces

docker compose -f docker-compose.sniffer.yml up -d --build

# ===== VALIDAÇÃO =====
./validate_deployment.sh

# ===== MONITORAMENTO =====
docker compose -f docker-compose.sniffer.yml logs -f sniffer
curl -H "Authorization: Bearer seu_token" \
  https://seu-backend.onrender.com/sniffer/status | jq .
```

---

## 📊 Expected Status

**Quando tudo estiver correto:**

```
🟢 https://projeto-ids-ips.vercel.app       [Frontend OK]
🟢 https://projeto-ids-ips.onrender.com/health  [Backend OK]
🟢 Sniffer container rodando                [Local OK]
🟢 Dashboard mostra interfaces: eth0, eth1, eth2, wlan0
🟢 Alertas aparecendo em tempo real
```

---

## ⚠️ Possíveis Erros

| Erro | Causa | Solução |
|---|---|---|
| CORS error no browser | `Access-Control-Allow-Origin` não inclui Vercel | Render env: `CORS_ALLOW_ORIGIN_REGEX=.*vercel.app` |
| Sniffer não conecta | Token inválido ou URL errada | Verificar `.env.sniffer` vs Render env vars |
| Interfaces vazias | Docker sem `--net host` | `docker-compose.sniffer.yml` deve ter `network_mode: host` |
| "Unauthorized" no sniffer status | Token expirado/errado | Regenerar token, usar mesmo em ambos |

---

## 📞 Documentos de Referência  

| Documento | Uso |
|---|---|
| `DEPLOYMENT_CLOUD_PLAN.md` | Plano completo detalhado |
| `DEPLOYMENT_STEP_BY_STEP.md` | Instruções passo-a-passo |
| `validate_deployment.sh` | Validar tudo com script |
| `DEPLOY_RENDER.md` | Deploy backend antigo (referência) |
| `.env.sniffer.example` | Template de configuração |

---

## 🎯 Timeline Estimado

- **Backend já hospedado:** concluído
- **Frontend já hospedado:** concluído  
- **Sniffer Local:** 10 min (docker + config)
- **Testes:** 5-10 min (validation + checks)

**Total restante:** ~15-25 minutos ⏱️

---

## ✨ Próximas Ações

Imediatamente após o deployment estar online:

1. **Sniffer:** Criar `.env.sniffer` e iniciar o container local
2. **Validação:** Rodar `validate_deployment.sh`
3. **Monitoramento:** Confirmar interfaces no dashboard
4. **Backups:** Conferir backup automático do PostgreSQL Render
5. **Logs Centralizados:** Integrar com serviço de logging

---

**Status:** 🟡 **BACKEND E FRONTEND ONLINE, FALTA SNIFFER**  
**Próxima ação:** Configurar o sniffer local e validar integração  
**Última atualização:** 2026-04-27
