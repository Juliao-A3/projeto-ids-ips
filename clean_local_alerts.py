#!/usr/bin/env python3
"""
Script para limpar alertas gerados pelo IP local (192.168.100.23)
durante testes de ataques web.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from backend.models import engine, Base, LogEvento, Alerta, IpsBloqueados, Session
from sqlalchemy.orm import sessionmaker

# IP local para remover alertas
LOCAL_IP = "192.168.100.23"

def limpar_alertas_locais():
    """Remove alertas e eventos gerados pela máquina local."""
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # 1. Contar alertas a remover
        alertas_removidos = session.query(Alerta).filter(
            (Alerta.ip_origem == LOCAL_IP) | (Alerta.ip_destino == LOCAL_IP)
        ).count()
        
        eventos_removidos = session.query(LogEvento).filter(
            (LogEvento.src_ip == LOCAL_IP) | (LogEvento.dest_ip == LOCAL_IP)
        ).count()
        
        ips_bloqueados_removidos = session.query(IpsBloqueados).filter(
            IpsBloqueados.ip_bloqueado == LOCAL_IP
        ).count()
        
        print(f"📊 Alertas a remover: {alertas_removidos}")
        print(f"📊 Eventos a remover: {eventos_removidos}")
        print(f"📊 IPs bloqueados a remover: {ips_bloqueados_removidos}")
        
        # 2. Confirmar operação
        resposta = input("\n⚠️  Confirmar limpeza? (s/n): ").strip().lower()
        if resposta != 's':
            print("❌ Operação cancelada.")
            return
        
        # 3. Remover eventos (isso remove alertas e análises em cascata)
        session.query(LogEvento).filter(
            (LogEvento.src_ip == LOCAL_IP) | (LogEvento.dest_ip == LOCAL_IP)
        ).delete(synchronize_session=False)
        
        # 4. Remover IPs bloqueados
        session.query(IpsBloqueados).filter(
            IpsBloqueados.ip_bloqueado == LOCAL_IP
        ).delete(synchronize_session=False)
        
        session.commit()
        
        print(f"\n✅ Limpeza concluída:")
        print(f"  - {alertas_removidos} alertas removidos")
        print(f"  - {eventos_removidos} eventos removidos")
        print(f"  - {ips_bloqueados_removidos} IPs bloqueados removidos")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erro durante limpeza: {e}")
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    print(f"🧹 Limpando alertas do IP local: {LOCAL_IP}\n")
    limpar_alertas_locais()
