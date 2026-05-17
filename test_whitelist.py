#!/usr/bin/env python3
"""
Script para validar a whitelist centralizada
"""

import sys
from pathlib import Path

# Adicionar backend ao path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from whitelist import get_whitelist

def test_whitelist():
    print("🧪 Testando Whitelist Centralizada...\n")
    
    whitelist = get_whitelist()
    
    print("✅ Whitelist inicializada com sucesso!")
    print(f"\n📍 IPs exacros na whitelist:")
    for ip in whitelist.get_all_ips():
        print(f"   - {ip}")
    
    print(f"\n📍 Ranges CIDR na whitelist: {len(whitelist.get_all_cidrs())} ranges")
    
    # Testes de verificação
    print(f"\n🔍 Testes de verificação:")
    test_cases = [
        ("127.0.0.1", True, "loopback local"),
        ("192.168.1.100", True, "rede privada 192.168.x.x"),
        ("10.0.0.50", True, "rede privada 10.x.x.x"),
        ("172.16.50.1", True, "rede privada 172.16.x.x"),
        ("8.8.8.8", True, "Google DNS"),
        ("8.8.4.4", True, "Google DNS"),
        ("203.0.113.42", False, "IP público aleatório"),
        ("198.51.100.93", False, "IP público aleatório"),
    ]
    
    for ip, expected, desc in test_cases:
        result = whitelist.is_ip_whitelisted(ip)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {ip:20} → {result:5} ({desc})")
    
    print(f"\n✨ Teste completo!")

if __name__ == "__main__":
    test_whitelist()
