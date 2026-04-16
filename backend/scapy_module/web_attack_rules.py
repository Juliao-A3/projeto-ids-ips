"""Regras heuristicas de ataques web para uso no sniffer em tempo real."""

from collections import defaultdict, deque
import time


class WebAttackRulesEngine:
    """Motor de deteccao heuristica para ataques web com estado por janela."""

    _WEB_PORTS = {80, 443, 8080, 8443}

    _WINDOW_BRUTE_WEB_S = 10.0
    _WINDOW_XSS_S = 10.0
    _WINDOW_SQLI_S = 12.0
    _WINDOW_BOT_S = 8.0
    _WINDOW_INFILTRATION_S = 30.0

    _MIN_BRUTE_WEB_ATTEMPTS = 3
    _MIN_XSS_ATTEMPTS = 3
    _MIN_SQLI_ATTEMPTS = 3
    _MIN_BOT_ATTEMPTS = 4
    _MIN_INFILTRATION_ATTEMPTS = 2

    def __init__(self, should_ignore_flow):
        """should_ignore_flow recebe (src_ip, dst_ip) e retorna bool."""
        self._should_ignore_flow = should_ignore_flow
        self._web_attempts = defaultdict(deque)
        self._xss_attempts = defaultdict(deque)
        self._sqli_attempts = defaultdict(deque)
        self._bot_attempts = defaultdict(deque)
        self._infiltration_attempts = defaultdict(deque)

    def reset(self):
        self._web_attempts.clear()
        self._xss_attempts.clear()
        self._sqli_attempts.clear()
        self._bot_attempts.clear()
        self._infiltration_attempts.clear()

    def detect(self, flow_dict: dict) -> tuple[str | None, float]:
        """Retorna (label, confianca) quando alguma regra dispara."""
        src_ip = str(flow_dict.get("src_ip", ""))
        dst_ip = str(flow_dict.get("dst_ip", ""))

        if self._should_ignore_flow(src_ip, dst_ip):
            return None, 0.0

        if self._is_web_bruteforce_early_suspicious(flow_dict):
            return "Brute Force -Web", 0.89
        if self._update_web_bruteforce_state(flow_dict) >= self._MIN_BRUTE_WEB_ATTEMPTS:
            return "Brute Force -Web", 0.92

        if self._is_xss_early_suspicious(flow_dict):
            return "Brute Force -XSS", 0.88
        if self._update_xss_state(flow_dict) >= self._MIN_XSS_ATTEMPTS:
            return "Brute Force -XSS", 0.91

        if self._is_sql_injection_early_suspicious(flow_dict):
            return "SQL Injection", 0.88
        if self._update_sql_injection_state(flow_dict) >= self._MIN_SQLI_ATTEMPTS:
            return "SQL Injection", 0.91

        if self._is_bot_early_suspicious(flow_dict):
            return "Bot", 0.90
        if self._update_bot_state(flow_dict) >= self._MIN_BOT_ATTEMPTS:
            return "Bot", 0.93

        if self._is_infiltration_early_suspicious(flow_dict):
            return "Infilteration", 0.88
        if self._update_infiltration_state(flow_dict) >= self._MIN_INFILTRATION_ATTEMPTS:
            return "Infilteration", 0.90

        return None, 0.0

    @staticmethod
    def _safe_float(value, default=0.0):
        try:
            parsed = float(value)
            return default if (parsed != parsed) else parsed
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _safe_int(value, default=0):
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return default

    def _is_web_flow(self, flow_dict: dict) -> bool:
        dst_port = self._safe_int(flow_dict.get("dst_port", 0))
        protocol = self._safe_int(flow_dict.get("protocol", 0))
        return dst_port in self._WEB_PORTS and protocol == 6

    def _flow_key(self, flow_dict: dict) -> tuple[str, str, int]:
        src_ip = str(flow_dict.get("src_ip", ""))
        dst_ip = str(flow_dict.get("dst_ip", ""))
        dst_port = self._safe_int(flow_dict.get("dst_port", 0))
        return (src_ip, dst_ip, dst_port)

    @staticmethod
    def _sliding_count(state: dict, key: tuple[str, str, int], window_s: float) -> int:
        now = time.time()
        attempts = state[key]
        attempts.append(now)
        cutoff = now - window_s
        while attempts and attempts[0] < cutoff:
            attempts.popleft()
        return len(attempts)

    def _is_web_bruteforce_early_suspicious(self, flow_dict: dict) -> bool:
        if not self._is_web_flow(flow_dict):
            return False

        syn_cnt = self._safe_float(flow_dict.get("syn_flag_cnt", 0.0))
        rst_cnt = self._safe_float(flow_dict.get("rst_flag_cnt", 0.0))
        ack_cnt = self._safe_float(flow_dict.get("ack_flag_cnt", 0.0))
        flow_pkts_s = self._safe_float(flow_dict.get("flow_pkts_s", 0.0))
        fwd_pkts = self._safe_float(flow_dict.get("tot_fwd_pkts", 0.0))
        bwd_pkts = self._safe_float(flow_dict.get("tot_bwd_pkts", 0.0))
        duration_s = self._safe_float(flow_dict.get("flow_duration", 0.0))
        total_pkts = fwd_pkts + bwd_pkts

        if syn_cnt >= 2 and rst_cnt >= 1 and duration_s <= 2 and total_pkts <= 30:
            return True
        if syn_cnt >= 2 and ack_cnt <= 4 and duration_s <= 8 and total_pkts <= 25 and flow_pkts_s >= 1.0:
            return True
        return False

    def _update_web_bruteforce_state(self, flow_dict: dict) -> int:
        if not self._is_web_flow(flow_dict):
            return 0
        return self._sliding_count(self._web_attempts, self._flow_key(flow_dict), self._WINDOW_BRUTE_WEB_S)

    def _is_xss_early_suspicious(self, flow_dict: dict) -> bool:
        if not self._is_web_flow(flow_dict):
            return False

        psh_cnt = self._safe_float(flow_dict.get("psh_flag_cnt", 0.0))
        ack_cnt = self._safe_float(flow_dict.get("ack_flag_cnt", 0.0))
        flow_pkts_s = self._safe_float(flow_dict.get("flow_pkts_s", 0.0))
        fwd_pkts = self._safe_float(flow_dict.get("tot_fwd_pkts", 0.0))
        bwd_pkts = self._safe_float(flow_dict.get("tot_bwd_pkts", 0.0))
        duration_s = self._safe_float(flow_dict.get("flow_duration", 0.0))
        total_bytes = self._safe_float(flow_dict.get("totlen_fwd_pkts", 0.0)) + self._safe_float(flow_dict.get("totlen_bwd_pkts", 0.0))
        total_pkts = fwd_pkts + bwd_pkts

        if psh_cnt >= 1 and ack_cnt >= 2 and 6 <= total_pkts <= 40 and duration_s <= 5 and 200 <= total_bytes <= 5000:
            return True
        if psh_cnt >= 2 and flow_pkts_s >= 3.0 and total_pkts <= 30 and duration_s <= 4:
            return True
        return False

    def _update_xss_state(self, flow_dict: dict) -> int:
        if not self._is_web_flow(flow_dict):
            return 0
        return self._sliding_count(self._xss_attempts, self._flow_key(flow_dict), self._WINDOW_XSS_S)

    def _is_sql_injection_early_suspicious(self, flow_dict: dict) -> bool:
        if not self._is_web_flow(flow_dict):
            return False

        psh_cnt = self._safe_float(flow_dict.get("psh_flag_cnt", 0.0))
        ack_cnt = self._safe_float(flow_dict.get("ack_flag_cnt", 0.0))
        urg_cnt = self._safe_float(flow_dict.get("urg_flag_cnt", 0.0))
        flow_pkts_s = self._safe_float(flow_dict.get("flow_pkts_s", 0.0))
        fwd_pkts = self._safe_float(flow_dict.get("tot_fwd_pkts", 0.0))
        bwd_pkts = self._safe_float(flow_dict.get("tot_bwd_pkts", 0.0))
        total_bytes = self._safe_float(flow_dict.get("totlen_fwd_pkts", 0.0)) + self._safe_float(flow_dict.get("totlen_bwd_pkts", 0.0))
        duration_s = self._safe_float(flow_dict.get("flow_duration", 0.0))
        total_pkts = fwd_pkts + bwd_pkts

        if psh_cnt >= 2 and ack_cnt >= 2 and 8 <= total_pkts <= 60 and duration_s <= 6 and 400 <= total_bytes <= 9000:
            return True
        if urg_cnt >= 1 and psh_cnt >= 1 and flow_pkts_s >= 2.0 and total_pkts <= 40:
            return True
        return False

    def _update_sql_injection_state(self, flow_dict: dict) -> int:
        if not self._is_web_flow(flow_dict):
            return 0
        return self._sliding_count(self._sqli_attempts, self._flow_key(flow_dict), self._WINDOW_SQLI_S)

    def _is_bot_early_suspicious(self, flow_dict: dict) -> bool:
        protocol = self._safe_int(flow_dict.get("protocol", 0))
        syn_cnt = self._safe_float(flow_dict.get("syn_flag_cnt", 0.0))
        ack_cnt = self._safe_float(flow_dict.get("ack_flag_cnt", 0.0))
        rst_cnt = self._safe_float(flow_dict.get("rst_flag_cnt", 0.0))
        flow_pkts_s = self._safe_float(flow_dict.get("flow_pkts_s", 0.0))
        flow_byts_s = self._safe_float(flow_dict.get("flow_byts_s", 0.0))
        fwd_pkts = self._safe_float(flow_dict.get("tot_fwd_pkts", 0.0))
        bwd_pkts = self._safe_float(flow_dict.get("tot_bwd_pkts", 0.0))
        duration_s = self._safe_float(flow_dict.get("flow_duration", 0.0))
        total_pkts = fwd_pkts + bwd_pkts

        if protocol == 6 and syn_cnt >= 25 and ack_cnt == 0 and rst_cnt <= 5 and flow_pkts_s >= 15:
            return True
        if protocol in (6, 17) and total_pkts >= 40 and duration_s <= 5 and (flow_pkts_s >= 20 or flow_byts_s >= 20000):
            return True
        return False

    def _update_bot_state(self, flow_dict: dict) -> int:
        src_ip = str(flow_dict.get("src_ip", ""))
        dst_ip = str(flow_dict.get("dst_ip", ""))
        if self._should_ignore_flow(src_ip, dst_ip):
            return 0

        protocol = self._safe_int(flow_dict.get("protocol", 0))
        if protocol not in (6, 17):
            return 0

        dst_port = self._safe_int(flow_dict.get("dst_port", 0))
        key = (src_ip, dst_ip, dst_port)
        return self._sliding_count(self._bot_attempts, key, self._WINDOW_BOT_S)

    def _is_infiltration_early_suspicious(self, flow_dict: dict) -> bool:
        dst_port = self._safe_int(flow_dict.get("dst_port", 0))
        protocol = self._safe_int(flow_dict.get("protocol", 0))
        duration_s = self._safe_float(flow_dict.get("flow_duration", 0.0))
        flow_pkts_s = self._safe_float(flow_dict.get("flow_pkts_s", 0.0))
        fwd_bytes = self._safe_float(flow_dict.get("totlen_fwd_pkts", 0.0))
        bwd_bytes = self._safe_float(flow_dict.get("totlen_bwd_pkts", 0.0))
        total_bytes = fwd_bytes + bwd_bytes

        if dst_port == 53 and protocol in (6, 17) and total_bytes >= 50000:
            return True

        if self._is_web_flow(flow_dict) and duration_s >= 60 and total_bytes < 1000 and flow_pkts_s <= 1.0:
            return True

        if self._is_web_flow(flow_dict) and duration_s >= 15 and bwd_bytes >= 5 * max(fwd_bytes, 1.0) and bwd_bytes >= 30000:
            return True

        return False

    def _update_infiltration_state(self, flow_dict: dict) -> int:
        src_ip = str(flow_dict.get("src_ip", ""))
        dst_ip = str(flow_dict.get("dst_ip", ""))
        if self._should_ignore_flow(src_ip, dst_ip):
            return 0

        dst_port = self._safe_int(flow_dict.get("dst_port", 0))
        protocol = self._safe_int(flow_dict.get("protocol", 0))
        is_dns = dst_port == 53 and protocol in (6, 17)
        if not (self._is_web_flow(flow_dict) or is_dns):
            return 0

        key = (src_ip, dst_ip, dst_port)
        return self._sliding_count(self._infiltration_attempts, key, self._WINDOW_INFILTRATION_S)
