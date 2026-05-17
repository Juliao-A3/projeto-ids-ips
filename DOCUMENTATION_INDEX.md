# 📚 Índice da Documentação - Relatórios e Notificações

## 🎯 Chegou aqui? Comece por aqui!

Escolha o seu perfil:

### 👨‍💻 **Desenvolvedor** (Quer entender o código)
1. ⭐ Leia: [Referência Rápida](./REPORTS_NOTIFICATIONS_QUICK_REFERENCE.md)
2. 📖 Leia: [Guia Técnico - Arquitetura](./REPORTS_NOTIFICATIONS_ARCHITECTURE.md)
3. 🔧 Leia: [Guia Completo - APIs](./REPORTS_NOTIFICATIONS_GUIDE.md)
4. 💻 Browse: [Exemplos - Python/JavaScript](./REPORTS_NOTIFICATIONS_EXAMPLES.md)

### 👨‍🔧 **DevOps/Sistema** (Quer configurar e manter)
1. ⭐ Leia: [Referência Rápida](./REPORTS_NOTIFICATIONS_QUICK_REFERENCE.md)
2. 🔧 Siga: Seção "Guia de Configuração" no [Guia Completo](./REPORTS_NOTIFICATIONS_GUIDE.md)
3. 🆘 Troubleshooting: Uma das seções nos 4 documentos
4. 🧪 Teste: Scripts de teste em [Exemplos](./REPORTS_NOTIFICATIONS_EXAMPLES.md)

### 👨‍💼 **Gerente/Analista** (Quer usar o sistema)
1. ⭐ Leia: Seções iniciais da [Referência Rápida](./REPORTS_NOTIFICATIONS_QUICK_REFERENCE.md)
2. 🎯 Entender: [O que são "Triggers"?](./REPORTS_NOTIFICATIONS_GUIDE.md#sistema-de-triggers)
3. 📊 Como gerar: [Relatório PDF](./REPORTS_NOTIFICATIONS_GUIDE.md#4-get-reportsexportpdf--)
4. 🔔 Como receber: Alertas por [Email](./REPORTS_NOTIFICATIONS_GUIDE.md#1-email-smtp), [Telegram](./REPORTS_NOTIFICATIONS_GUIDE.md#2-telegram-bot), [Teams](./REPORTS_NOTIFICATIONS_GUIDE.md#3-microsoft-teams)

---

## 📄 Estrutura dos 4 Documentos

### 1️⃣ REPORTS_NOTIFICATIONS_GUIDE.md
**Tipo:** Documentação Técnica Completa  
**Tamanho:** ~10.000 palavras  
**Ideal para:** Entender tudo em detalhes

**Seções:**
- ✅ Visão Geral
- ✅ Sistema de Relatórios (endpoints, modelos, PDF)
- ✅ Sistema de Notificações (email, telegram, teams)
- ✅ Fluxo de Notificação
- ✅ Frontend Components
- ✅ Guia de Configuração (passo-a-passo)
- ✅ Segurança
- ✅ Troubleshooting
- ✅ API Resumida
- ✅ Métricas
- ✅ Melhorias Futuras

**Quando consultar:**
- "Como funciona a geração de PDFs?"
- "Qual é a diferença entre detalhado e resumido?"
- "Como configurar a senha do Gmail?"
- "Quais são os triggers de notificação?"

---

### 2️⃣ REPORTS_NOTIFICATIONS_EXAMPLES.md
**Tipo:** Exemplos Práticos de Código  
**Tamanho:** ~7.000 palavras  
**Ideal para:** Implementar e testar

**Seções:**
- ✅ Exemplos com cURL (11 exemplos)
- ✅ Exemplos em Python (7 scripts)
- ✅ Exemplos em TypeScript/React (3 componentes)
- ✅ Casos de Uso (4 cenários do mundo real)
- ✅ Script Completo de Setup
- ✅ Checklist de Implementação

**Quando consultar:**
- "Como faço o download de um PDF via Python?"
- "Como testo se o email está funcionando?"
- "Qual é o código para um componente React?"
- "Como agendar relatórios automáticos?"

---

### 3️⃣ REPORTS_NOTIFICATIONS_ARCHITECTURE.md
**Tipo:** Diagramas, Fluxogramas, Arquitetura  
**Tamanho:** ~5.000 palavras  
**Ideal para:** Visualizar e arquitetar

**Seções:**
- ✅ Arquitetura do Sistema (diagrama ASCII)
- ✅ Fluxo de Geração de Relatório PDF
- ✅ Fluxo de Notificação de Alerta
- ✅ Estrutura de Dados
- ✅ Layout do PDF (mockup)
- ✅ Fluxo de Segurança de Credenciais
- ✅ Performance e Escalabilidade
- ✅ Testes Recomendados
- ✅ Checklist de Verificação

**Quando consultar:**
- "Como funciona o sistema no geral?"
- "Qual é o fluxo de um alerta?"
- "Qual é a estrutura de dados do relatório?"
- "Devo otimizar algo?"

---

### 4️⃣ REPORTS_NOTIFICATIONS_QUICK_REFERENCE.md
**Tipo:** Referência Rápida / Cheat Sheet  
**Tamanho:** ~2.500 palavras  
**Ideal para:** Consulta rápida (aba aberta)

**Seções:**
- ✅ Início Rápido (5 min)
- ✅ Endpoints Principais
- ✅ Parâmetros de Filtros
- ✅ Estruturas de Resposta (JSON)
- ✅ Configurações (Email, Telegram, Teams)
- ✅ Triggers
- ✅ Diagnóstico
- ✅ One-liners Python
- ✅ Permissões
- ✅ Erros Comuns & Soluções
- ✅ Limites
- ✅ Arquivos Importantes

**Quando consultar:**
- "Qual é a URL do endpoint de relatórios?"
- "Como configuro email rápido?"
- "Qual é o limite de alertas?"
- "O que significa 'ready: false'?"

---

## 🗂️ Mapa Mental da Funcionalidade

```
AEGIS Relatórios & Notificações
│
├─ RELATÓRIOS
│  ├─ Endpoints
│  │  ├─ /reports/summary → Métricas
│  │  ├─ /reports/incidents → Lista
│  │  ├─ /reports/attack-volume → Gráfico
│  │  └─ /reports/export/pdf → 📥 Download
│  │
│  ├─ Filtros
│  │  ├─ period: 24h, 7d, 30d
│  │  ├─ severity: all, critica, alta, media, baixa
│  │  └─ tipo: detalhado, resumido
│  │
│  ├─ Relatório PDF
│  │  ├─ Design: A4, múltiplas páginas
│  │  ├─ Conteúdo: Métricas, gráficos, tabelas
│  │  └─ Gerado: ReportLab + Matplotlib
│  │
│  └─ Frontend
│     ├─ Componente: RelatorioManagement
│     └─ Hook: useReports
│
├─ NOTIFICAÇÕES
│  ├─ Canais
│  │  ├─ Email (SMTP)
│  │  │  ├─ Providers: Gmail, Outlook, Custom
│  │  │  ├─ Auth: App Password / Senha
│  │  │  └─ Modo: Síncrono
│  │  │
│  │  ├─ Telegram (Bot API)
│  │  │  ├─ Config: Bot Token + Chat ID
│  │  │  └─ Modo: Assíncrono
│  │  │
│  │  └─ Teams (Webhook)
│  │     ├─ Config: Webhook URL
│  │     └─ Modo: Assíncrono
│  │
│  ├─ Triggers (Filtros de Severidade)
│  │  ├─ trigger_critical
│  │  ├─ trigger_high
│  │  └─ trigger_medium
│  │
│  ├─ Configuração
│  │  ├─ GET /notifications/config
│  │  ├─ PUT /notifications/config
│  │  └─ GET /notifications/diagnostics
│  │
│  ├─ Teste
│  │  ├─ POST /notifications/test/email
│  │  ├─ POST /notifications/test/telegram
│  │  └─ POST /notifications/test/teams
│  │
│  ├─ Service
│  │  ├─ notification_service.py
│  │  ├─ notification_routes.py
│  │  └─ models.py → NotificationConfig
│  │
│  └─ Frontend
│     ├─ Componente: NotificationsManagement
│     └─ Hook: useNotifications
│
└─ Database
   ├─ NotificationConfig (configurações)
   ├─ LogEvento (eventos/alertas)
   └─ IpsBloqueados (IPs bloqueados)
```

---

## 🎓 Tópicos por Dificuldade

### 🟢 Iniciante
- Como gerar um PDF simples
- Como configurar email com Gmail
- Como verificar o status dos canais

**Documentos:**
- [Guia Completo - Configuração](./REPORTS_NOTIFICATIONS_GUIDE.md#guia-de-configuração)
- [Referência Rápida - Setup](./REPORTS_NOTIFICATIONS_QUICK_REFERENCE.md#-início-rápido-5-min)

### 🟡 Intermediário
- Entender triggers e filtros
- Implementar scripts de relatórios automáticos
- Debugar problemas de notificação

**Documentos:**
- [Exemplos - Python](./REPORTS_NOTIFICATIONS_EXAMPLES.md#-exemplos-em-python)
- [Guia Completo - Sistema de Triggers](./REPORTS_NOTIFICATIONS_GUIDE.md#sistema-de-triggers)
- [Referência Rápida - Erros](./REPORTS_NOTIFICATIONS_QUICK_REFERENCE.md#-erros-comuns)

### 🔴 Avançado
- Otimizar performance (cache, connection pools)
- Implementar retry logic e backoff
- Estender sistema com novos canais (Slack, Discord)
- Criptografar credenciais na DB

**Documentos:**
- [Arquitetura - Performance](./REPORTS_NOTIFICATIONS_ARCHITECTURE.md#-performance-e-escalabilidade)
- [Exemplos - Casos Avançados](./REPORTS_NOTIFICATIONS_EXAMPLES.md#-casos-de-uso)
- [Guia Completo - Melhorias Futuras](./REPORTS_NOTIFICATIONS_GUIDE.md#-melhorias-futuras-sugeridas)

---

## 🔍 Busca por Palavra-chave

**"Como..."**
- ...gerar PDF? → [Guia § 1.4](./REPORTS_NOTIFICATIONS_GUIDE.md#4-get-reportsexportpdf--)
- ...configurar email? → [Guia § 5.1](./REPORTS_NOTIFICATIONS_GUIDE.md#passo-1-gmail-com-2fa)
- ...ativar telegram? → [Guia § 5.2](./REPORTS_NOTIFICATIONS_GUIDE.md#passo-2-telegram)
- ...testar notificações? → [Exemplos § 10](./REPORTS_NOTIFICATIONS_EXAMPLES.md#1️⏸️-1️-testar-envio-de-email)
- ...agendar relatórios? → [Exemplos § 3](./REPORTS_NOTIFICATIONS_EXAMPLES.md#3-gerar-relatório-automático-diário)

**"Qual é..."**
- ...a URL do endpoint? → [Referência § Endpoints](./REPORTS_NOTIFICATIONS_QUICK_REFERENCE.md#-endpoints-principais)
- ...o limite de alertas? → [Referência § Limites](./REPORTS_NOTIFICATIONS_QUICK_REFERENCE.md#-limites)
- ...a estrutura de dados? → [Arquitetura § 3](./REPORTS_NOTIFICATIONS_ARCHITECTURE.md#-estrutura-de-dados-do-relatório)

**"O que é..."**
- ...um trigger? → [Guia § 4.8](./REPORTS_NOTIFICATIONS_GUIDE.md#sistema-de-triggers)
- ...truncagem? → [Guia § 1.1](./REPORTS_NOTIFICATIONS_GUIDE.md#limites-por-tipo)
- ...app password? → [Guia § 5.1](./REPORTS_NOTIFICATIONS_GUIDE.md#configuração-gmail-com-2fa)

---

## 📊 Quantidade de Conteúdo por Documento

| Documento | Palavras | Seções | Exemplos | Diagramas |
|-----------|----------|--------|----------|-----------|
| Guide | 10.000+ | 15+ | 5+ | 3+ |
| Examples | 7.000+ | 5 | 20+ | 0 |
| Architecture | 5.000+ | 8 | 0 | 10+ |
| Quick Ref | 2.500+ | 20 | 15+ | 0 |
| **Total** | **24.500+** | **48+** | **40+** | **13+** |

---

## 🎯 Roadmap De Leitura Recomendado

### Cenário 1: "Quero começar rápido" (30 min)
1. [Quick Reference - Início Rápido](./REPORTS_NOTIFICATIONS_QUICK_REFERENCE.md#-início-rápido-5-min) (5 min)
2. [Examples - cURL](./REPORTS_NOTIFICATIONS_EXAMPLES.md#-exemplos-com-curl) (10 min)
3. [Guide - Configuração](./REPORTS_NOTIFICATIONS_GUIDE.md#guia-de-configuração) (15 min)

### Cenário 2: "Quero documentação completa" (2 horas)
1. [Quick Reference](./REPORTS_NOTIFICATIONS_QUICK_REFERENCE.md) (15 min)
2. [Architecture](./REPORTS_NOTIFICATIONS_ARCHITECTURE.md) (30 min)
3. [Guide](./REPORTS_NOTIFICATIONS_GUIDE.md) (60 min)
4. [Examples](./REPORTS_NOTIFICATIONS_EXAMPLES.md) (15 min)

### Cenário 3: "Quero implementar código" (1.5 horas)
1. [Quick Reference - APIs](./REPORTS_NOTIFICATIONS_QUICK_REFERENCE.md#-endpoints-principais) (5 min)
2. [Architecture - Estrutura](./REPORTS_NOTIFICATIONS_ARCHITECTURE.md#-estrutura-de-dados-do-relatório) (10 min)
3. [Examples - Setup](./REPORTS_NOTIFICATIONS_EXAMPLES.md#setup-inicial) (5 min)
4. [Examples - Python/JS](./REPORTS_NOTIFICATIONS_EXAMPLES.md#-exemplos-em-python) (45 min)
5. [Examples - Casos de Uso](./REPORTS_NOTIFICATIONS_EXAMPLES.md#-casos-de-uso) (30 min)

### Cenário 4: "Preciso debugar um problema" (20 min)
1. [Quick Reference - Erros](./REPORTS_NOTIFICATIONS_QUICK_REFERENCE.md#-erros-comuns) (5 min)
2. [Guide - Troubleshooting](./REPORTS_NOTIFICATIONS_GUIDE.md#⑦-troubleshooting) (10 min)
3. [Architecture - Diagnóstico](./REPORTS_NOTIFICATIONS_ARCHITECTURE.md) (5 min)

---

## 🔗 Links Diretos aos Tópicos Principais

### Endpoints da API
- [Todos os endpoints](./REPORTS_NOTIFICATIONS_GUIDE.md#endpoints-de-notificações)
- [GET /reports/summary](./REPORTS_NOTIFICATIONS_GUIDE.md#1-get-reportssummary)
- [GET /reports/export/pdf](./REPORTS_NOTIFICATIONS_GUIDE.md#4-get-reportsexportpdf--)
- [GET /notifications/config](./REPORTS_NOTIFICATIONS_GUIDE.md#1-get-notificationsconfig)
- [GET /notifications/diagnostics](./REPORTS_NOTIFICATIONS_GUIDE.md#3-get-notificationsdiagnostics)

### Configuração de Canais
- [Email SMTP](./REPORTS_NOTIFICATIONS_GUIDE.md#1-email-smtp)
- [Telegram Bot](./REPORTS_NOTIFICATIONS_GUIDE.md#2-telegram-bot)
- [Teams Webhook](./REPORTS_NOTIFICATIONS_GUIDE.md#3-microsoft-teams)

### Exemplos de Código
- [Python - Setup email](./REPORTS_NOTIFICATIONS_EXAMPLES.md#4-configurar-notificações-por-email)
- [Python - Gerar PDF](./REPORTS_NOTIFICATIONS_EXAMPLES.md#1-gerar-relatório-pdf-programaticamente)
- [JavaScript - Componente de Download](./REPORTS_NOTIFICATIONS_EXAMPLES.md#2-componente-de-download-de-relatório)
- [cURL - Todos os exemplos](./REPORTS_NOTIFICATIONS_EXAMPLES.md#-exemplos-com-curl)

### Troubleshooting
- [Email não é enviado](./REPORTS_NOTIFICATIONS_QUICK_REFERENCE.md#-email-não-é-enviado)
- [Telegram não funciona](./REPORTS_NOTIFICATIONS_QUICK_REFERENCE.md#-telegram-não-funciona)
- [PDF não gera](./REPORTS_NOTIFICATIONS_QUICK_REFERENCE.md#-pdf-não-gera)
- [Notificações não chegam](./REPORTS_NOTIFICATIONS_QUICK_REFERENCE.md#-notificações-não-chegam)

---

## 📞 Ainda Tem Dúvidas?

**Não achou no índice?**
- Use Ctrl+F em cada documento para buscar palavras-chave
- Leia a seção "Perguntas Frequentes" no final do [Guia Completo](./REPORTS_NOTIFICATIONS_GUIDE.md)
- Verifique os [casos de uso](./REPORTS_NOTIFICATIONS_EXAMPLES.md#-casos-de-uso) para cenários similares

---

## ✅ Checklist - Antes de Começar

- [ ] Li a [Referência Rápida](./REPORTS_NOTIFICATIONS_QUICK_REFERENCE.md)
- [ ] Escolhi meu documento principal (Guide, Examples, Architecture)
- [ ] Tenho acesso ao servidor AEGIS
- [ ] Tenho credenciais do Gmail/Telegram/Teams (se configurar)
- [ ] Tenho JWT token para APIs
- [ ] Testei GET /reports/summary com cURL

**Agora sim, pode começar!** 🚀

---

**Última atualização:** 13 de Abril de 2026  
**Versão:** 1.0  
**Documentação para:** AEGIS v4.0.2

