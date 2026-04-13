# 🔧 Correção - Alertas Não Sendo Salvos no BD

## 🐛 Problema Identificado

**Os alertas do sniffer NÃO estavam sendo registrados no banco de dados.**

### Análise

Encontrei que:

1. **Endpoint `/flow-input` não persistia dados**
   - O cicflowmeter faz POST para `/sniffer/flow-input` com cada fluxo
   - Esta rota recebia os dados, processava, mas **NÃO chamava a função de persistência**
   - Os alertas apareçiam no WebSocket (visíveis no frontend), mas não eram salvos

2. **A função `_persistir_alerta_async()` era usada apenas no callback**
   - Era chamada apenas em `_callback_fluxo()` via `asyncio.create_task()`
   - Mas `_callback_fluxo()` só é usada quando há listener ativo no sniffer_realtime.py
   - O cicflowmeter subprocess não chama esse callback

3. **Fluxo incorreto:**
   ```
   cicflowmeter → POST /flow-input
     ✓ Processa dados
     ✓ Envia para WebSocket
     ✓ Registra bloqueio de IP
     ✗ NÃO salva no BD ← PROBLEMA!
   ```

---

## ✅ Solução Aplicada

### Mudança 1: Adicionar Persistência ao `/flow-input`

**Arquivo:** `backend/sniffer_routes.py` (endpoint `/flow-input`)

```python
# ✅ FIXO: Persistir alerta de forma assíncrona
if pkt_info["tipo"] == "ataque":
    # ... bloqueio de IP ...
    
    # Agendar persistência no event loop
    try:
        loop = _get_loop()
        asyncio.run_coroutine_threadsafe(_persistir_alerta_async(pkt_info), loop)
    except Exception as persist_err:
        print(f"⚠ Erro ao agendar persistência: {persist_err}")
```

**Por quê este approach:**
- Usa `asyncio.run_coroutine_threadsafe()` para garantir que a coroutine roda no event loop correto
- O event loop FastAPI pode não ser o mesmo da thread que recebe o POST
- Não bloqueia a resposta HTTP

### Mudança 2: Melhorar `_persistir_alerta_async()` com Logging

Adicionei logs detalhados para rastrear cada etapa:

```python
[PERSIST] ✓ Sessão criada com sucesso
[PERSIST] ✓ LogEvento criado (ID: 123)
[PERSIST] ✓ Alerta salvo (ID: 456)
[PERSIST] ✓ Notificações processadas
```

**Debugging:**
- Valida tipo do fluxo
- Valida se `_session_factory` existe
- Mostra ID do evento/alerta criado
- Captura erros com contexto

---

## 📊 Verificação

Executar o script de verificação:

```bash
python check_alerts_db.py
```

Deverá mostrar:
```
[✓] Total de LogEventos na BD: 42
[✓] Total de Alertas na BD: 42
[✓] LogEventos nos últimos 5 minutos: 5
[✓] Alertas nos últimos 5 minutos: 5

[📋] Últimos 5 eventos:
  - 2026-04-13T18:30:45: 192.168.1.100 → 10.0.0.50 (TCP) [SeverID:alta]
  - ...
```

---

## 🔍 Fluxo Agora Correto

```
cicflowmeter → POST /flow-input
  ✓ Processa dados
  ✓ Envia para WebSocket
  ✓ Registra bloqueio de IP
  ✓ Agenda persistência (FIXO!)
    └─ _persistir_alerta_async()
      ├─ Cria LogEvento
      ├─ Cria Alerta
      ├─ Envia notificações
      └─ Salva na BD (FIXO!)
```

---

## 📋 Resumo das Mudanças

| Ficheiro | Linha | Mudança |
|----------|-------|---------|
| `sniffer_routes.py` | 450-495 | Adicionar chamada a `_persistir_alerta_async()` em `/flow-input` |
| `sniffer_routes.py` | 82-158 | Melhorar logging em `_persistir_alerta_async()` |
| `sniffer_routes.py` | 195 | Melhorar mensagens de erro |

---

## 🧪 Como Testar

1. **Iniciar backend:**
   ```bash
   cd /home/jgd/projeto-ids-ips
   sudo .venv/bin/python -m uvicorn backend.main:app --reload
   ```

2. **Iniciar sniffer via frontend ou cURL:**
   ```bash
   curl -X POST http://localhost:8000/sniffer/start \
     -H "Authorization: Bearer TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"interface": "eth0", "filtro": null, "bloquear": true}'
   ```

3. **Gerar tráfego de teste**

4. **Verificar BD:**
   ```bash
   python check_alerts_db.py
   ```

5. **Logs do backend:**
   ```
   [PERSIST] ✓ Sessão criada...
   [PERSIST] ✓ LogEvento criado...
   ```

---

## ⚠️ Notas Importantes

- A correção usa `asyncio.run_coroutine_threadsafe()` para garantir compatibilidade com threads
- O event loop é obtido via `_get_loop()` que cria um loop dedicado se necessário
- Erros de persistência não afetam a resposta HTTP (async background)
- Logs novos ajudam a debugar problemas futuros

---

## 🔮 Melhorias Futuras Sugeridas

1. **Adicionar retry logic** com backoff exponencial
2. **Implementar circuit breaker** para DB
3. **Meter fila de persistência** (Redis, RabbitMQ)
4. **Batch inserts** para melhor performance
5. **Métricas** de alertas salvos vs falhados

---

**Data:** 13 de Abril de 2026  
**Status:** ✅ RESOLVIDO  
**Prioridade:** 🔴 CRÍTICA (impedia salvamento de todos os alertas)

