#!/usr/bin/env python3
"""Servidor HTTP local simples para simular beaconing/polling em laboratorio.

Endpoints:
- /
- /cmd
- /upload

Uso:
  python testes/beacon_http_server.py --host 127.0.0.1 --port 8080
"""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime


class BeaconHandler(BaseHTTPRequestHandler):
    server_version = "BeaconHTTP/1.0"

    def _send_ok(self, body: str) -> None:
        data = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        now = datetime.now().isoformat(timespec="seconds")
        print(f"[{now}] GET {self.path} from {self.client_address[0]}:{self.client_address[1]}")

        if self.path in {"/", "/cmd", "/upload"}:
            self._send_ok(f"ok: {self.path}\n")
        else:
            self._send_ok("ok\n")

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        # Evita o log padrao do BaseHTTPRequestHandler para manter a saida limpa.
        return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Servidor HTTP local para teste de beaconing")
    parser.add_argument("--host", default="127.0.0.1", help="Endereco para escutar")
    parser.add_argument("--port", type=int, default=8080, help="Porta para escutar")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = ThreadingHTTPServer((args.host, args.port), BeaconHandler)
    print(f"[BeaconHTTP] a escutar em http://{args.host}:{args.port}")
    print("[BeaconHTTP] endpoints disponiveis: /, /cmd, /upload")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[BeaconHTTP] encerrado")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
