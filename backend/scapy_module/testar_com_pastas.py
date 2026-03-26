# backend/scapy_module/testar_com_pastas.py
# Testa todos os PCAPs de uma pasta com análise por fluxos (78 features)

import sys
from pathlib import Path
import argparse
import json
from datetime import datetime

PROJECT_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_PATH))

from backend.scapy_module.predictor import ModelPredictor
from backend.scapy_module.extractor import FlowExtractor
from scapy.all import rdpcap

class TestadorComPastas:
    """
    Testa o modelo com PCAPs das pastas normal e attacks (análise por fluxos)
    """
    
    def __init__(self, modelo_path=None):
        if modelo_path is None:
            self.modelo_path = PROJECT_PATH / "models" / "modelo_principal.pkl"
        else:
            self.modelo_path = Path(modelo_path)
        
        print(f"📂 A usar modelo: {self.modelo_path.name}")
        self.predictor = ModelPredictor(self.modelo_path)
        
        self.pasta_normal = PROJECT_PATH / "data" / "pcaps" / "normal"
        self.pasta_attacks = PROJECT_PATH / "data" / "pcaps" / "attacks"
        
        print(f"📁 Pasta normal: {self.pasta_normal}")
        print(f"📁 Pasta attacks: {self.pasta_attacks}")
    
    def _processar_pcap(self, pcap_path, max_packets=None):
        """Processa um PCAP e retorna fluxos"""
        print(f"   📁 Processando: {pcap_path.name}")
        
        packets = rdpcap(str(pcap_path))
        if max_packets and len(packets) > max_packets:
            packets = packets[:max_packets]
        
        flow_extractor = FlowExtractor()
        for pkt in packets:
            flow_extractor.process_packet(pkt, pkt.time)
        
        flows = flow_extractor.get_completed_flows()
        print(f"      Fluxos extraídos: {len(flows)}")
        
        return flows
    
    def testar_pasta_normal(self, max_packets=5000):
        """Testa TODOS os PCAPs da pasta normal"""
        print("\n" + "="*70)
        print("✅ TESTAR TRÁFEGO NORMAL (deve ter POUCAS anomalias)")
        print("="*70)
        
        pcaps = list(self.pasta_normal.glob("*.pcap")) + list(self.pasta_normal.glob("*.pcapng"))
        
        if not pcaps:
            print("❌ Nenhum PCAP encontrado na pasta normal!")
            return []
        
        print(f"📊 Encontrados {len(pcaps)} PCAPs")
        
        resultados = []
        total_fluxos = 0
        total_anomalias = 0
        
        for pcap in pcaps[:5]:  # Limitar a 5 PCAPs
            print(f"\n📁 {pcap.name}")
            flows = self._processar_pcap(pcap, max_packets)
            
            fluxos_anomalos = 0
            for flow in flows:
                pred, _ = self.predictor.predict_flow(flow)
                if pred == -1:
                    fluxos_anomalos += 1
            
            resultados.append({
                'arquivo': pcap.name,
                'total_fluxos': len(flows),
                'anomalias': fluxos_anomalos,
                'percentual': (fluxos_anomalos / len(flows) * 100) if flows else 0
            })
            
            total_fluxos += len(flows)
            total_anomalias += fluxos_anomalos
        
        return resultados, total_fluxos, total_anomalias
    
    def testar_pasta_attacks(self, max_packets=5000):
        """Testa TODOS os PCAPs da pasta attacks"""
        print("\n" + "="*70)
        print("⚠️ TESTAR TRÁFEGO DE ATAQUE (deve ter MUITAS anomalias)")
        print("="*70)
        
        pcaps = list(self.pasta_attacks.glob("*.pcap")) + list(self.pasta_attacks.glob("*.pcapng"))
        
        if not pcaps:
            print("❌ Nenhum PCAP encontrado na pasta attacks!")
            return []
        
        print(f"📊 Encontrados {len(pcaps)} PCAPs")
        
        resultados = []
        total_fluxos = 0
        total_anomalias = 0
        
        for pcap in pcaps[:5]:  # Limitar a 5 PCAPs
            print(f"\n📁 {pcap.name}")
            flows = self._processar_pcap(pcap, max_packets)
            
            fluxos_anomalos = 0
            for flow in flows:
                pred, _ = self.predictor.predict_flow(flow)
                if pred == -1:
                    fluxos_anomalos += 1
            
            resultados.append({
                'arquivo': pcap.name,
                'total_fluxos': len(flows),
                'anomalias': fluxos_anomalos,
                'percentual': (fluxos_anomalos / len(flows) * 100) if flows else 0
            })
            
            total_fluxos += len(flows)
            total_anomalias += fluxos_anomalos
        
        return resultados, total_fluxos, total_anomalias
    
    def testar_ambas_pastas(self, max_packets=5000):
        """Testa PCAPs de AMBAS as pastas e mostra comparação"""
        print("\n" + "="*70)
        print("🔍 TESTAR AMBAS AS PASTAS")
        print("="*70)
        
        normais, total_normais, anom_normais = self.testar_pasta_normal(max_packets)
        ataques, total_ataques, anom_ataques = self.testar_pasta_attacks(max_packets)
        
        print("\n" + "="*70)
        print("📊 RESUMO COMPARATIVO")
        print("="*70)
        
        if normais:
            print(f"\n✅ TRÁFEGO NORMAL:")
            print(f"   Total fluxos: {total_normais}")
            print(f"   Anomalias: {anom_normais} ({anom_normais/total_normais*100:.2f}%)")
        
        if ataques:
            print(f"\n⚠️ TRÁFEGO DE ATAQUE:")
            print(f"   Total fluxos: {total_ataques}")
            print(f"   Anomalias: {anom_ataques} ({anom_ataques/total_ataques*100:.2f}%)")
        
        return normais, ataques


def main():
    parser = argparse.ArgumentParser(description='Testar modelo com PCAPs')
    parser.add_argument('--pasta', choices=['normal', 'attacks', 'ambas'], 
                       default='ambas', help='Qual pasta testar')
    parser.add_argument('--modelo', help='Caminho do modelo .pkl')
    parser.add_argument('--limite', type=int, default=5000, 
                       help='Limite de pacotes por PCAP')
    
    args = parser.parse_args()
    
    testador = TestadorComPastas(args.modelo)
    
    if args.pasta == 'normal':
        testador.testar_pasta_normal(max_packets=args.limite)
    elif args.pasta == 'attacks':
        testador.testar_pasta_attacks(max_packets=args.limite)
    else:
        testador.testar_ambas_pastas(max_packets=args.limite)

if __name__ == "__main__":
    main()