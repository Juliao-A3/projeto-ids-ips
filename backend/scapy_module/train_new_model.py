# backend/scapy_module/train_new_model.py
# Script para TREINAR NOVOS modelos com PCAPs, LOGS ou CSV (CIC-IDS2017)
# Suporta 78 features (fluxos)

import numpy as np
import pickle
from pathlib import Path
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
import sys
import json
import pandas as pd
import random

PROJECT_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_PATH))

from backend.scapy_module.extractor import FlowExtractor

class NovoModeloTrainer:
    """
    Treina NOVOS modelos com PCAPs, LOGS do Sniffer ou CSV (CIC-IDS2017)
    """
    
    def __init__(self, feature_names=None):
        self.flow_extractor = FlowExtractor()
        self.project_root = PROJECT_PATH
        self.models_folder = self.project_root / "models"
        self.pcaps_normal = self.project_root / "data" / "pcaps" / "normal"
        self.pcaps_attacks = self.project_root / "data" / "pcaps" / "attacks"
        self.logs_dir = self.project_root / "data" / "logs"
        self.csv_dir = self.project_root / "data" / "cic-ids2017"
        
        # Criar pastas
        self.models_folder.mkdir(exist_ok=True)
        self.pcaps_normal.parent.mkdir(parents=True, exist_ok=True)
        self.pcaps_normal.mkdir(exist_ok=True)
        self.pcaps_attacks.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        self.csv_dir.mkdir(exist_ok=True)
        
        # Feature names (78 features do CIC-IDS2017)
        if feature_names:
            self.feature_names = feature_names
        else:
            self.feature_names = self.flow_extractor.get_feature_names()
    
    # ========== CARREGAR DADOS DOS LOGS DO SNIFFER ==========
    def carregar_logs_sniffer(self, max_entries=5000):
        """Carrega dados dos logs do sniffer (fluxos)"""
        print("\n" + "="*70)
        print("📊 CARREGAR DADOS DOS LOGS DO SNIFFER")
        print("="*70)
        
        logs_files = list(self.logs_dir.glob("ips_*.json"))
        
        if not logs_files:
            print("❌ Nenhum log encontrado em data/logs/")
            return None, None
        
        print(f"📁 Encontrados {len(logs_files)} ficheiros de log")
        ultimo_log = max(logs_files, key=lambda x: x.stat().st_mtime)
        print(f"📂 Usando log: {ultimo_log.name}")
        
        try:
            with open(ultimo_log, 'r') as f:
                linhas = f.readlines()
                
            dados = []
            labels = []
            
            for linha in linhas[-max_entries:]:
                try:
                    entry = json.loads(linha)
                    total_fluxos = entry.get('total_fluxos', 0)
                    anomalias = entry.get('anomalias', 0)
                    
                    # Simular dados (substituir quando tiveres dados reais)
                    for _ in range(min(100, total_fluxos)):
                        # Criar um fluxo simulado
                        feat = [0] * len(self.feature_names)
                        # Simulação básica
                        for i in range(len(feat)):
                            feat[i] = random.random()
                        
                        dados.append(feat)
                        labels.append(1 if random.random() < (anomalias/total_fluxos if total_fluxos > 0 else 0.1) else 0)
                except:
                    continue
            
            if not dados:
                print("❌ Não foi possível extrair dados dos logs")
                return None, None
            
            X = np.array(dados, dtype=np.float32)
            y = np.array(labels)
            
            print(f"✅ Dados extraídos: {len(X)} amostras")
            print(f"   Normais: {sum(y==0)} ({sum(y==0)/len(y)*100:.1f}%)")
            print(f"   Anomalias: {sum(y==1)} ({sum(y==1)/len(y)*100:.1f}%)")
            print(f"   Features: {X.shape[1]}")
            
            return X, y
            
        except Exception as e:
            print(f"❌ Erro ao carregar logs: {e}")
            return None, None
    
    # ========== CARREGAR DADOS DOS PCAPS ==========
    def preparar_dados_pcaps(self, max_packets_per_pcap=2000):
        """Prepara dados de treino a partir dos PCAPs (fluxos)"""
        print("\n" + "="*70)
        print("📊 PREPARAR DADOS DOS PCAPS (FLUXOS)")
        print("="*70)
        
        todas_features = []
        todas_labels = []
        
        print("\n📊 PROCESSAR TRÁFEGO NORMAL")
        pcaps_normais = list(self.pcaps_normal.glob("*.pcap")) + list(self.pcaps_normal.glob("*.pcapng"))
        
        if not pcaps_normais:
            print("⚠️ Nenhum PCAP normal encontrado!")
        
        for pcap in pcaps_normais[:3]:  # Limitar a 3 PCAPs para testes
            print(f"\n📁 {pcap.name}")
            # Usar FlowExtractor para processar o PCAP
            flow_extractor = FlowExtractor()
            
            # Ler PCAP e extrair fluxos
            from scapy.all import rdpcap
            packets = rdpcap(str(pcap))
            
            for pkt in packets[:max_packets_per_pcap]:
                flow_extractor.process_packet(pkt, pkt.time)
            
            # Obter fluxos completados
            flows = flow_extractor.get_completed_flows()
            
            for flow in flows:
                features = flow.get_features()
                feature_values = list(features.values())
                todas_features.append(feature_values)
                todas_labels.append(0)  # normal
            
            print(f"   ✅ Adicionados {len(flows)} fluxos normais")
        
        print("\n⚠️ PROCESSAR ATAQUES")
        pcaps_ataques = list(self.pcaps_attacks.glob("*.pcap")) + list(self.pcaps_attacks.glob("*.pcapng"))
        
        if not pcaps_ataques:
            print("⚠️ Nenhum PCAP de ataque encontrado!")
        
        for pcap in pcaps_ataques[:3]:  # Limitar a 3 PCAPs para testes
            print(f"\n📁 {pcap.name}")
            flow_extractor = FlowExtractor()
            
            from scapy.all import rdpcap
            packets = rdpcap(str(pcap))
            
            for pkt in packets[:max_packets_per_pcap]:
                flow_extractor.process_packet(pkt, pkt.time)
            
            flows = flow_extractor.get_completed_flows()
            
            for flow in flows:
                features = flow.get_features()
                feature_values = list(features.values())
                todas_features.append(feature_values)
                todas_labels.append(1)  # ataque
            
            print(f"   ✅ Adicionados {len(flows)} fluxos de ataque")
        
        if not todas_features:
            print("❌ Nenhum dado extraído!")
            return None, None
        
        X_final = np.array(todas_features, dtype=np.float32)
        y_final = np.array(todas_labels)
        
        # Embaralhar
        idx = np.random.permutation(len(X_final))
        X_final = X_final[idx]
        y_final = y_final[idx]
        
        print("\n" + "="*70)
        print("✅ DATASET CRIADO")
        print(f"   Total amostras: {len(X_final)}")
        print(f"   Normais: {sum(y_final==0)} ({sum(y_final==0)/len(y_final)*100:.1f}%)")
        print(f"   Anomalias: {sum(y_final==1)} ({sum(y_final==1)/len(y_final)*100:.1f}%)")
        print(f"   Features: {X_final.shape[1]}")
        
        return X_final, y_final
    
    # ========== CARREGAR DADOS DO CSV (CIC-IDS2017) ==========
    def carregar_csv_cicids2017(self, csv_path=None):
        """
        Carrega dados do CSV do CIC-IDS2017 (78 features)
        """
        print("\n" + "="*70)
        print("📊 CARREGAR DADOS DO CIC-IDS2017 (CSV)")
        print("="*70)
        
        if csv_path is None:
            csv_files = list(self.csv_dir.glob("*.csv"))
            if not csv_files:
                print("❌ Nenhum CSV encontrado em data/cic-ids2017/")
                print("   Descarregue os CSVs de: https://www.kaggle.com/datasets/cicdataset/cicids2017")
                return None, None
            
            print("\n📁 CSVs disponíveis:")
            for i, f in enumerate(csv_files):
                size_mb = f.stat().st_size / 1024 / 1024
                print(f"   {i+1}. {f.name} ({size_mb:.1f} MB)")
            
            escolha = input("\nEscolha o número do CSV (ou 0 para cancelar): ").strip()
            if escolha == '0':
                return None, None
            try:
                csv_path = csv_files[int(escolha) - 1]
            except:
                print("❌ Opção inválida")
                return None, None
        
        print(f"\n📂 A carregar: {csv_path.name}")
        
        try:
            # Ler CSV
            df = pd.read_csv(csv_path, low_memory=False)
            print(f"✅ CSV carregado: {df.shape[0]} linhas, {df.shape[1]} colunas")
            
            # Identificar coluna de label
            label_col = None
            for col in df.columns:
                if 'label' in col.lower() or 'Label' in col:
                    label_col = col
                    break
            
            if label_col is None:
                print("⚠️ Não foi encontrada coluna de label")
                print(f"   Colunas disponíveis: {list(df.columns)[:10]}...")
                return None, None
            
            print(f"📋 Coluna de label: {label_col}")
            
            # Mapear labels
            df['label_binary'] = df[label_col].apply(
                lambda x: 0 if str(x).upper() in ['BENIGN', 'NORMAL', 'BENING'] else 1
            )
            
            # Selecionar colunas de features (todas exceto label)
            feature_cols = [col for col in df.columns if col not in [label_col, 'label_binary']]
            
            # Filtrar apenas as features que temos no extractor
            available_features = []
            for target_feat in self.feature_names:
                for col in feature_cols:
                    if target_feat in col or col in target_feat:
                        available_features.append(col)
                        break
            
            if not available_features:
                print("⚠️ Nenhuma feature correspondente encontrada")
                print(f"   Usando primeiras {min(78, len(feature_cols))} features...")
                available_features = feature_cols[:78]
            
            X = df[available_features].values
            y = df['label_binary'].values
            
            # Normalizar
            scaler = StandardScaler()
            X = scaler.fit_transform(X)
            
            # Limitar número de amostras
            max_samples = 50000
            if len(X) > max_samples:
                print(f"📊 A reduzir de {len(X)} para {max_samples} amostras...")
                indices = np.random.choice(len(X), max_samples, replace=False)
                X = X[indices]
                y = y[indices]
            
            print(f"\n✅ Dados preparados: {len(X)} amostras")
            print(f"   Normais: {sum(y==0)} ({sum(y==0)/len(y)*100:.1f}%)")
            print(f"   Anomalias: {sum(y==1)} ({sum(y==1)/len(y)*100:.1f}%)")
            print(f"   Features: {X.shape[1]}")
            
            return X, y
            
        except Exception as e:
            print(f"❌ Erro ao carregar CSV: {e}")
            return None, None
    
    # ========== TREINO DO MODELO ==========
    def treinar_novo_modelo(self, X, y, contamination=0.15, test_size=0.25):
        """Treina um NOVO modelo e guarda como .pkl"""
        print("\n" + "="*70)
        print("🚀 TREINAR NOVO MODELO (78 features)")
        print("="*70)
        
        if X is None or y is None:
            return None
        
        # Dividir treino/teste
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"\n📊 Divisão dos dados:")
        print(f"   Treino: {X_train.shape[0]} amostras")
        print(f"   Teste: {X_test.shape[0]} amostras")
        print(f"   Features: {X_train.shape[1]}")
        
        # Normalizar
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        print("\n🔄 A treinar Isolation Forest...")
        model = IsolationForest(
            n_estimators=200,
            contamination=contamination,
            random_state=42,
            n_jobs=-1,
            verbose=0
        )
        
        model.fit(X_train_scaled)
        print("✅ Modelo treinado!")
        
        # Avaliar
        y_pred = model.predict(X_test_scaled)
        y_pred_binary = np.where(y_pred == 1, 0, 1)
        
        acuracia = accuracy_score(y_test, y_pred_binary)
        cm = confusion_matrix(y_test, y_pred_binary)
        
        print("\n" + "="*70)
        print("📊 RESULTADOS DO NOVO MODELO")
        print("="*70)
        print(f"🎯 ACURÁCIA: {acuracia*100:.2f}%")
        
        print("\n📊 Matriz de Confusão:")
        print("                 Predito")
        print("                Normal  Anomalia")
        print(f"Real Normal     {cm[0,0]:6d}  {cm[0,1]:6d}")
        print(f"     Anomalia   {cm[1,0]:6d}  {cm[1,1]:6d}")
        
        # Guardar novo modelo
        self._guardar_modelo(model, scaler, acuracia, X.shape[1])
        
        return model, acuracia
    
    def _guardar_modelo(self, model, scaler, acuracia, n_features):
        """Guarda o novo modelo na pasta models"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"modelo_fluxo_{timestamp}_{acuracia*100:.2f}%.pkl"
        modelo_path = self.models_folder / nome_arquivo
        
        dados_modelo = {
            'modelo': model,
            'scaler': scaler,
            'feature_names': self.feature_names,
            'acuracia': acuracia,
            'data_treino': datetime.now().isoformat(),
            'n_features': n_features,
            'versao': 'fluxo_80_features',
            'info': f'Modelo treinado com {n_features} features (fluxos)'
        }
        
        with open(modelo_path, 'wb') as f:
            pickle.dump(dados_modelo, f)
        
        print(f"\n💾 NOVO modelo guardado: {modelo_path}")
        print(f"🎯 Acurácia: {acuracia*100:.2f}%")
        print(f"📋 Features guardadas: {len(self.feature_names)}")


def main():
    """Função principal para treinar novo modelo"""
    print("="*70)
    print("🔧 TREINAR NOVO MODELO (78 FEATURES - FLUXOS)")
    print("="*70)
    
    # Perguntar origem dos dados
    print("\n📊 ORIGEM DOS DADOS:")
    print("   1. PCAPs (ficheiros .pcap/.pcapng em data/pcaps/)")
    print("   2. Logs do Sniffer (dados em tempo real de data/logs/)")
    print("   3. CSV do CIC-IDS2017 (data/cic-ids2017/)")
    
    origem = input("\nEscolhe a origem (1-3): ").strip()
    
    # Perguntar features
    print("\n📋 Configuração de features:")
    print("   1. Usar features padrão (78 features do CIC-IDS2017)")
    print("   2. Definir novas features manualmente")
    
    opcao = input("\nEscolhe uma opção (1-2): ").strip()
    
    feature_names = None
    if opcao == '2':
        print("\n📝 Definir features manualmente:")
        n = int(input("Quantas features? "))
        feature_names = []
        for i in range(n):
            nome = input(f"Feature {i}: ")
            feature_names.append(nome)
        print(f"✅ Definidas {len(feature_names)} features")
    
    # Criar trainer
    trainer = NovoModeloTrainer(feature_names)
    
    # Preparar dados conforme origem
    if origem == '1':
        print("\n📁 Usando PCAPs como fonte de dados")
        X, y = trainer.preparar_dados_pcaps()
    elif origem == '2':
        print("\n📊 Usando logs do Sniffer como fonte de dados")
        X, y = trainer.carregar_logs_sniffer()
    elif origem == '3':
        print("\n📄 Usando CSV do CIC-IDS2017 como fonte de dados")
        X, y = trainer.carregar_csv_cicids2017()
    else:
        print("❌ Opção inválida")
        return
    
    if X is None:
        print("\n❌ Não foi possível preparar os dados!")
        return
    
    # Treinar
    trainer.treinar_novo_modelo(X, y)

if __name__ == "__main__":
    main()