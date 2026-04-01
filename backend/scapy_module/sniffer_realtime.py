# backend/scapy_module/sniffer_realtime.py

import sys
from pathlib import Path
import threading
import time
import subprocess
import platform
import json
import re
from datetime import datetime
from collections import deque, defaultdict

PROJECT_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_PATH))

from backend.scapy_module.predictor import ModelPredictor
from backend.scapy_module.extractor import FlowExtractor
from scapy.all import sniff, IP, TCP, UDP, ICMP, get_if_list


class IPSRealtime:

    def __init__(self, modelo_path=None, interface=None, filtro=None, callback=None, bloquear=True):

        # ── Modelo ──────────────────────────────────────────────────────────
        if modelo_path is None:
            models_dir = PROJECT_PATH / "models"
            self.modelo_path = models_dir / "random_forest_server_model.pkl"
            if not self.modelo_path.exists():
                # fallback para qualquer pkl disponível
                pkls = sorted(models_dir.glob("*.pkl"))
                if not pkls:
                    raise FileNotFoundError(f"Nenhum modelo encontrado em: {models_dir}")
                self.modelo_path = pkls[0]
            print(f"📂 Modelo: {self.modelo_path.name}")
        else:
            self.modelo_path = Path(modelo_path)

        self.predictor = ModelPredictor(self.modelo_path)

        # ── Extractor de fluxos ─────────────────────────────────────────────
        self.flow_extractor = FlowExtractor(timeout=2)

        # ── Filtro BPF ──────────────────────────────────────────────────────
        self.filtro = filtro
        if self.filtro:
            print(f"🔍 Filtro BPF: {self.filtro}")

        # ── Interfaces ──────────────────────────────────────────────────────
        self.interface_names = {}
        raw_interfaces = get_if_list()

        if interface is None or interface.lower() == "todas":
            self.interface_list = raw_interfaces
            print(f"📡 Modo: TODAS as interfaces ({len(raw_interfaces)})")
        else:
            found = [i for i in raw_interfaces
                     if interface.lower() in i.lower()
                     or interface.lower() in self._friendly(i).lower()]
            self.interface_list = found if found else [interface]
            print(f"📡 Interface: {self.interface_list[0]}")

        for i in self.interface_list:
            self.interface_names[i] = self._friendly(i)

        # ── Configuração ────────────────────────────────────────────────────
        self.callback = callback
        self.bloquear = bloquear

        # ── Estado ──────────────────────────────────────────────────────────
        self.contador_fluxos = 0
        self.anomalias       = 0
        self.bloqueios       = 0
        self.ultimos_fluxos  = deque(maxlen=100)
        self.ips_bloqueados  = set()
        self.contagem_ips    = defaultdict(int)
        self.running         = False
        self.sniffer_threads = []
        self.sistema         = platform.system()
        self.inicio          = datetime.now()

        self.interface_stats   = defaultdict(int)
        self.interface_ativas  = set()
        self.interface_inativas = set(self.interface_list)

        self.whitelist = {
            '8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1',
            '192.168.1.1', '192.168.0.1',
        }

        # ── Logs ────────────────────────────────────────────────────────────
        self.log_dir = PROJECT_PATH / "data" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file    = self.log_dir / f"ips_{datetime.now().strftime('%Y%m%d')}.json"
        self.sessoes_log = self.log_dir / "sessoes.json"
        self.carregar_logs()

        self.stats      = {'TCP': 0, 'UDP': 0, 'ICMP': 0, 'OUTROS': 0}
        self.portas_tcp = defaultdict(int)
        self.portas_udp = defaultdict(int)

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _friendly(self, iface):
        """Converte UUID/nome de interface para nome legível."""
        mapa = {
            'wi-fi': 'Wi-Fi', 'wireless': 'Wi-Fi', 'wlan': 'Wi-Fi',
            'ethernet': 'Ethernet', 'lan': 'Ethernet',
            'loopback': 'Loopback', 'lo': 'Loopback',
            'bluetooth': 'Bluetooth',
            'virtualbox': 'VirtualBox', 'vbox': 'VirtualBox',
            'vmware': 'VMware', 'vmnet': 'VMware',
            'vpn': 'VPN', 'ppp': 'VPN',
        }
        low = iface.lower()
        for k, v in mapa.items():
            if k in low:
                return v
        m = re.search(r'\{([^}]+)\}', iface)
        if m:
            return f"Interface_{m.group(1)[:8]}"
        return iface[:20] + ('...' if len(iface) > 20 else '')

    def get_friendly_interface_name(self, iface):
        return self.interface_names.get(iface, self._friendly(iface))

    def _get_protocol_name(self, proto):
        return {6: 'TCP', 17: 'UDP', 1: 'ICMP'}.get(proto, f'OUTRO({proto})')

    # ── Logs ────────────────────────────────────────────────────────────────

    def carregar_logs(self):
        try:
            if self.sessoes_log.exists():
                with open(self.sessoes_log) as f:
                    self.historico = json.load(f)
            else:
                self.historico = []
        except Exception:
            self.historico = []

    def salvar_log(self):
        entry = {
            'timestamp':       datetime.now().isoformat(),
            'duracao':         str(datetime.now() - self.inicio),
            'total_fluxos':    self.contador_fluxos,
            'anomalias':       self.anomalias,
            'bloqueios':       self.bloqueios,
            'ips_bloqueados':  list(self.ips_bloqueados),
            'contagem_ips':    dict(self.contagem_ips),
            'stats_protocolo': dict(self.stats),
        }
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

        self.historico.append({
            'inicio': self.inicio.isoformat(),
            'fim':    datetime.now().isoformat(),
            'resumo': {
                'fluxos':    self.contador_fluxos,
                'anomalias': self.anomalias,
                'bloqueios': self.bloqueios,
            }
        })
        with open(self.sessoes_log, 'w') as f:
            json.dump(self.historico[-50:], f, indent=2)

    # ── Whitelist / Bloqueio ─────────────────────────────────────────────────

    def adicionar_whitelist(self, ip):
        self.whitelist.add(ip)

    def remover_whitelist(self, ip):
        self.whitelist.discard(ip)

    def bloquear_ip(self, ip):
        if ip in self.ips_bloqueados or ip in self.whitelist:
            return
        try:
            if self.sistema == "Windows":
                regra = f"IPS_Bloco_{ip.replace('.', '_')}"
                subprocess.run(
                    f'netsh advfirewall firewall add rule name="{regra}" '
                    f'dir=in action=block remoteip={ip}',
                    shell=True, capture_output=True
                )
            else:
                subprocess.run(
                    f'sudo iptables -A INPUT -s {ip} -j DROP',
                    shell=True, capture_output=True
                )
            self.ips_bloqueados.add(ip)
            self.bloqueios += 1
            print(f"🔒 IP BLOQUEADO: {ip}")
        except Exception as e:
            print(f"❌ Erro ao bloquear {ip}: {e}")

    def desbloquear_ip(self, ip):
        if ip not in self.ips_bloqueados:
            return
        try:
            if self.sistema == "Windows":
                regra = f"IPS_Bloco_{ip.replace('.', '_')}"
                subprocess.run(
                    f'netsh advfirewall firewall delete rule name="{regra}"',
                    shell=True, capture_output=True
                )
            else:
                subprocess.run(
                    f'sudo iptables -D INPUT -s {ip} -j DROP',
                    shell=True, capture_output=True
                )
            self.ips_bloqueados.discard(ip)
            print(f"🔓 IP DESBLOQUEADO: {ip}")
        except Exception as e:
            print(f"❌ Erro ao desbloquear {ip}: {e}")

    def limpar_todas_regras(self):
        for ip in list(self.ips_bloqueados):
            self.desbloquear_ip(ip)

    # ── Processamento de fluxo ───────────────────────────────────────────────

    def processar_fluxo(self, flow, iface=None):
        self.contador_fluxos += 1

        try:
            # Random Forest devolve (label_int, label_str, confiança)
            pred_int, pred_str, confianca = self.predictor.predict_flow(flow)
            is_attack = self.predictor.is_attack(pred_int)

            fluxo_info = {
                'tipo':       'ataque' if is_attack else 'normal',
                'timestamp':  datetime.now().isoformat(),
                'src_ip':     flow.src_ip,
                'dst_ip':     flow.dst_ip,
                'src_port':   flow.src_port,
                'dst_port':   flow.dst_port,
                'protocolo':  self._get_protocol_name(flow.protocol),
                'duration':   flow.end_time - flow.start_time if flow.start_time else 0,
                'packets':    flow.total_packets,
                'bytes':      flow.total_bytes,
                'contador':   self.contador_fluxos,
                'interface':  self.get_friendly_interface_name(iface) if iface else 'Desconhecida',
                'label':      pred_str,        # "Bot", "SSH-Bruteforce", "Benign", etc.
                'label_int':  pred_int,
                'confianca':  round(confianca * 100, 1),  # ex: 97.3
                'bloqueado':  False,
                'cor':        'red' if is_attack else 'green',
            }

            if is_attack:
                self.anomalias += 1

                if flow.src_ip and flow.src_ip not in self.whitelist:
                    self.contagem_ips[flow.src_ip] += 1
                    if self.bloquear:
                        self.bloquear_ip(flow.src_ip)
                        fluxo_info['bloqueado'] = True

                self._mostrar_alerta(flow, fluxo_info)
            else:
                if self.contador_fluxos % 100 == 0:
                    self._mostrar_normal(flow, fluxo_info)

            if self.callback:
                self.callback(fluxo_info)

            self.ultimos_fluxos.append(fluxo_info)

            if self.contador_fluxos % 100 == 0:
                self._mostrar_estatisticas()

        except Exception as e:
            print(f"❌ Erro ao processar fluxo: {e}")

    def _mostrar_alerta(self, flow, info):
        estado = "🔒 BLOQUEADO" if info['bloqueado'] else "⚠️  ATAQUE"
        print(f"\033[91m{estado} #{info['contador']} "
              f"[{info['protocolo']}] {info['label']} ({info['confianca']}%)\033[0m")
        print(f"   {flow.src_ip}:{flow.src_port} → {flow.dst_ip}:{flow.dst_port}")
        print(f"   Pacotes: {flow.total_packets} | Bytes: {flow.total_bytes}")
        if flow.src_ip in self.contagem_ips:
            print(f"   Ocorrências deste IP: {self.contagem_ips[flow.src_ip]}")

    def _mostrar_normal(self, flow, info):
        print(f"✅ Normal #{info['contador']} [{info['protocolo']}]: "
              f"{flow.src_ip} → {flow.dst_ip} ({info['confianca']}%)")

    def _mostrar_estatisticas(self):
        taxa = (self.anomalias / self.contador_fluxos * 100) if self.contador_fluxos else 0
        print("\n" + "="*60)
        print(f"📊 {self.contador_fluxos} fluxos | "
              f"⚠️ {self.anomalias} ataques ({taxa:.1f}%) | "
              f"🔒 {self.bloqueios} bloqueios")
        print("="*60 + "\n")

    # ── Captura ──────────────────────────────────────────────────────────────

    def _packet_handler(self, pkt, iface):
        if not self.running:
            return
        if iface:
            self.interface_stats[iface] += 1
            self.interface_ativas.add(iface)
            self.interface_inativas.discard(iface)

        self.flow_extractor.process_packet(pkt, time.time())

        for flow in self.flow_extractor.get_completed_flows():
            self.processar_fluxo(flow, iface)

    def _sniff_thread(self, iface):
        try:
            print(f"   🔵 Captura iniciada: {self.get_friendly_interface_name(iface)}")
            sniff(
                iface=iface,
                prn=lambda pkt: self._packet_handler(pkt, iface),
                filter=self.filtro,
                store=False,
                stop_filter=lambda x: not self.running
            )
        except Exception as e:
            if self.running:
                print(f"   ❌ Erro em {iface}: {e}")

    def iniciar(self):
        print("\n" + "="*60)
        print("🚀 AEGIS IPS — Random Forest (10 features)")
        print("="*60)
        print(f"📂 Modelo:     {self.modelo_path.name}")
        print(f"📡 Interfaces: {len(self.interface_list)}")
        print(f"🔒 Bloqueio:   {'SIM' if self.bloquear else 'NÃO'}")
        print(f"✅ Whitelist:  {len(self.whitelist)} IPs")
        print("="*60 + "\n")

        self.running = True
        self.inicio  = datetime.now()

        self.sniffer_threads = []
        for iface in self.interface_list:
            t = threading.Thread(target=self._sniff_thread, args=(iface,), daemon=True)
            t.start()
            self.sniffer_threads.append(t)

        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.parar()

    def parar(self):
        if not self.running:
            return

        print("\n⏹️  A parar...")
        self.running = False
        time.sleep(1)

        for flow in self.flow_extractor.get_completed_flows():
            self.processar_fluxo(flow)

        print(f"📦 Fluxos: {self.contador_fluxos} | "
              f"⚠️ Ataques: {self.anomalias} | "
              f"🔒 Bloqueios: {self.bloqueios}")

        self.salvar_log()
        print(f"📁 Log: {self.log_file}")
        print("✅ IPS parado!")


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--interface', '-i')
    p.add_argument('--modelo',    '-m')
    p.add_argument('--filtro',    '-f')
    p.add_argument('--no-bloqueio', action='store_true')
    args = p.parse_args()

    ips = IPSRealtime(
        modelo_path=args.modelo,
        interface=args.interface,
        filtro=args.filtro,
        bloquear=not args.no_bloqueio
    )
    ips.iniciar()


if __name__ == "__main__":
    main()