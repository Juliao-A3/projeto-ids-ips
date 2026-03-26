# backend/scapy_module/predictor.py
# Predictor para modelo com 78 features (fluxos)

import pickle
import numpy as np
from pathlib import Path
from datetime import datetime
import json
import sys

PROJECT_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_PATH))

from backend.scapy_module.extractor import FlowExtractor

class ModelPredictor:
    """
    Classifica fluxos usando modelo treinado (78 features)
    """
    
    def __init__(self, model_path=None):
        """
        Carrega o modelo .pkl e configura o extrator
        """
        if model_path is None:
            self.model_path = PROJECT_PATH / "models" / "modelo_principal.pkl"
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
        self.scaler = None
        
        # CASO 1: É um dicionário
        if isinstance(self.model_data, dict):
            print("📋 Modelo carregado como dicionário")
            print(f"   Chaves disponíveis: {list(self.model_data.keys())}")
            
            # Tentar encontrar o modelo
            if 'modelo' in self.model_data:
                self.model = self.model_data['modelo']
                print("   ✅ Usando chave 'modelo'")
            elif 'model' in self.model_data:
                self.model = self.model_data['model']
                print("   ✅ Usando chave 'model'")
            elif 'classifier' in self.model_data:
                self.model = self.model_data['classifier']
                print("   ✅ Usando chave 'classifier'")
            else:
                # Procurar qualquer objeto com predict
                for key, value in self.model_data.items():
                    if hasattr(value, 'predict'):
                        self.model = value
                        print(f"   ✅ Encontrado modelo na chave: '{key}'")
                        break
                
                if self.model is None:
                    print("   ⚠️ Nenhum modelo encontrado")
                    self.model = self.model_data
            
            # Carregar feature_names e acurácia
            self.feature_names = self.model_data.get('feature_names', None)
            self.acuracia = self.model_data.get('acuracia', 'desconhecida')
            self.scaler = self.model_data.get('scaler', None)
        
        # CASO 2: É diretamente o modelo
        else:
            self.model = self.model_data
            print("📋 Modelo carregado diretamente")
            
            if hasattr(self.model, 'feature_names_in_'):
                self.feature_names = list(self.model.feature_names_in_)
                print(f"   ✅ Features encontradas: {len(self.feature_names)}")
        
        # Verificar se o modelo tem método predict
        if not hasattr(self.model, 'predict'):
            print("❌ ERRO: O objeto carregado NÃO tem método 'predict'")
            print(f"   Tipo do objeto: {type(self.model)}")
        else:
            print(f"✅ Modelo carregado com sucesso!")
            print(f"   Acurácia: {self.acuracia}")
            
            if hasattr(self.model, 'n_features_in_'):
                print(f"   Features esperadas: {self.model.n_features_in_}")
            elif self.feature_names:
                print(f"   Features esperadas: {len(self.feature_names)}")
        
        # Inicializar extrator de fluxos
        self.flow_extractor = FlowExtractor()
    
    def predict_flow(self, flow):
        """
        Classifica um fluxo individual
        """
        features = flow.get_features()
        feature_values = np.array([list(features.values())], dtype=np.float32)
        
        # Normalizar se scaler disponível
        if self.scaler:
            feature_values = self.scaler.transform(feature_values)
        
        # Verificar número de features
        expected_features = self.model.n_features_in_ if hasattr(self.model, 'n_features_in_') else len(self.feature_names)
        if feature_values.shape[1] != expected_features:
            print(f"⚠️ Número de features diferente! Esperado: {expected_features}, Obtido: {feature_values.shape[1]}")
            # Ajustar
            if feature_values.shape[1] > expected_features:
                feature_values = feature_values[:, :expected_features]
            else:
                pad = np.zeros((1, expected_features - feature_values.shape[1]))
                feature_values = np.hstack([feature_values, pad])
        
        pred = self.model.predict(feature_values)[0]
        score = self.model.score_samples(feature_values)[0] if hasattr(self.model, 'score_samples') else 0
        
        return pred, score
    
    def predict_flows(self, flows):
        """
        Classifica múltiplos fluxos
        """
        features_list = []
        for flow in flows:
            features = flow.get_features()
            features_list.append(list(features.values()))
        
        X = np.array(features_list, dtype=np.float32)
        
        # Normalizar
        if self.scaler:
            X = self.scaler.transform(X)
        
        # Verificar número de features
        expected_features = self.model.n_features_in_ if hasattr(self.model, 'n_features_in_') else len(self.feature_names)
        if X.shape[1] != expected_features:
            if X.shape[1] > expected_features:
                X = X[:, :expected_features]
            else:
                pad = np.zeros((X.shape[0], expected_features - X.shape[1]))
                X = np.hstack([X, pad])
        
        predictions = self.model.predict(X)
        scores = self.model.score_samples(X) if hasattr(self.model, 'score_samples') else np.zeros(len(X))
        
        return predictions, scores
    
    def predict_flow_features(self, feature_values):
        """
        Classifica usando array de features já extraído
        """
        X = np.array([feature_values], dtype=np.float32)
        
        if self.scaler:
            X = self.scaler.transform(X)
        
        pred = self.model.predict(X)[0]
        score = self.model.score_samples(X)[0] if hasattr(self.model, 'score_samples') else 0
        
        return pred, score


# Para testar diretamente
if __name__ == "__main__":
    if len(sys.argv) > 1:
        model_path = sys.argv[1] if len(sys.argv) > 1 else None
        predictor = ModelPredictor(model_path)
        print("✅ Predictor pronto para classificar fluxos!")
    else:
        predictor = ModelPredictor()
        print("✅ Predictor carregado com modelo padrão!")