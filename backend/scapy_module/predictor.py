# backend/scapy_module/predictor.py

import pickle
import json
import numpy as np
import pandas as pd
<<<<<<< HEAD
from pathlib import Path
import sys
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

PROJECT_PATH = Path(__file__).resolve().parent.parent.parent
=======
try:
        import tensorflow as tf
        TF_AVAILABLE = True
except ImportError:
        tf = None
        TF_AVAILABLE = False

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
STUDY_DIR  = os.path.join(BASE_DIR, "..", "..", "estudo")   # pasta estudo na raiz do projeto

MODEL_PATH    = os.path.join(STUDY_DIR, "ids_deep_learning_model.keras")
SCALER_PATH   = os.path.join(STUDY_DIR, "ids_scaler.pkl")
ENCODER_PATH  = os.path.join(STUDY_DIR, "ids_label_encoder.pkl")
FEATURES_PATH = os.path.join(STUDY_DIR, "ids_features.pkl")

# ── Load artefacts ─────────────────────────────────────────────────────────
def _load_pickle(path: str, name: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"[Predictor] Ficheiro não encontrado: {path}")
    with open(path, "rb") as f:
        obj = pickle.load(f)
    print(f"[Predictor] {name} carregado ✓")
    return obj

model = None
scaler = None
le = None
feature_names = []
_CLASS_INDEX = {}

if TF_AVAILABLE:
    try:
        print("[Predictor] A carregar modelo Keras...")
        model         = tf.keras.models.load_model(MODEL_PATH)
        scaler        = _load_pickle(SCALER_PATH,    "ids_scaler.pkl")
        le            = _load_pickle(ENCODER_PATH,   "ids_label_encoder.pkl")
        feature_names = list(_load_pickle(FEATURES_PATH, "ids_features.pkl"))
        print(f"[Predictor] Features ({len(feature_names)}): {feature_names}")
        print(f"[Predictor] Classes  ({len(le.classes_)}): {list(le.classes_)}")
        _CLASS_INDEX = {str(name).strip().lower(): idx for idx, name in enumerate(le.classes_)}
    except Exception as e:
        print(f"[Predictor] Modelo nao disponivel: {e}")
else:
    print("[Predictor] TensorFlow nao disponivel - modo cloud")
_WEB_PORTS = {80, 443, 8080, 8443}
>>>>>>> 85b6a24ae68ef8aae4e61f071fe9a0a7eb0089e7


def _resolver_modelo_padrao() -> Path:
    models_dir = PROJECT_PATH / "models"

    # 1) Modelo ativo salvo pela API
    ref_path = models_dir / "modelo_ativo.json"
    try:
        if ref_path.exists():
            with open(ref_path, "r", encoding="utf-8") as f:
                ref = json.load(f)
            nome = ref.get("nome")
            if nome:
                candidato = models_dir / nome
                if candidato.exists():
                    return candidato
    except Exception:
        pass

    # 2) Runtime model utilizado pelo backend
    best_model = models_dir / "best_model.pkl"
    if best_model.exists():
        return best_model

    # 3) Legados
    legacy_paths = [
        models_dir / "random_forest_server_model_20.pkl",
        models_dir / "random_forest_server_model.pkl",
    ]
    for p in legacy_paths:
        if p.exists():
            return p

    # 4) Fallback para o mais recente
    pkls = sorted(models_dir.glob("*.pkl"), key=lambda p: p.stat().st_mtime, reverse=True)
    if pkls:
        return pkls[0]

    raise FileNotFoundError(f"Nenhum modelo encontrado em: {models_dir}")

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
        path = Path(model_path) if model_path else _resolver_modelo_padrao()

        print(f"📂 A carregar modelo: {path.name}")
        

        if not path.exists():
            raise FileNotFoundError(f"Modelo não encontrado: {path}")

        with path.open('rb') as f:
            dados = pickle.load(f)

        if isinstance(dados, dict):
            print(f"   Chaves: {list(dados.keys())}")
            self.model    = dados.get('modelo') or dados.get('model') or dados.get('classifier')
            self.scaler   = dados.get('scaler', None)
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

        # Nomes das features guardados no modelo (sklearn >= 1.0)
        self.feature_names = list(getattr(self.model, 'feature_names_in_', [])) or None
        print(f"🔑 Features do modelo: {self.feature_names}")

    # ── Helpers internos ──────────────────────────────────────────────────

    def _to_dataframe(self, X: np.ndarray) -> pd.DataFrame:
        if self.feature_names:
            return pd.DataFrame(X, columns=self.feature_names)
        return pd.DataFrame(X)

    def _features_from_dict(self, features: dict) -> pd.DataFrame:
        """
        Recebe o dicionário do extractor.py (inclui chaves '_*' de metadados)
        e devolve um DataFrame com apenas as colunas que o modelo conhece,
        pela ordem correcta.
        """
        # Remover metadados (chaves que começam com '_')
        feat_clean = {k: v for k, v in features.items() if not k.startswith('_')}

        if self.feature_names:
            # Seleccionar e ordenar exactamente as features do modelo
            row = {col: feat_clean.get(col, 0.0) for col in self.feature_names}
            return pd.DataFrame([row], columns=self.feature_names)
        else:
            return pd.DataFrame([feat_clean])

    # ── API principal (usada pelo sniffer_realtime NFStream) ──────────────

    def predict_from_dict(self, features: dict) -> dict:
        """
        Recebe o dicionário devolvido por extrair_features_nfstream().
        Devolve {'label': str, 'confidence': float, 'label_int': int}.
        """
        X_df = self._features_from_dict(features)
        print(f"Features antes do scaler: {X_df.values}")

        X_model = X_df
        if self.scaler:
            X_scaled = self.scaler.transform(X_df)
            X_model = self._to_dataframe(X_scaled)
            print(f"Features depois do scaler: {X_model.values}")

        pred_int = int(self.model.predict(X_model)[0])
        label    = LABEL_MAP.get(pred_int, f"Desconhecido ({pred_int})")

        if hasattr(self.model, 'predict_proba'):
            proba      = self.model.predict_proba(X_model)[0]
            confidence = float(np.max(proba))
        else:
            confidence = 1.0

        return {
            'label':     label,
            'label_int': pred_int,
            'confidence': confidence,
        }

    # ── API legada (mantida para compatibilidade com rotas existentes) ────

    def predict_flow(self, flow):
        """Recebe objecto Flow com get_model_features(). Devolve (int, str, float)."""
        X      = flow.get_model_features().reshape(1, -1)
        X_df   = self._to_dataframe(X)

        if self.scaler:
            X_df = self._to_dataframe(self.scaler.transform(X_df))

        pred_int  = int(self.model.predict(X_df)[0])
        pred_str  = LABEL_MAP.get(pred_int, f"Desconhecido ({pred_int})")
        confianca = float(np.max(self.model.predict_proba(X_df)[0])) if hasattr(self.model, 'predict_proba') else 1.0

        return pred_int, pred_str, confianca

    def predict_flows(self, flows):
        if not flows:
            return []
        X    = np.vstack([f.get_model_features() for f in flows])
        X_df = self._to_dataframe(X)
        if self.scaler:
            X_df = self._to_dataframe(self.scaler.transform(X_df))
        preds     = self.model.predict(X_df)
        confianças = np.max(self.model.predict_proba(X_df), axis=1) if hasattr(self.model, 'predict_proba') else np.ones(len(preds))
        return [(int(p), LABEL_MAP.get(int(p), str(p)), float(c)) for p, c in zip(preds, confianças)]

    def is_attack(self, pred_int):
        return pred_int != 0

    def get_label(self, pred_int):
        return LABEL_MAP.get(pred_int, f"Desconhecido ({pred_int})")


# ── Singleton de módulo ───────────────────────────────────────────────────────
_predictor: ModelPredictor | None = None

def _get_predictor() -> ModelPredictor:
    global _predictor
    if _predictor is None:
        _predictor = ModelPredictor()
    return _predictor


def prever_fluxo(features: dict) -> dict | None:
    """
    Função de módulo chamada pelo sniffer_realtime.py (NFStream).

    Parâmetros
    ----------
    features : dict
        Dicionário devolvido por extrair_features_nfstream()
        (pode conter chaves '_*' de metadados — são ignoradas).

    Retorna
    -------
    dict  {'label': str, 'confidence': float, 'label_int': int}
    None  se ocorrer algum erro.
    """
    try:
        return _get_predictor().predict_from_dict(features)
    except Exception as exc:
        import logging
        logging.getLogger(__name__).error(f"Erro em prever_fluxo: {exc}", exc_info=True)
        return None


if __name__ == "__main__":
<<<<<<< HEAD
    path = sys.argv[1] if len(sys.argv) > 1 else None
    p = ModelPredictor(path)
    print("✅ Predictor pronto!")
=======
    dummy  = {feat: 0.0 for feat in feature_names}
    result = predict_flow(dummy)
    print("[Predictor] Teste com zeros:", result)
>>>>>>> 85b6a24ae68ef8aae4e61f071fe9a0a7eb0089e7
