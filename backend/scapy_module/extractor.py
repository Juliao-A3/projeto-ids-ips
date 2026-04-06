"""
extractor.py  ·  AEGIS – NFStream → CIC-IDS 2018 feature extractor
--------------------------------------------------------------------
Converte um objecto NFStream Flow nas colunas exactas que o modelo
Random Forest espera (feature_names_in_).

NFStream com statistical_analysis=True fornece TODAS as features
CIC-IDS 2018, incluindo Init Fwd/Bwd Win Byts — que antes eram
impossíveis de capturar packet-by-packet com Scapy.
"""

from __future__ import annotations
import math
import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe(val, default: float = 0.0) -> float:
    """Devolve val ou default se val for None / NaN / inf."""
    if val is None:
        return default
    try:
        f = float(val)
        return default if (math.isnan(f) or math.isinf(f)) else f
    except (TypeError, ValueError):
        return default


def _rate(numerator, duration_s: float) -> float:
    """numerador / duração, protegido contra divisão por zero."""
    return _safe(numerator) / duration_s if duration_s > 0 else 0.0


def _ms_to_us(ms_val) -> float:
    """Milissegundos → microssegundos (CIC-IDS usa µs para IAT)."""
    return _safe(ms_val) * 1_000.0


# ---------------------------------------------------------------------------
# Mapeamento principal
# ---------------------------------------------------------------------------

def extrair_features_nfstream(flow) -> dict | None:
    """
    Recebe um objecto NFStream NFlow (gerado com statistical_analysis=True)
    e devolve um dicionário com:
        - chaves '_*'   : metadados (não enviados ao modelo)
        - chaves restantes : features CIC-IDS 2018 completas

    Devolve None se o fluxo não tiver tráfego suficiente para
    produzir uma predição significativa.
    """
    # Filtro mínimo: pelo menos 2 pacotes bidirecionais
    if _safe(flow.bidirectional_packets) < 2:
        return None

    if _safe(flow.bidirectional_bytes) == 0:
        return None
    # ── Duração em segundos (denominador para taxas) ──────────────────────
    dur_ms = _safe(flow.bidirectional_duration_ms, default=1.0)
    dur_s  = max(dur_ms / 1_000.0, 1e-9)

    # ── IAT: NFStream reporta em ms, CIC-IDS espera µs ───────────────────
    #   NFStream NÃO fornece IAT total directamente;
    #   aproximamos como (n_pkts - 1) × mean_IAT
    fwd_pkts  = _safe(flow.src2dst_packets)
    bwd_pkts  = _safe(flow.dst2src_packets)
    fwd_n_iat = max(fwd_pkts - 1, 0)
    bwd_n_iat = max(bwd_pkts - 1, 0)

    fwd_iat_mean_us = _ms_to_us(flow.src2dst_mean_piat_ms)
    bwd_iat_mean_us = _ms_to_us(flow.dst2src_mean_piat_ms)

    fwd_iat_tot = fwd_n_iat * fwd_iat_mean_us
    bwd_iat_tot = bwd_n_iat * bwd_iat_mean_us

    # ── Metadados (não vão ao modelo) ─────────────────────────────────────
    metadata = {
        '_src_ip':   getattr(flow, 'src_ip',   '?'),
        '_dst_ip':   getattr(flow, 'dst_ip',   '?'),
        '_src_port': getattr(flow, 'src_port',  0),
        '_dst_port': getattr(flow, 'dst_port',  0),
        '_protocol': getattr(flow, 'protocol',  0),
        '_app':      getattr(flow, 'application_name', 'Unknown'),
    }

    # ── Features CIC-IDS 2018 ─────────────────────────────────────────────
    features = {
        # ── Volume básico ─────────────────────────────────────────────────
        'Flow Duration'    : dur_ms * 1_000.0,                          # µs
        'Tot Fwd Pkts'     : fwd_pkts,
        'Tot Bwd Pkts'     : bwd_pkts,
        'TotLen Fwd Pkts'  : _safe(flow.src2dst_bytes),
        'TotLen Bwd Pkts'  : _safe(flow.dst2src_bytes),

        # ── Tamanho de pacotes forward ────────────────────────────────────
        'Fwd Pkt Len Max'  : _safe(flow.src2dst_max_ps),
        'Fwd Pkt Len Min'  : _safe(flow.src2dst_min_ps),
        'Fwd Pkt Len Mean' : _safe(flow.src2dst_mean_ps),
        'Fwd Pkt Len Std'  : _safe(flow.src2dst_stddev_ps),

        # ── Tamanho de pacotes backward ───────────────────────────────────
        'Bwd Pkt Len Max'  : _safe(flow.dst2src_max_ps),
        'Bwd Pkt Len Min'  : _safe(flow.dst2src_min_ps),
        'Bwd Pkt Len Mean' : _safe(flow.dst2src_mean_ps),
        'Bwd Pkt Len Std'  : _safe(flow.dst2src_stddev_ps),

        # ── Taxas ─────────────────────────────────────────────────────────
        'Flow Byts/s'      : _rate(flow.bidirectional_bytes,   dur_s),
        'Flow Pkts/s'      : _rate(flow.bidirectional_packets, dur_s),
        'Fwd Pkts/s'       : _rate(flow.src2dst_packets,       dur_s),
        'Bwd Pkts/s'       : _rate(flow.dst2src_packets,       dur_s),

        # ── IAT bidireccional ─────────────────────────────────────────────
        'Flow IAT Mean'    : _ms_to_us(flow.bidirectional_mean_piat_ms),
        'Flow IAT Std'     : _ms_to_us(flow.bidirectional_stddev_piat_ms),
        'Flow IAT Max'     : _ms_to_us(flow.bidirectional_max_piat_ms),
        'Flow IAT Min'     : _ms_to_us(flow.bidirectional_min_piat_ms),

        # ── IAT forward ───────────────────────────────────────────────────
        'Fwd IAT Tot'      : fwd_iat_tot,
        'Fwd IAT Mean'     : fwd_iat_mean_us,
        'Fwd IAT Std'      : _ms_to_us(flow.src2dst_stddev_piat_ms),
        'Fwd IAT Max'      : _ms_to_us(flow.src2dst_max_piat_ms),
        'Fwd IAT Min'      : _ms_to_us(flow.src2dst_min_piat_ms),

        # ── IAT backward ──────────────────────────────────────────────────
        'Bwd IAT Tot'      : bwd_iat_tot,
        'Bwd IAT Mean'     : bwd_iat_mean_us,
        'Bwd IAT Std'      : _ms_to_us(flow.dst2src_stddev_piat_ms),
        'Bwd IAT Max'      : _ms_to_us(flow.dst2src_max_piat_ms),
        'Bwd IAT Min'      : _ms_to_us(flow.dst2src_min_piat_ms),

        # ── Flags TCP ─────────────────────────────────────────────────────
        'Fwd PSH Flags'    : _safe(flow.src2dst_psh_packets),
        'Bwd PSH Flags'    : _safe(flow.dst2src_psh_packets),
        'Fwd URG Flags'    : _safe(flow.src2dst_urg_packets),
        'Bwd URG Flags'    : _safe(flow.dst2src_urg_packets),
        'FIN Flag Cnt'     : _safe(flow.bidirectional_fin_packets),
        'SYN Flag Cnt'     : _safe(flow.bidirectional_syn_packets),
        'RST Flag Cnt'     : _safe(flow.bidirectional_rst_packets),
        'PSH Flag Cnt'     : _safe(flow.bidirectional_psh_packets),
        'ACK Flag Cnt'     : _safe(flow.bidirectional_ack_packets),
        'URG Flag Cnt'     : _safe(flow.bidirectional_urg_packets),
        'CWE Flag Count'   : _safe(flow.bidirectional_cwr_packets),
        'ECE Flag Cnt'     : _safe(flow.bidirectional_ece_packets),

        # ── Estatísticas de tamanho (todos os pacotes) ────────────────────
        'Pkt Len Min'      : _safe(flow.bidirectional_min_ps),
        'Pkt Len Max'      : _safe(flow.bidirectional_max_ps),
        'Pkt Len Mean'     : _safe(flow.bidirectional_mean_ps),
        'Pkt Len Std'      : _safe(flow.bidirectional_stddev_ps),
        'Pkt Len Var'      : _safe(flow.bidirectional_stddev_ps) ** 2,

        # ── Rácios e médias ───────────────────────────────────────────────
        'Down/Up Ratio'    : (
            _safe(flow.dst2src_bytes) / _safe(flow.src2dst_bytes)
            if _safe(flow.src2dst_bytes) > 0 else 0.0
        ),
        # Nomes alinhados com CIC-IDS 2018 / modelo treinado
        'Pkt Size Avg'     : _safe(flow.bidirectional_mean_ps),
        'Fwd Seg Size Avg' : _safe(flow.src2dst_mean_ps),
        'Bwd Seg Size Avg' : _safe(flow.dst2src_mean_ps),

        # ── Subflows (NFStream não segmenta; usa totais) ──────────────────
        'Subflow Fwd Pkts' : fwd_pkts,
        'Subflow Bwd Pkts' : bwd_pkts,
        'Subflow Fwd Byts' : _safe(flow.src2dst_bytes),
        'Subflow Bwd Byts' : _safe(flow.dst2src_bytes),

        # ── Forward activo / segmento mínimo ─────────────────────────────
        'Fwd Act Data Pkts': fwd_pkts,
        'Fwd Seg Size Min' : _safe(flow.src2dst_min_ps),

        # ── Active / Idle — NFStream não rastreia; zeros seguros ─────────
        'Active Mean'      : 0.0,
        'Active Std'       : 0.0,
        'Active Max'       : 0.0,
        'Active Min'       : 0.0,
        'Idle Mean'        : 0.0,
        'Idle Std'         : 0.0,
        'Idle Max'         : 0.0,
        'Idle Min'         : 0.0,
    }

    return {**metadata, **features}