# backend/scapy_module/explicador.py
# Explicador de decisões do modelo (SHAP/LIME)

import numpy as np
import pickle
from pathlib import Path
import sys

PROJECT_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_PATH))

class Explicador:
    """
    Explica porque um fluxo foi classificado como anomalia
    Usa SHAP (se disponível) ou método simplificado
    """
    
    def __init__(self, modelo_path=None):
        self.modelo_path = modelo_path
        self.model = None
        self.feature_names = None
        self.shap_available = False
        
        # Tentar importar SHAP
        try:
            import shap
            self.shap = shap
            self.shap_available = True
        except ImportError:
            print("⚠️ SHAP não instalado. Usando método simplificado.")
        
        # Carregar modelo
        if modelo_path:
            self._carregar_modelo(modelo_path)
    
    def _carregar_modelo(self, modelo_path):
        """Carrega o modelo para usar SHAP"""
        try:
            with open(modelo_path, 'rb') as f:
                data = pickle.load(f)
            
            if isinstance(data, dict):
                self.model = data.get('modelo')
                self.feature_names = data.get('feature_names', [])
            else:
                self.model = data
            
            print(f"✅ Modelo carregado para explicação")
        except Exception as e:
            print(f"❌ Erro ao carregar modelo: {e}")
    
    def explicar(self, features, feature_names=None):
        """
        Explica porque uma amostra foi classificada como anomalia
        
        Args:
            features: array de features (1D ou 2D)
            feature_names: lista de nomes das features
        
        Returns:
            dict: explicação com contribuições
        """
        if feature_names is None:
            feature_names = self.feature_names
        
        # Converter para 2D se necessário
        if features.ndim == 1:
            features = features.reshape(1, -1)
        
        # Verificar se o modelo está carregado
        if self.model is None:
            return self._explicar_simplificado(features, feature_names)
        
        # Usar SHAP se disponível
        if self.shap_available:
            return self._explicar_shap(features, feature_names)
        else:
            return self._explicar_simplificado(features, feature_names)
    
    def _explicar_shap(self, features, feature_names):
        """Usa SHAP para explicar"""
        try:
            # Criar explainer
            explainer = self.shap.TreeExplainer(self.model)
            
            # Calcular SHAP values
            shap_values = explainer.shap_values(features)
            
            # Se for Isolation Forest, shap_values pode ser lista
            if isinstance(shap_values, list):
                shap_values = shap_values[0]
            
            # Ordenar por importância
            importances = []
            for i, name in enumerate(feature_names[:features.shape[1]]):
                importances.append({
                    'feature': name,
                    'importance': float(abs(shap_values[0][i]))
                })
            
            importances.sort(key=lambda x: x['importance'], reverse=True)
            
            return {
                'metodo': 'SHAP',
                'contribuicoes': importances[:5],  # Top 5 features
                'predicao': 'anomalia' if self.model.predict(features)[0] == -1 else 'normal'
            }
        except Exception as e:
            return self._explicar_simplificado(features, feature_names)
    
    def _explicar_simplificado(self, features, feature_names):
        """Método simplificado sem SHAP"""
        
        # Se não temos nomes, criar nomes genéricos
        if not feature_names:
            feature_names = [f'feature_{i}' for i in range(features.shape[1])]
        
        # Calcular desvio da média (simulação)
        importances = []
        for i, name in enumerate(feature_names[:features.shape[1]]):
            # Simular importância baseada no valor
            valor = abs(features[0][i])
            importancia = min(valor / 10, 1.0) if valor > 0 else 0
            
            importances.append({
                'feature': name,
                'importance': importancia,
                'value': float(features[0][i])
            })
        
        importances.sort(key=lambda x: x['importance'], reverse=True)
        
        return {
            'metodo': 'simplificado',
            'contribuicoes': importances[:5],
            'predicao': 'anomalia' if self.model and self.model.predict(features)[0] == -1 else 'desconhecida'
        }
    
    def explicar_fluxo(self, fluxo):
        """Explica a classificação de um fluxo"""
        features = fluxo.get_features()
        feature_values = list(features.values())
        feature_names = list(features.keys())
        
        return self.explicar(feature_values, feature_names)


# Instância global
explicador = Explicador()