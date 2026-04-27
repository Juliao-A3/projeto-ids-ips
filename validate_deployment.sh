#!/bin/bash

# ======================================================
# SCRIPT DE VALIDAÇÃO - DEPLOYMENT CLOUD
# ======================================================
# Valida se Backend (Render), Frontend (Vercel) e Sniffer Local estão online
# Uso: ./validate_deployment.sh

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# URLs (editar com seus valores)
BACKEND_URL="${BACKEND_URL:-https://seu-backend.onrender.com}"
FRONTEND_URL="${FRONTEND_URL:-https://seu-projeto.vercel.app}"
SENSOR_TOKEN="${SENSOR_API_TOKEN:-seu_token_super_seguro}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🔍 VALIDAÇÃO DE DEPLOYMENT CLOUD${NC}"
echo -e "${BLUE}========================================${NC}\n"

# ======================================================
# 1. TESTAR BACKEND RENDER
# ======================================================
echo -e "${YELLOW}[1/5] Testando Backend Render...${NC}"

if curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health" | grep -q "200"; then
    echo -e "${GREEN}✅ Backend está ONLINE${NC}"
    
    # Teste Swagger UI
    if curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/docs" | grep -q "200"; then
        echo -e "${GREEN}✅ API Docs (Swagger) está ONLINE${NC}"
    else
        echo -e "${RED}❌ API Docs não acessível${NC}"
    fi
    
    # Teste Database
    if curl -s "$BACKEND_URL/health" | grep -q "database.*ok\|postgresql.*connected"; then
        echo -e "${GREEN}✅ PostgreSQL está CONECTADO${NC}"
    else
        echo -e "${YELLOW}⚠️  Status do PostgreSQL não verificado (ok)${NC}"
    fi
else
    echo -e "${RED}❌ Backend OFFLINE ou inacessível${NC}"
    echo -e "   URL: $BACKEND_URL"
fi

echo ""

# ======================================================
# 2. TESTAR FRONTEND VERCEL
# ======================================================
echo -e "${YELLOW}[2/5] Testando Frontend Vercel...${NC}"

if curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" | grep -qE "200|301|302"; then
    echo -e "${GREEN}✅ Frontend está ONLINE${NC}"
    
    # Verificar se main.js existe (bundle Vite)
    if curl -s "$FRONTEND_URL" | grep -q "main.*\.js\|main.*\.jsx"; then
        echo -e "${GREEN}✅ Build Vite está correto${NC}"
    else
        echo -e "${YELLOW}⚠️  Build pode estar incorreto${NC}"
    fi
else
    echo -e "${RED}❌ Frontend OFFLINE ou inacessível${NC}"
    echo -e "   URL: $FRONTEND_URL"
fi

echo ""

# ======================================================
# 3. TESTAR AUTENTICAÇÃO SNIFFER
# ======================================================
echo -e "${YELLOW}[3/5] Testando Autenticação Sniffer...${NC}"

AUTH_RESPONSE=$(curl -s -w "\n%{http_code}" \
  -H "Authorization: Bearer $SENSOR_TOKEN" \
  "$BACKEND_URL/sniffer/status")

HTTP_CODE=$(echo "$AUTH_RESPONSE" | tail -n1)
BODY=$(echo "$AUTH_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Autenticação de Sniffer está OK${NC}"
    
    # Extrair dados do response
    if echo "$BODY" | grep -q "interfaces\|sensor_name"; then
        echo -e "${GREEN}✅ Sniffer está respondendo${NC}"
        echo -e "   Response: $(echo "$BODY" | head -c 100)..."
    fi
elif [ "$HTTP_CODE" = "401" ]; then
    echo -e "${RED}❌ Token de Autenticação INVÁLIDO${NC}"
else
    echo -e "${RED}❌ Erro na chamada: HTTP $HTTP_CODE${NC}"
fi

echo ""

# ======================================================
# 4. TESTAR SNIFFER LOCAL
# ======================================================
echo -e "${YELLOW}[4/5] Testando Sniffer Local (Docker)...${NC}"

if command -v docker &> /dev/null; then
    if docker ps | grep -q "ids-ips-sniffer-local\|sniffer"; then
        echo -e "${GREEN}✅ Container Sniffer está RODANDO${NC}"
        
        # Verificar interfaces
        if docker exec ids-ips-sniffer-local ip link show &>/dev/null; then
            IFCOUNT=$(docker exec ids-ips-sniffer-local ip link show | grep -c "^[0-9]" || echo "0")
            echo -e "${GREEN}✅ Sniffer consegue acessar $IFCOUNT interfaces${NC}"
        fi
        
        # Verificar logs
        if docker logs ids-ips-sniffer-local 2>&1 | grep -qi "error\|failed"; then
            echo -e "${RED}❌ Há ERROS nos logs do sniffer${NC}"
        else
            echo -e "${GREEN}✅ Logs do sniffer parecem OK${NC}"
        fi
    else
        echo -e "${RED}❌ Container Sniffer NÃO está RODANDO${NC}"
        echo -e "   Inicie com: docker compose -f docker-compose.sniffer.yml up -d"
    fi
else
    echo -e "${YELLOW}⚠️  Docker não encontrado - pulando teste${NC}"
fi

echo ""

# ======================================================
# 5. TESTAR COMUNICAÇÃO SNIFFER → BACKEND
# ======================================================
echo -e "${YELLOW}[5/5] Testando Comunicação Sniffer → Backend...${NC}"

# Simular evento de teste
TEST_EVENT=$(cat <<EOF
{
  "sensor_name": "Test-Validator",
  "interface": "eth0",
  "zone": "wan",
  "event_type": "alert",
  "alert_type": "connectivity_test",
  "source_ip": "127.0.0.1",
  "dest_ip": "127.0.0.1",
  "confidence": 0.99,
  "timestamp": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')",
  "details": {"test": true}
}
EOF
)

TEST_RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST "$BACKEND_URL/sniffer/events" \
  -H "Authorization: Bearer $SENSOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$TEST_EVENT")

TEST_HTTP_CODE=$(echo "$TEST_RESPONSE" | tail -n1)
TEST_BODY=$(echo "$TEST_RESPONSE" | head -n-1)

if [ "$TEST_HTTP_CODE" = "200" ] || [ "$TEST_HTTP_CODE" = "201" ]; then
    echo -e "${GREEN}✅ Envio de eventos está funcionando${NC}"
elif [ "$TEST_HTTP_CODE" = "422" ]; then
    echo -e "${YELLOW}⚠️  Validação de evento falhou (schema)${NC}"
    echo -e "   Response: $TEST_BODY"
else
    echo -e "${RED}❌ Erro ao enviar evento: HTTP $TEST_HTTP_CODE${NC}"
fi

echo ""

# ======================================================
# RESUMO FINAL
# ======================================================
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}📊 RESUMO DA VALIDAÇÃO${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "Backend Render:      ${BACKEND_URL}"
echo -e "Frontend Vercel:     ${FRONTEND_URL}"
echo -e "Sniffer Local:       ${SENSOR_NAME:-Não configurado}"
echo ""
echo -e "${GREEN}✅ DEPLOYMENT PODE ESTAR OK${NC}"
echo ""
echo "Próximos passos:"
echo "1. Acessar dashboard: $FRONTEND_URL"
echo "2. Fazer login"
echo "3. Verificar se interfaces do sniffer aparecem"
echo "4. Monitor alertas em tempo real"
echo ""
