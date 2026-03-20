# Script para TESTAR modelo com TODOS os PCAPs das pastas normal e attacks Suporta .pcap e .pcapng

import sys
from pathlib import Path
from datetime import datetime
import json

PROJECT_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_PATH))

from backend.scapy_module.predictor import ModelPredictor

class TestadorComPastas:
    """
    Testa o modelo com PCAPs das pastas normal e attacks (suporta .pcap e .pcapng)
    """
    
    def __init__(self, modelo_path=None):
        if modelo_path is None:
            self.modelo_path = PROJECT_PATH / "models" / "best_model.pkl"
        else:
            self.modelo_path = Path(modelo_path)
        
        print(f"📂 A usar modelo: {self.modelo_path.name}")
        self.predictor = ModelPredictor(self.modelo_path)
        
        # Pastas de PCAPs
        self.pasta_normal = PROJECT_PATH / "data" / "pcaps" / "normal"
        self.pasta_attacks = PROJECT_PATH / "data" / "pcaps" / "attacks"
        
        print(f"📁 Pasta normal: {self.pasta_normal}")
        print(f"📁 Pasta attacks: {self.pasta_attacks}")
    
    def testar_pasta_normal(self, max_packets=5000):
        """
        Testa TODOS os PCAPs da pasta normal (suporta .pcap e .pcapng)
        """
        print("\n" + "="*70)
        print("✅ TESTAR TRÁFEGO NORMAL")
        print("="*70)
        
        pcaps = list(self.pasta_normal.glob("*.pcap")) + list(self.pasta_normal.glob("*.pcapng"))
        
        if not pcaps:
            print("❌ Nenhum PCAP encontrado na pasta normal!")
            return []
        
        print(f"📊 Encontrados {len(pcaps)} PCAPs")
        
        resultados = []
        for pcap in pcaps:
            print(f"\n📁 Testando: {pcap.name}")
            res = self.predictor.predict_pcap(pcap, max_packets=max_packets)
            if res:
                res['tipo'] = 'normal'
                res['arquivo'] = pcap.name
                resultados.append(res)
        
        return resultados
    
    def testar_pasta_attacks(self, max_packets=5000):
        """
        Testa TODOS os PCAPs da pasta attacks (suporta .pcap e .pcapng)
        """
        print("\n" + "="*70)
        print("⚠️ TESTAR TRÁFEGO DE ATAQUE")
        print("="*70)
        
        pcaps = list(self.pasta_attacks.glob("*.pcap")) + list(self.pasta_attacks.glob("*.pcapng"))
        
        if not pcaps:
            print("❌ Nenhum PCAP encontrado na pasta attacks!")
            return []
        
        print(f"📊 Encontrados {len(pcaps)} PCAPs")
        
        resultados = []
        for pcap in pcaps:
            print(f"\n📁 Testando: {pcap.name}")
            res = self.predictor.predict_pcap(pcap, max_packets=max_packets)
            if res:
                res['tipo'] = 'attack'
                res['arquivo'] = pcap.name
                resultados.append(res)
        
        return resultados
    
    def testar_ambas_pastas(self, max_packets=5000):
        """
        Testa PCAPs de AMBAS as pastas e mostra comparação
        """
        print("\n" + "="*70)
        print("🔍 TESTAR AMBAS AS PASTAS")
        print("="*70)
        
        normais = self.testar_pasta_normal(max_packets)
        ataques = self.testar_pasta_attacks(max_packets)
        
        self.mostrar_resumo(normais, ataques)
        self.guardar_resultados(normais, ataques)
        
        return normais, ataques
    
    def mostrar_resumo(self, normais, ataques):
        """
        Mostra resumo comparativo dos resultados
        """
        print("\n" + "="*70)
        print("📊 RESUMO COMPARATIVO")
        print("="*70)
        
        if normais:
            total_normais = sum(r['total_pacotes'] for r in normais)
            anomalias_normais = sum(r['anomalias'] for r in normais)
            print(f"\n✅ TRÁFEGO NORMAL:")
            print(f"   Total PCAPs: {len(normais)}")
            print(f"   Total pacotes: {total_normais}")
            print(f"   Total anomalias: {anomalias_normais}")
            print(f"   Percentual médio: {anomalias_normais/total_normais*100:.2f}%")
        
        if ataques:
            total_ataques = sum(r['total_pacotes'] for r in ataques)
            anomalias_ataques = sum(r['anomalias'] for r in ataques)
            print(f"\n⚠️ TRÁFEGO DE ATAQUE:")
            print(f"   Total PCAPs: {len(ataques)}")
            print(f"   Total pacotes: {total_ataques}")
            print(f"   Total anomalias: {anomalias_ataques}")
            print(f"   Percentual médio: {anomalias_ataques/total_ataques*100:.2f}%")
    
    def guardar_resultados(self, normais, ataques):
        """Guarda resultados em JSON na pasta data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        resultados_path = PROJECT_PATH / "data" / f"teste_completo_{timestamp}.json"
        
        dados = {
            'data_teste': datetime.now().isoformat(),
            'modelo': str(self.modelo_path),
            'resultados_normais': normais,
            'resultados_ataques': ataques
        }
        
        with open(resultados_path, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados em: {resultados_path}")


# Interface linha de comando
if __name__ == "__main__":
    import argparse
    
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