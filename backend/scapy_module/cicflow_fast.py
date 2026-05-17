"""
cicflow_fast.py

Wrapper para executar o cicflowmeter com timeouts agressivos de expiração
de fluxo, reduzindo atraso de minutos na emissão para o backend.
"""

import argparse
import inspect
import tempfile
import time
import threading
from pathlib import Path

from cicflowmeter import sniffer as cic_sniffer
import cicflowmeter.flow_session as flow_session_mod
from cicflowmeter.features.context import PacketDirection
from cicflowmeter.features.flow_bytes import FlowBytes
from cicflowmeter.writer import HttpWriter
from scapy.sessions import DefaultSession
from scapy.sendrecv import AsyncSniffer


def _apply_runtime_safety_patches() -> None:
    """Evita crash do cicflowmeter em fluxos sem pacotes FORWARD válidos."""

    def _safe_min_forward_header_bytes(self) -> int:
        if not self.flow.packets:
            return 0

        values = [
            self._header_size(packet)
            for packet, direction in self.flow.packets
            if direction == PacketDirection.FORWARD
        ]
        return min(values) if values else 0

    FlowBytes.get_min_forward_header_bytes = _safe_min_forward_header_bytes

    def _safe_http_write(self, data):
        try:
            resp = self.session.post(self.url, json=data, timeout=5)
            resp.raise_for_status()
        except Exception as exc:
            message = str(exc)
            expected_shutdown_errors = (
                "Connection reset by peer",
                "Connection aborted",
                "Connection refused",
            )
            if any(fragment in message for fragment in expected_shutdown_errors):
                return
            try:
                self.logger.exception("HTTPWriter failed posting flow")
            except Exception:
                print(f"[cicflowmeter] HTTPWriter failed posting flow: {exc}")

    HttpWriter.write = _safe_http_write


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interface", required=True, help="Interface de captura")
    parser.add_argument("--url", required=True, help="Endpoint HTTP para POST dos fluxos")
    parser.add_argument("--expired-update", type=float, default=3.0, help="Idle timeout do fluxo em segundos")
    parser.add_argument("--packets-per-gc", type=int, default=200, help="Pacotes para disparar GC")
    parser.add_argument("--verbose", action="store_true", help="Logs detalhados")
    return parser


def _create_sniffer_without_bpf(args):
    """
    Cria AsyncSniffer sem filtro BPF.
    Em alguns ambientes Linux + container host mode, o filtro BPF
    do cicflowmeter pode resultar em zero pacotes capturados.
    """
    # Compatibilidade entre versões do cicflowmeter:
    # - API moderna: FlowSession(output_mode=..., output=...) + prn=session.process
    # - API legada: FlowSession como classe de sessão do Scapy (session=FlowSession, prn=None)
    flow_session_mod.FlowSession.output_mode = "url"
    flow_session_mod.FlowSession.output = args.url
    flow_session_mod.FlowSession.fields = None
    flow_session_mod.FlowSession.verbose = args.verbose

    init_sig = inspect.signature(flow_session_mod.FlowSession.__init__)
    supports_runtime_args = "output_mode" in init_sig.parameters

    if supports_runtime_args:
        session = flow_session_mod.FlowSession(
            output_mode="url",
            output=args.url,
            fields=None,
            verbose=args.verbose,
        )
        mode_label = "modern-prn"
        use_background_gc = True
    else:
        session = flow_session_mod.FlowSession()
        mode_label = "legacy-prn"
        use_background_gc = False

    process_impl = flow_session_mod.FlowSession.process
    if process_impl is DefaultSession.process and hasattr(session, "on_packet_received"):
        packet_handler = session.on_packet_received
    else:
        packet_handler = session.process

    def _safe_packet_handler(pkt):
        try:
            return packet_handler(pkt)
        except Exception as exc:
            print(f"[cicflow_fast] WARN packet handler error: {exc}", flush=True)
            return None

    print(f"[cicflow_fast] MODO cicflowmeter={mode_label}", flush=True)

    # Evita depender de API privada do cicflowmeter (_start_periodic_gc),
    # que muda entre versões e pode derrubar o subprocesso do sniffer.
    if use_background_gc:
        gc_interval = float(getattr(cic_sniffer, "GC_INTERVAL", 1.0))
        session._gc_stop = threading.Event()

        def _gc_worker() -> None:
            while not session._gc_stop.is_set():
                try:
                    session.garbage_collect(time.time())
                except Exception:
                    pass
                session._gc_stop.wait(gc_interval)

        gc_thread = threading.Thread(target=_gc_worker, daemon=True)
        gc_thread.start()

    sniffer = AsyncSniffer(
        iface=args.interface,
        filter="ip and (tcp or udp)",
        prn=_safe_packet_handler,
        store=False,
    )
    return sniffer, session


def main() -> None:
    import sys

    # Log file
    log_candidates = [
        Path(tempfile.gettempdir()) / "cicflow_fast.log",
        Path(__file__).resolve().parent / "cicflow_fast.log",
    ]
    logfile = None
    for candidate in log_candidates:
        try:
            candidate.parent.mkdir(parents=True, exist_ok=True)
            logfile = open(candidate, "a", encoding="utf-8")
            break
        except OSError:
            continue

    def log(msg):
        if logfile:
            logfile.write(f"{msg}\n")
            logfile.flush()
        print(msg, file=sys.stderr, flush=True)
    
    args = _build_parser().parse_args()
    
    log(f"[cicflow_fast] START Iniciando com interface={args.interface}, url={args.url}")

    _apply_runtime_safety_patches()

    # Sobrescreve valores importados em flow_session.py.
    # Compatibilidade: versões atuais usam GARBAGE_COLLECT_PACKETS.
    flow_session_mod.EXPIRED_UPDATE = float(args.expired_update)
    if hasattr(flow_session_mod, "GARBAGE_COLLECT_PACKETS"):
        flow_session_mod.GARBAGE_COLLECT_PACKETS = int(args.packets_per_gc)
    else:
        flow_session_mod.PACKETS_PER_GC = int(args.packets_per_gc)

    gc_value = getattr(
        flow_session_mod,
        "GARBAGE_COLLECT_PACKETS",
        getattr(flow_session_mod, "PACKETS_PER_GC", None),
    )
    log(f"[cicflow_fast] EXPIRED_UPDATE={flow_session_mod.EXPIRED_UPDATE}, GC_PACKETS={gc_value}")

    try:
        log(f"[cicflow_fast] Chamando cic_sniffer.create_sniffer()...")
        created = _create_sniffer_without_bpf(args)
        log(f"[cicflow_fast] create_sniffer retornou: {type(created)}")
    except Exception as e:
        log(f"[cicflow_fast] ERRO em create_sniffer: {e}")
        import traceback
        if logfile:
            traceback.print_exc(file=logfile)
            logfile.close()
        return

    # Compatibilidade entre versões do cicflowmeter:
    # algumas retornam apenas AsyncSniffer e outras retornam (sniffer, session).
    session = None
    try:
        if isinstance(created, tuple):
            sniffer = created[0]
            if len(created) > 1:
                session = created[1]
        else:
            sniffer = created
        log(f"[cicflow_fast] Sniffer obtido type={type(sniffer)}, iniciando...")
    except Exception as e:
        log(f"[cicflow_fast] ERRO ao processar sniffer: {e}")
        import traceback
        if logfile:
            traceback.print_exc(file=logfile)
            logfile.close()
        return

    try:
        sniffer.start()
        log(f"[cicflow_fast] Sniffer iniciado, aguardando fluxos...")
        sniffer.join()
        log(f"[cicflow_fast] sniffer.join() retornou")
    except KeyboardInterrupt:
        log(f"[cicflow_fast] Interrupção recebida")
        sniffer.stop()
    except Exception as e:
        log(f"[cicflow_fast] ERRO durante captura: {e}")
        import traceback
        if logfile:
            traceback.print_exc(file=logfile)
    finally:
        if session is not None and hasattr(session, "_gc_stop"):
            session._gc_stop.set()
        log(f"[cicflow_fast] Encerrando, logfile fechado")
        if logfile:
            logfile.close()


if __name__ == "__main__":
    main()
