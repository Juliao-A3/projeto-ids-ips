#!/bin/bash

# ========================================================
# SETUP INTERATIVO - Configurar Sniffer Local
# ========================================================
# Este script ajuda a criar .env.sniffer de forma interativa

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

clear

echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🚀 SETUP INTERATIVO - CONFIGURAR SNIFFER LOCAL${NC}"
echo -e "${BLUE}════════════════════════════════════════════════${NC}\n"

echo "Este script cria o arquivo .env.sniffer com suas configurações."
echo "Se você já tem .env.sniffer, será feito backup."
echo ""

# ========================================================
# 1. BACKUP DO ARQUIVO ANTERIOR
# ========================================================

if [ -f .env.sniffer ]; then
    echo -e "${YELLOW}⚠️  .env.sniffer já existe!${NC}"
    read -p "Deseja fazer backup e criar novo? (s/n): " -n 1 -r RESP
    echo
    if [[ $RESP =~ ^[Ss]$ ]]; then
        BACKUP_NAME=".env.sniffer.backup.$(date +%Y%m%d_%H%M%S)"
        cp .env.sniffer "$BACKUP_NAME"
        echo -e "${GREEN}✅ Backup salvo em: $BACKUP_NAME${NC}\n"
    else
        echo "Abortado. Use --force para sobrescrever."
        exit 1
    fi
fi

# ========================================================
# 2. BACKEND CONFIGURATION
# ========================================================

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}1️⃣  CONFIGURAÇÃO BACKEND CLOUD${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo "Insira a URL do seu backend no Render:"
echo "Exemplo: https://seu-backend.onrender.com"
read -p "URL Backend: " BACKEND_URL

if [[ ! $BACKEND_URL =~ ^https?:// ]]; then
    echo -e "${RED}❌ URL inválida. Deve começar com http:// ou https://${NC}"
    exit 1
fi

echo ""
echo "Insira o token de autenticação para o Sniffer:"
echo "Este deve ser o mesmo configurado em Render: SENSOR_API_TOKEN"
echo "Se não sabe, use uma string forte (ex: $(openssl rand -hex 32))"
read -sp "Token (não será exibido): " SENSOR_API_TOKEN
echo ""

if [ -z "$SENSOR_API_TOKEN" ]; then
    echo -e "${RED}❌ Token não pode estar vazio${NC}"
    exit 1
fi

# ========================================================
# 3. INTERFACES DE REDE
# ========================================================

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}2️⃣  INTERFACES DE REDE${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo "Interfaces detectadas neste PC:"
echo ""

if command -v ip &> /dev/null; then
    echo "$(ip link show | grep -E '^[0-9]+:' | awk '{print $2}' | sed 's/:$//')"
elif command -v ifconfig &> /dev/null; then
    echo "$(ifconfig -a | grep -oE '^[a-z0-9]+' | sort -u)"
else
    echo "⚠️  Não foi possível detectar interfaces automaticamente"
fi

echo ""
echo "Digite as interfaces que deseja monitorar (separadas por vírgula):"
echo "Exemplo: eth0,eth1,wlan0"
read -p "Interfaces: " INTERFACES

if [ -z "$INTERFACES" ]; then
    echo -e "${RED}❌ Deve fornecer pelo menos uma interface${NC}"
    exit 1
fi

# ========================================================
# 4. ZONE MAPPING
# ========================================================

echo ""
echo -e "${CYAN}3️⃣  MAPEAMENTO DE ZONAS${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo "Agora vamos mapear cada interface para sua zona (WAN, LAN, WLAN, etc)."
echo "Sua configuração de interfaces: $INTERFACES"
echo ""

IFS=',' read -ra IFACE_ARRAY <<< "$INTERFACES"
ZONE_MAP=""

for iface in "${IFACE_ARRAY[@]}"; do
    iface=$(echo "$iface" | xargs)  # trim whitespace
    read -p "  $iface é: (wan/lan/wlan): " zone
    
    case "$zone" in
        wan|lan|wlan)
            if [ -z "$ZONE_MAP" ]; then
                ZONE_MAP="$iface:$zone"
            else
                ZONE_MAP="$ZONE_MAP,$iface:$zone"
            fi
            ;;
        *)
            echo -e "${YELLOW}⚠️  Zona inválida, usando 'lan' como padrão${NC}"
            if [ -z "$ZONE_MAP" ]; then
                ZONE_MAP="$iface:lan"
            else
                ZONE_MAP="$ZONE_MAP,$iface:lan"
            fi
            ;;
    esac
done

# ========================================================
# 5. SENSOR IDENTIFICATION
# ========================================================

echo ""
echo -e "${CYAN}4️⃣  IDENTIFICAÇÃO DO SENSOR${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

HOSTNAME=$(hostname -s 2>/dev/null || echo "pc")
DEFAULT_SENSOR_NAME="Sniffer-Local-PC-$HOSTNAME"

read -p "Nome do Sensor [$DEFAULT_SENSOR_NAME]: " SENSOR_NAME
SENSOR_NAME=${SENSOR_NAME:-$DEFAULT_SENSOR_NAME}

read -p "Localização do Sensor [Matriz]: " SENSOR_LOCATION
SENSOR_LOCATION=${SENSOR_LOCATION:-Matriz}

# ========================================================
# 6. IDS/IPS CONFIGURATION
# ========================================================

echo ""
echo -e "${CYAN}5️⃣  CONFIGURAÇÃO IDS/IPS${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo "Threshold de confiança (0.5 = alto, 0.7 = médio, 0.9 = baixo):"
read -p "IDS_THRESHOLD [0.7]: " IDS_THRESHOLD
IDS_THRESHOLD=${IDS_THRESHOLD:-0.7}

echo "Confiança mínima para bloquear (0.8 recomendado):"
read -p "IPS_MIN_CONFIDENCE [0.8]: " IPS_MIN_CONFIDENCE
IPS_MIN_CONFIDENCE=${IPS_MIN_CONFIDENCE:-0.8}

echo "Janela de tempo para correlação (segundos):"
read -p "IPS_ATTACK_WINDOW_SECONDS [60]: " IPS_ATTACK_WINDOW_SECONDS
IPS_ATTACK_WINDOW_SECONDS=${IPS_ATTACK_WINDOW_SECONDS:-60}

# ========================================================
# 7. LOGGING CONFIGURATION
# ========================================================

echo ""
echo -e "${CYAN}6️⃣  LOGGING${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo "Nível de log (DEBUG/INFO/WARNING/ERROR):"
read -p "LOG_LEVEL [INFO]: " LOG_LEVEL
LOG_LEVEL=${LOG_LEVEL:-INFO}

# ========================================================
# 8. GERAR .env.sniffer
# ========================================================

echo ""
echo -e "${CYAN}7️⃣  GERANDO ARQUIVO .env.sniffer${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

cat > .env.sniffer << EOF
# ==========================================
# CONFIGURAÇÃO DO SNIFFER LOCAL
# Gerada em: $(date)
# ==========================================

# 🌐 CONEXÃO COM BACKEND CLOUD
BACKEND_URL=$BACKEND_URL
SENSOR_API_TOKEN=$SENSOR_API_TOKEN
BACKEND_RECONNECT_INTERVAL=30
BACKEND_TIMEOUT=10

# 🔍 INTERFACES DE REDE A MONITORAR
INTERFACES=$INTERFACES
ZONE_MAP=$ZONE_MAP

# 📝 IDENTIFICAÇÃO DO SENSOR
SENSOR_NAME=$SENSOR_NAME
SENSOR_LOCATION=$SENSOR_LOCATION

# 🎯 CONFIGURAÇÃO DE DETECÇÃO IDS/IPS
IDS_THRESHOLD=$IDS_THRESHOLD
IPS_MIN_CONFIDENCE=$IPS_MIN_CONFIDENCE
IPS_ATTACK_WINDOW_SECONDS=$IPS_ATTACK_WINDOW_SECONDS
MAX_ALERTS_PER_MINUTE=100

# 📊 CAPTURA DE TRÁFEGO
PACKET_CAPTURE_SIZE=65535
PACKETS_PER_SECOND_LIMIT=0
ENABLE_DPI=true

# 🚨 ALERTAS E NOTIFICAÇÕES
ALERT_MODES=all
STREAM_ALERTS=true
SUMMARY_INTERVAL=300

# 📝 LOGGING
LOG_LEVEL=$LOG_LEVEL
LOG_FILE=./logs/sniffer.log
LOG_FILE_MAX_SIZE=100
LOG_FILE_BACKUP_COUNT=10

# 🔄 SINCRONIZAÇÃO E HEARTBEAT
HEARTBEAT_INTERVAL=30
BACKEND_HEARTBEAT_TIMEOUT=60
ENABLE_OFFLINE_MODE=true
OFFLINE_BUFFER_DB=./data/offline_buffer.db
OFFLINE_BUFFER_MAX_EVENTS=10000

# 🔐 CERTIFICADOS SSL/TLS
VERIFY_SSL=true

# 📊 ESTATÍSTICAS E RELATÓRIOS
REPORT_INTERVAL_MINUTES=60
SEND_STATISTICS=true

# 🏗️ AMBIENTE
ENVIRONMENT=production
DEBUG=false

# 🔔 VARIÁVEIS INTERNAS
SENSOR_MODE=sniffer
SENSOR_PID=\$RANDOM
APP_VERSION=1.0.0
EOF

echo -e "${GREEN}✅ Arquivo .env.sniffer criado com sucesso!${NC}\n"

# ========================================================
# 9. PRÓXIMOS PASSOS
# ========================================================

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}✨ PRÓXIMOS PASSOS${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo "1. Verificar o arquivo criado:"
echo -e "   ${YELLOW}cat .env.sniffer${NC}"
echo ""

echo "2. Iniciar o Sniffer Local:"
echo -e "   ${YELLOW}docker compose -f docker-compose.sniffer.yml up -d --build${NC}"
echo ""

echo "3. Ver logs do sniffer:"
echo -e "   ${YELLOW}docker compose -f docker-compose.sniffer.yml logs -f sniffer${NC}"
echo ""

echo "4. Validar conexão com backend:"
echo -e "   ${YELLOW}./validate_deployment.sh${NC}"
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ SETUP CONCLUÍDO!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo "Resumo da configuração:"
echo "  Backend URL:     $BACKEND_URL"
echo "  Interfaces:      $INTERFACES"
echo "  Sensor Name:     $SENSOR_NAME"
echo "  Log Level:       $LOG_LEVEL"
echo ""

read -p "Deseja iniciar o sniffer agora? (s/n): " -n 1 -r RESP
echo
if [[ $RESP =~ ^[Ss]$ ]]; then
    echo -e "${YELLOW}Iniciando sniffer...${NC}\n"
    docker compose -f docker-compose.sniffer.yml up -d --build
    sleep 3
    echo ""
    echo -e "${GREEN}✅ Sniffer iniciado!${NC}"
    echo "Verifique os logs com:"
    echo -e "  ${YELLOW}docker compose -f docker-compose.sniffer.yml logs -f${NC}"
else
    echo "OK. Para iniciar depois, execute:"
    echo -e "  ${YELLOW}docker compose -f docker-compose.sniffer.yml up -d --build${NC}"
fi

echo ""
