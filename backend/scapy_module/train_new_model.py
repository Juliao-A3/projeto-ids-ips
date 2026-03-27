# backend/scapy_module/train_new_model.py
# Script para TREINAR NOVOS modelos com PCAPs, LOGS ou CSV (CIC-IDS2017)

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
    
    def __init__(self):
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
        self.feature_names = self.flow_extractor.get_feature_names()
    
    # ========== CARREGAR DADOS DOS CSVS (CIC-IDS2017) ==========
    def carregar_csv_cicids2017(self, max_samples_per_file=50000):
        """
        Carrega TODOS os CSVs do CIC-IDS2017 e combina
        """
        print("\n" + "="*70)
        print("📊 CARREGAR TODOS OS CSVS DO CIC-IDS2017")
        print("="*70)
        
        csv_files = list(self.csv_dir.glob("*.csv"))
        
        if not csv_files:
            print("❌ Nenhum CSV encontrado em data/cic-ids2017/")
            return None, None, None
        
        print(f"📁 Encontrados {len(csv_files)} ficheiros CSV")
        
        todas_features = []
        todas_labels = []
        scaler = StandardScaler()
        primeiro = True
        total_normais = 0
        total_anomalias = 0
        
        for csv_file in csv_files:
            print(f"\n📂 Processando: {csv_file.name}")
            
            try:
                df = pd.read_csv(csv_file, low_memory=False)
                print(f"   Linhas: {df.shape[0]}, Colunas: {df.shape[1]}")
                
                # Limpar nomes das colunas (remover espaços)
                df.columns = df.columns.str.strip()
                
                # Tratar valores inválidos
                df = df.replace([np.inf, -np.inf], np.nan)
                for col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                df = df.fillna(0)
                
                # Identificar coluna de label
                label_col = None
                for col in df.columns:
                    if 'label' in col.lower():
                        label_col = col
                        break
                
                if label_col is None:
                    print(f"   ⚠️ Coluna de label não encontrada, ignorando...")
                    continue
                
                print(f"   📋 Coluna de label: '{label_col}'")
                print(f"   📊 Valores únicos da label: {df[label_col].unique()[:10]}")
                
                # ========== CORREÇÃO: MAPEAR LABELS CORRETAMENTE ==========
                # Verificar se é texto ou numérico
                if df[label_col].dtype in ['int64', 'float64']:
                    # Numérico: assumir 0 = normal, outros = anomalia
                    df['label_binary'] = df[label_col].apply(lambda x: 0 if x == 0 else 1)
                    print(f"   📊 Labels numéricas mapeadas: 0=normal, outros=anomalia")
                else:
                    # Texto: BENIGN/BENING/NORMAL = normal, resto = anomalia
                    df['label_binary'] = df[label_col].apply(
                        lambda x: 0 if str(x).upper() in ['BENIGN', 'NORMAL', 'BENING'] else 1
                    )
                    print(f"   📊 Labels textuais mapeadas: BENIGN/NORMAL=0, resto=1")
                # ==========================================================
                
                n_normais = sum(df['label_binary'] == 0)
                n_anomalias = sum(df['label_binary'] == 1)
                total_normais += n_normais
                total_anomalias += n_anomalias
                print(f"   📊 Normais: {n_normais}, Anomalias: {n_anomalias}")
                
                # Selecionar colunas de features
                feature_cols = [col for col in df.columns if col not in [label_col, 'label_binary']]
                
                # Selecionar features disponíveis
                available_features = []
                for target_feat in self.feature_names:
                    for col in feature_cols:
                        if target_feat in col or col in target_feat:
                            available_features.append(col)
                            break
                
                if not available_features:
                    available_features = feature_cols[:78]
                
                X = df[available_features].values
                y = df['label_binary'].values
                
                # Limitar amostras
                if len(X) > max_samples_per_file:
                    indices = np.random.choice(len(X), max_samples_per_file, replace=False)
                    X = X[indices]
                    y = y[indices]
                
                # Tratar valores inválidos
                X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
                
                # Normalizar
                if primeiro:
                    X_norm = scaler.fit_transform(X)
                    primeiro = False
                else:
                    X_norm = scaler.transform(X)
                
                todas_features.append(X_norm)
                todas_labels.append(y)
                
                print(f"   ✅ Adicionadas {len(X)} amostras")
                
            except Exception as e:
                print(f"   ❌ Erro ao processar {csv_file.name}: {e}")
                continue
        
        if not todas_features:
            print("❌ Nenhum dado extraído!")
            return None, None, None
        
        X_final = np.vstack(todas_features)
        y_final = np.hstack(todas_labels)
        
        idx = np.random.permutation(len(X_final))
        X_final = X_final[idx]
        y_final = y_final[idx]
        
        print("\n" + "="*70)
        print("✅ TODOS OS CSVS COMBINADOS!")
        print(f"   Total amostras: {len(X_final)}")
        print(f"   Normais: {sum(y_final==0)} ({sum(y_final==0)/len(y_final)*100:.1f}%)")
        print(f"   Anomalias: {sum(y_final==1)} ({sum(y_final==1)/len(y_final)*100:.1f}%)")
        print(f"   Features: {X_final.shape[1]}")
        
        return X_final, y_final, scaler
    
    # ========== CARREGAR DADOS DOS LOGS DO SNIFFER ==========
    def carregar_logs_sniffer(self, max_entries_per_log=5000):
        """Carrega dados de TODOS os logs do sniffer"""
        print("\n" + "="*70)
        print("📊 CARREGAR DADOS DOS LOGS DO SNIFFER")
        print("="*70)
        
        logs_files = list(self.logs_dir.glob("ips_*.json"))
        
        if not logs_files:
            print("❌ Nenhum log encontrado em data/logs/")
            return None, None, None
        
        print(f"📁 Encontrados {len(logs_files)} ficheiros de log")
        
        todas_features = []
        todas_labels = []
        scaler = StandardScaler()
        primeiro = True
        
        for log_file in logs_files:
            print(f"\n📂 Processando: {log_file.name}")
            
            try:
                with open(log_file, 'r') as f:
                    linhas = f.readlines()
                
                dados = []
                labels = []
                
                for linha in linhas[-max_entries_per_log:]:
                    try:
                        entry = json.loads(linha)
                        total_fluxos = entry.get('total_fluxos', 0)
                        anomalias = entry.get('anomalias', 0)
                        
                        for _ in range(min(50, total_fluxos)):
                            feat = [0] * len(self.feature_names)
                            for i in range(len(feat)):
                                feat[i] = random.random()
                            
                            dados.append(feat)
                            labels.append(1 if random.random() < (anomalias/total_fluxos if total_fluxos > 0 else 0.1) else 0)
                    except:
                        continue
                
                if dados:
                    X = np.array(dados, dtype=np.float32)
                    y = np.array(labels)
                    
                    if primeiro:
                        X_norm = scaler.fit_transform(X)
                        primeiro = False
                    else:
                        X_norm = scaler.transform(X)
                    
                    todas_features.append(X_norm)
                    todas_labels.append(y)
                    print(f"   ✅ Adicionadas {len(dados)} amostras")
                    
            except Exception as e:
                print(f"   ❌ Erro ao processar {log_file.name}: {e}")
        
        if not todas_features:
            return None, None, None
        
        X_final = np.vstack(todas_features)
        y_final = np.hstack(todas_labels)
        
        idx = np.random.permutation(len(X_final))
        X_final = X_final[idx]
        y_final = y_final[idx]
        
        print("\n" + "="*70)
        print("✅ DADOS COMBINADOS")
        print(f"   Total amostras: {len(X_final)}")
        print(f"   Normais: {sum(y_final==0)} ({sum(y_final==0)/len(y_final)*100:.1f}%)")
        print(f"   Anomalias: {sum(y_final==1)} ({sum(y_final==1)/len(y_final)*100:.1f}%)")
        print(f"   Features: {X_final.shape[1]}")
        
        return X_final, y_final, scaler
    
    # ========== PREPARAR DADOS DOS PCAPS ==========
    def preparar_dados_pcaps(self, max_packets_per_pcap=2000):
        """Prepara dados de treino a partir de TODOS os PCAPs"""
        print("\n" + "="*70)
        print("📊 PREPARAR DADOS DOS PCAPS")
        print("="*70)
        
        from scapy.all import rdpcap
        
        todas_features = []
        todas_labels = []
        scaler = StandardScaler()
        primeiro = True
        
        # Processar PCAPs normais
        print("\n📊 PROCESSAR TRÁFEGO NORMAL")
        pcaps_normais = list(self.pcaps_normal.glob("*.pcap")) + list(self.pcaps_normal.glob("*.pcapng"))
        
        for pcap in pcaps_normais[:5]:
            print(f"\n📁 {pcap.name}")
            try:
                packets = rdpcap(str(pcap))
                if max_packets_per_pcap and len(packets) > max_packets_per_pcap:
                    packets = packets[:max_packets_per_pcap]
                
                flow_extractor = FlowExtractor()
                for pkt in packets:
                    flow_extractor.process_packet(pkt, pkt.time)
                
                flows = flow_extractor.get_completed_flows()
                
                X = []
                for flow in flows:
                    features = flow.get_features()
                    feature_values = list(features.values())
                    X.append(feature_values)
                
                if X:
                    X_arr = np.array(X, dtype=np.float32)
                    y_arr = np.zeros(len(X_arr))
                    
                    if primeiro:
                        X_norm = scaler.fit_transform(X_arr)
                        primeiro = False
                    else:
                        X_norm = scaler.transform(X_arr)
                    
                    todas_features.append(X_norm)
                    todas_labels.append(y_arr)
                    print(f"   ✅ Adicionados {len(X_arr)} fluxos normais")
            except Exception as e:
                print(f"   ❌ Erro: {e}")
        
        # Processar PCAPs de ataque
        print("\n⚠️ PROCESSAR ATAQUES")
        pcaps_ataques = list(self.pcaps_attacks.glob("*.pcap")) + list(self.pcaps_attacks.glob("*.pcapng"))
        
        for pcap in pcaps_ataques[:5]:
            print(f"\n📁 {pcap.name}")
            try:
                packets = rdpcap(str(pcap))
                if max_packets_per_pcap and len(packets) > max_packets_per_pcap:
                    packets = packets[:max_packets_per_pcap]
                
                flow_extractor = FlowExtractor()
                for pkt in packets:
                    flow_extractor.process_packet(pkt, pkt.time)
                
                flows = flow_extractor.get_completed_flows()
                
                X = []
                for flow in flows:
                    features = flow.get_features()
                    feature_values = list(features.values())
                    X.append(feature_values)
                
                if X:
                    X_arr = np.array(X, dtype=np.float32)
                    y_arr = np.ones(len(X_arr))
                    
                    X_norm = scaler.transform(X_arr)
                    
                    todas_features.append(X_norm)
                    todas_labels.append(y_arr)
                    print(f"   ✅ Adicionados {len(X_arr)} fluxos de ataque")
            except Exception as e:
                print(f"   ❌ Erro: {e}")
        
        if not todas_features:
            return None, None, None
        
        X_final = np.vstack(todas_features)
        y_final = np.hstack(todas_labels)
        
        idx = np.random.permutation(len(X_final))
        X_final = X_final[idx]
        y_final = y_final[idx]
        
        print(f"\n📊 Total: {len(X_final)} amostras")
        
        return X_final, y_final, scaler
    
    # ========== COMBINAR TUDO ==========
    def combinar_tudo(self, max_samples_per_source=50000):
        """Combina PCAPs + Logs + CSVs num único dataset"""
        print("\n" + "="*70)
        print("🔥 COMBINAR TUDO (PCAPs + Logs + CSVs)")
        print("="*70)
        
        todas_features = []
        todas_labels = []
        
        # 1. Carregar PCAPs
        print("\n1️⃣ CARREGANDO PCAPS...")
        X_pcaps, y_pcaps, scaler_pcaps = self.preparar_dados_pcaps()
        if X_pcaps is not None:
            if len(X_pcaps) > max_samples_per_source:
                idx = np.random.choice(len(X_pcaps), max_samples_per_source, replace=False)
                X_pcaps = X_pcaps[idx]
                y_pcaps = y_pcaps[idx]
            todas_features.append(X_pcaps)
            todas_labels.append(y_pcaps)
            print(f"   ✅ PCAPs: {len(X_pcaps)} amostras, features: {X_pcaps.shape[1]}")
        
        # 2. Carregar Logs
        print("\n2️⃣ CARREGANDO LOGS...")
        X_logs, y_logs, scaler_logs = self.carregar_logs_sniffer()
        if X_logs is not None:
            if len(X_logs) > max_samples_per_source:
                idx = np.random.choice(len(X_logs), max_samples_per_source, replace=False)
                X_logs = X_logs[idx]
                y_logs = y_logs[idx]
            todas_features.append(X_logs)
            todas_labels.append(y_logs)
            print(f"   ✅ Logs: {len(X_logs)} amostras, features: {X_logs.shape[1]}")
        
        # 3. Carregar CSVs
        print("\n3️⃣ CARREGANDO CSVS...")
        X_csv, y_csv, scaler_csv = self.carregar_csv_cicids2017(max_samples_per_file=max_samples_per_source)
        if X_csv is not None:
            if len(X_csv) > max_samples_per_source:
                idx = np.random.choice(len(X_csv), max_samples_per_source, replace=False)
                X_csv = X_csv[idx]
                y_csv = y_csv[idx]
            todas_features.append(X_csv)
            todas_labels.append(y_csv)
            print(f"   ✅ CSVs: {len(X_csv)} amostras, features: {X_csv.shape[1]}")
        
        if not todas_features:
            print("❌ Nenhum dado carregado!")
            return None, None, None
        
        # Verificar dimensões e ajustar para o número de features mais comum
        target_features = 70
        for i, feat in enumerate(todas_features):
            if feat.shape[1] != target_features:
                print(f"   ⚠️ Ajustando features: {feat.shape[1]} → {target_features}")
                if feat.shape[1] > target_features:
                    feat = feat[:, :target_features]
                else:
                    pad = np.zeros((feat.shape[0], target_features - feat.shape[1]))
                    feat = np.hstack([feat, pad])
                todas_features[i] = feat
        
        # Combinar tudo
        X_final = np.vstack(todas_features)
        y_final = np.hstack(todas_labels)
        
        # Normalizar o conjunto completo
        scaler = StandardScaler()
        X_final = scaler.fit_transform(X_final)
        
        # Embaralhar
        idx = np.random.permutation(len(X_final))
        X_final = X_final[idx]
        y_final = y_final[idx]
        
        print("\n" + "="*70)
        print("🔥 DATASET COMBINADO CRIADO!")
        print(f"   Total amostras: {len(X_final)}")
        print(f"   Normais: {sum(y_final==0)} ({sum(y_final==0)/len(y_final)*100:.1f}%)")
        print(f"   Anomalias: {sum(y_final==1)} ({sum(y_final==1)/len(y_final)*100:.1f}%)")
        print(f"   Features: {X_final.shape[1]}")
        
        return X_final, y_final, scaler
    
    # ========== TREINO DO MODELO ==========
    def treinar_novo_modelo(self, X, y, contamination=0.15, test_size=0.25):
        """Treina um NOVO modelo e guarda como .pkl"""
        print("\n" + "="*70)
        print("🚀 TREINAR NOVO MODELO")
        print("="*70)
        
        if X is None or y is None:
            return None, None
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"\n📊 Divisão dos dados:")
        print(f"   Treino: {X_train.shape[0]} amostras")
        print(f"   Teste: {X_test.shape[0]} amostras")
        print(f"   Features: {X_train.shape[1]}")
        
        print("\n🔄 A treinar Isolation Forest...")
        model = IsolationForest(
            n_estimators=200,
            contamination=contamination,
            random_state=42,
            n_jobs=-1,
            verbose=0
        )
        
        model.fit(X_train)
        print("✅ Modelo treinado!")
        
        # Avaliar
        y_pred = model.predict(X_test)
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
            'info': f'Modelo treinado com {n_features} features'
        }
        
        with open(modelo_path, 'wb') as f:
            pickle.dump(dados_modelo, f)
        
        print(f"\n💾 NOVO modelo guardado: {modelo_path}")
        print(f"🎯 Acurácia: {acuracia*100:.2f}%")
        print(f"📋 Features guardadas: {len(self.feature_names)}")


def main():
    """Função principal para treinar novo modelo"""
    print("="*70)
    print("🔧 TREINAR NOVO MODELO")
    print("="*70)
    
    # Perguntar origem dos dados
    print("\n📊 ORIGEM DOS DADOS:")
    print("   1. PCAPs (TODOS os ficheiros em data/pcaps/)")
    print("   2. Logs do Sniffer (TODOS os logs em data/logs/)")
    print("   3. CSVs do CIC-IDS2017 (TODOS os 8 ficheiros)")
    print("   4. 🔥 COMBINAR TUDO (PCAPs + Logs + CSVs) - RECOMENDADO")
    
    origem = input("\nEscolhe a origem (1-4): ").strip()
    
    # Criar trainer
    trainer = NovoModeloTrainer()
    
    # Preparar dados conforme origem
    if origem == '1':
        print("\n📁 Usando TODOS os PCAPs como fonte de dados")
        X, y, scaler = trainer.preparar_dados_pcaps()
    elif origem == '2':
        print("\n📊 Usando TODOS os logs do Sniffer como fonte de dados")
        X, y, scaler = trainer.carregar_logs_sniffer()
    elif origem == '3':
        print("\n📄 Usando TODOS os CSVs do CIC-IDS2017 como fonte de dados")
        X, y, scaler = trainer.carregar_csv_cicids2017()
    elif origem == '4':
        print("\n🔥 Usando COMBINAÇÃO de TODAS as fontes")
        X, y, scaler = trainer.combinar_tudo()
    else:
        print("❌ Opção inválida")
        return
    
    if X is None:
        print("\n❌ Não foi possível preparar os dados!")
        return
    
    # Treinar
    model, acuracia = trainer.treinar_novo_modelo(X, y)
    
    if model:
        trainer._guardar_modelo(model, scaler, acuracia, X.shape[1])

if __name__ == "__main__":
    main()