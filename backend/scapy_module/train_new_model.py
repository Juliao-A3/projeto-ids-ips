# backend/scapy_module/train_new_model.py
# Script para TREINAR NOVOS modelos com PCAPs, LOGS ou CSV (CIC-IDS2017)

import numpy as np
import pickle
from pathlib import Path
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
import sys
import json
import pandas as pd  # NOVO: para ler CSV

PROJECT_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_PATH))

from backend.scapy_module.extractor import ScapyExtractor

class NovoModeloTrainer:
    """
    Treina NOVOS modelos com PCAPs, LOGS do Sniffer ou CSV (CIC-IDS2017)
    """
    
    def __init__(self, feature_names=None):
        self.extractor = ScapyExtractor(feature_names)
        self.project_root = PROJECT_PATH
        self.models_folder = self.project_root / "models"
        self.pcaps_normal = self.project_root / "data" / "pcaps" / "normal"
        self.pcaps_attacks = self.project_root / "data" / "pcaps" / "attacks"
        self.logs_dir = self.project_root / "data" / "logs"
        self.csv_dir = self.project_root / "data" / "cic-ids2017"  # NOVO
        
        # Criar pastas
        self.models_folder.mkdir(exist_ok=True)
        self.pcaps_normal.parent.mkdir(parents=True, exist_ok=True)
        self.pcaps_normal.mkdir(exist_ok=True)
        self.pcaps_attacks.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        self.csv_dir.mkdir(exist_ok=True)  # NOVO
    
    # ========== CARREGAR DADOS DOS LOGS DO SNIFFER ==========
    def carregar_logs_sniffer(self, max_entries=5000):
        """Carrega dados dos logs do sniffer"""
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
                    total_pacotes = entry.get('total_pacotes', 0)
                    anomalias = entry.get('anomalias', 0)
                    
                    # Simular dados (substituir quando tiveres dados reais)
                    for _ in range(min(100, total_pacotes)):
                        feat = [0] * len(self.extractor.feature_names)
                        # Simulação
                        feat[0] = np.random.randint(64, 1500)
                        feat[1] = np.random.choice([6, 17, 1])
                        feat[2] = np.random.randint(32, 128)
                        feat[3] = np.random.randint(1024, 65535)
                        feat[4] = np.random.randint(0, 255)
                        feat[5] = np.random.randint(1024, 65535)
                        feat[6] = np.random.randint(1, 65535)
                        feat[7] = np.random.randint(0, 1400)
                        feat[8] = np.random.random()
                        feat[9] = np.random.randint(0, 2)
                        feat[10] = np.random.randint(0, 2)
                        feat[11] = np.random.randint(0, 2)
                        feat[12] = np.random.randint(0, 2)
                        feat[13] = np.random.uniform(0, 1)
                        
                        dados.append(feat)
                        labels.append(1 if np.random.random() < (anomalias/total_pacotes if total_pacotes > 0 else 0.1) else 0)
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
            
            return X, y
            
        except Exception as e:
            print(f"❌ Erro ao carregar logs: {e}")
            return None, None
    
    # ========== CARREGAR DADOS DOS PCAPS ==========
    def preparar_dados_pcaps(self, max_packets_per_pcap=2000):
        """Prepara dados de treino a partir dos PCAPs"""
        print("\n" + "="*70)
        print("📊 PREPARAR DADOS DOS PCAPS")
        print("="*70)
        
        todas_features = []
        todas_labels = []
        
        print("\n📊 PROCESSAR TRÁFEGO NORMAL")
        pcaps_normais = list(self.pcaps_normal.glob("*.pcap")) + list(self.pcaps_normal.glob("*.pcapng"))
        
        if not pcaps_normais:
            print("⚠️ Nenhum PCAP normal encontrado!")
        
        for pcap in pcaps_normais[:5]:
            print(f"\n📁 {pcap.name}")
            X = self.extractor.extract_from_pcap(pcap, max_packets=max_packets_per_pcap)
            if X is not None and len(X) > 0:
                todas_features.append(X)
                todas_labels.append(np.zeros(len(X)))
                print(f"   ✅ Adicionados {len(X)} pacotes normais")
        
        print("\n⚠️ PROCESSAR ATAQUES")
        pcaps_ataques = list(self.pcaps_attacks.glob("*.pcap")) + list(self.pcaps_attacks.glob("*.pcapng"))
        
        if not pcaps_ataques:
            print("⚠️ Nenhum PCAP de ataque encontrado!")
        
        for pcap in pcaps_ataques[:5]:
            print(f"\n📁 {pcap.name}")
            X = self.extractor.extract_from_pcap(pcap, max_packets=max_packets_per_pcap)
            if X is not None and len(X) > 0:
                todas_features.append(X)
                todas_labels.append(np.ones(len(X)))
                print(f"   ✅ Adicionados {len(X)} pacotes de ataque")
        
        if not todas_features:
            print("❌ Nenhum dado extraído!")
            return None, None
        
        X_final = np.vstack(todas_features)
        y_final = np.hstack(todas_labels)
        
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
    
    # ========== NOVO: CARREGAR DADOS DO CSV (CIC-IDS2017) ==========
    def carregar_csv_cicids2017(self, csv_path=None):
        """
        Carrega dados do CSV do CIC-IDS2017
        """
        print("\n" + "="*70)
        print("📊 CARREGAR DADOS DO CIC-IDS2017 (CSV)")
        print("="*70)
        
        # Se não especificar, listar CSVs disponíveis
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
            
            # Identificar coluna de label (normalmente 'Label')
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
            
            # Mapear labels: 'BENIGN' ou 'normal' -> 0, outros -> 1
            df['label_binary'] = df[label_col].apply(
                lambda x: 0 if str(x).upper() in ['BENIGN', 'NORMAL', 'BENING'] else 1
            )
            
            # Mapear features para as 14 do teu modelo
            # (mapeamento básico - ajusta conforme necessário)
            feature_mapping = {
                'packet_size': ['Packet Length', 'Total Length of Fwd Packets', 'Flow Duration'],
                'protocol': ['Protocol', 'Fwd PSH Flags', 'Bwd PSH Flags'],
                'ttl': ['Init_Win_bytes_forward', 'Init_Win_bytes_backward'],
                'window_size': ['Init_Win_bytes_forward', 'Init_Win_bytes_backward'],
                'tcp_flags': ['Fwd PSH Flags', 'Bwd PSH Flags', 'Fwd URG Flags', 'Bwd URG Flags'],
                'src_port': ['Src Port'],
                'dst_port': ['Dst Port'],
                'payload_size': ['Packet Length', 'Average Packet Size'],
                'ip_entropy': ['Flow Duration', 'Flow IAT Mean'],
                'flag_syn': ['Fwd PSH Flags'],
                'flag_ack': ['Fwd URG Flags'],
                'flag_fin': ['Fwd URG Flags'],
                'flag_rst': ['Fwd URG Flags'],
                'inter_arrival': ['Flow IAT Mean', 'Flow IAT Std']
            }
            
            # Selecionar features disponíveis no CSV
            features_available = []
            for target_feat in self.extractor.feature_names:
                found = False
                for possible_col in feature_mapping.get(target_feat, []):
                    for col in df.columns:
                        if possible_col in col:
                            features_available.append(col)
                            found = True
                            break
                    if found:
                        break
                if not found:
                    print(f"⚠️ Feature '{target_feat}' não encontrada no CSV")
            
            if not features_available:
                print("❌ Nenhuma feature correspondente encontrada")
                return None, None
            
            # Usar features disponíveis
            X = df[features_available].values
            y = df['label_binary'].values
            
            # Normalizar
            from sklearn.preprocessing import StandardScaler
            scaler = StandardScaler()
            X = scaler.fit_transform(X)
            
            # Limitar número de amostras (para não sobrecarregar)
            max_samples = 50000
            if len(X) > max_samples:
                print(f"📊 A reduzir de {len(X)} para {max_samples} amostras...")
                indices = np.random.choice(len(X), max_samples, replace=False)
                X = X[indices]
                y = y[indices]
            
            print(f"\n✅ Dados preparados: {len(X)} amostras")
            print(f"   Normais: {sum(y==0)} ({sum(y==0)/len(y)*100:.1f}%)")
            print(f"   Anomalias: {sum(y==1)} ({sum(y==1)/len(y)*100:.1f}%)")
            print(f"   Features: {X.shape[1]} (mapeadas)")
            
            return X, y
            
        except Exception as e:
            print(f"❌ Erro ao carregar CSV: {e}")
            return None, None
    
    # ========== TREINO DO MODELO ==========
    def treinar_novo_modelo(self, X, y, contamination=0.15, test_size=0.25):
        """Treina um NOVO modelo e guarda como .pkl"""
        print("\n" + "="*70)
        print("🚀 TREINAR NOVO MODELO")
        print("="*70)
        
        if X is None or y is None:
            return None
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"\n📊 Divisão dos dados:")
        print(f"   Treino: {X_train.shape[0]} amostras")
        print(f"   Teste: {X_test.shape[0]} amostras")
        
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
        
        self._guardar_modelo(model, acuracia, X.shape[1])
        
        return model, acuracia
    
    def _guardar_modelo(self, model, acuracia, n_features):
        """Guarda o novo modelo na pasta models"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"modelo_scapy_{timestamp}_{acuracia*100:.2f}%.pkl"
        modelo_path = self.models_folder / nome_arquivo
        
        dados_modelo = {
            'modelo': model,
            'feature_names': self.extractor.feature_names,
            'acuracia': acuracia,
            'data_treino': datetime.now().isoformat(),
            'n_features': n_features,
            'versao': 'treinado',
            'info': f'Modelo treinado com {n_features} features'
        }
        
        with open(modelo_path, 'wb') as f:
            pickle.dump(dados_modelo, f)
        
        print(f"\n💾 NOVO modelo guardado: {modelo_path}")
        print(f"🎯 Acurácia: {acuracia*100:.2f}%")
        print(f"📋 Features guardadas: {len(self.extractor.feature_names)}")


def main():
    """Função principal para treinar novo modelo"""
    print("="*70)
    print("🔧 TREINAR NOVO MODELO")
    print("="*70)
    
    # Perguntar origem dos dados
    print("\n📊 ORIGEM DOS DADOS:")
    print("   1. PCAPs (ficheiros .pcap/.pcapng em data/pcaps/)")
    print("   2. Logs do Sniffer (dados em tempo real de data/logs/)")
    print("   3. CSV do CIC-IDS2017 (data/cic-ids2017/)")
    
    origem = input("\nEscolhe a origem (1-3): ").strip()
    
    # Perguntar features
    print("\n📋 Configuração de features:")
    print("   1. Usar features do modelo existente (recomendado)")
    print("   2. Definir novas features manualmente")
    print("   3. Usar features padrão (14 features exemplo)")
    
    opcao = input("\nEscolhe uma opção (1-3): ").strip()
    
    feature_names = None
    if opcao == '1':
        modelo_existente = PROJECT_PATH / "models" / "best_model.pkl"
        if modelo_existente.exists():
            with open(modelo_existente, 'rb') as f:
                dados = pickle.load(f)
            if isinstance(dados, dict) and 'feature_names' in dados:
                feature_names = dados['feature_names']
                print(f"✅ Carregadas {len(feature_names)} features do modelo existente")
    elif opcao == '2':
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