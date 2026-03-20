# Script para TREINAR NOVOS modelos com PCAPs reais Suporta .pcap e .pcapng

import numpy as np
import pickle
from pathlib import Path
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import sys
import json

PROJECT_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_PATH))

from backend.scapy_module.extractor import ScapyExtractor

class NovoModeloTrainer:
    """
    Treina NOVOS modelos com PCAPs reais
    """
    
    def __init__(self, feature_names=None):
        self.extractor = ScapyExtractor(feature_names)
        self.project_root = PROJECT_PATH
        self.models_folder = self.project_root / "models"
        self.pcaps_normal = self.project_root / "data" / "pcaps" / "normal"
        self.pcaps_attacks = self.project_root / "data" / "pcaps" / "attacks"
        
        # Criar pastas
        self.models_folder.mkdir(exist_ok=True)
        self.pcaps_normal.parent.mkdir(parents=True, exist_ok=True)
        self.pcaps_normal.mkdir(exist_ok=True)
        self.pcaps_attacks.mkdir(exist_ok=True)
    
    def preparar_dados(self, max_packets_per_pcap=2000):
        """
        Prepara dados de treino a partir dos PCAPs (suporta .pcap e .pcapng)
        """
        print("\n" + "="*70)
        print("🔍 PREPARAR DADOS PARA NOVO MODELO")
        print("="*70)
        
        todas_features = []
        todas_labels = []
        
        # 1. Processar PCAPs normais (CORRIGIDO: suporta .pcap e .pcapng)
        print("\n📊 PROCESSAR TRÁFEGO NORMAL")
        pcaps_normais = list(self.pcaps_normal.glob("*.pcap")) + list(self.pcaps_normal.glob("*.pcapng"))
        
        if not pcaps_normais:
            print("⚠️ Nenhum PCAP normal encontrado!")
        
        for pcap in pcaps_normais:
            print(f"\n📁 {pcap.name}")
            X = self.extractor.extract_from_pcap(pcap, max_packets=max_packets_per_pcap)
            if X is not None and len(X) > 0:
                todas_features.append(X)
                todas_labels.append(np.zeros(len(X)))
                print(f"   ✅ Adicionados {len(X)} pacotes normais")
        
        # 2. Processar PCAPs de ataque (CORRIGIDO: suporta .pcap e .pcapng)
        print("\n⚠️ PROCESSAR ATAQUES")
        pcaps_ataques = list(self.pcaps_attacks.glob("*.pcap")) + list(self.pcaps_attacks.glob("*.pcapng"))
        
        if not pcaps_ataques:
            print("⚠️ Nenhum PCAP de ataque encontrado!")
        
        for pcap in pcaps_ataques:
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
    
    def treinar_novo_modelo(self, contamination=0.15, test_size=0.25):
        """
        Treina um NOVO modelo e guarda como .pkl com as features incluídas
        """
        print("\n" + "="*70)
        print("🚀 TREINAR NOVO MODELO")
        print("="*70)
        
        # Preparar dados
        X, y = self.preparar_dados()
        
        if X is None:
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
        
        # Guardar novo modelo COM AS FEATURES
        self._guardar_modelo(model, acuracia, X.shape[1])
        
        return model, acuracia
    
    def _guardar_modelo(self, model, acuracia, n_features):
        """Guarda o novo modelo na pasta models"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"modelo_scapy_{timestamp}_{acuracia*100:.2f}%.pkl"
        modelo_path = self.models_folder / nome_arquivo
        
        # Guarda TUDO - modelo, features, acurácia, data
        dados_modelo = {
            'modelo': model,
            'feature_names': self.extractor.feature_names,
            'acuracia': acuracia,
            'data_treino': datetime.now().isoformat(),
            'n_features': n_features,
            'n_amostras_treino': n_features,
            'versao': 'treinado_com_pcaps_reais',
            'info': f'Modelo treinado com {n_features} features'
        }
        
        with open(modelo_path, 'wb') as f:
            pickle.dump(dados_modelo, f)
        
        print(f"\n💾 NOVO modelo guardado: {modelo_path}")
        print(f"🎯 Acurácia: {acuracia*100:.2f}%")
        print(f"📋 Features guardadas no modelo: {len(self.extractor.feature_names)}")
        
        # Config também na pasta data
        config_path = self.project_root / "data" / f"config_{timestamp}.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump({
                'feature_names': self.extractor.feature_names,
                'acuracia': float(acuracia),
                'data': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"📋 Configuração guardada em: {config_path}")


def main():
    """Função principal para treinar novo modelo"""
    print("="*70)
    print("🔧 TREINAR NOVO MODELO COM PCAPS REAIS")
    print("="*70)
    
    # Primeiro, pergunta se quer usar features personalizadas
    print("\n📋 Configuração de features:")
    print("   1. Usar features do modelo existente (recomendado)")
    print("   2. Definir novas features manualmente")
    print("   3. Usar features padrão (14 features exemplo)")
    
    opcao = input("\nEscolhe uma opção (1-3): ").strip()
    
    feature_names = None
    if opcao == '1':
        # Tentar carregar do modelo existente
        modelo_existente = PROJECT_PATH / "models" / "best_model.pkl"
        if modelo_existente.exists():
            with open(modelo_existente, 'rb') as f:
                dados = pickle.load(f)
            if isinstance(dados, dict) and 'feature_names' in dados:
                feature_names = dados['feature_names']
                print(f"✅ Carregadas {len(feature_names)} features do modelo existente")
    
    trainer = NovoModeloTrainer(feature_names)
    resultado = trainer.treinar_novo_modelo()
    
    if resultado:
        print("\n" + "="*70)
        print("✅ NOVO MODELO CRIADO COM SUCESSO!")
        print("="*70)

if __name__ == "__main__":
    main()