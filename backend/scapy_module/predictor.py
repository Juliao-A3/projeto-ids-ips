import os
import pickle
import numpy as np
import pandas as pd
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

print("[Predictor] A carregar modelo Keras...")
model         = tf.keras.models.load_model(MODEL_PATH)
scaler        = _load_pickle(SCALER_PATH,    "ids_scaler.pkl")
le            = _load_pickle(ENCODER_PATH,   "ids_label_encoder.pkl")
feature_names = list(_load_pickle(FEATURES_PATH, "ids_features.pkl"))

print(f"[Predictor] Features ({len(feature_names)}): {feature_names}")
print(f"[Predictor] Classes  ({len(le.classes_)}): {list(le.classes_)}")

_CLASS_INDEX = {str(name).strip().lower(): idx for idx, name in enumerate(le.classes_)}
_WEB_PORTS = {80, 443, 8080, 8443}


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

    if protocol == 6 and syn_cnt >= 20 and ack_cnt == 0 and total_pkts >= 20:
        if dst_port == 22:
            return "SSH-Bruteforce", 0.95
        if dst_port == 21:
            return "FTP-BruteForce", 0.95
        if dst_port in _WEB_PORTS:
            return "Brute Force -Web", 0.95
        return "Bot", 0.90

    if protocol == 17 and total_pkts >= 50 and (flow_pkts_s >= 10 or flow_byts_s >= 10000):
        return "Bot", 0.90

    if protocol == 1 and total_pkts >= 50:
        return "Bot", 0.90

    if dst_port == 53 and total_pkts >= 100 and total_bytes >= 50000:
        return "Infilteration", 0.90

    if dst_port in _WEB_PORTS and duration >= 60 and total_bytes < 1000 and flow_pkts_s <= 1:
        return "Infilteration", 0.90

    if protocol == 6 and syn_cnt >= 50 and ack_cnt == 0 and rst_cnt <= 5 and flow_pkts_s >= 20:
        return "Bot", 0.88

    return None, 0.0


# ── Predict ────────────────────────────────────────────────────────────────
def predict_flow(flow_values: dict) -> dict:
    """
    Recebe um dicionário com os valores do fluxo e devolve a predição.

    Parâmetros
    ----------
    flow_values : dict
        Chaves = nomes das features (devem coincidir com ids_features.pkl).

    Retorno
    -------
    dict com:
        label_int    – índice numérico da classe prevista
        label_str    – nome da classe (ex: "Benign", "DoS", "Web Attack")
        confidence   – probabilidade máxima (0.0–1.0)
        is_attack    – bool (True se não for "Benign")
    """
    # 1. Constrói DataFrame com a ordem correta de features
    row = {feat: float(flow_values.get(feat, 0.0)) for feat in feature_names}
    df  = pd.DataFrame([row], columns=feature_names)

    # 2. Aplica o scaler
    X_scaled = scaler.transform(df)

    # 3. Predição com o modelo Keras
    pred_prob  = model.predict(X_scaled, verbose=0)   # shape: (1, n_classes)
    classe_idx = int(np.argmax(pred_prob[0]))
    confidence = float(np.max(pred_prob[0]))

    # 4. Converte índice → nome da classe via LabelEncoder
    label_str = str(le.classes_[classe_idx])
    is_attack = label_str.lower().strip() != "benign"

    # 5. Se o modelo fixo insiste em benigno mas o fluxo é claramente suspeito,
    #    aplica um fallback conservador baseado em regras simples do tráfego.
    if not is_attack:
        heuristic_label, heuristic_confidence = _heuristic_attack_label(flow_values)
        if heuristic_label is not None:
            heuristic_index = _CLASS_INDEX.get(heuristic_label.lower())
            if heuristic_index is not None:
                classe_idx = heuristic_index
                label_str = heuristic_label
                confidence = max(confidence, heuristic_confidence)
                is_attack = True

    return {
        "label_int":  classe_idx,
        "label_str":  label_str,
        "confidence": confidence,
        "is_attack":  is_attack,
    }


# ── Compatibilidade com código legado (testar_com_pastas, testar_modelo) ─────
class ModelPredictor:
    """Stub para compatibilidade com código legado que importa esta classe."""
    def __init__(self, modelo_path=None):
        self.model = model
        self.scaler = scaler
        self.feature_names = feature_names

    def predict_from_dict(self, features: dict) -> dict:
        """Compatibilidade com API antiga."""
        return predict_flow(features)

    def predict_flow(self, flow):
        """Compatibilidade com código antigo."""
        if hasattr(flow, 'get_model_features'):
            # Fluxo é objeto legado que tem get_model_features()
            X = flow.get_model_features().reshape(1, -1)
            X_scaled = scaler.transform(X)
            pred_prob = model.predict(X_scaled, verbose=0)
            classe_idx = int(np.argmax(pred_prob[0]))
            confidence = float(np.max(pred_prob[0]))
            label_str = str(le.classes_[classe_idx])
            pred_binario = 1 if label_str.lower().strip() == "benign" else -1
            return pred_binario, label_str, confidence
        else:
            # Fluxo é dicionário
            result = predict_flow(flow if isinstance(flow, dict) else {})
            pred_binario = 1 if not result.get("is_attack", False) else -1
            return pred_binario, result.get("label_str", "Benign"), result.get("confidence", 0.0)


# ── Teste rápido ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    dummy  = {feat: 0.0 for feat in feature_names}
    result = predict_flow(dummy)
    print("[Predictor] Teste com zeros:", result)
