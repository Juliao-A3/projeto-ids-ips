# backend/scapy_module/train_new_model.py
# Script para TREINAR NOVOS modelos com PCAPs ou LOGS do Sniffer

import numpy as np
import pickle
from pathlib import Path
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
import sys
import json
import random

PROJECT_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_PATH))

from backend.scapy_module.extractor import ScapyExtractor

class NovoModeloTrainer:
    """
    Treina NOVOS modelos com PCAPs ou LOGS do Sniffer
    """
    
    def __init__(self, feature_names=None):
        self.extractor = ScapyExtractor(feature_names)
        self.project_root = PROJECT_PATH
        self.models_folder = self.project_root / "models"
        self.pcaps_normal = self.project_root / "data" / "pcaps" / "normal"
        self.pcaps_attacks = self.project_root / "data" / "pcaps" / "attacks"
        self.logs_dir = self.project_root / "data" / "logs"
        
        # Criar pastas
        self.models_folder.mkdir(exist_ok=True)
        self.pcaps_normal.parent.mkdir(parents=True, exist_ok=True)
        self.pcaps_normal.mkdir(exist_ok=True)
        self.pcaps_attacks.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
    
    def carregar_logs_sniffer(self, max_entries=5000):
        """
        Carrega dados dos logs do sniffer
        """
        print("\n" + "="*70)
        print("📊 CARREGAR DADOS DOS LOGS DO SNIFFER")
        print("="*70)
        
        logs_files = list(self.logs_dir.glob("ips_*.json"))
        
        if not logs_files:
            print("❌ Nenhum log encontrado em data/logs/")
            return None, None
        
        print(f"📁 Encontrados {len(logs_files)} ficheiros de log")
        
        # Usar o log mais recente
        ultimo_log = max(logs_files, key=lambda x: x.stat().st_mtime)
        print(f"📂 Usando log: {ultimo_log.name}")
        
        try:
            with open(ultimo_log, 'r') as f:
                linhas = f.readlines()
                
            dados = []
            labels = []
            
            for linha in linhas[-max_entries:]:  # últimas N entradas
                try:
                    entry = json.loads(linha)
                    
                    # Extrair dados da entrada
                    total_pacotes = entry.get('total_pacotes', 0)
                    anomalias = entry.get('anomalias', 0)
                    
                    # Gerar features simuladas baseadas nas estatísticas
                    # (para treino real, precisamos dos pacotes individuais)
                    for _ in range(min(100, total_pacotes)):  # limite por segurança
                        feat = [0] * len(self.extractor.feature_names)
                        # Simulação - substituir por dados reais quando disponíveis
                        feat[0] = random.randint(64, 1500)  # packet_size
                        feat[1] = random.choice([6, 17, 1])  # protocol
                        feat[2] = random.randint(32, 128)   # ttl
                        feat[3] = random.randint(1024, 65535)  # window_size
                        feat[4] = random.randint(0, 255)    # tcp_flags
                        feat[5] = random.randint(1024, 65535)  # src_port
                        feat[6] = random.randint(1, 65535)   # dst_port
                        feat[7] = random.randint(0, 1400)   # payload_size
                        feat[8] = random.random()           # ip_entropy
                        feat[9] = random.randint(0, 1)      # flag_syn
                        feat[10] = random.randint(0, 1)     # flag_ack
                        feat[11] = random.randint(0, 1)     # flag_fin
                        feat[12] = random.randint(0, 1)     # flag_rst
                        feat[13] = random.uniform(0, 1)     # inter_arrival
                        
                        dados.append(feat)
                        # label: 0 = normal, 1 = anomalia
                        labels.append(1 if random.random() < (anomalias/total_pacotes if total_pacotes > 0 else 0.1) else 0)
                        
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
    
    def preparar_dados_pcaps(self, max_packets_per_pcap=2000):
        """
        Prepara dados de treino a partir dos PCAPs
        """
        print("\n" + "="*70)
        print("📊 PREPARAR DADOS DOS PCAPS")
        print("="*70)
        
        todas_features = []
        todas_labels = []
        
        # 1. Processar PCAPs normais
        print("\n📊 PROCESSAR TRÁFEGO NORMAL")
        pcaps_normais = list(self.pcaps_normal.glob("*.pcap")) + list(self.pcaps_normal.glob("*.pcapng"))
        
        if not pcaps_normais:
            print("⚠️ Nenhum PCAP normal encontrado!")
        
        for pcap in pcaps_normais[:5]:  # Limitar a 5 PCAPs
            print(f"\n📁 {pcap.name}")
            X = self.extractor.extract_from_pcap(pcap, max_packets=max_packets_per_pcap)
            if X is not None and len(X) > 0:
                todas_features.append(X)
                todas_labels.append(np.zeros(len(X)))
                print(f"   ✅ Adicionados {len(X)} pacotes normais")
        
        # 2. Processar PCAPs de ataque
        print("\n⚠️ PROCESSAR ATAQUES")
        pcaps_ataques = list(self.pcaps_attacks.glob("*.pcap")) + list(self.pcaps_attacks.glob("*.pcapng"))
        
        if not pcaps_ataques:
            print("⚠️ Nenhum PCAP de ataque encontrado!")
        
        for pcap in pcaps_ataques[:5]:  # Limitar a 5 PCAPs
            print(f"\n📁 {pcap.name}")
            X = self.extractor.extract_from_pcap(pcap, max_packets=max_packets_per_pcap)
            if X is not None and len(X) > 0:
                todas_features.append(X)
                todas_labels.append(np.ones(len(X)))
                print(f"   ✅ Adicionados {len(X)} pacotes de ataque")
        
        # 3. Combinar tudo
        if not todas_features:
            print("❌ Nenhum dado extraído!")
            return None, None
        
        X_final = np.vstack(todas_features)
        y_final = np.hstack(todas_labels)
        
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
    
    def treinar_novo_modelo(self, X, y, contamination=0.15, test_size=0.25):
        """
        Treina um NOVO modelo e guarda como .pkl com as features incluídas
        """
        print("\n" + "="*70)
        print("🚀 TREINAR NOVO MODELO")
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
        
        # Treinar modelo
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
        
        # Guardar novo modelo
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
    
    origem = input("\nEscolhe a origem (1-2): ").strip()
    
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
    else:
        print("\n📊 Usando logs do Sniffer como fonte de dados")
        X, y = trainer.carregar_logs_sniffer()
    
    if X is None:
        print("\n❌ Não foi possível preparar os dados!")
        return
    
    # Treinar
    trainer.treinar_novo_modelo(X, y)

if __name__ == "__main__":
    main()