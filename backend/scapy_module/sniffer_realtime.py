"""
sniffer_realtime.py — Captura via cicflowmeter subprocess
O cicflowmeter corre como processo externo e faz POST de cada fluxo
para /sniffer/flow-input. O FastAPI classifica e envia pelo WebSocket.

API pública:
    iniciar(interface, callback, loop)
    parar()
    estado()
    processar_fluxo(flow_dict)  ← chamado pelo endpoint /sniffer/flow-input
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import subprocess
import threading
import asyncio
import time
from urllib.parse import quote
from collections import defaultdict, deque
import ipaddress

from extractor import extrair_features
from predictor import predict_flow
from whitelist import get_whitelist
from web_attack_rules import WebAttackRulesEngine

# Configuração
FASTAPI_PORT  = 8000
FLOW_ENDPOINT = (
    os.getenv("SNIFFER_FLOW_ENDPOINT")
    or os.getenv("FLOW_ENDPOINT")
    or f"http://127.0.0.1:{FASTAPI_PORT}/sniffer/flow-input"
)

# Whitelist centralizada
_whitelist_manager = get_whitelist()

# Controle por ambiente para evitar falso positivo em tráfego interno conhecido.
_WHITELIST_ENABLED = os.getenv("WHITELIST_ENABLED", "1") == "1"

def _should_ignore_flow(src_ip: str, dst_ip: str) -> bool:
    """Verifica se um fluxo deve ser ignorado por estar na whitelist."""
    if not _WHITELIST_ENABLED:
        return False  # DEBUG: Permitir tudo
    # Ignora apenas tráfego totalmente interno/permitido.
    # Se só uma ponta estiver whitelisted (ex.: host protegido), mantém deteção ativa.
    return _whitelist_manager.is_ip_whitelisted(src_ip) and _whitelist_manager.is_ip_whitelisted(dst_ip)

# Estado interno 
_processes: dict[str, subprocess.Popen] = {}
_threads: dict[str, threading.Thread] = {}
_proc_lock = threading.Lock()
_stop_event = threading.Event()

_callback  = None
_loop:     asyncio.AbstractEventLoop | None = None

contador_fluxos   = 0
ataques_detetados = 0
_start_time       = 0.0

_SSH_BRUTE_WINDOW_S = float(os.getenv("SSH_BRUTE_WINDOW_SECONDS", "120"))
_FTP_BRUTE_WINDOW_S = 20.0
_SSH_BRUTE_MIN_ATTEMPTS = max(1, int(os.getenv("SSH_BRUTE_MIN_ATTEMPTS", "2")))
_FTP_BRUTE_MIN_ATTEMPTS = 3
_ssh_attempts: dict[tuple[str, str, int], deque[float]] = defaultdict(deque)
_ftp_attempts: dict[tuple[str, str, int], deque[float]] = defaultdict(deque)
_noisy_label_attempts: dict[tuple[str, str], deque[float]] = defaultdict(deque)
_ENABLE_HEURISTIC_ATTACK_OVERRIDE = os.getenv("ENABLE_HEURISTIC_ATTACK_OVERRIDE", "1") == "1"
_ENABLE_SSH_FTP_HEURISTIC_OVERRIDE = os.getenv("ENABLE_SSH_FTP_HEURISTIC_OVERRIDE", "1") == "1"
_ENABLE_WEB_HEURISTIC_OVERRIDE = os.getenv("ENABLE_WEB_HEURISTIC_OVERRIDE", "0") == "1"
_web_attack_rules = WebAttackRulesEngine(_should_ignore_flow)
_MIN_ATTACK_CONFIDENCE = float(os.getenv("ATTACK_MIN_CONFIDENCE", "0.82"))
_MIN_INFILTRATION_CONFIDENCE = float(os.getenv("INFILTRATION_MIN_CONFIDENCE", "0.90"))
_MIN_LOCAL_NOISE_CONFIDENCE = float(os.getenv("LOCAL_NOISE_MIN_CONFIDENCE", "0.93"))
_LIKELY_NOISE_PORTS = {67, 68, 123, 137, 138, 1900, 5353, 5355}
_SUPPRESS_GENERIC_HTTPS_ATTACKS = os.getenv("SUPPRESS_GENERIC_HTTPS_ATTACKS", "1") == "1"
_SUPPRESS_LOCAL_CONTROL_PLANE = os.getenv("SUPPRESS_LOCAL_CONTROL_PLANE", "1") == "1"
_SUPPRESS_DISCOVERY_NOISE = os.getenv("SUPPRESS_DISCOVERY_NOISE", "1") == "1"
_NOISY_LABEL_WINDOW_S = float(os.getenv("NOISY_LABEL_WINDOW_SECONDS", "45"))
_NOISY_LABEL_MIN_EVENTS = max(1, int(os.getenv("NOISY_LABEL_MIN_EVENTS", "3")))
_NOISY_LABEL_MIN_CONFIDENCE = float(os.getenv("NOISY_LABEL_MIN_CONFIDENCE", "0.95"))
_NOISY_ATTACK_LABELS = {
    item.strip().lower()
    for item in os.getenv(
        "NOISY_ATTACK_LABELS",
        "infilteration,infiltration,bot,brute force -web,brute force -xss,sql injection",
    ).split(",")
    if item.strip()
}
_LOCAL_CONTROL_PLANE_PORTS = {
    int(item.strip())
    for item in os.getenv("LOCAL_CONTROL_PLANE_PORTS", "8000,8080,8081,5173,4173").split(",")
    if item.strip().isdigit()
}
_WEB_PORTS = {80, 443, 8080, 8443}
_METADATA_SERVICE_IPS = {
    ip.strip()
    for ip in os.getenv("METADATA_SERVICE_IPS", "169.254.169.254").split(",")
    if ip.strip()
}
_SUPPRESS_METADATA_SERVICE = os.getenv("SUPPRESS_METADATA_SERVICE", "1") == "1"
_suppressed_noise_flows = 0


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


def _duration_seconds(flow_dict: dict) -> float:
    """
    Normaliza flow_duration para segundos.
    O exporter costuma enviar microsegundos em muitos ambientes.
    """
    raw = _safe_float(flow_dict.get("flow_duration", 0.0))
    if raw <= 0:
        return 0.0

    # Heurística de unidade:
    # valores muito altos para um único fluxo curto normalmente vêm em microssegundos.
    if raw > 1000:
        return raw / 1_000_000.0
    return raw


def _resolve_service_flow(flow_dict: dict, service_port: int, protocol_required: int = 6):
    """
    Normaliza direção para fluxos de serviço (ex.: SSH 22, FTP 21).
    Retorna (attacker_ip, victim_ip) quando a porta de serviço aparece em qualquer lado.
    """
    protocol = _safe_int(flow_dict.get("protocol", 0))
    if protocol != protocol_required:
        return None

    src_ip = str(flow_dict.get("src_ip", "")).strip()
    dst_ip = str(flow_dict.get("dst_ip", "")).strip()
    src_port = _safe_int(flow_dict.get("src_port", 0))
    dst_port = _safe_int(flow_dict.get("dst_port", 0))

    if dst_port == service_port and src_port != service_port:
        return (src_ip, dst_ip)

    if src_port == service_port and dst_port != service_port:
        # Fluxo veio invertido: vítima no src, origem provável no dst.
        return (dst_ip, src_ip)

    if src_port == service_port and dst_port == service_port:
        return (src_ip, dst_ip)

    return None


def _is_private_or_local_ip(ip_value: str) -> bool:
    try:
        ip_obj = ipaddress.ip_address(str(ip_value).strip())
        return bool(
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_multicast
        )
    except ValueError:
        return False


def _is_broadcast_ipv4(ip_value: str) -> bool:
    ip_str = str(ip_value).strip()
    return ip_str.count(".") == 3 and ip_str.endswith(".255")


def _is_generic_https_attack_noise(flow_dict: dict, resultado: dict) -> bool:
    if not _SUPPRESS_GENERIC_HTTPS_ATTACKS:
        return False

    if not bool(resultado.get("is_attack", False)):
        return False

    label_norm = str(resultado.get("label_str", "")).strip().lower()
    noisy_labels = (
        "infilteration",
        "infiltration",
        "bot",
        "brute force -web",
        "brute force -xss",
        "sql injection",
    )
    if not any(token in label_norm for token in noisy_labels):
        return False

    src_ip = str(flow_dict.get("src_ip", "")).strip()
    dst_ip = str(flow_dict.get("dst_ip", "")).strip()
    src_port = _safe_int(flow_dict.get("src_port", 0))
    dst_port = _safe_int(flow_dict.get("dst_port", 0))
    protocol = _safe_int(flow_dict.get("protocol", 0))
    syn_cnt = _safe_float(flow_dict.get("syn_flag_cnt", 0.0))
    rst_cnt = _safe_float(flow_dict.get("rst_flag_cnt", 0.0))
    total_pkts = _safe_float(flow_dict.get("tot_fwd_pkts", 0.0)) + _safe_float(flow_dict.get("tot_bwd_pkts", 0.0))

    # Foco em sessão TLS cliente-servidor "normal" (lado privado <-> lado público).
    is_tls = (src_port == 443 or dst_port == 443) and protocol == 6
    private_public_pair = _is_private_or_local_ip(src_ip) ^ _is_private_or_local_ip(dst_ip)
    no_flood_signals = syn_cnt < 20 and rst_cnt < 5 and total_pkts < 5000

    return bool(is_tls and private_public_pair and no_flood_signals)


def _is_discovery_noise_flow(flow_dict: dict) -> bool:
    src_ip = str(flow_dict.get("src_ip", "")).strip()
    dst_ip = str(flow_dict.get("dst_ip", "")).strip()
    src_port = _safe_int(flow_dict.get("src_port", 0))
    dst_port = _safe_int(flow_dict.get("dst_port", 0))

    return bool(
        dst_ip.startswith("224.")
        or dst_ip.startswith("239.")
        or _is_broadcast_ipv4(dst_ip)
        or src_port in _LIKELY_NOISE_PORTS
        or dst_port in _LIKELY_NOISE_PORTS
        or _is_private_or_local_ip(src_ip) and _is_private_or_local_ip(dst_ip) and dst_port in {53, 5353, 1900}
    )


def _is_local_control_plane_flow(flow_dict: dict) -> bool:
    src_ip = str(flow_dict.get("src_ip", "")).strip()
    dst_ip = str(flow_dict.get("dst_ip", "")).strip()
    src_port = _safe_int(flow_dict.get("src_port", 0))
    dst_port = _safe_int(flow_dict.get("dst_port", 0))

    if src_port not in _LOCAL_CONTROL_PLANE_PORTS and dst_port not in _LOCAL_CONTROL_PLANE_PORTS:
        return False

    if not (_is_private_or_local_ip(src_ip) and _is_private_or_local_ip(dst_ip)):
        return False

    # Tráfego de dashboard/API local entre hosts privados tende a gerar ruído e falsos positivos.
    return True


def _is_metadata_service_flow(flow_dict: dict) -> bool:
    if not _SUPPRESS_METADATA_SERVICE:
        return False

    src_ip = str(flow_dict.get("src_ip", "")).strip()
    dst_ip = str(flow_dict.get("dst_ip", "")).strip()

    if src_ip in _METADATA_SERVICE_IPS or dst_ip in _METADATA_SERVICE_IPS:
        return True

    # Link-local metadata services costumam aparecer sem muito contexto; não tratar como ataque.
    return bool(
        _is_private_or_local_ip(src_ip)
        and dst_ip.startswith("169.254.")
    )


def _should_suppress_noise_flow(flow_dict: dict) -> bool:
    if _is_metadata_service_flow(flow_dict):
        return True
    if _SUPPRESS_DISCOVERY_NOISE and _is_discovery_noise_flow(flow_dict):
        return True
    if _SUPPRESS_LOCAL_CONTROL_PLANE and _is_local_control_plane_flow(flow_dict):
        return True
    return False


def _required_confidence_for_label(label_str: str) -> float:
    label_norm = str(label_str or "").strip().lower()
    if "infilteration" in label_norm or "infiltration" in label_norm:
        return _MIN_INFILTRATION_CONFIDENCE
    return _MIN_ATTACK_CONFIDENCE


def _should_downgrade_attack(flow_dict: dict, resultado: dict) -> bool:
    if not bool(resultado.get("is_attack", False)):
        return False

    confidence = _safe_float(resultado.get("confidence", 0.0))
    label_str = str(resultado.get("label_str", ""))

    if _is_generic_https_attack_noise(flow_dict, resultado):
        return True

    required_conf = _required_confidence_for_label(label_str)
    if confidence < required_conf:
        return True

    src_ip = str(flow_dict.get("src_ip", "")).strip()
    dst_ip = str(flow_dict.get("dst_ip", "")).strip()
    dst_port = _safe_int(flow_dict.get("dst_port", 0))
    label_norm = label_str.lower().strip()

    # Em tráfego local/infra (broadcast, multicast, discovery), exige confiança mais alta
    # para evitar ruído recorrente marcado como "Infilteration".
    local_or_noise_traffic = (
        _is_broadcast_ipv4(dst_ip)
        or _is_private_or_local_ip(src_ip)
        or _is_private_or_local_ip(dst_ip)
        or dst_port in _LIKELY_NOISE_PORTS
    )

    if local_or_noise_traffic and (
        "infilteration" in label_norm
        or "infiltration" in label_norm
        or "bot" in label_norm
    ):
        return confidence < _MIN_LOCAL_NOISE_CONFIDENCE

    if _is_generic_web_session_noise(flow_dict, resultado):
        return True

    if _is_metadata_service_flow(flow_dict):
        return True

    return False


def _is_generic_web_session_noise(flow_dict: dict, resultado: dict) -> bool:
    """Despromove Bot/labels web quando o fluxo parece apenas tráfego web normal."""
    if not bool(resultado.get("is_attack", False)):
        return False

    label_norm = _normalize_label(resultado.get("label_str", ""))
    if label_norm not in {"bot", "brute force -web", "brute force -xss", "sql injection"}:
        return False

    src_ip = str(flow_dict.get("src_ip", "")).strip()
    dst_ip = str(flow_dict.get("dst_ip", "")).strip()
    src_port = _safe_int(flow_dict.get("src_port", 0))
    dst_port = _safe_int(flow_dict.get("dst_port", 0))
    protocol = _safe_int(flow_dict.get("protocol", 0))
    syn_cnt = _safe_float(flow_dict.get("syn_flag_cnt", 0.0))
    rst_cnt = _safe_float(flow_dict.get("rst_flag_cnt", 0.0))
    ack_cnt = _safe_float(flow_dict.get("ack_flag_cnt", 0.0))
    psh_cnt = _safe_float(flow_dict.get("psh_flag_cnt", 0.0))
    total_pkts = _safe_float(flow_dict.get("tot_fwd_pkts", 0.0)) + _safe_float(flow_dict.get("tot_bwd_pkts", 0.0))
    flow_pkts_s = _safe_float(flow_dict.get("flow_pkts_s", 0.0))
    duration_s = _safe_float(flow_dict.get("flow_duration", 0.0))

    is_web_session = protocol == 6 and (src_port in _WEB_PORTS or dst_port in _WEB_PORTS)
    private_public_pair = _is_private_or_local_ip(src_ip) ^ _is_private_or_local_ip(dst_ip)
    if not (is_web_session and private_public_pair):
        return False

    no_burst_signals = syn_cnt <= 2 and rst_cnt <= 2 and ack_cnt <= 20 and psh_cnt <= 10
    modest_volume = total_pkts <= 120 and flow_pkts_s <= 10.0

    if label_norm == "bot":
        return bool(duration_s >= 15 and no_burst_signals and modest_volume)

    return bool(duration_s >= 20 and no_burst_signals and modest_volume)


def _normalize_label(value: str) -> str:
    return str(value or "").strip().lower()


def _is_noisy_label(label_norm: str) -> bool:
    if label_norm in _NOISY_ATTACK_LABELS:
        return True
    return any(tag in label_norm for tag in _NOISY_ATTACK_LABELS)


def _should_gate_noisy_attack(flow_dict: dict, resultado: dict) -> bool:
    """
    Evita marcar ataque em labels ruidosas com 1 evento isolado.
    Mantém ataque imediato quando confiança for muito alta.
    """
    if not bool(resultado.get("is_attack", False)):
        return False

    label_norm = _normalize_label(resultado.get("label_str", ""))
    if not _is_noisy_label(label_norm):
        return False

    confidence = _safe_float(resultado.get("confidence", 0.0))
    if confidence >= _NOISY_LABEL_MIN_CONFIDENCE:
        return False

    src_ip = str(flow_dict.get("src_ip", "")).strip()
    if not src_ip:
        return True

    now = time.time()
    key = (src_ip, label_norm)
    attempts = _noisy_label_attempts[key]
    attempts.append(now)
    cutoff = now - _NOISY_LABEL_WINDOW_S
    while attempts and attempts[0] < cutoff:
        attempts.popleft()

    return len(attempts) < _NOISY_LABEL_MIN_EVENTS


def _is_ssh_bruteforce_candidate(flow_dict: dict) -> bool:
    """Fluxo curto/repetitivo típico de tentativa de autenticação SSH falhada."""
    ssh_flow = _resolve_service_flow(flow_dict, service_port=22, protocol_required=6)
    syn_cnt = _safe_float(flow_dict.get("syn_flag_cnt", 0.0))
    rst_cnt = _safe_float(flow_dict.get("rst_flag_cnt", 0.0))
    fwd_pkts = _safe_float(flow_dict.get("tot_fwd_pkts", 0.0))
    bwd_pkts = _safe_float(flow_dict.get("tot_bwd_pkts", 0.0))
    duration_s = _duration_seconds(flow_dict)

    if ssh_flow is None:
        return False

    total_pkts = fwd_pkts + bwd_pkts
    return (
        syn_cnt >= 2
        and rst_cnt >= 1
        and duration_s <= 1.5
        and total_pkts <= 15
    )


def _is_ssh_early_suspicious(flow_dict: dict) -> bool:
    """Heurística antecipada para não esperar vários fluxos antes de alertar."""
    ssh_flow = _resolve_service_flow(flow_dict, service_port=22, protocol_required=6)
    syn_cnt = _safe_float(flow_dict.get("syn_flag_cnt", 0.0))
    rst_cnt = _safe_float(flow_dict.get("rst_flag_cnt", 0.0))
    ack_cnt = _safe_float(flow_dict.get("ack_flag_cnt", 0.0))
    fwd_pkts = _safe_float(flow_dict.get("tot_fwd_pkts", 0.0))
    bwd_pkts = _safe_float(flow_dict.get("tot_bwd_pkts", 0.0))
    duration_s = _duration_seconds(flow_dict)

    if ssh_flow is None:
        return False

    total_pkts = fwd_pkts + bwd_pkts

    # Primeiro estágio: padrão clássico de tentativa/falha em SSH.
    # Não depende de duração porque flow_duration pode vir em unidade diferente.
    if syn_cnt >= 2 and rst_cnt >= 1 and total_pkts <= 60:
        return True

    # Segundo estágio: bursts curtos de handshake sem troca normal de dados.
    if syn_cnt >= 3 and duration_s <= 6 and total_pkts <= 20 and ack_cnt <= 2:
        return True

    # Terceiro estágio: tentativa SSH curta com poucos pacotes,
    # mesmo sem RST explícito no primeiro fluxo.
    if syn_cnt >= 2 and duration_s <= 20 and total_pkts <= 50:
        return True

    # Quarto estágio: tentativa curta de autenticação em SSH,
    # comum em brute force com cadência mais baixa (Hydra/Ncrack).
    if syn_cnt >= 1 and duration_s <= 8 and total_pkts <= 20 and bwd_pkts <= 8:
        return True

    return False


def _is_ftp_early_suspicious(flow_dict: dict) -> bool:
    """Heurística antecipada para tentativas FTP repetidas com falha."""
    ftp_flow = _resolve_service_flow(flow_dict, service_port=21, protocol_required=6)
    syn_cnt = _safe_float(flow_dict.get("syn_flag_cnt", 0.0))
    rst_cnt = _safe_float(flow_dict.get("rst_flag_cnt", 0.0))
    ack_cnt = _safe_float(flow_dict.get("ack_flag_cnt", 0.0))
    psh_cnt = _safe_float(flow_dict.get("psh_flag_cnt", 0.0))
    fwd_pkts = _safe_float(flow_dict.get("tot_fwd_pkts", 0.0))
    bwd_pkts = _safe_float(flow_dict.get("tot_bwd_pkts", 0.0))
    duration_s = _duration_seconds(flow_dict)

    if ftp_flow is None:
        return False

    total_pkts = fwd_pkts + bwd_pkts

    # Padrão FTP de tentativa curta com resposta de falha no canal de controlo.
    if syn_cnt >= 1 and ack_cnt >= 1 and duration_s <= 12 and 6 <= total_pkts <= 45 and fwd_pkts >= 2 and (rst_cnt >= 1 or psh_cnt >= 1):
        return True

    # Burst de sessões FTP curtas sem evolução para transferência de dados.
    if syn_cnt >= 2 and duration_s <= 8 and total_pkts <= 28 and ack_cnt <= 4 and bwd_pkts <= 12:
        return True

    return False


def _is_ftp_bruteforce_candidate(flow_dict: dict) -> bool:
    """Candidato de tentativa FTP para contagem por frequência."""
    ftp_flow = _resolve_service_flow(flow_dict, service_port=21, protocol_required=6)
    syn_cnt = _safe_float(flow_dict.get("syn_flag_cnt", 0.0))
    ack_cnt = _safe_float(flow_dict.get("ack_flag_cnt", 0.0))
    fwd_pkts = _safe_float(flow_dict.get("tot_fwd_pkts", 0.0))
    bwd_pkts = _safe_float(flow_dict.get("tot_bwd_pkts", 0.0))
    duration_s = _duration_seconds(flow_dict)

    if ftp_flow is None:
        return False

    total_pkts = fwd_pkts + bwd_pkts
    return (
        syn_cnt >= 1
        and ack_cnt >= 1
        and duration_s <= 20
        and 4 <= total_pkts <= 60
    )


def _update_ssh_bruteforce_state(flow_dict: dict) -> int:
    """Conta tentativas SSH suspeitas numa janela deslizante."""
    src_ip = str(flow_dict.get("src_ip", ""))
    dst_ip = str(flow_dict.get("dst_ip", ""))
    
    # NÃO contar IPs whitelisted
    if _should_ignore_flow(src_ip, dst_ip):
        return 0
    
    service_flow = _resolve_service_flow(flow_dict, service_port=22, protocol_required=6)

    # Conta conexões SSH/TCP para detectar brute force por frequência,
    # mesmo quando o exporter inverte src/dst no fluxo.
    if service_flow is None:
        return 0

    total_pkts = _safe_float(flow_dict.get("tot_fwd_pkts", 0.0)) + _safe_float(flow_dict.get("tot_bwd_pkts", 0.0))
    duration_s = _duration_seconds(flow_dict)
    if total_pkts > 300 and duration_s > 120:
        return 0

    attacker_ip, victim_ip = service_flow
    key = (attacker_ip, victim_ip, 22)

    now = time.time()
    attempts = _ssh_attempts[key]
    attempts.append(now)
    cutoff = now - _SSH_BRUTE_WINDOW_S
    while attempts and attempts[0] < cutoff:
        attempts.popleft()

    return len(attempts)


def _update_ftp_bruteforce_state(flow_dict: dict) -> int:
    """Conta tentativas FTP suspeitas numa janela deslizante."""
    src_ip = str(flow_dict.get("src_ip", ""))
    dst_ip = str(flow_dict.get("dst_ip", ""))
    
    # NÃO contar IPs whitelisted
    if _should_ignore_flow(src_ip, dst_ip):
        return 0
    
    service_flow = _resolve_service_flow(flow_dict, service_port=21, protocol_required=6)

    # Conta apenas tentativas FTP candidatas, evitando sessões legítimas longas.
    if not (service_flow is not None and _is_ftp_bruteforce_candidate(flow_dict)):
        return 0

    attacker_ip, victim_ip = service_flow
    key = (attacker_ip, victim_ip, 21)

    now = time.time()
    attempts = _ftp_attempts[key]
    attempts.append(now)
    cutoff = now - _FTP_BRUTE_WINDOW_S
    while attempts and attempts[0] < cutoff:
        attempts.popleft()

    return len(attempts)


# API pública 
def estado() -> dict:
    with _proc_lock:
        active = [iface for iface, proc in _processes.items() if proc and proc.poll() is None]
        interfaces = sorted(active)

    rodando = len(interfaces) > 0
    return {
        "rodando":            rodando,
        "interface":          interfaces[0] if interfaces else "",
        "interfaces":         interfaces,
        "fluxos_processados": contador_fluxos,
        "ataques_detetados":  ataques_detetados,
        "uptime_s":           round(time.time() - _start_time, 1) if rodando and _start_time else 0,
    }


def iniciar(interface: str, callback, loop: asyncio.AbstractEventLoop):
    iniciar_multiplas([interface], callback, loop)


def iniciar_multiplas(interfaces: list[str], callback, loop: asyncio.AbstractEventLoop):
    global _callback, _loop, _stop_event
    global contador_fluxos, ataques_detetados, _start_time

    sanitized = [str(i or "").strip() for i in interfaces if str(i or "").strip()]
    if not sanitized:
        raise ValueError("Nenhuma interface válida informada")

    _callback = callback
    _loop = loop

    est = estado()
    if not est.get("rodando"):
        _start_time = time.time()
        _stop_event.clear()
        contador_fluxos = 0
        ataques_detetados = 0
        _ssh_attempts.clear()
        _ftp_attempts.clear()
        _web_attack_rules.reset()

    for interface in sanitized:
        with _proc_lock:
            existing = _processes.get(interface)
            if existing and existing.poll() is None:
                continue

        thread = threading.Thread(
            target=_lançar_cicflowmeter,
            args=(interface,),
            daemon=True,
            name=f"sniffer-cicflowmeter-{interface}",
        )
        with _proc_lock:
            _threads[interface] = thread
        thread.start()
        print(f"[Sniffer] Subprocess iniciado → interface: {interface} | endpoint: {FLOW_ENDPOINT}")


def parar():
    global _processes, _threads

    _stop_event.set()

    with _proc_lock:
        processes = list(_processes.items())
        threads = list(_threads.items())

    for _, proc in processes:
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    for _, thread in threads:
        if thread and thread.is_alive():
            thread.join(timeout=5)

    with _proc_lock:
        _processes.clear()
        _threads.clear()

    print("[Sniffer] Captura parada.")


# Chamado pelo endpoint /sniffer/flow-input 
async def processar_fluxo(flow_dict: dict, sensor_interface: str | None = None):
    """
    Chamado pelo FastAPI quando o cicflowmeter faz POST de um fluxo.
    Classifica e envia para o callback (WebSocket).
    """
    global contador_fluxos, ataques_detetados, _suppressed_noise_flows

    try:
        if _should_suppress_noise_flow(flow_dict):
            _suppressed_noise_flows += 1
            if _suppressed_noise_flows % 50 == 0:
                print(
                    f"[Sniffer] Fluxos suprimidos por ruído local/discovery: {_suppressed_noise_flows}",
                )
            return None

        features  = extrair_features(flow_dict)
        resultado = predict_flow(features)

        # Por padrão, usa somente o resultado do modelo.
        # Override global opcional + chaves granulares para controlar falso positivo web.
        global_override_enabled = _ENABLE_HEURISTIC_ATTACK_OVERRIDE
        ssh_ftp_override_enabled = _ENABLE_SSH_FTP_HEURISTIC_OVERRIDE or global_override_enabled
        web_override_enabled = _ENABLE_WEB_HEURISTIC_OVERRIDE or global_override_enabled

        if (ssh_ftp_override_enabled or web_override_enabled) and not resultado.get("is_attack", False):
            ssh_attempt_count = _update_ssh_bruteforce_state(flow_dict) if ssh_ftp_override_enabled else 0
            ftp_attempt_count = _update_ftp_bruteforce_state(flow_dict) if ssh_ftp_override_enabled else 0
            web_label, web_confidence = _web_attack_rules.detect(flow_dict) if web_override_enabled else (None, 0.0)
            if ssh_ftp_override_enabled and _is_ssh_early_suspicious(flow_dict):
                resultado["is_attack"] = True
                resultado["label_str"] = "SSH-Bruteforce"
                resultado["confidence"] = max(float(resultado.get("confidence", 0.0)), 0.89)
            elif ssh_ftp_override_enabled and ssh_attempt_count >= _SSH_BRUTE_MIN_ATTEMPTS:
                resultado["is_attack"] = True
                resultado["label_str"] = "SSH-Bruteforce"
                resultado["confidence"] = max(float(resultado.get("confidence", 0.0)), 0.92)
            elif ssh_ftp_override_enabled and _is_ftp_early_suspicious(flow_dict):
                resultado["is_attack"] = True
                resultado["label_str"] = "FTP-BruteForce"
                resultado["confidence"] = max(float(resultado.get("confidence", 0.0)), 0.89)
            elif ssh_ftp_override_enabled and ftp_attempt_count >= _FTP_BRUTE_MIN_ATTEMPTS:
                resultado["is_attack"] = True
                resultado["label_str"] = "FTP-BruteForce"
                resultado["confidence"] = max(float(resultado.get("confidence", 0.0)), 0.92)
            elif web_override_enabled and web_label is not None:
                resultado["is_attack"] = True
                resultado["label_str"] = web_label
                resultado["confidence"] = max(float(resultado.get("confidence", 0.0)), web_confidence)

        if _should_downgrade_attack(flow_dict, resultado):
            resultado["is_attack"] = False
            resultado["label_str"] = "Benign"

        if _should_gate_noisy_attack(flow_dict, resultado):
            resultado["is_attack"] = False
            resultado["label_str"] = "Benign"

        contador_fluxos += 1
        if resultado["is_attack"]:
            ataques_detetados += 1

        # Log no terminal 
        status = "⚠️  ATAQUE" if resultado["is_attack"] else "✅ Normal"
        print(
            f"[Fluxo #{contador_fluxos}] {status} | "
            f"{flow_dict.get('src_ip','?')}:{flow_dict.get('src_port','?')} → "
            f"{flow_dict.get('dst_ip','?')}:{flow_dict.get('dst_port','?')} | "
            f"Label: {resultado['label_str']} | "
            f"Confiança: {round(resultado['confidence']*100,2)}% | "
            f"Risco: {round(max(0.0, 100.0 - (resultado['confidence'] * 100.0)), 2)}%"
        )

        dados = {
            "id":         contador_fluxos,
            "src_ip":     flow_dict.get("src_ip",  ""),
            "dst_ip":     flow_dict.get("dst_ip",  ""),
            "src_port":   flow_dict.get("src_port", 0),
            "dst_port":   flow_dict.get("dst_port", 0),
            "protocol":   flow_dict.get("protocol", 0),
            "label":      resultado["label_str"],
            "confidence": round(resultado["confidence"] * 100, 2),
            "is_attack":  resultado["is_attack"],
            "label_int":  resultado["label_int"],
            "sensor_interface": str(sensor_interface or "").strip(),
        }

        if _callback is not None:
            try:
                await _callback(dados)
            except Exception as cb_err:
                print(f"[Sniffer] Erro ao enviar callback de fluxo: {cb_err}")

        return dados

    except Exception as e:
        print(f"[Sniffer] Erro ao classificar fluxo: {e}")
        return None


# Subprocess 
def _lançar_cicflowmeter(interface: str):

    # Usa wrapper local para reduzir latência de export de fluxos.
    python = sys.executable

    cmd = [
        python,
        "-m",
        "backend.scapy_module.cicflow_fast",
        "--interface",
        interface,
        "--url",
        f"{FLOW_ENDPOINT}?interface={quote(interface, safe='')}",
        "--expired-update",
        "1.0",
        "--packets-per-gc",
        "50",
    ]

    print(f"[Sniffer] CMD: {' '.join(cmd)}")

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        with _proc_lock:
            _processes[interface] = proc

        for line in proc.stdout:
            if _stop_event.is_set():
                break
            line = line.strip()
            if line:
                print(f"[cicflowmeter] {line}")

        proc.wait()

    except FileNotFoundError:
        print(f"[Sniffer] ERRO: python não encontrado em {python}")
    except Exception as e:
        print(f"[Sniffer] Erro no subprocess: {e}")
    finally:
        with _proc_lock:
            _processes.pop(interface, None)
            _threads.pop(interface, None)