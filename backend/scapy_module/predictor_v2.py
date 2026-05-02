"""
predictor_v2.py — Preditor Keras-first.

Tenta carregar o modelo Keras e, se isso falhar, usa apenas heurísticas.
Não há fallback para Random Forest neste arquivo.
"""

import os
import pickle

import numpy as np
import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
STUDY_DIR  = os.path.join(BASE_DIR, "..", "..", "estudo")

MODEL_KERAS_PATH      = os.path.join(STUDY_DIR, "ids_deep_learning_model.keras")
SCALER_PATH           = os.path.join(STUDY_DIR, "ids_scaler.pkl")
ENCODER_PATH          = os.path.join(STUDY_DIR, "ids_label_encoder.pkl")
FEATURES_PATH         = os.path.join(STUDY_DIR, "ids_features.pkl")
COMPONENTS_PATH       = os.path.join(STUDY_DIR, "ids_components.pkl")

# ── Estado global ──────────────────────────────────────────────────────────
model_type = None  # "keras", "heuristic" ou "deferred"
model = None
scaler = None
le = None
pca = None
feature_names = []
_CLASS_INDEX = {}
_WEB_PORTS = {80, 443, 8080, 8443}

def _load_pickle(path: str, name: str):
    """Carrega um pickle silenciosamente."""
    try:
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        return None

def _initialize_models():
    """Tenta carregar o modelo Keras; se falhar, usa heurísticas."""
    global model_type, model, scaler, le, pca, feature_names, _CLASS_INDEX

    # Carrega componentes compartilhados primeiro
    scaler_tmp = _load_pickle(SCALER_PATH, "")
    le_tmp = _load_pickle(ENCODER_PATH, "")
    features_tmp = _load_pickle(FEATURES_PATH, "")
    pca_tmp = _load_pickle(COMPONENTS_PATH, "")

    if scaler_tmp and le_tmp and features_tmp:
        scaler = scaler_tmp
        le = le_tmp
        feature_names = list(features_tmp)
        pca = pca_tmp
        _CLASS_INDEX = {str(name).strip().lower(): idx for idx, name in enumerate(le.classes_)}

    # Não carregamos o TensorFlow no momento da importação — isso evita
    # que o processo falhe ao inicializar GPUs em ambientes instáveis.
    # Se existir um modelo Keras, marcamos como 'deferred' para carregar
    # apenas quando necessário (na primeira predição).
    try:
        if os.path.exists(MODEL_KERAS_PATH):
            model_type = "deferred"
            print("[Predictor] Modelo Keras encontrado — carregamento adiado (lazy).")
            return
    except Exception:
        pass

    # Fallback final: apenas heurísticas
    model_type = "heuristic"
    print(f"[Predictor] ⚠️  Usando APENAS HEURÍSTICAS (sem modelo ML)")
    print(f"[Predictor]    Detecção baseada em regras de tráfego")

# Inicializar na importação
_initialize_models()


def _ensure_keras_loaded():
    """Tenta carregar o modelo Keras sob demanda.

    Evita importar TensorFlow no momento da importação do módulo.
    """
    global model_type, model
    if model_type != "deferred":
        return
    try:
        if not os.path.exists(MODEL_KERAS_PATH):
            model_type = "heuristic"
            return
        import tensorflow as tf
        loaded = tf.keras.models.load_model(MODEL_KERAS_PATH)
        model = loaded
        model_type = "keras"
        print(f"[Predictor] ✅ Modelo KERAS carregado em tempo de execução ({os.path.getsize(MODEL_KERAS_PATH) / (1024*1024):.1f}MB)")
    except Exception:
        model_type = "heuristic"
        print("[Predictor] Falha ao carregar modelo Keras em tempo de execução — usando heurísticas.")

# ── Helper functions ───────────────────────────────────────────────────────
def _safe_float(value, default=0.0):
    try:
        parsed = float(value)
        return default if (parsed != parsed) else parsed
    except (TypeError, ValueError):
        return default

def _safe_int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default

def _heuristic_attack_label(flow_values: dict) -> tuple[str | None, float]:
    """Fallback conservador para tráfego claramente malicioso."""
    dst_port = _safe_int(flow_values.get("Dst Port", 0))
    protocol = _safe_int(flow_values.get("Protocol", 0))
    duration = _safe_float(flow_values.get("Flow Duration", 0.0))
    total_fwd_pkts = _safe_float(flow_values.get("Tot Fwd Pkts", 0.0))
    total_bwd_pkts = _safe_float(flow_values.get("Tot Bwd Pkts", 0.0))
    total_pkts = total_fwd_pkts + total_bwd_pkts
    flow_pkts_s = _safe_float(flow_values.get("Flow Pkts/s", 0.0))
    flow_byts_s = _safe_float(flow_values.get("Flow Byts/s", 0.0))
    syn_cnt = _safe_float(flow_values.get("SYN Flag Cnt", 0.0))
    ack_cnt = _safe_float(flow_values.get("ACK Flag Cnt", 0.0))
    rst_cnt = _safe_float(flow_values.get("RST Flag Cnt", 0.0))
    total_bytes = _safe_float(flow_values.get("TotLen Fwd Pkts", 0.0)) + _safe_float(flow_values.get("TotLen Bwd Pkts", 0.0))

    # SSH/FTP brute-force
    if protocol == 6 and syn_cnt >= 20 and ack_cnt == 0 and total_pkts >= 20:
        if dst_port == 22:
            return "SSH-Bruteforce", 0.95
        if dst_port == 21:
            return "FTP-BruteForce", 0.95
        if dst_port in _WEB_PORTS:
            return "Brute Force -Web", 0.95
        return "Bot", 0.90

    # UDP flooding/Bot
    if protocol == 17 and total_pkts >= 50 and (flow_pkts_s >= 10 or flow_byts_s >= 10000):
        return "Bot", 0.90

    # ICMP flooding
    if protocol == 1 and total_pkts >= 50:
        return "Bot", 0.90

    # DNS exfiltration
    if dst_port == 53 and total_pkts >= 100 and total_bytes >= 50000:
        return "Infilteration", 0.90

    # HTTPS tunneling
    if dst_port in _WEB_PORTS and duration >= 60 and total_bytes < 1000 and flow_pkts_s <= 1:
        return "Infilteration", 0.90

    # SYN flood
    if protocol == 6 and syn_cnt >= 50 and ack_cnt == 0 and rst_cnt <= 5 and flow_pkts_s >= 20:
        return "Bot", 0.88

    return None, 0.0


def _label_to_index(label_str: str) -> int:
    label_norm = str(label_str or "").strip().lower()
    return int(_CLASS_INDEX.get(label_norm, -1))

# ── Main prediction function ──────────────────────────────────────────────
def predict_flow(flow_values: dict) -> dict:
    """
    Classifica um fluxo de rede.

    Parâmetros
    ----------
    flow_values : dict
        Chaves = nomes das features do CIC

    Retorno
    -------
    dict com:
        label_int    – índice numérico da classe prevista
        label_str    – nome da classe ("Benign", "DoS", "Bot", etc.)
        confidence   – probabilidade (0.0–1.0)
        is_attack    – bool
        model_type   – qual modelo foi usado na predição
    """
    
    # Fallback de emergência se não houver features
    if not feature_names:
        heuristic_label, heuristic_conf = _heuristic_attack_label(flow_values)
        return {
            "label_int": _label_to_index(heuristic_label or "Benign"),
            "label_str": heuristic_label or "Unknown",
            "confidence": heuristic_conf,
            "is_attack": heuristic_label is not None,
            "model_type": "heuristic_emergency",
        }

    # Construir vetor de features
    try:
        row = {feat: float(flow_values.get(feat, 0.0)) for feat in feature_names}
        X = np.array([list(row.values())])
    except Exception:
        return {
            "label_int": -1,
            "label_str": "Error",
            "confidence": 0.0,
            "is_attack": False,
            "model_type": "error",
        }

    # ── Predição com Keras (se disponível)
    if model_type == "deferred":
        _ensure_keras_loaded()

    if model_type == "keras":
        try:
            import tensorflow as tf
            X_scaled = scaler.transform(X)
            pred_prob = model.predict(X_scaled, verbose=0)
            classe_idx = int(np.argmax(pred_prob[0]))
            confidence = float(np.max(pred_prob[0]))
            label_str = str(le.classes_[classe_idx])
            is_attack = label_str.lower().strip() != "benign"
            return {
                "label_int": classe_idx,
                "label_str": label_str,
                "confidence": confidence,
                "is_attack": is_attack,
                "model_type": "keras",
            }
        except Exception as e:
            # Fallthrough to heuristics
            pass

    # ── Fallback final: apenas heurísticas ──────────────────────────────
    heuristic_label, heuristic_confidence = _heuristic_attack_label(flow_values)
    if heuristic_label is not None:
        return {
            "label_int": _label_to_index(heuristic_label),
            "label_str": heuristic_label,
            "confidence": heuristic_confidence,
            "is_attack": True,
            "model_type": "heuristic",
        }
    else:
        return {
            "label_int": _label_to_index("Benign"),
            "label_str": "Benign",
            "confidence": 0.5,
            "is_attack": False,
            "model_type": "heuristic",
        }


class ModelPredictor:
    """Compatibilidade com código legado."""

    def __init__(self, modelo_path=None):
        self.model = model
        self.scaler = scaler
        self.feature_names = feature_names

    def predict_from_dict(self, features: dict) -> dict:
        return predict_flow(features)

    def predict_flow(self, flow):
        if hasattr(flow, "get_model_features"):
            _ensure_keras_loaded()
            X = flow.get_model_features().reshape(1, -1)
            X_scaled = scaler.transform(X)
            pred_prob = model.predict(X_scaled, verbose=0)
            classe_idx = int(np.argmax(pred_prob[0]))
            confidence = float(np.max(pred_prob[0]))
            label_str = str(le.classes_[classe_idx])
            pred_binario = 1 if label_str.lower().strip() == "benign" else -1
            return pred_binario, label_str, confidence

        result = predict_flow(flow if isinstance(flow, dict) else {})
        pred_binario = 1 if not result.get("is_attack", False) else -1
        return pred_binario, result.get("label_str", "Benign"), result.get("confidence", 0.0)

# ── Teste ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n[Predictor] Modo: {model_type}")
    print(f"[Predictor] Features: {len(feature_names)}")
    
    # Teste com fluxo benign (zeros)
    dummy = {feat: 0.0 for feat in feature_names}
    result = predict_flow(dummy)
    print(f"[Predictor] Teste (zeros): {result}")
    
    # Teste com fluxo suspeito (muitos SYN)
    suspicious = {feat: 0.0 for feat in feature_names}
    suspicious["Dst Port"] = 22
    suspicious["SYN Flag Cnt"] = 50
    suspicious["ACK Flag Cnt"] = 0
    suspicious["Tot Fwd Pkts"] = 50
    suspicious["Protocol"] = 6
    result = predict_flow(suspicious)
    print(f"[Predictor] Teste (SSH brute): {result}")
