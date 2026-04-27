# 📚 DOCUMENTAÇÃO DE DEPLOYMENT - GUIA DE NAVEGAÇÃO

## Objetivo do Projeto
Levar o projeto **online e funcionando**:
- ☁️ Backend + Database no **Render**
- 🌐 Frontend no **Vercel** 
- 🔍 Sniffer rodando **localmente** (este PC) enviando dados para a nuvem
- 📊 **Tudo integrado e monitorável** via dashboard web

---

## 📖 Documentos Disponíveis

### 1. **DEPLOYMENT_SUMMARY.md** ⭐ **COMECE AQUI**
**Para:** Visão geral e entender o que fazer  
**Conteúdo:**
- Visão arquitetura final
- 4 etapas principais
- Valores críticos
- Comandos rápidos
- Timeline estimada

**Tempo de leitura:** 5 min

---

### 2. **DEPLOYMENT_STEP_BY_STEP.md** 🚀 **INSTRUÇÕES DETALHADAS**
**Para:** Executar passo-a-passo  
**Conteúdo:**
- Etapa 1: Preparar Backend (10 min)
- Etapa 2: Deploy Backend no Render (15 min)
- Etapa 3: Preparar Frontend (5 min)
- Etapa 4: Deploy Frontend no Vercel (10 min)
- Etapa 5: Configurar Sniffer Local (15 min)
- Etapa 6: Validação Final (5 min)
- Troubleshooting rápido

**Tempo total:** ~60 min  
**Use este quando estiver pronto para começar o deployment real**

---

### 3. **DEPLOYMENT_CLOUD_PLAN.md** 📋 **REFE

RÊNCIA COMPLETA**
**Para:** Entender todos os detalhes  
**Conteúdo:**
- Arquitetura visual completa
- 7 fases detalhadas
- Endpoints de integração
- URLs finais
- Troubleshooting avançado

**Tempo de leitura:** 15 min  
**Use quando tiver dúvidas específicas**

---

### 4. **check_before_deployment.sh** ✅ **VALIDAÇÃO PRÉ-VOO**
**Para:** Verificar se tudo está pronto antes de começar  
**Comando:**
```bash
bash check_before_deployment.sh
```
**O que valida:**
- Git repository OK
- Backend estrutura OK
- Frontend estrutura OK
- Docker instalado
- Render.yaml válido
- Alembic configurado
- Arquivos críticos existem

**Resultado:** 🟢 Verde = Pronto | 🔴 Vermelho = Corrigir antes

---

### 5. **validate_deployment.sh** 🔍 **VALIDAÇÃO PÓS-DEPLOY**
**Para:** Validar após deployment estar online  
**Comando:**
```bash
chmod +x validate_deployment.sh
./validate_deployment.sh
```
**O que verifica:**
- Backend Render online
- Frontend Vercel online
- Autenticação Sniffer funcionando
- Container Sniffer rodando
- Comunicação Sniffer → Backend

**Resultado:** 🟢 Verde = Tudo OK | 🔴 Vermelho = Há problema

---

## 🎯 Como Usar Esta Documentação

### Cenário 1: Primeira Vez (Iniciante)
1. Ler: **DEPLOYMENT_SUMMARY.md** (5 min)
2. Executar: **check_before_deployment.sh** (2 min)
3. Se OK → Ler: **DEPLOYMENT_STEP_BY_STEP.md** (5 min)
4. Executar: Seguir as etapas do Step-by-Step
5. Após online → Executar: **validate_deployment.sh** (2 min)

**Tempo total:** ~2 horas (incluindo upload + build)

---

### Cenário 2: Já com Experiência
1. Ler rápido: **DEPLOYMENT_SUMMARY.md** (3 min)
2. Executar diretamente os comandos do **DEPLOYMENT_STEP_BY_STEP.md**
3. Use **DEPLOYMENT_CLOUD_PLAN.md** como referência se tiver dúvidas

**Tempo total:** ~45 min

---

### Cenário 3: Troubleshooting
1. Se erro → Abrir **DEPLOYMENT_STEP_BY_STEP.md** seção "Troubleshooting"
2. Se ainda não resolvido → Ver **DEPLOYMENT_CLOUD_PLAN.md** seção "Troubleshooting"
3. Se problema local → Executar **validate_deployment.sh** para diagnóstico

---

## 🗂️ Arquivos de Configuração

| Arquivo | Descrição | Criar/Editar |
|---|---|---|
| `.env.sniffer` | Config do Sniffer (backend URL, token, interfaces) | Criar baseado em `.env.sniffer.example` |
| `frontend/.env.production` | Config Frontend para Vercel | Editar |
| `Render env vars` | Variáveis no dashboard Render | Editar no dashboard |
| `docker-compose.sniffer.yml` | Docker compose para sniffer local | Já existe |
| `render.yaml` | Config automatico do Render | Já existe |

---

## 🔑 Valores Críticos para Guardar

Após começar o deployment, salve estes valores em lugar seguro:

```yaml
Render Backend:
  URL: https://seu-backend.onrender.com
  Database URL: postgres://... (auto-gerado)
  SENSOR_API_TOKEN: seu_token_super_seguro

Vercel Frontend:
  URL: https://seu-projeto.vercel.app
  
Local Sniffer:
  Token: seu_token_super_seguro
  Interfaces: eth0,eth1,eth2,wlan0
  Status URL: https://seu-backend.onrender.com/sniffer/status
```

---

## 📅 Checklist de Progresso

- [ ] Ler DEPLOYMENT_SUMMARY.md
- [ ] Executar check_before_deployment.sh
- [ ] Completar Etapa 1 (Backend prep)
- [ ] Completar Etapa 2 (Backend Render deploy)
- [ ] Completar Etapa 3 (Frontend prep)
- [ ] Completar Etapa 4 (Frontend Vercel deploy)
- [ ] Completar Etapa 5 (Sniffer local config)
- [ ] Completar Etapa 6 (Validações)
- [ ] Executar validate_deployment.sh
- [ ] Acessar frontend e fazer login
- [ ] Verificar interfaces no dashboard
- [ ] 🎉 **TUDO ONLINE!**

---

## ❓ FAQ Rápido

**P: Por onde começo?**
R: Leia `DEPLOYMENT_SUMMARY.md` (5 min), depois execute `check_before_deployment.sh`

**P: Quanto tempo leva?**
R: ~1 hora se tudo bem. +30 min se tiver erros.

**P: Preciso editar código?**
R: Mínimo. Só configuração (.env, URLs, tokens)

**P: E se der erro no meio?**
R: Consulte "Troubleshooting" em DEPLOYMENT_STEP_BY_STEP.md

**P: Render/Vercel são pagos?**
R: Não! Têm tier grátis com limite, mas é ok para o projeto.

**P: Preciso de mais um PC para o sniffer?**
R: Não! O sniffer roda neste PC local (Docker).

---

## 🚀 Próximos Passos (Depois que Estiver Online)

1. Setup de domínio próprio
2. Configurar SMTP para emails
3. CI/CD automático com GitHub Actions
4. Backups automáticos
5. Monitoramento de uptime
6. ~~Ficar rico~~ 😄

---

## 📞 Referência Rápida

| Documento | Para | Comando |
|---|---|---|
| Começar | Explicação | `cat DEPLOYMENT_SUMMARY.md` |
| Validar antes | Checklist | `bash check_before_deployment.sh` |
| Fazer deploy | Passo-a-passo | seguir DEPLOYMENT_STEP_BY_STEP.md |
| Consultar | Detalhes | `cat DEPLOYMENT_CLOUD_PLAN.md` |
| Validar depois | Testes pós-deploy | `bash validate_deployment.sh` |

---

## 🎓 Estrutura de Aprendizado

```
INICIANTE (Leia na ordem)
¹ DEPLOYMENT_SUMMARY.md
² DEPLOYMENT_STEP_BY_STEP.md
³ execute check_before_deployment.sh
⁴ execute validate_deployment.sh

EXPERIENTE (Direto)
¹ Skip para DEPLOYMENT_STEP_BY_STEP.md, fase por fase
² Use DEPLOYMENT_CLOUD_PLAN.md como referência

TROUBLESHOOTING
¹ DEPLOYMENT_STEP_BY_STEP.md → Troubleshooting
² DEPLOYMENT_CLOUD_PLAN.md → Troubleshooting
³ validate_deployment.sh → Diagnóstico
```

---

## ✨ Agora Você Tem Tudo Para...

✅ Entender a arquitetura  
✅ Preparar o projeto  
✅ Fazer deploy no Render  
✅ Deploy no Vercel  
✅ Conectar Sniffer local  
✅ Validar tudo funcionando  
✅ **LEVAR TUDO PARA A CLOUD!** ☁️

---

**Última atualização:** 2026-04-27  
**Status:** 🟢 Pronto para usar  
**Tempo total:** 1-2 horas
