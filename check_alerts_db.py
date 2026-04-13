#!/usr/bin/env python3
"""
Script para testar se alertas estão sendo salvos no BD
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from backend.dependencies import get_session
from backend.models import LogEvento, Alerta
from sqlalchemy import func
from datetime import datetime, timezone, timedelta

def check_alerts():
    """Verifica alertas salvos nos últimos 5 minutos"""
    
    try:
        session = next(get_session())
        
        # ✅ Total de LogEventos
        total_logs = session.query(LogEvento).count()
        print(f"[✓] Total de LogEventos na BD: {total_logs}")
        
        # ✅ Total de Alertas
        total_alertas = session.query(Alerta).count()
        print(f"[✓] Total de Alertas na BD: {total_alertas}")
        
        # ✅ Últimos 5 minutos
        cinco_min_atras = datetime.now(timezone.utc) - timedelta(minutes=5)
        logs_recentes = session.query(LogEvento).filter(
            LogEvento.timestamp >= cinco_min_atras
        ).count()
        print(f"[✓] LogEventos nos últimos 5 minutos: {logs_recentes}")
        
        alertas_recentes = session.query(Alerta).filter(
            Alerta.criado_em >= cinco_min_atras
        ).count()
        print(f"[✓] Alertas nos últimos 5 minutos: {alertas_recentes}")
        
        # ✅ Últimos eventos
        print("\n[📋] Últimos 5 eventos:")
        ultimos = session.query(LogEvento).order_by(
            LogEvento.timestamp.desc()
        ).limit(5).all()
        
        for log in ultimos:
            print(f"  - {log.timestamp}: {log.src_ip} → {log.dest_ip} ({log.protocolo}) [SeverID:{log.severidade}]")
        
        session.close()
        
    except Exception as e:
        print(f"[❌] Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("VERIFICAR ALERTAS NO BD")
    print("=" * 60)
    check_alerts()
