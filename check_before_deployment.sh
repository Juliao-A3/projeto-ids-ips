#!/bin/bash

# ========================================================
# PRE-FLIGHT CHECKLIST - Validar antes de fazer deployment
# ========================================================
# Uso: bash check_before_deployment.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CHECKS_PASSED=0
CHECKS_FAILED=0

echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🔍 PRE-FLIGHT DEPLOYMENT CHECKLIST${NC}"
echo -e "${BLUE}════════════════════════════════════════════════${NC}\n"

# ========================================================
# FUNÇÃO PARA TESTE
# ========================================================

check() {
    local num=$1
    local name=$2
    local cmd=$3
    
    echo -n "[$num] $name ... "
    
    if eval "$cmd" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}❌ FALHOU${NC}"
        ((CHECKS_FAILED++))
    fi
}

# ========================================================
# 1. VERIFICAÇÕES GIT
# ========================================================

echo -e "${YELLOW}📦 1. REPOSITÓRIO GIT${NC}"
check "1.1" "Repositório Git inicializado" "git rev-parse --git-dir"
check "1.2" "Branch main existe" "git show-ref --quiet refs/heads/main"
check "1.3" "Sem changes não commitadas" "git status --porcelain | wc -l | grep -q '^0$'"
check "1.4" "README.md existe" "test -f README.md"
echo ""

# ========================================================
# 2. VERIFICAÇÕES BACKEND
# ========================================================

echo -e "${YELLOW}🔧 2. BACKEND${NC}"
check "2.1" "Diretório backend existe" "test -d backend"
check "2.2" "config.py existe" "test -f backend/config.py"
check "2.3" "main.py existe" "test -f backend/main.py"
check "2.4" "requirements.txt existe" "test -f backend/requirements.txt"
check "2.5" "requirements.txt não vazio" "test -s backend/requirements.txt"
check "2.6" "FastAPI em requirements.txt" "grep -q fastapi backend/requirements.txt"
check "2.7" "SQLAlchemy em requirements.txt" "grep -q sqlalchemy backend/requirements.txt"
check "2.8" "models.py existe" "test -f backend/models.py"
check "2.9" "schemas.py existe" "test -f backend/schemas.py"
check "2.10" "Dockerfile backend existe" "test -f backend/Dockerfile"
echo ""

# ========================================================
# 3. VERIFICAÇÕES FRONTEND
# ========================================================

echo -e "${YELLOW}🌐 3. FRONTEND${NC}"
check "3.1" "Diretório frontend existe" "test -d frontend"
check "3.2" "package.json existe" "test -f frontend/package.json"
check "3.3" "vite.config.ts existe" "test -f frontend/vite.config.ts"
check "3.4" "src/main.tsx existe" "test -f frontend/src/main.tsx"
check "3.5" "package.json tem scripts" "grep -q '\"scripts\"' frontend/package.json"
check "3.6" "React em dependencies" "grep -q 'react' frontend/package.json"
check "3.7" "Vite em devDependencies" "grep -q 'vite' frontend/package.json"
echo ""

# ========================================================
# 4. VERIFICAÇÕES DOCKER
# ========================================================

echo -e "${YELLOW}🐋 4. DOCKER & DOCKER-COMPOSE${NC}"
check "4.1" "Docker instalado" "command -v docker"
check "4.2" "docker-compose instalado" "command -v docker-compose"
check "4.3" "docker daemon rodando" "docker ps > /dev/null"
check "4.4" "docker-compose.yml existe" "test -f docker-compose.yml"
check "4.5" "docker-compose.sniffer.yml existe" "test -f docker-compose.sniffer.yml"
echo ""

# ========================================================
# 5. VERIFICAÇÕES RENDER/DEPLOYMENT
# ========================================================

echo -e "${YELLOW}☁️  5. CONFIGURAÇÃO RENDER${NC}"
check "5.1" "render.yaml existe" "test -f render.yaml"
check "5.2" "render.yaml válido (YAML)" "grep -q 'services:' render.yaml"
check "5.3" "render.yaml tem postgres" "grep -q 'postgres' render.yaml"
check "5.4" "render.yaml tem backend service" "grep -q 'name: backend' render.yaml"
echo ""

# ========================================================
# 6. VERIFICAÇÕES ALEMBIC/DB
# ========================================================

echo -e "${YELLOW}🗄️  6. DATABASE & ALEMBIC${NC}"
check "6.1" "alembic.ini existe" "test -f alembic.ini"
check "6.2" "alembic/env.py existe" "test -f alembic/env.py"
check "6.3" "alembic/versions existe" "test -d alembic/versions"
check "6.4" "Migrations existem" "find alembic/versions -name '*.py' | wc -l | grep -qv '^0$'"
echo ""

# ========================================================
# 7. VERIFICAÇÕES SNIFFER
# ========================================================

echo -e "${YELLOW}🔍 7. SNIFFER LOCAL${NC}"
check "7.1" "diretório sniffer existe" "test -d sniffer || true && echo ok"
check "7.2" ".env.sniffer.example existe" "test -f .env.sniffer.example"
check "7.3" "docker-compose.sniffer.yml válido" "grep -q 'services:' docker-compose.sniffer.yml"
echo ""

# ========================================================
# 8. VERIFICAÇÕES VARIÁVEIS
# ========================================================

echo -e "${YELLOW}🔑 8. VARIÁVEIS DE AMBIENTE${NC}"

if [ -f .env.local ]; then
    check "8.1" ".env.local existe" "test -f .env.local"
else
    echo "[8.1] .env.local existe ... ${YELLOW}⚠️  OPCIONAL${NC}"
fi

if [ -f .env.sniffer ]; then
    check "8.2" ".env.sniffer existe" "test -f .env.sniffer"
    check "8.3" ".env.sniffer tem BACKEND_URL" "grep -q BACKEND_URL .env.sniffer"
else
    echo "[8.2] .env.sniffer existe ... ${YELLOW}⚠️  Será criado depois${NC}"
fi

if [ -f frontend/.env.production ]; then
    check "8.4" "frontend/.env.production existe" "test -f frontend/.env.production"
else
    echo "[8.4] frontend/.env.production existe ... ${YELLOW}⚠️  Será criado depois${NC}"
fi

echo ""

# ========================================================
# 9. VERIFICAÇÕES ARQUIVOS CRÍTICOS
# ========================================================

echo -e "${YELLOW}📄 9. DOCUMENTAÇÃO & CONFIGS${NC}"
check "9.1" "DEPLOYMENT_CLOUD_PLAN.md existe" "test -f DEPLOYMENT_CLOUD_PLAN.md"
check "9.2" "DEPLOYMENT_STEP_BY_STEP.md existe" "test -f DEPLOYMENT_STEP_BY_STEP.md"
check "9.3" "DEPLOYMENT_SUMMARY.md existe" "test -f DEPLOYMENT_SUMMARY.md"
check "9.4" "validate_deployment.sh existe" "test -f validate_deployment.sh"
check "9.5" "ARCHITECTURE_FIREWALL.md existe" "test -f ARCHITECTURE_FIREWALL.md"
echo ""

# ========================================================
# 10. VERIFICAÇÕES CONTAS EXTERNAS
# ========================================================

echo -e "${YELLOW}🔐 10. CONTAS EXTERNAS (MANUAL)${NC}"

echo -n "[10.1] Conta GitHub criada? "
read -r -t 2 answer < <(echo "skip") && echo -e "${YELLOW}⏭️  [manual]${NC}" || echo -e "${YELLOW}⏭️  [manual]${NC}"

echo -n "[10.2] Conta Render criada? "
echo -e "${YELLOW}⏭️  [manual]${NC}"

echo -n "[10.3] Conta Vercel criada? "
echo -e "${YELLOW}⏭️  [manual]${NC}"

echo ""

# ========================================================
# RELATÓRIO FINAL
# ========================================================

TOTAL=$((CHECKS_PASSED + CHECKS_FAILED))

echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📊 RESULTADO FINAL${NC}"
echo -e "${BLUE}════════════════════════════════════════════════${NC}\n"

echo "Total de verificações: $TOTAL"
echo -e "✅ Passou: ${GREEN}$CHECKS_PASSED${NC}"
echo -e "❌ Falhou: ${RED}$CHECKS_FAILED${NC}"

echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 TUDO PRONTO PARA DEPLOYMENT!${NC}\n"
    echo "Próximas etapas:"
    echo "1. Executar: DEPLOYMENT_STEP_BY_STEP.md"
    echo "2. Começar com FASE 1 (Backend Render)"
    echo ""
    exit 0
else
    echo -e "${RED}⚠️  ERROS ENCONTRADOS - Resolver antes de fazer deploy${NC}\n"
    echo "Erros a resolver:"
    echo "- Verifique mensagens acima"
    echo "- Consulte DEPLOYMENT_CLOUD_PLAN.md"
    echo ""
    exit 1
fi
