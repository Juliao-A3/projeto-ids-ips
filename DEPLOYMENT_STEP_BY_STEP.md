# ⚡ DEPLOYMENT RÁPIDO - RENDER + VERCEL + SNIFFER LOCAL

## 🎯 Objetivo Final Hoje
- ✅ Backend rodando em Render (Online)
- ✅ Frontend rodando em Vercel (Online)  
- ✅ Sniffer local conectado e enviando dados
- ✅ Tudo acessível e funcionando

---

## ✅ ETAPA 1: BACKEND JÁ PUBLICADO

O backend já está no Render. Só confirme:

- [ ] `https://seu-backend.onrender.com/health` responde 200
- [ ] `https://seu-backend.onrender.com/docs` abre corretamente
- [ ] `CORS_ALLOW_ORIGIN_REGEX` aceita `*.vercel.app`
### 1.1 Verificar `render.yaml`

```bash
cat render.yaml
```

**Deve conter:**
```yaml
services:
  - name: db
    type: postgres
  - name: backend
    type: web
    buildCommand: "..."
    startCommand: "..."
```

### 1.2 Revisar `backend/config.py`

```bash
nano backend/config.py
```

**Verificar:**
- [ ] `CORS_ALLOW_ORIGIN_REGEX` inclui `*.vercel.app`
- [ ] `FRONTEND_ORIGINS` correto
- [ ] Suporte a variáveis de ambiente

### 1.3 Confirmar `backend/requirements.txt`

```bash
grep -E "fastapi|pydantic|sqlalchemy|alembic" backend/requirements.txt
```

### 1.4 Teste Local (Opcional)

```bash
docker compose up -d db
sleep 5
docker compose up backend
# Testar em http://localhost:8000/docs
```

---

## ✅ ETAPA 2: FRONTEND JÁ PUBLICADO

O frontend já está na Vercel. Só confirme:

- [ ] A URL pública carrega sem erro
- [ ] O login abre o backend correto
- [ ] `VITE_API_URL` aponta para o Render

### 2.1 Acessar Vercel Dashboard

```
https://vercel.com/dashboard
```

- [ ] Login com conta GitHub

### 2.2 Confirmar Project Settings

- [ ] Root Directory aponta para `frontend`
- [ ] Framework Preset está em Vite
- [ ] Build Command é `npm run build`
- [ ] Output Directory é `dist`

### 2.3 Conferir Variável de Ambiente

```
VITE_API_URL=https://projeto-ids-ips.onrender.com
```

### 2.4 Verificar Deploy

- [ ] URL pública abre sem erro
- [ ] Requisições no browser apontam para o backend do Render

### 2.5 Testar Frontend Online

```bash
curl https://projeto-ids-ips.vercel.app/ | head -20
```

**✅ Resultado esperado:** HTML com `<head>` e `<body>`

---

## 🚀 ETAPA 3: PREPARAR FRONTEND (se precisar corrigir)

### 3.1 Verificar `frontend/vite.config.ts`

```bash
cat frontend/vite.config.ts | grep -A5 "build\|outDir"
```

### 3.2 Criar ou Editar `frontend/.env.production`

```bash
nano frontend/.env.production
```

**Conteúdo:**
```
VITE_API_URL=https://seu-backend.onrender.com
VITE_ENV=production
```

### 3.3 Teste Local (Opcional)

```bash
cd frontend
npm install
npm run build
# Resultado em: frontend/dist/
```

### 3.4 Git Commit

```bash
git add frontend/
git commit -m "chore: configurar frontend para Vercel"
git push origin main
```

---

## 🚀 ETAPA 4: DEPLOY FRONTEND NO VERCEL (somente se houver ajuste)

### 4.1 Acessar Vercel Dashboard

```
https://vercel.com/dashboard
```

- [ ] Login com conta GitHub

### 4.2 Import Project

- [ ] **Add New → Project**
- [ ] **Import Git Repository**
- [ ] Selecionar `seu-usuario/projeto-ids-ips`

### 4.3 Configurar Build

**Project Settings:**
- Root Directory: `frontend`
- Framework Preset: **Vite**
- Build Command: `npm run build`
- Output Directory: `dist`

### 4.4 Variáveis de Ambiente

```
VITE_API_URL=https://seu-backend.onrender.com
```

### 4.5 Deploy

- [ ] Clicar **Deploy**
- Aguardar... (2-3 min)
- [ ] Get URL → `https://seu-projeto.vercel.app`

### 4.6 Testar Frontend Online

```bash
curl https://seu-projeto.vercel.app | head -20
```

**✅ Resultado esperado:** HTML com `<head>` e `<body>`

---

## 🚀 ETAPA 5: CONFIGURAR SNIFFER LOCAL (15 min)

### 5.1 Preparar `.env.sniffer`

```bash
cp .env.sniffer.example .env.sniffer
nano .env.sniffer
```

**Valores importantes:**
```ini
BACKEND_URL=https://projeto-ids-ips.onrender.com
SENSOR_API_TOKEN=rnd_NI58G0zUFnPDd88wjSYPfCnCBfZO
INTERFACES=eth0,eth1,eth2,wlan0
ZONE_MAP=eth0:wan,eth1:lan,eth2:lan,wlan0:wlan
SENSOR_NAME=Sniffer-Local-PC-$(hostname -s)
LOG_LEVEL=INFO
SEND_STATISTICS=true
STREAM_ALERTS=true
```

### 5.2 Listar Interfaces do PC

```bash
# Linux/Mac
ip link show          # Ou: ifconfig

# Windows (WSL)
ipconfig /all

# Docker
docker run --rm --net host alpine ip link show
```

**Exemplo de saída:**
```
1: lo: <LOOPBACK> ...
2: eth0: <BROADCAST,MULTICAST,UP> ...
3: eth1: <BROADCAST,MULTICAST,UP> ...
4: wlan0: <BROADCAST,MULTICAST,UP> ...
```

### 5.3 Editar INTERFACES no `.env.sniffer`

```bash
# Se seu PC tem eth0, eth1, eth2
INTERFACES=eth0,eth1,eth2

# Se tem apenas WiFi e Ethernet
INTERFACES=enp0s3,wlan0

# Docker internal (desenvolvimento)
INTERFACES=docker0,eth0
```

### 5.4 Criar docker-compose.sniffer.yml

**Já fornecido em:** `docker-compose.sniffer.yml`

Verificar se existe:
```bash
ls -la docker-compose.sniffer.yml
```

### 5.5 Iniciar Sniffer Local

```bash
# Parar qualquer instância anterior
docker compose -f docker-compose.sniffer.yml down 2>/dev/null || true

# Iniciar fresh
docker compose -f docker-compose.sniffer.yml up -d --build

# Aguardar container inicializar
sleep 5

# Verificar status
docker compose -f docker-compose.sniffer.yml ps
```

**✅ Deve mostrar:**
```
NAME                         STATUS
ids-ips-sniffer-local        Up X seconds
```

### 5.6 Validar Conexão Sniffer → Backend

```bash
# Testar dentro do container
docker exec ids-ips-sniffer-local \
  curl -H "Authorization: Bearer seu_token" \
  https://seu-backend.onrender.com/sniffer/status

# Ou testar de fora
curl -H "Authorization: Bearer seu_token" \
  https://seu-backend.onrender.com/sniffer/status | jq .
```

**✅ Resultado esperado:**
```json
{
  "status": "running",
  "sensor_name": "Sniffer-Local-PC-...",
  "interfaces": ["eth0", "eth1", ...],
  "packets_captured": 1234
}
```

---

## ✅ ETAPA 6: VALIDAÇÃO FINAL (5 min)

### 6.1 Rodar Script de Validação

```bash
chmod +x validate_deployment.sh
./validate_deployment.sh
```

### 6.2 Checklist de Acesso

```bash
# Frontend
curl https://seu-projeto.vercel.app -I

# Backend docs
curl https://seu-backend.onrender.com/docs -I

# API test
curl https://seu-backend.onrender.com/health

# Sniffer status
curl -H "Authorization: Bearer seu_token" \
  https://seu-backend.onrender.com/sniffer/status
```

### 6.3 Verificar Logs

```bash
# Backend Render
# → https://dashboard.render.com → seu-backend → Logs

# Frontend Vercel
# → https://vercel.com/seu-projeto → Deployments → Logs

# Sniffer Local
docker compose -f docker-compose.sniffer.yml logs -f sniffer
```

### 6.4 Testar na Cloud

**Abrir navegador:**

1. https://seu-projeto.vercel.app
2. Fazer login
3. Ir para Dashboard
4. Verificar se interfaces do PC local aparecem
5. Monitorar alertas em tempo real

---

## 🎯 Checklist Final

- [ ] **Backend Render online** - `https://seu-backend.onrender.com/health` = 200
- [ ] **Frontend Vercel online** - `https://seu-projeto.vercel.app` carrega com sucesso
- [ ] **Sniffer local rodando** - `docker ps` mostra container UP
- [ ] **Sniffer conectado** - `/sniffer/status` retorna dados
- [ ] **Dashboard mostra interfaces** - Todas as interfaces do PC aparecem
- [ ] **Autenticação funciona** - Login/logout OK
- [ ] **Alertas chegando** - Dashboard mostra dados em tempo real
- [ ] **Logs limpos** - Sem erros críticos

---

## 🆘 Troubleshooting Rápido

| Problema | Solução |
|---|---|
| Backend não faz deploy | Verificar `render.yaml` syntax; revisar logs no Render |
| Frontend "Cannot find module" | Verificar `VITE_API_URL`; npm install em `frontend/` |
| Sniffer não conecta | Checar token em `SENSOR_API_TOKEN`; testar curl manualmente |
| CORS error no Dashboard | Backend precisa de `CORS_ALLOW_ORIGIN_REGEX=.*vercel.app` |
| Interfaces não aparecem | Sniffer precisa ser iniciado com `--net host` em Docker |
| Token inválido | Regenerar `SENSOR_API_TOKEN` em ambos lugares (Render env + .env.sniffer) |

---

## 📞 Referências Rápidas

```bash
# Ver status de tudo
./validate_deployment.sh

# Reiniciar sniffer
docker compose -f docker-compose.sniffer.yml restart sniffer

# Ver logs de sniffer
docker compose -f docker-compose.sniffer.yml logs --tail=50 sniffer

# Ver logs de backend (Render)
# https://dashboard.render.com → seu-backend → Logs

# Reruns no Render
# https://dashboard.render.com → seu-backend → Manual Deploy → Redeploy
```

---

## 🎓 Próximos Passos (Depois)

1. Adicionar domínio próprio (opcional)
2. Configurar SMTP para emails
3. Setup de backups automáticos
4. Monitoramento e alertas de uptime
5. CI/CD automático com GitHub Actions

---

**Tempo estimado:** 1 hora  
**Dificuldade:** Média  
**Pré-requisitos:** GitHub, conta Render (grátis), conta Vercel (grátis)

Boa sorte! 🚀
