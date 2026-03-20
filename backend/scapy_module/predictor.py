# Predictor - USA modelo existente para classificar PCAPs

import pickle
import numpy as np
from pathlib import Path
from datetime import datetime
import json
import sys

PROJECT_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_PATH))

from backend.scapy_module.extractor import ScapyExtractor

class ModelPredictor:
    """
    Classifica PCAPs usando modelo treinado
    """
    
    def __init__(self, model_path=None):
        """
        Carrega o modelo .pkl e configura o extrator
        """
        if model_path is None:
            self.model_path = PROJECT_PATH / "models" / "best_model.pkl"
        else:
            self.model_path = Path(model_path)
        
        print(f"📂 A carregar modelo: {self.model_path}")
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Modelo não encontrado: {self.model_path}")
        
        # Carregar modelo
        with open(self.model_path, 'rb') as f:
            self.model_data = pickle.load(f)
        
        # Extrair informações do modelo
        self.model = None
        self.feature_names = None
        self.acuracia = 'desconhecida'
        
        # CASO 1: É um dicionário
        if isinstance(self.model_data, dict):
            print("📋 Modelo carregado como dicionário")
            print(f"   Chaves disponíveis: {list(self.model_data.keys())}")
            
            # Tentar encontrar o modelo em diferentes chaves possíveis
            if 'modelo' in self.model_data:
                self.model = self.model_data['modelo']
                print("   ✅ Usando chave 'modelo'")
            elif 'model' in self.model_data:
                self.model = self.model_data['model']
                print("   ✅ Usando chave 'model'")
            elif 'classifier' in self.model_data:
                self.model = self.model_data['classifier']
                print("   ✅ Usando chave 'classifier'")
            elif 'xgb_model' in self.model_data:
                self.model = self.model_data['xgb_model']
                print("   ✅ Usando chave 'xgb_model'")
            elif 'estimator' in self.model_data:
                self.model = self.model_data['estimator']
                print("   ✅ Usando chave 'estimator'")
            else:
                # Se não encontrar nenhuma chave conhecida, procura qualquer objeto com método predict
                encontrado = False
                for key, value in self.model_data.items():
                    if hasattr(value, 'predict'):
                        self.model = value
                        print(f"   ✅ Encontrado modelo na chave: '{key}'")
                        encontrado = True
                        break
                
                if not encontrado:
                    print("   ❌ Nenhuma chave com método 'predict' encontrada")
                    print("   O dicionário contém:", list(self.model_data.keys()))
                    self.model = self.model_data  # vai falhar, mas mostramos erro
            
            # Carregar feature_names e acurácia se existirem
            self.feature_names = self.model_data.get('feature_names', None)
            self.acuracia = self.model_data.get('acuracia', 'desconhecida')
        
        # CASO 2: É diretamente o modelo
        else:
            self.model = self.model_data
            print("📋 Modelo carregado diretamente")
            
            if hasattr(self.model, 'feature_names_in_'):
                self.feature_names = list(self.model.feature_names_in_)
                print(f"   ✅ Features encontradas: {len(self.feature_names)}")
        
        # Verificar se o modelo tem método predict
        if self.model and hasattr(self.model, 'predict'):
            print(f"✅ Modelo carregado com sucesso!")
            print(f"   Acurácia: {self.acuracia}")
            
            if hasattr(self.model, 'n_features_in_'):
                print(f"   Features esperadas: {self.model.n_features_in_}")
            elif self.feature_names:
                print(f"   Features esperadas: {len(self.feature_names)}")
        else:
            print(f"❌ ERRO: O objeto carregado NÃO tem método 'predict'")
            print(f"   Tipo do objeto: {type(self.model)}")
            if isinstance(self.model_data, dict):
                print("   O modelo pode estar numa das chaves acima")
        
        # Inicializar extrator com as features corretas
        if self.feature_names:
            print(f"   Usando {len(self.feature_names)} features do modelo")
            self.extractor = ScapyExtractor(self.feature_names)
        elif hasattr(self.model, 'n_features_in_'):
            n_feats = self.model.n_features_in_
            print(f"   Modelo espera {n_feats} features (nomes genéricos)")
            generic_names = [f'feature_{i}' for i in range(n_feats)]
            self.extractor = ScapyExtractor(generic_names)
        else:
            print("   ⚠️ Usando features exemplo (14 features)")
            self.extractor = ScapyExtractor()
    
    def predict_pcap(self, pcap_path, max_packets=10000):
        """
        Classifica um PCAP e retorna resultados
        """
        print(f"\n🔍 A analisar: {pcap_path}")
        
        # Extrair features
        X = self.extractor.extract_from_pcap(pcap_path, max_packets)
        
        if X is None:
            return None
        
        # Verificar compatibilidade
        modelo_espera = None
        if self.feature_names:
            modelo_espera = len(self.feature_names)
        elif hasattr(self.model, 'n_features_in_'):
            modelo_espera = self.model.n_features_in_
        
        if modelo_espera and X.shape[1] != modelo_espera:
            print(f"⚠️ Número de features diferente!")
            print(f"   Modelo espera: {modelo_espera}")
            print(f"   Extraídas: {X.shape[1]}")
            print("   A ajustar...")
            
            if X.shape[1] > modelo_espera:
                X = X[:, :modelo_espera]
                print(f"   → Truncado para {modelo_espera} features")
            else:
                pad = np.zeros((X.shape[0], modelo_espera - X.shape[1]))
                X = np.hstack([X, pad])
                print(f"   → Preenchido para {modelo_espera} features")
        
        print(f"\n🤖 A classificar {len(X)} pacotes...")
        
        # Garantir que o modelo tem método predict
        if not hasattr(self.model, 'predict'):
            print("❌ ERRO: Modelo não tem método 'predict'!")
            return None
        
        # Classificar
        try:
            y_pred = self.model.predict(X)
            
            # Debug
            print(f"   Valores únicos nas predições: {np.unique(y_pred)}")
            print(f"   Total normais (1): {np.sum(y_pred == 1)}")
            print(f"   Total anomalias (-1): {np.sum(y_pred == -1)}")
            
            # Converter se necessário (se vier 0/1 em vez de -1/1)
            if set(y_pred) == {0, 1}:
                y_pred = np.where(y_pred == 1, 1, -1)
                print("   ⚠️ Convertido de 0/1 para -1/1")
                print(f"   Após conversão: Normais={np.sum(y_pred == 1)}, Anomalias={np.sum(y_pred == -1)}")
            
            # Scores
            if hasattr(self.model, 'score_samples'):
                y_scores = self.model.score_samples(X)
            else:
                y_scores = np.zeros(len(X))
                
        except Exception as e:
            print(f"❌ Erro ao classificar: {e}")
            return None
        
        # Resultados
        n_total = len(y_pred)
        n_anomalias = np.sum(y_pred == -1)
        n_normais = np.sum(y_pred == 1)
        
        resultados = {
            'pcap': str(pcap_path),
            'data_analise': datetime.now().isoformat(),
            'modelo_usado': str(self.model_path),
            'acuracia_modelo': str(self.acuracia),
            'total_pacotes': int(n_total),
            'normais': int(n_normais),
            'anomalias': int(n_anomalias),
            'percentual_anomalias': float(n_anomalias / n_total * 100) if n_total > 0 else 0
        }
        
        # Mostrar resultados
        print("\n" + "="*60)
        print("📊 RESULTADOS DA ANÁLISE")
        print("="*60)
        print(f"📦 Total pacotes: {resultados['total_pacotes']}")
        print(f"✅ Normais: {resultados['normais']} ({resultados['normais']/n_total*100:.2f}%)")
        print(f"⚠️ Anomalias: {resultados['anomalias']} ({resultados['anomalias']/n_total*100:.2f}%)")
        
        # Guardar resultados
        self._save_results(resultados)
        
        return resultados
    
    def _save_results(self, resultados):
        """Guarda resultados em JSON na pasta data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        resultados_path = PROJECT_PATH / "data" / f"resultados_{timestamp}.json"
        resultados_path.parent.mkdir(exist_ok=True)
        
        with open(resultados_path, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados em: {resultados_path}")


# Para testar diretamente
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python predictor.py <pcap_file> [modelo_path]")
        print("Exemplo: python predictor.py data/pcaps/normal/normal.pcapng models/best_model.pkl")
        sys.exit(1)
    
    pcap_path = sys.argv[1]
    model_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    predictor = ModelPredictor(model_path)
    predictor.predict_pcap(pcap_path)