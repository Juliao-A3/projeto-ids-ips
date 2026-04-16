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
from collections import defaultdict, deque

from extractor import extrair_features
from predictor import predict_flow
from whitelist import get_whitelist
from web_attack_rules import WebAttackRulesEngine

# Configuração
FASTAPI_PORT  = 8000
FLOW_ENDPOINT = f"http://127.0.0.1:{FASTAPI_PORT}/sniffer/flow-input"

# Whitelist centralizada
_whitelist_manager = get_whitelist()


def _should_ignore_flow(src_ip: str, dst_ip: str) -> bool:
    """Verifica se um fluxo deve ser ignorado por estar na whitelist."""
    return _whitelist_manager.is_ip_whitelisted(src_ip) or _whitelist_manager.is_ip_whitelisted(dst_ip)

# Estado interno 
_process:  subprocess.Popen | None  = None
_thread:   threading.Thread | None  = None
_stop_event = threading.Event()

_callback  = None
_loop:     asyncio.AbstractEventLoop | None = None

contador_fluxos   = 0
ataques_detetados = 0
_interface        = ""
_start_time       = 0.0

_SSH_BRUTE_WINDOW_S = 10.0
_FTP_BRUTE_WINDOW_S = 20.0
_SSH_BRUTE_MIN_ATTEMPTS = 2
_FTP_BRUTE_MIN_ATTEMPTS = 3
_ssh_attempts: dict[tuple[str, str, int], deque[float]] = defaultdict(deque)
_ftp_attempts: dict[tuple[str, str, int], deque[float]] = defaultdict(deque)
_ENABLE_HEURISTIC_ATTACK_OVERRIDE = os.getenv("ENABLE_HEURISTIC_ATTACK_OVERRIDE", "1") == "1"
_web_attack_rules = WebAttackRulesEngine(_should_ignore_flow)


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


def _is_ssh_bruteforce_candidate(flow_dict: dict) -> bool:
    """Fluxo curto/repetitivo típico de tentativa de autenticação SSH falhada."""
    dst_port = _safe_int(flow_dict.get("dst_port", 0))
    protocol = _safe_int(flow_dict.get("protocol", 0))
    syn_cnt = _safe_float(flow_dict.get("syn_flag_cnt", 0.0))
    rst_cnt = _safe_float(flow_dict.get("rst_flag_cnt", 0.0))
    fwd_pkts = _safe_float(flow_dict.get("tot_fwd_pkts", 0.0))
    bwd_pkts = _safe_float(flow_dict.get("tot_bwd_pkts", 0.0))
    duration_s = _safe_float(flow_dict.get("flow_duration", 0.0))

    if dst_port != 22 or protocol != 6:
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
    dst_port = _safe_int(flow_dict.get("dst_port", 0))
    protocol = _safe_int(flow_dict.get("protocol", 0))
    syn_cnt = _safe_float(flow_dict.get("syn_flag_cnt", 0.0))
    rst_cnt = _safe_float(flow_dict.get("rst_flag_cnt", 0.0))
    ack_cnt = _safe_float(flow_dict.get("ack_flag_cnt", 0.0))
    fwd_pkts = _safe_float(flow_dict.get("tot_fwd_pkts", 0.0))
    bwd_pkts = _safe_float(flow_dict.get("tot_bwd_pkts", 0.0))
    duration_s = _safe_float(flow_dict.get("flow_duration", 0.0))

    if dst_port != 22 or protocol != 6:
        return False

    total_pkts = fwd_pkts + bwd_pkts

    # Primeiro estágio: conexão SSH curta com padrão de tentativa/falha.
    if syn_cnt >= 3 and rst_cnt >= 1 and total_pkts <= 30:
        return True

    # Segundo estágio: bursts curtos de handshake sem troca normal de dados.
    if syn_cnt >= 3 and duration_s <= 6 and total_pkts <= 20 and ack_cnt <= 2:
        return True

    # Terceiro estágio: tentativa SSH curta com poucos pacotes,
    # mesmo sem RST explícito no primeiro fluxo.
    if syn_cnt >= 2 and duration_s <= 20 and total_pkts <= 50:
        return True

    return False


def _is_ftp_early_suspicious(flow_dict: dict) -> bool:
    """Heurística antecipada para tentativas FTP repetidas com falha."""
    dst_port = _safe_int(flow_dict.get("dst_port", 0))
    protocol = _safe_int(flow_dict.get("protocol", 0))
    syn_cnt = _safe_float(flow_dict.get("syn_flag_cnt", 0.0))
    rst_cnt = _safe_float(flow_dict.get("rst_flag_cnt", 0.0))
    ack_cnt = _safe_float(flow_dict.get("ack_flag_cnt", 0.0))
    psh_cnt = _safe_float(flow_dict.get("psh_flag_cnt", 0.0))
    fwd_pkts = _safe_float(flow_dict.get("tot_fwd_pkts", 0.0))
    bwd_pkts = _safe_float(flow_dict.get("tot_bwd_pkts", 0.0))
    duration_s = _safe_float(flow_dict.get("flow_duration", 0.0))

    if dst_port != 21 or protocol != 6:
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
    dst_port = _safe_int(flow_dict.get("dst_port", 0))
    protocol = _safe_int(flow_dict.get("protocol", 0))
    syn_cnt = _safe_float(flow_dict.get("syn_flag_cnt", 0.0))
    ack_cnt = _safe_float(flow_dict.get("ack_flag_cnt", 0.0))
    fwd_pkts = _safe_float(flow_dict.get("tot_fwd_pkts", 0.0))
    bwd_pkts = _safe_float(flow_dict.get("tot_bwd_pkts", 0.0))
    duration_s = _safe_float(flow_dict.get("flow_duration", 0.0))

    if dst_port != 21 or protocol != 6:
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
    
    dst_port = _safe_int(flow_dict.get("dst_port", 0))
    protocol = _safe_int(flow_dict.get("protocol", 0))

    # Conta toda conexão SSH/TCP para detectar brute force por frequência,
    # mesmo quando flags variam entre tentativas.
    if not (dst_port == 22 and protocol == 6):
        return 0

    key = (src_ip, dst_ip, dst_port)

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
    
    dst_port = _safe_int(flow_dict.get("dst_port", 0))
    protocol = _safe_int(flow_dict.get("protocol", 0))

    # Conta apenas tentativas FTP candidatas, evitando sessões legítimas longas.
    if not (dst_port == 21 and protocol == 6 and _is_ftp_bruteforce_candidate(flow_dict)):
        return 0

    src_ip = str(flow_dict.get("src_ip", ""))
    dst_ip = str(flow_dict.get("dst_ip", ""))
    dst_port = _safe_int(flow_dict.get("dst_port", 21))
    key = (src_ip, dst_ip, dst_port)

    now = time.time()
    attempts = _ftp_attempts[key]
    attempts.append(now)
    cutoff = now - _FTP_BRUTE_WINDOW_S
    while attempts and attempts[0] < cutoff:
        attempts.popleft()

    return len(attempts)


# API pública 
def estado() -> dict:
    rodando = _process is not None and _process.poll() is None
    return {
        "rodando":            rodando,
        "interface":          _interface,
        "fluxos_processados": contador_fluxos,
        "ataques_detetados":  ataques_detetados,
        "uptime_s":           round(time.time() - _start_time, 1) if rodando and _start_time else 0,
    }


def iniciar(interface: str, callback, loop: asyncio.AbstractEventLoop):
    global _callback, _loop, _stop_event, _thread
    global contador_fluxos, ataques_detetados, _interface, _start_time

    _callback         = callback
    _loop             = loop
    _interface        = interface
    _start_time       = time.time()
    _stop_event.clear()
    contador_fluxos   = 0
    ataques_detetados = 0
    _ssh_attempts.clear()
    _ftp_attempts.clear()
    _web_attack_rules.reset()

    _thread = threading.Thread(
        target=_lançar_cicflowmeter,
        args=(interface,),
        daemon=True,
        name="sniffer-cicflowmeter",
    )
    _thread.start()
    print(f"[Sniffer] Subprocess iniciado → interface: {interface} | endpoint: {FLOW_ENDPOINT}")


def parar():
    global _process, _thread

    _stop_event.set()

    if _process and _process.poll() is None:
        _process.terminate()
        try:
            _process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _process.kill()
        _process = None

    if _thread and _thread.is_alive():
        _thread.join(timeout=5)
    _thread = None

    print("[Sniffer] Captura parada.")


# Chamado pelo endpoint /sniffer/flow-input 
async def processar_fluxo(flow_dict: dict):
    """
    Chamado pelo FastAPI quando o cicflowmeter faz POST de um fluxo.
    Classifica e envia para o callback (WebSocket).
    """
    global contador_fluxos, ataques_detetados

    try:
        features  = extrair_features(flow_dict)
        resultado = predict_flow(features)

        # Por padrão, usa somente o resultado do modelo.
        # Para reativar override heurístico: ENABLE_HEURISTIC_ATTACK_OVERRIDE=1
        if _ENABLE_HEURISTIC_ATTACK_OVERRIDE and not resultado.get("is_attack", False):
            ssh_attempt_count = _update_ssh_bruteforce_state(flow_dict)
            ftp_attempt_count = _update_ftp_bruteforce_state(flow_dict)
            web_label, web_confidence = _web_attack_rules.detect(flow_dict)
            if _is_ssh_early_suspicious(flow_dict):
                resultado["is_attack"] = True
                resultado["label_str"] = "SSH-Bruteforce"
                resultado["confidence"] = max(float(resultado.get("confidence", 0.0)), 0.89)
            elif ssh_attempt_count >= _SSH_BRUTE_MIN_ATTEMPTS:
                resultado["is_attack"] = True
                resultado["label_str"] = "SSH-Bruteforce"
                resultado["confidence"] = max(float(resultado.get("confidence", 0.0)), 0.92)
            elif _is_ftp_early_suspicious(flow_dict):
                resultado["is_attack"] = True
                resultado["label_str"] = "FTP-BruteForce"
                resultado["confidence"] = max(float(resultado.get("confidence", 0.0)), 0.89)
            elif ftp_attempt_count >= _FTP_BRUTE_MIN_ATTEMPTS:
                resultado["is_attack"] = True
                resultado["label_str"] = "FTP-BruteForce"
                resultado["confidence"] = max(float(resultado.get("confidence", 0.0)), 0.92)
            elif web_label is not None:
                resultado["is_attack"] = True
                resultado["label_str"] = web_label
                resultado["confidence"] = max(float(resultado.get("confidence", 0.0)), web_confidence)

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
    global _process

    # Usa wrapper local para reduzir latência de export de fluxos.
    python = sys.executable

    cmd = [
        python,
        "-m",
        "backend.scapy_module.cicflow_fast",
        "--interface",
        interface,
        "--url",
        FLOW_ENDPOINT,
        "--expired-update",
        "1.0",
        "--packets-per-gc",
        "50",
    ]

    print(f"[Sniffer] CMD: {' '.join(cmd)}")

    try:
        _process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        for line in _process.stdout:
            if _stop_event.is_set():
                break
            line = line.strip()
            if line:
                print(f"[cicflowmeter] {line}")

        _process.wait()

    except FileNotFoundError:
        print(f"[Sniffer] ERRO: python não encontrado em {python}")
    except Exception as e:
        print(f"[Sniffer] Erro no subprocess: {e}")