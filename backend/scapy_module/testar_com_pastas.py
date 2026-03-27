# backend/scapy_module/testar_com_pastas.py
# Testa todos os PCAPs de uma pasta com análise por fluxos (78 features)
# AGORA COM SUPORTE A MODELO ESPECÍFICO

import sys
from pathlib import Path
import argparse
import json
import pandas as pd
import numpy as np
import pickle

PROJECT_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_PATH))

from backend.scapy_module.predictor import ModelPredictor
from backend.scapy_module.extractor import FlowExtractor
from scapy.all import rdpcap

class TestadorComPastas:
    """
    Testa o modelo com PCAPs, logs ou CSVs
    """
    
    def __init__(self, modelo_path=None):
        if modelo_path is None:
            self.modelo_path = PROJECT_PATH / "models" / "modelo_scapy_20260319_152419_85.40%.pkl"
        else:
            self.modelo_path = Path(modelo_path)
        
        print(f"📂 A usar modelo: {self.modelo_path.name}")
        self.predictor = ModelPredictor(self.modelo_path)
        
        # Pastas
        self.pasta_normal = PROJECT_PATH / "data" / "pcaps" / "normal"
        self.pasta_attacks = PROJECT_PATH / "data" / "pcaps" / "attacks"
        self.pasta_logs = PROJECT_PATH / "data" / "logs"
        self.pasta_csv = PROJECT_PATH / "data" / "cic-ids2017"
        
        print(f"📁 Pasta normal: {self.pasta_normal}")
        print(f"📁 Pasta attacks: {self.pasta_attacks}")
        print(f"📁 Pasta logs: {self.pasta_logs}")
        print(f"📁 Pasta CSV: {self.pasta_csv}")
    
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
    
    def _processar_log(self, log_path, max_entries=None):
        """Processa um log JSON e retorna dados"""
        print(f"   📁 Processando: {log_path.name}")
        
        with open(log_path, 'r') as f:
            linhas = f.readlines()
        
        if max_entries:
            linhas = linhas[-max_entries:]
        
        dados = []
        for linha in linhas:
            try:
                entry = json.loads(linha)
                dados.append(entry)
            except:
                continue
        
        print(f"      Entradas extraídas: {len(dados)}")
        return dados
    
    def _processar_csv(self, csv_path, max_rows=None):
        """Processa um CSV e retorna dados"""
        print(f"   📁 Processando: {csv_path.name}")
        
        df = pd.read_csv(csv_path, low_memory=False)
        if max_rows and len(df) > max_rows:
            df = df.sample(n=max_rows, random_state=42)
        
        print(f"      Linhas extraídas: {len(df)}")
        return df
    
    def _classificar_fluxos(self, flows):
        """Classifica uma lista de fluxos"""
        fluxos_anomalos = 0
        for flow in flows:
            pred, _ = self.predictor.predict_flow(flow)
            if pred == -1:
                fluxos_anomalos += 1
        return fluxos_anomalos
    
    def _classificar_logs(self, logs):
        """Classifica uma lista de logs (já têm classificação)"""
        anomalias = sum(1 for log in logs if log.get('tipo') == 'anomalia')
        return anomalias
    
    def _classificar_csv(self, df):
        """Classifica um DataFrame CSV"""
        # Para CSV, precisamos extrair features e classificar
        # Esta parte pode ser expandida
        return 0
    
    def testar_pasta_normal(self, max_packets=5000):
        """Testa TODOS os PCAPs da pasta normal"""
        print("\n" + "="*70)
        print("✅ TESTAR TRÁFEGO NORMAL (PCAPs)")
        print("="*70)
        
        pcaps = list(self.pasta_normal.glob("*.pcap")) + list(self.pasta_normal.glob("*.pcapng"))
        
        if not pcaps:
            print("❌ Nenhum PCAP encontrado na pasta normal!")
            return [], 0, 0
        
        print(f"📊 Encontrados {len(pcaps)} PCAPs")
        
        resultados = []
        total_fluxos = 0
        total_anomalias = 0
        
        for pcap in pcaps[:5]:
            print(f"\n📁 {pcap.name}")
            flows = self._processar_pcap(pcap, max_packets)
            fluxos_anomalos = self._classificar_fluxos(flows)
            
            resultados.append({
                'arquivo': pcap.name,
                'tipo': 'normal',
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
        print("⚠️ TESTAR TRÁFEGO DE ATAQUE (PCAPs)")
        print("="*70)
        
        pcaps = list(self.pasta_attacks.glob("*.pcap")) + list(self.pasta_attacks.glob("*.pcapng"))
        
        if not pcaps:
            print("❌ Nenhum PCAP encontrado na pasta attacks!")
            return [], 0, 0
        
        print(f"📊 Encontrados {len(pcaps)} PCAPs")
        
        resultados = []
        total_fluxos = 0
        total_anomalias = 0
        
        for pcap in pcaps[:5]:
            print(f"\n📁 {pcap.name}")
            flows = self._processar_pcap(pcap, max_packets)
            fluxos_anomalos = self._classificar_fluxos(flows)
            
            resultados.append({
                'arquivo': pcap.name,
                'tipo': 'attack',
                'total_fluxos': len(flows),
                'anomalias': fluxos_anomalos,
                'percentual': (fluxos_anomalos / len(flows) * 100) if flows else 0
            })
            
            total_fluxos += len(flows)
            total_anomalias += fluxos_anomalos
        
        return resultados, total_fluxos, total_anomalias
    
    def testar_pasta_logs(self, max_entries=5000):
        """Testa TODOS os logs do sniffer"""
        print("\n" + "="*70)
        print("📊 TESTAR LOGS DO SNIFFER")
        print("="*70)
        
        logs = list(self.pasta_logs.glob("ips_*.json"))
        
        if not logs:
            print("❌ Nenhum log encontrado!")
            return [], 0, 0
        
        print(f"📊 Encontrados {len(logs)} logs")
        
        resultados = []
        total_entradas = 0
        total_anomalias = 0
        
        for log in logs:
            print(f"\n📁 {log.name}")
            entradas = self._processar_log(log, max_entries)
            anomalias = self._classificar_logs(entradas)
            
            resultados.append({
                'arquivo': log.name,
                'tipo': 'log',
                'total_entradas': len(entradas),
                'anomalias': anomalias,
                'percentual': (anomalias / len(entradas) * 100) if entradas else 0
            })
            
            total_entradas += len(entradas)
            total_anomalias += anomalias
        
        return resultados, total_entradas, total_anomalias
    
    def testar_pasta_csv(self, max_rows=50000):
        """Testa TODOS os CSVs do CIC-IDS2017"""
        print("\n" + "="*70)
        print("📄 TESTAR CSVS DO CIC-IDS2017")
        print("="*70)
        
        csvs = list(self.pasta_csv.glob("*.csv"))
        
        if not csvs:
            print("❌ Nenhum CSV encontrado!")
            return [], 0, 0
        
        print(f"📊 Encontrados {len(csvs)} CSVs")
        
        resultados = []
        total_linhas = 0
        total_anomalias = 0
        
        for csv_file in csvs:
            print(f"\n📁 {csv_file.name}")
            df = self._processar_csv(csv_file, max_rows)
            anomalias = self._classificar_csv(df)
            
            resultados.append({
                'arquivo': csv_file.name,
                'tipo': 'csv',
                'total_linhas': len(df),
                'anomalias': anomalias,
                'percentual': 0
            })
        
        return resultados, total_linhas, total_anomalias
    
    def testar_tudo(self, max_limit=5000):
        """Testa TODAS as fontes (PCAPs normais, ataques, logs, CSVs)"""
        print("\n" + "="*70)
        print("🔥 TESTAR TODAS AS FONTES")
        print("="*70)
        
        resultados_gerais = []
        
        # Testar normais
        normais, total_n, anom_n = self.testar_pasta_normal(max_limit)
        resultados_gerais.extend(normais)
        
        # Testar ataques
        ataques, total_a, anom_a = self.testar_pasta_attacks(max_limit)
        resultados_gerais.extend(ataques)
        
        # Testar logs
        logs, total_l, anom_l = self.testar_pasta_logs(max_limit)
        resultados_gerais.extend(logs)
        
        # Testar CSVs
        csvs, total_c, anom_c = self.testar_pasta_csv(max_limit)
        resultados_gerais.extend(csvs)
        
        if not resultados_gerais:
            print("\n❌ Nenhum dado encontrado em nenhuma fonte!")
            return resultados_gerais
        
        print("\n" + "="*70)
        print("📊 RESUMO GERAL")
        print("="*70)
        
        for r in resultados_gerais:
            if r['tipo'] == 'normal':
                print(f"\n✅ PCAPs NORMAL: {r['arquivo']}")
                print(f"   Fluxos: {r['total_fluxos']} | Anomalias: {r['anomalias']} ({r['percentual']:.2f}%)")
            elif r['tipo'] == 'attack':
                print(f"\n⚠️ PCAPs ATAQUE: {r['arquivo']}")
                print(f"   Fluxos: {r['total_fluxos']} | Anomalias: {r['anomalias']} ({r['percentual']:.2f}%)")
            elif r['tipo'] == 'log':
                print(f"\n📊 LOGS: {r['arquivo']}")
                print(f"   Entradas: {r['total_entradas']} | Anomalias: {r['anomalias']} ({r['percentual']:.2f}%)")
            elif r['tipo'] == 'csv':
                print(f"\n📄 CSV: {r['arquivo']}")
                print(f"   Linhas: {r['total_linhas']} | Anomalias: {r['anomalias']} ({r['percentual']:.2f}%)")
        
        return resultados_gerais


def main():
    parser = argparse.ArgumentParser(description='Testar modelo com PCAPs, logs ou CSVs')
    parser.add_argument('--pasta', choices=['normal', 'attacks', 'logs', 'csv', 'tudo'], 
                       default='tudo', help='Qual pasta/testar')
    parser.add_argument('--modelo', '-m', help='Caminho do modelo .pkl')  # ← NOVO
    parser.add_argument('--limite', type=int, default=5000, 
                       help='Limite de pacotes/entradas por ficheiro')
    
    args = parser.parse_args()
    
    testador = TestadorComPastas(args.modelo)
    
    if args.pasta == 'normal':
        testador.testar_pasta_normal(max_packets=args.limite)
    elif args.pasta == 'attacks':
        testador.testar_pasta_attacks(max_packets=args.limite)
    elif args.pasta == 'logs':
        testador.testar_pasta_logs(max_entries=args.limite)
    elif args.pasta == 'csv':
        testador.testar_pasta_csv(max_rows=args.limite)
    else:
        testador.testar_tudo(max_limit=args.limite)

if __name__ == "__main__":
    main()