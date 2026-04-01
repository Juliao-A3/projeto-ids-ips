# backend/scapy_module/predictor.py

import pickle
import numpy as np
import pandas as pd
from pathlib import Path
import sys

PROJECT_PATH = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = PROJECT_PATH / "models" / "random_forest_server_model.pkl"

LABEL_MAP = {
    0: "Benign",
    1: "Bot",
    2: "Brute Force -Web",
    3: "Brute Force -XSS",
    4: "FTP-BruteForce",
    5: "Infilteration",
    6: "SQL Injection",
    7: "SSH-Bruteforce"
}

class ModelPredictor:

    def __init__(self, model_path=None):
        path = Path(model_path) if model_path else MODEL_PATH

        print(f"📂 A carregar modelo: {path.name}")

        if not path.exists():
            raise FileNotFoundError(f"Modelo não encontrado: {path}")

        with path.open('rb') as f:
            dados = pickle.load(f)

        if isinstance(dados, dict):
            print(f"   Chaves: {list(dados.keys())}")
            self.model  = dados.get('modelo') or dados.get('model') or dados.get('classifier')
            self.scaler = dados.get('scaler', None)
            self.acuracia = dados.get('acuracia', 'desconhecida')

            if self.model is None:
                for v in dados.values():
                    if hasattr(v, 'predict'):
                        self.model = v
                        break
        else:
            self.model    = dados
            self.scaler   = None
            self.acuracia = 'desconhecida'

        if not hasattr(self.model, 'predict'):
            raise ValueError(f"❌ Objecto carregado não tem método predict. Tipo: {type(self.model)}")

        n = getattr(self.model, 'n_features_in_', '?')
        print(f"✅ Modelo carregado!")
        print(f"   Tipo:      {type(self.model).__name__}")
        print(f"   Features:  {n}")
        print(f"   Classes:   {list(self.model.classes_) if hasattr(self.model, 'classes_') else '?'}")
        print(f"   Acurácia:  {self.acuracia}")
        print(f"   Scaler:    {'Sim' if self.scaler else 'Não'}")

        if n != '?' and n != 10:
            print(f"⚠️  ATENÇÃO: modelo espera {n} features mas o extractor fornece 10.")

        # Guardar os nomes das features do modelo (se existirem)
        self.feature_names = list(getattr(self.model, 'feature_names_in_', [])) or None

    def _to_dataframe(self, X: np.ndarray) -> pd.DataFrame:
        """
        Converte numpy array para DataFrame com os nomes de features do modelo,
        eliminando o UserWarning do sklearn sobre feature names.
        """
        if self.feature_names:
            return pd.DataFrame(X, columns=self.feature_names)
        return pd.DataFrame(X)

    def predict_flow(self, flow):
        """
        Recebe um objecto Flow e devolve (label_int, label_str, confiança).
        """
        X = flow.get_model_features().reshape(1, -1)
        X_df = self._to_dataframe(X)

        if self.scaler:
            X_scaled = self.scaler.transform(X_df)
            X_df = self._to_dataframe(X_scaled)

        pred_int = int(self.model.predict(X_df)[0])
        pred_str = LABEL_MAP.get(pred_int, f"Desconhecido ({pred_int})")

        if hasattr(self.model, 'predict_proba'):
            proba     = self.model.predict_proba(X_df)[0]
            confianca = float(np.max(proba))
        else:
            confianca = 1.0

        return pred_int, pred_str, confianca

    def predict_flows(self, flows):
        """
        Classifica uma lista de fluxos de uma vez.
        Devolve lista de (label_int, label_str, confiança).
        """
        if not flows:
            return []

        X = np.vstack([f.get_model_features() for f in flows])
        X_df = self._to_dataframe(X)

        if self.scaler:
            X_scaled = self.scaler.transform(X_df)
            X_df = self._to_dataframe(X_scaled)

        preds = self.model.predict(X_df)

        if hasattr(self.model, 'predict_proba'):
            probas    = self.model.predict_proba(X_df)
            confianças = np.max(probas, axis=1)
        else:
            confianças = np.ones(len(preds))

        resultado = []
        for pred_int, conf in zip(preds, confianças):
            pred_int = int(pred_int)
            resultado.append((
                pred_int,
                LABEL_MAP.get(pred_int, str(pred_int)),
                float(conf)
            ))

        return resultado

    def is_attack(self, pred_int):
        """Devolve True se a previsão não for Benign."""
        return pred_int != 0

    def get_label(self, pred_int):
        """Devolve o nome do label dado o inteiro."""
        return LABEL_MAP.get(pred_int, f"Desconhecido ({pred_int})")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    p = ModelPredictor(path)
    print("✅ Predictor pronto!")