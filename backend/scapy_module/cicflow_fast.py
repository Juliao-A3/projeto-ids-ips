"""
cicflow_fast.py

Wrapper para executar o cicflowmeter com timeouts agressivos de expiração
de fluxo, reduzindo atraso de minutos na emissão para o backend.
"""

import argparse

from cicflowmeter import sniffer as cic_sniffer
import cicflowmeter.flow_session as flow_session_mod
from cicflowmeter.features.context import PacketDirection
from cicflowmeter.features.flow_bytes import FlowBytes
from cicflowmeter.writer import HttpWriter


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


def main() -> None:
    args = _build_parser().parse_args()

    _apply_runtime_safety_patches()

    # Sobrescreve valores importados em flow_session.py.
    flow_session_mod.EXPIRED_UPDATE = float(args.expired_update)
    flow_session_mod.PACKETS_PER_GC = int(args.packets_per_gc)

    sniffer, session = cic_sniffer.create_sniffer(
        input_file=None,
        input_interface=args.interface,
        output_mode="url",
        output=args.url,
        fields=None,
        verbose=args.verbose,
    )

    sniffer.start()

    try:
        sniffer.join()
    except KeyboardInterrupt:
        sniffer.stop()
    finally:
        if hasattr(session, "_gc_stop"):
            session._gc_stop.set()
            session._gc_thread.join(timeout=2.0)
        sniffer.join()
        session.flush_flows()


if __name__ == "__main__":
    main()
