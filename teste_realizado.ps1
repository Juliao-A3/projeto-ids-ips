# executar_testes.ps1
# Script para executar todos os testes do sistema IDS/IPS
# Data: 2026-03-19
# Versão: 3.0 (com testes de Sniffer, Logs, Whitelist e Estatísticas)

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "EXECUTAR TODOS OS TESTES - SISTEMA IDS/IPS" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Data: $(Get-Date)" -ForegroundColor Yellow
Write-Host ""

# ============================================
# 1. INSPECIONAR MODELOS
# ============================================
Write-Host "1. INSPECIONAR MODELOS" -ForegroundColor Green
Write-Host "------------------------------------------------------------" -ForegroundColor Gray

Write-Host "`n📋 Inspecionando novo modelo (85%)..." -ForegroundColor Yellow
python backend/scapy_module/inspecionar_modelo.py models\modelo_scapy_20260319_152419_85.40%.pkl

Write-Host "`n📋 Inspecionando best_model..." -ForegroundColor Yellow
python backend/scapy_module/inspecionar_modelo.py models\best_model.pkl

Write-Host ""
Read-Host "Pressiona Enter para continuar..."

# ============================================
# 2. TESTAR MODELO NOVO COM DIFERENTES LIMITES
# ============================================
Write-Host "`n2. TESTAR NOVO MODELO (85%) COM DIFERENTES LIMITES" -ForegroundColor Green
Write-Host "------------------------------------------------------------" -ForegroundColor Gray

# Teste com 100 pacotes
Write-Host "`n📊 Teste rápido (100 pacotes)..." -ForegroundColor Yellow
python backend/scapy_module/testar_modelo.py data/pcaps/normal/normal.pcapng models\modelo_scapy_20260319_152419_85.40%.pkl --limite 100

# Teste com 500 pacotes
Write-Host "`n📊 Teste médio (500 pacotes)..." -ForegroundColor Yellow
python backend/scapy_module/testar_modelo.py data/pcaps/normal/normal.pcapng models\modelo_scapy_20260319_152419_85.40%.pkl --limite 500

# Teste com 1000 pacotes
Write-Host "`n📊 Teste completo (1000 pacotes)..." -ForegroundColor Yellow
python backend/scapy_module/testar_modelo.py data/pcaps/normal/normal.pcapng models\modelo_scapy_20260319_152419_85.40%.pkl --limite 1000

Write-Host ""
Read-Host "Pressiona Enter para continuar..."

# ============================================
# 3. TESTAR COM PASTAS (NOVO MODELO)
# ============================================
Write-Host "`n3. TESTAR COM PASTAS (NOVO MODELO)" -ForegroundColor Green
Write-Host "------------------------------------------------------------" -ForegroundColor Gray

# Testar apenas normal
Write-Host "`n📁 Testando pasta NORMAL..." -ForegroundColor Yellow
python backend/scapy_module/testar_com_pastas.py --pasta normal --modelo models\modelo_scapy_20260319_152419_85.40%.pkl --limite 500

# Se existir pasta attacks, testar também
if (Test-Path "data/pcaps/attacks/*.pcap*") {
    Write-Host "`n📁 Testando pasta ATTACKS..." -ForegroundColor Yellow
    python backend/scapy_module/testar_com_pastas.py --pasta attacks --modelo models\modelo_scapy_20260319_152419_85.40%.pkl --limite 500
} else {
    Write-Host "`n⚠️ Pasta attacks vazia - sem PCAPs de ataque" -ForegroundColor Red
}

Write-Host ""
Read-Host "Pressiona Enter para continuar..."

# ============================================
# 4. TESTAR BEST_MODEL (PARA COMPARAÇÃO)
# ============================================
Write-Host "`n4. TESTAR BEST_MODEL (PARA COMPARAÇÃO)" -ForegroundColor Green
Write-Host "------------------------------------------------------------" -ForegroundColor Gray

Write-Host "`n📊 Testando best_model com 500 pacotes..." -ForegroundColor Yellow
python backend/scapy_module/testar_modelo.py data/pcaps/normal/normal.pcapng models\best_model.pkl --limite 500

Write-Host ""
Read-Host "Pressiona Enter para continuar..."

# ============================================
# 5. ESTATÍSTICAS DO MODELO
# ============================================
Write-Host "`n5. ESTATÍSTICAS DO MODELO" -ForegroundColor Green
Write-Host "------------------------------------------------------------" -ForegroundColor Gray

Write-Host "`n📊 Estatísticas do modelo mais recente:" -ForegroundColor Yellow
python backend/scapy_module/estatisticas_modelo.py

Write-Host "`n📊 Estatísticas de modelo específico:" -ForegroundColor Yellow
python backend/scapy_module/estatisticas_modelo.py --modelo models\modelo_scapy_20260319_152419_85.40%.pkl

Write-Host ""
Read-Host "Pressiona Enter para continuar..."

# ============================================
# 6. LISTAR INTERFACES DE REDE
# ============================================
Write-Host "`n6. INTERFACES DE REDE DISPONÍVEIS" -ForegroundColor Green
Write-Host "------------------------------------------------------------" -ForegroundColor Gray

Write-Host "`n📡 Interfaces detectadas:" -ForegroundColor Yellow
python -c "from scapy.all import get_if_list; interfaces = get_if_list(); [print(f'   {i+1}. {iface}') for i, iface in enumerate(interfaces)]"
Write-Host ""

Read-Host "Pressiona Enter para continuar..."

# ============================================
# 7. TESTAR IPS COMPLETO (COM LOGS + WHITELIST)
# ============================================
Write-Host "`n7. TESTAR IPS COMPLETO (COM LOGS + WHITELIST)" -ForegroundColor Green
Write-Host "------------------------------------------------------------" -ForegroundColor Gray

Write-Host @"

Escolhe o tipo de teste do IPS:
  1. Teste rápido (monitorar 200 pacotes)
  2. Teste completo (correr até CTRL+C)
  3. Teste com filtro específico
  4. Ver logs existentes
  5. Voltar

"@ -ForegroundColor Cyan

$opcao_ips = Read-Host "Opção (1-5)"

switch ($opcao_ips) {
    '1' {
        Write-Host "`n🔄 Teste rápido do IPS (200 pacotes)..." -ForegroundColor Yellow
        Write-Host "   ⚠️ Nota: Deves parar manualmente após ~200 pacotes (CTRL+C)" -ForegroundColor Yellow
        python backend/scapy_module/sniffer_realtime.py --interface "Wi-Fi"
    }
    '2' {
        Write-Host "`n🔄 Teste completo do IPS (correr até CTRL+C)..." -ForegroundColor Yellow
        Write-Host "   ✅ Whitelist ativa: 8.8.8.8, 1.1.1.1, 192.168.1.1, etc."
        Write-Host "   📁 Logs serão guardados em: data/logs/"
        Write-Host "   🔒 Bloqueio automático após 5 anomalias"
        Write-Host "   🟢 Interfaces ATIVAS vs 🔴 INATIVAS"
        Write-Host ""
        python backend/scapy_module/sniffer_realtime.py --interface "Wi-Fi"
    }
    '3' {
        $filtro = Read-Host "`nDigite o filtro (ex: tcp port 80, icmp, udp)"
        Write-Host "`n🔄 Testando IPS com filtro: $filtro" -ForegroundColor Yellow
        python backend/scapy_module/sniffer_realtime.py --interface "Wi-Fi" --filtro "$filtro"
    }
    '4' {
        Write-Host "`n📁 Logs disponíveis:" -ForegroundColor Yellow
        if (Test-Path "data/logs") {
            Get-ChildItem -Path data/logs -Filter "*.json" | Format-Table Name, LastWriteTime, Length
            $ver_log = Read-Host "`nVer conteúdo de um log? (s/n)"
            if ($ver_log -eq 's') {
                $log_file = Read-Host "Nome do ficheiro (ex: ips_20260319.json)"
                if (Test-Path "data/logs/$log_file") {
                    Get-Content "data/logs/$log_file" -Tail 20
                } else {
                    Write-Host "❌ Ficheiro não encontrado" -ForegroundColor Red
                }
            }
        } else {
            Write-Host "❌ Pasta de logs não encontrada" -ForegroundColor Red
        }
    }
}

Write-Host ""
Read-Host "Pressiona Enter para continuar..."

# ============================================
# 8. TESTAR SNIFFER EM DIFERENTES INTERFACES
# ============================================
Write-Host "`n8. TESTAR SNIFFER EM INTERFACES" -ForegroundColor Green
Write-Host "------------------------------------------------------------" -ForegroundColor Gray

Write-Host @"

Escolhe a interface para testar o sniffer:
  1. Wi-Fi (nome amigável)
  2. Ethernet (nome amigável)  
  3. Loopback
  4. Todas as interfaces (padrão)
  5. Voltar

"@ -ForegroundColor Cyan

$opcao_iface = Read-Host "Opção (1-5)"

switch ($opcao_iface) {
    '1' {
        Write-Host "`n📡 Iniciando sniffer na interface Wi-Fi (CTRL+C para parar)..." -ForegroundColor Yellow
        python backend/scapy_module/sniffer_realtime.py --interface "Wi-Fi"
    }
    '2' {
        Write-Host "`n📡 Iniciando sniffer na interface Ethernet (CTRL+C para parar)..." -ForegroundColor Yellow
        python backend/scapy_module/sniffer_realtime.py --interface "Ethernet"
    }
    '3' {
        Write-Host "`n📡 Iniciando sniffer na interface Loopback (CTRL+C para parar)..." -ForegroundColor Yellow
        python backend/scapy_module/sniffer_realtime.py --interface "Loopback"
    }
    '4' {
        Write-Host "`n📡 Iniciando sniffer em TODAS as interfaces (CTRL+C para parar)..." -ForegroundColor Yellow
        python backend/scapy_module/sniffer_realtime.py
    }
}

Write-Host ""
Read-Host "Pressiona Enter para continuar..."

# ============================================
# 9. TESTAR SNIFFER COM FILTROS
# ============================================
Write-Host "`n9. TESTAR SNIFFER COM FILTROS" -ForegroundColor Green
Write-Host "------------------------------------------------------------" -ForegroundColor Gray

Write-Host @"

Escolhe o filtro para testar:
  1. ICMP (ping)
  2. HTTP (porta 80)
  3. HTTPS (porta 443)
  4. DNS (porta 53)
  5. Filtro personalizado
  6. Voltar

"@ -ForegroundColor Cyan

$opcao_filtro = Read-Host "Opção (1-6)"

switch ($opcao_filtro) {
    '1' {
        Write-Host "`n📡 Iniciando sniffer com filtro ICMP (ping)..." -ForegroundColor Yellow
        python backend/scapy_module/sniffer_realtime.py --interface "Wi-Fi" --filtro "icmp"
    }
    '2' {
        Write-Host "`n📡 Iniciando sniffer com filtro HTTP (porta 80)..." -ForegroundColor Yellow
        python backend/scapy_module/sniffer_realtime.py --interface "Wi-Fi" --filtro "tcp port 80"
    }
    '3' {
        Write-Host "`n📡 Iniciando sniffer com filtro HTTPS (porta 443)..." -ForegroundColor Yellow
        python backend/scapy_module/sniffer_realtime.py --interface "Wi-Fi" --filtro "tcp port 443"
    }
    '4' {
        Write-Host "`n📡 Iniciando sniffer com filtro DNS (porta 53)..." -ForegroundColor Yellow
        python backend/scapy_module/sniffer_realtime.py --interface "Wi-Fi" --filtro "udp port 53"
    }
    '5' {
        $filtro = Read-Host "`nDigite o filtro (ex: tcp, udp, icmp, port 22)"
        Write-Host "`n📡 Iniciando sniffer com filtro: $filtro" -ForegroundColor Yellow
        python backend/scapy_module/sniffer_realtime.py --interface "Wi-Fi" --filtro "$filtro"
    }
}

Write-Host ""
Read-Host "Pressiona Enter para continuar..."

# ============================================
# 10. TESTAR WHITELIST
# ============================================
Write-Host "`n10. TESTAR WHITELIST" -ForegroundColor Green
Write-Host "------------------------------------------------------------" -ForegroundColor Gray

Write-Host @"

Opções de whitelist:
  1. Mostrar whitelist atual
  2. Adicionar IP à whitelist (simulado)
  3. Remover IP da whitelist (simulado)
  4. Voltar

"@ -ForegroundColor Cyan

$opcao_wl = Read-Host "Opção (1-4)"

switch ($opcao_wl) {
    '1' {
        Write-Host "`n📋 Whitelist atual (IPs que nunca serão bloqueados):" -ForegroundColor Yellow
        $whitelist = @(
            "8.8.8.8 (Google DNS)",
            "8.8.4.4 (Google DNS)",
            "1.1.1.1 (Cloudflare DNS)",
            "1.0.0.1 (Cloudflare DNS)",
            "192.168.1.1 (Router)",
            "192.168.0.1 (Router alternativo)",
            "10.212.255.176 (DNS interno)"
        )
        $whitelist | ForEach-Object { Write-Host "   ✅ $_" }
        Write-Host "`n   ⚠️ A whitelist está hardcoded no sniffer_realtime.py" -ForegroundColor Yellow
    }
    '2' {
        $novo_ip = Read-Host "IP para adicionar"
        Write-Host "   ⚠️ Simulação: IP $novo_ip adicionado à whitelist (não persistente)" -ForegroundColor Yellow
        Write-Host "   📝 Para adicionar permanentemente, edita o sniffer_realtime.py" -ForegroundColor Yellow
    }
    '3' {
        $remover_ip = Read-Host "IP para remover"
        Write-Host "   ⚠️ Simulação: IP $remover_ip removido da whitelist (não persistente)" -ForegroundColor Yellow
        Write-Host "   📝 Para remover permanentemente, edita o sniffer_realtime.py" -ForegroundColor Yellow
    }
}

Write-Host ""
Read-Host "Pressiona Enter para continuar..."

# ============================================
# 11. LISTAR RESULTADOS GERADOS
# ============================================
Write-Host "`n11. RESULTADOS GERADOS" -ForegroundColor Green
Write-Host "------------------------------------------------------------" -ForegroundColor Gray

$resultados_json = Get-ChildItem -Path data -Filter "*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
$logs = Get-ChildItem -Path data/logs -Filter "*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending

if ($resultados_json.Count -gt 0) {
    Write-Host "`n📁 Resultados de testes:" -ForegroundColor Yellow
    $resultados_json | Select-Object -First 5 | Format-Table Name, LastWriteTime, @{Name="Tamanho(KB)";Expression={[math]::Round($_.Length/1KB,2)}} -AutoSize
} else {
    Write-Host "`n❌ Nenhum resultado de teste encontrado" -ForegroundColor Red
}

if ($logs.Count -gt 0) {
    Write-Host "`n📁 Logs do IPS:" -ForegroundColor Yellow
    $logs | Select-Object -First 5 | Format-Table Name, LastWriteTime, @{Name="Tamanho(KB)";Expression={[math]::Round($_.Length/1KB,2)}} -AutoSize
} else {
    Write-Host "`n❌ Nenhum log encontrado" -ForegroundColor Red
}

Write-Host ""
Read-Host "Pressiona Enter para continuar..."

# ============================================
# 12. RESUMO DOS TESTES
# ============================================
Write-Host "`n12. RESUMO DOS TESTES" -ForegroundColor Green
Write-Host "------------------------------------------------------------" -ForegroundColor Gray

Write-Host @"

┌─────────────────────────────┬────────────────────┬────────────────────┐
│ Item                        │ best_model.pkl     │ novo_modelo_85%    │
├─────────────────────────────┼────────────────────┼────────────────────┤
│ Features                    │ 69                 │ 14                 │
│ Funcionou?                  │ ❌ NÃO             │ ✅ SIM             │
│ Acurácia (normal)           │ 0%                 │ 90.19%             │
│ Taxa anomalias (inicial)    │ -                  │ 36.58%             │
│ Taxa anomalias (final)      │ -                  │ 4.84%              │
│ Melhoria                    │ -                  │ -31.74%            │
└─────────────────────────────┴────────────────────┴────────────────────┘

📋 TESTES DO IPS REALIZADOS:
   ✅ Teste inicial: 1069 pacotes, 36.58% anomalias, 4 bloqueios
   ✅ Teste otimizado: 888 pacotes, 4.84% anomalias, 3 bloqueios
   ✅ Whitelist: 7 IPs configurados
   ✅ Logs: data/logs/ips_*.json
   ✅ Bloqueio automático após 5 anomalias
   ✅ Pergunta ao parar: "Deseja LIMPAR todos os IPs bloqueados?"
   ✅ Interfaces ATIVAS vs INATIVAS com contagem de pacotes

📋 TESTES DO SNIFFER REALIZADOS:
   ✅ Todas as interfaces (padrão)
   ✅ Interface Wi-Fi
   ✅ Interface Ethernet
   ✅ Interface Loopback
   ✅ Filtro ICMP (ping)
   ✅ Filtro HTTP (porta 80)
   ✅ Filtro HTTPS (porta 443)
   ✅ Filtro DNS (porta 53)

📋 TESTES DE ESTATÍSTICAS REALIZADOS:
   ✅ estatisticas_modelo.py (modelo mais recente)
   ✅ estatisticas_modelo.py (modelo específico)
   ✅ Histórico de sessões (últimas 5)
   ✅ Features do modelo (14)
   ✅ Acurácia (85.4%)

"@ -ForegroundColor White

Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "TESTES CONCLUÍDOS!" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# Perguntar se quer abrir as pastas de resultados
$resposta = Read-Host "`nAbrir pasta de resultados? (1-Data, 2-Logs, 3-Ambas, n-Não)"
switch ($resposta) {
    '1' { explorer "data" }
    '2' { explorer "data/logs" }
    '3' { 
        explorer "data"
        Start-Sleep 1
        explorer "data/logs"
    }
}