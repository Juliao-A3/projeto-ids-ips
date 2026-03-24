# backend/scapy_module/sniffer_realtime.py
# IPS com nomes amigáveis para interfaces, filtros BPF e portas no resumo

import sys
from pathlib import Path
import threading
import time
import subprocess
import platform
import json
import re
from datetime import datetime

PROJECT_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_PATH))

from backend.scapy_module.predictor import ModelPredictor
from backend.scapy_module.extractor import ScapyExtractor
from scapy.all import sniff, IP, TCP, UDP, ICMP, get_if_list
from collections import deque, defaultdict

class IPSRealtime:
    def __init__(self, modelo_path=None, interface=None, filtro=None, callback=None, bloquear=True):
        # ========== FUNÇÃO PARA NOMES AMIGÁVEIS ==========
        def get_friendly_name(iface):
            """Converte UUIDs do Windows para nomes amigáveis"""
            friendly_names = {
                'Wi-Fi': ['wi-fi', 'wireless', 'wlan', 'wi fi', 'wi-fi'],
                'Ethernet': ['ethernet', 'lan', 'cabo', 'cable'],
                'Loopback': ['loopback', 'lo', 'localhost'],
                'Bluetooth': ['bluetooth', 'bt'],
                'VirtualBox': ['virtualbox', 'vbox', 'vboxnet'],
                'VMware': ['vmware', 'vmnet'],
                'Hyper-V': ['hyper-v', 'hyperv', 'vswitch', 'ethernet adapter v'],
                'VPN': ['vpn', 'ppp', 'tunnel'],
                'Bridge': ['bridge', 'br']
            }

            iface_lower = iface.lower()

            for friendly, patterns in friendly_names.items():
                for pattern in patterns:
                    if pattern in iface_lower:
                        return friendly

            match = re.search(r'\{([^}]+)\}', iface)
            if match:
                uuid_short = match.group(1)[:8]
                return f"Interface_{uuid_short}"

            return iface[:20] + "..." if len(iface) > 20 else iface
        # ==================================================

        # Se não especificar modelo, procura o mais recente
        if modelo_path is None:
            models_dir = PROJECT_PATH / "models"
            modelos = list(models_dir.glob("modelo_scapy_*.pkl"))
            if modelos:
                self.modelo_path = max(modelos, key=lambda x: x.stat().st_mtime)
                print(f"📂 Usando modelo mais recente: {self.modelo_path.name}")
            else:
                self.modelo_path = models_dir / "best_model.pkl"
                print(f"📂 Usando modelo padrão: best_model.pkl")
        else:
            self.modelo_path = Path(modelo_path)

        print(f"📂 A carregar modelo: {self.modelo_path}")
        self.predictor = ModelPredictor(self.modelo_path)
        self.extractor = ScapyExtractor(self.predictor.feature_names)

        self.filtro = filtro
        if self.filtro:
            print(f"🔍 Filtro BPF ativo: {self.filtro}")

        # ========== TRATAMENTO DE INTERFACES ==========
        if interface is None or interface.lower() == "todas":
            raw_interfaces = get_if_list()
            self.interface_list = []
            self.interface_names = {}

            print(f"📡 Modo: TODAS as interfaces ({len(raw_interfaces)} encontradas)")
            for i, raw_iface in enumerate(raw_interfaces):
                friendly = get_friendly_name(raw_iface)
                self.interface_list.append(raw_iface)
                self.interface_names[raw_iface] = friendly
                print(f"   {i+1}. {friendly}")
        else:
            raw_interfaces = get_if_list()
            found = False

            for raw_iface in raw_interfaces:
                friendly = get_friendly_name(raw_iface)
                if interface.lower() in friendly.lower() or interface.lower() in raw_iface.lower():
                    self.interface_list = [raw_iface]
                    self.interface_names = {raw_iface: friendly}
                    print(f"📡 Interface específica: {friendly}")
                    found = True
                    break

            if not found:
                self.interface_list = [interface]
                self.interface_names = {interface: get_friendly_name(interface)}
                print(f"📡 Interface específica: {self.interface_names[interface]}")
        # ================================================

        self.callback = callback
        self.bloquear = bloquear
        self.contador = 0
        self.anomalias = 0
        self.bloqueios = 0
        self.ultimos_pacotes = deque(maxlen=100)
        self.ips_bloqueados = set()
        self.contagem_ips = defaultdict(int)
        self.running = False
        self.sniffer_threads = []
        self.sistema = platform.system()
        self.inicio = datetime.now()

        self.interface_stats = defaultdict(int)
        self.interface_ativas = set()
        self.interface_inativas = set(self.interface_list)

        self.whitelist = {
            '8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1',
            '192.168.1.1', '192.168.0.1', '10.212.255.176', 
            "192.168.100.1", "127.0.0.1" 
        }

        self.log_dir = PROJECT_PATH / "data" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / f"ips_{datetime.now().strftime('%Y%m%d')}.json"
        self.sessoes_log = self.log_dir / "sessoes.json"
        self.carregar_logs()

        self.stats = {'TCP': 0, 'UDP': 0, 'ICMP': 0, 'OUTROS': 0}

        self.portas_tcp = defaultdict(int)
        self.portas_udp = defaultdict(int)

    def get_friendly_interface_name(self, iface):
        return self.interface_names.get(iface, iface[:20] + "...")

    def carregar_logs(self):
        if self.sessoes_log.exists():
            try:
                with open(self.sessoes_log, 'r') as f:
                    self.historico = json.load(f)
            except:
                self.historico = []
        else:
            self.historico = []

    def salvar_log(self):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'duracao': str(datetime.now() - self.inicio),
            'total_pacotes': self.contador,
            'anomalias': self.anomalias,
            'bloqueios': self.bloqueios,
            'ips_bloqueados': list(self.ips_bloqueados),
            'contagem_ips': dict(self.contagem_ips),
            'stats_protocolo': dict(self.stats),
            'filtro': self.filtro,
            'portas_tcp': dict(self.portas_tcp),
            'portas_udp': dict(self.portas_udp),
            'interface_stats': {
                self.get_friendly_interface_name(k): v
                for k, v in self.interface_stats.items()
            },
            'interface_ativas': [self.get_friendly_interface_name(i) for i in self.interface_ativas],
            'interface_inativas': [self.get_friendly_interface_name(i) for i in self.interface_inativas]
        }

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

        self.historico.append({
            'inicio': self.inicio.isoformat(),
            'fim': datetime.now().isoformat(),
            'resumo': {
                'pacotes': self.contador,
                'anomalias': self.anomalias,
                'bloqueios': self.bloqueios,
                'ips': len(self.ips_bloqueados),
                'interfaces_ativas': len(self.interface_ativas)
            }
        })

        with open(self.sessoes_log, 'w') as f:
            json.dump(self.historico[-50:], f, indent=2)

    def adicionar_whitelist(self, ip):
        self.whitelist.add(ip)
        print(f"✅ IP {ip} adicionado à whitelist")

    def remover_whitelist(self, ip):
        if ip in self.whitelist:
            self.whitelist.remove(ip)
            print(f"✅ IP {ip} removido da whitelist")

    def bloquear_ip(self, ip):
        if ip in self.ips_bloqueados or ip in self.whitelist:
            return

        try:
            if self.sistema == "Windows":
                nome_regra = f"IPS_Bloco_{ip.replace('.', '_')}"
                cmd = f'netsh advfirewall firewall add rule name="{nome_regra}" dir=in action=block remoteip={ip}'
                subprocess.run(cmd, shell=True, capture_output=True)
                print(f"🔒 IP BLOQUEADO (Windows): {ip}")
            elif self.sistema == "Linux":
                cmd = f'sudo iptables -A INPUT -s {ip} -j DROP'
                subprocess.run(cmd, shell=True, capture_output=True)
                print(f"🔒 IP BLOQUEADO (Linux): {ip}")

            self.ips_bloqueados.add(ip)
            self.bloqueios += 1
            self.salvar_log()
        except Exception as e:
            print(f"❌ Erro ao bloquear IP {ip}: {e}")

    def desbloquear_ip(self, ip):
        if ip not in self.ips_bloqueados:
            return

        try:
            if self.sistema == "Windows":
                nome_regra = f"IPS_Bloco_{ip.replace('.', '_')}"
                cmd = f'netsh advfirewall firewall delete rule name="{nome_regra}"'
                subprocess.run(cmd, shell=True, capture_output=True)
                print(f"🔓 IP DESBLOQUEADO (Windows): {ip}")
            elif self.sistema == "Linux":
                cmd = f'sudo iptables -D INPUT -s {ip} -j DROP'
                subprocess.run(cmd, shell=True, capture_output=True)
                print(f"🔓 IP DESBLOQUEADO (Linux): {ip}")

            self.ips_bloqueados.remove(ip)
            self.salvar_log()
        except Exception as e:
            print(f"❌ Erro ao desbloquear IP {ip}: {e}")

    def limpar_todas_regras(self):
        print("\n🧹 A limpar regras de bloqueio...")
        for ip in list(self.ips_bloqueados):
            self.desbloquear_ip(ip)
        print("✅ Regras limpas!")
        self.salvar_log()

    def _obter_servico(self, porta):
        """Retorna o nome do serviço para uma porta conhecida"""
        servicos = {
            20: "FTP Data", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
            53: "DNS", 80: "HTTP", 110: "POP3", 123: "NTP", 143: "IMAP",
            443: "HTTPS", 445: "SMB", 465: "SMTPS", 587: "SMTP", 993: "IMAPS",
            995: "POP3S", 3389: "RDP", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt"
        }
        return servicos.get(porta, "Desconhecido")

    def processar_pacote(self, pkt, iface=None):
        if not self.running:
            return

        self.contador += 1

        if iface:
            self.interface_stats[iface] += 1
            self.interface_ativas.add(iface)
            if iface in self.interface_inativas:
                self.interface_inativas.remove(iface)
            friendly_iface = self.get_friendly_interface_name(iface)
        else:
            friendly_iface = "Desconhecida"

        if TCP in pkt:
            self.stats['TCP'] += 1
            proto = "TCP"
            tcp = pkt[TCP]
            self.portas_tcp[tcp.sport] += 1
            self.portas_tcp[tcp.dport] += 1
        elif UDP in pkt:
            self.stats['UDP'] += 1
            proto = "UDP"
            udp = pkt[UDP]
            self.portas_udp[udp.sport] += 1
            self.portas_udp[udp.dport] += 1
        elif ICMP in pkt:
            self.stats['ICMP'] += 1
            proto = "ICMP"
        else:
            self.stats['OUTROS'] += 1
            proto = "OUTRO"

        try:
            feat = self.extractor._extract_packet_features(pkt, None)
            pred = self.predictor.model.predict([feat])[0]

            pkt_info = {
                'tipo': 'anomalia' if pred == -1 else 'normal',
                'timestamp': datetime.now().isoformat(),
                'protocolo': proto,
                'tamanho': len(pkt),
                'contador': self.contador,
                'interface': friendly_iface
            }

            ip_suspeito = None
            if IP in pkt:
                ip = pkt[IP]
                pkt_info['src_ip'] = ip.src
                pkt_info['dst_ip'] = ip.dst
                ip_suspeito = ip.src

                if TCP in pkt:
                    tcp = pkt[TCP]
                    pkt_info['src_port'] = tcp.sport
                    pkt_info['dst_port'] = tcp.dport
                    pkt_info['flags'] = str(tcp.flags)
                elif UDP in pkt:
                    udp = pkt[UDP]
                    pkt_info['src_port'] = udp.sport
                    pkt_info['dst_port'] = udp.dport

            if pred == -1:
                self.anomalias += 1
                pkt_info['cor'] = 'red'
                pkt_info['bloqueado'] = False

                if ip_suspeito and ip_suspeito not in self.whitelist:
                    self.contagem_ips[ip_suspeito] += 1

                    if self.bloquear and self.contagem_ips[ip_suspeito] >= 5:
                        self.bloquear_ip(ip_suspeito)
                        pkt_info['bloqueado'] = True

                self._mostrar_alerta(pkt, proto, ip_suspeito, friendly_iface)
            else:
                pkt_info['cor'] = 'green'
                pkt_info['bloqueado'] = False
                if self.contador % 100 == 0:
                    self._mostrar_normal(pkt, proto, friendly_iface)

            if self.callback:
                self.callback(pkt_info)

            self.ultimos_pacotes.append(pkt_info)

            if self.contador % 100 == 0:
                self._mostrar_estatisticas()

        except Exception as e:
            print(f"❌ Erro ao processar pacote: {e}")

    def _mostrar_alerta(self, pkt, proto, ip_suspeito=None, iface=None):
        cor_vermelho = '\033[91m'
        cor_amarelo = '\033[93m'
        cor_azul = '\033[94m'
        cor_reset = '\033[0m'

        interface_info = f" [📡 {iface}]" if iface else ""

        if ip_suspeito and ip_suspeito in self.whitelist:
            print(f"{cor_azul}⚪ WHITELIST #{self.contador}{interface_info} [{proto}]{cor_reset}")
        elif ip_suspeito and ip_suspeito in self.ips_bloqueados:
            print(f"{cor_amarelo}🔒 BLOQUEADO #{self.contador}{interface_info} [{proto}]{cor_reset}")
        else:
            print(f"{cor_vermelho}⚠️ ANOMALIA #{self.contador}{interface_info} [{proto}]{cor_reset}")

        if IP in pkt:
            ip = pkt[IP]
            status = ""
            if ip.src in self.whitelist:
                status = " [WHITELIST]"
            elif ip.src in self.ips_bloqueados:
                status = " [BLOQUEADO]"

            print(f"   IP: {ip.src} → {ip.dst}{status}")

            if TCP in pkt:
                tcp = pkt[TCP]
                print(f"   TCP: {tcp.sport} → {tcp.dport} | Flags: {tcp.flags}")
            elif UDP in pkt:
                udp = pkt[UDP]
                print(f"   UDP: {udp.sport} → {udp.dport}")
            elif ICMP in pkt:
                icmp = pkt[ICMP]
                print(f"   ICMP: type={icmp.type} code={icmp.code}")

        print(f"   Tamanho: {len(pkt)} bytes")

        if ip_suspeito and ip_suspeito in self.contagem_ips:
            print(f"   Anomalias deste IP: {self.contagem_ips[ip_suspeito]}")

    def _mostrar_normal(self, pkt, proto, iface=None):
        interface_info = f" [📡 {iface}]" if iface else ""
        if IP in pkt:
            ip = pkt[IP]
            print(f"✅ Normal #{self.contador}{interface_info}: {ip.src} → {ip.dst} [{proto}]")

    def _mostrar_estatisticas(self):
        taxa = (self.anomalias / self.contador) * 100 if self.contador > 0 else 0

        print("\n" + "="*80)
        print(f"📊 ESTATÍSTICAS ({self.contador} pacotes)")
        print("="*80)
        print(f"📦 Total: {self.contador}")
        print(f"✅ Normais: {self.contador - self.anomalias}")
        print(f"⚠️ Anomalias: {self.anomalias} ({taxa:.2f}%)")
        print(f"🔒 Bloqueios: {self.bloqueios}")
        print(f"🚫 IPs bloqueados: {len(self.ips_bloqueados)}")
        print(f"✅ IPs na whitelist: {len(self.whitelist)}")
        if self.filtro:
            print(f"🔍 Filtro ativo: {self.filtro}")

        if self.portas_tcp:
            print("\n📊 TOP PORTAS TCP:")
            for porta, count in sorted(self.portas_tcp.items(), key=lambda x: x[1], reverse=True)[:10]:
                servico = self._obter_servico(porta)
                print(f"   Porta {porta}: {count} pacotes ({servico})")

        if self.portas_udp:
            print("\n📊 TOP PORTAS UDP:")
            for porta, count in sorted(self.portas_udp.items(), key=lambda x: x[1], reverse=True)[:10]:
                servico = self._obter_servico(porta)
                print(f"   Porta {porta}: {count} pacotes ({servico})")

        print(f"\n📡 INTERFACES DE REDE:")
        print(f"   Total de interfaces: {len(self.interface_list)}")
        print(f"   🟢 ATIVAS ({len(self.interface_ativas)}):")
        for iface in sorted(self.interface_ativas):
            friendly = self.get_friendly_interface_name(iface)
            print(f"      - {friendly}: {self.interface_stats[iface]} pacotes")

        if self.interface_inativas:
            print(f"   🔴 INATIVAS ({len(self.interface_inativas)}):")
            for iface in sorted(self.interface_inativas):
                friendly = self.get_friendly_interface_name(iface)
                print(f"      - {friendly}")
        else:
            print(f"   ✅ Todas as interfaces geraram tráfego!")

        print("\n📈 Por protocolo:")
        for proto, count in self.stats.items():
            perc = (count / self.contador) * 100 if self.contador > 0 else 0
            print(f"   {proto}: {count} ({perc:.1f}%)")

        if self.ips_bloqueados:
            print("\n🚫 IPs BLOQUEADOS:")
            for ip in list(self.ips_bloqueados)[:5]:
                print(f"   - {ip} ({self.contagem_ips[ip]} anomalias)")

        print("="*80 + "\n")

    def _sniff_thread_func(self, iface):
        try:
            friendly = self.get_friendly_interface_name(iface)
            print(f"   🔵 Iniciada captura em: {friendly}")
            sniff(
                iface=iface,
                prn=lambda pkt: self.processar_pacote(pkt, iface),
                filter=self.filtro,
                store=False,
                stop_filter=lambda x: not self.running
            )
        except Exception as e:
            if self.running:
                print(f"   ❌ Erro em {self.get_friendly_interface_name(iface)}: {e}")

    def iniciar(self):
        print("\n" + "="*80)
        print("🚀 IPS EM TEMPO REAL")
        print("="*80)
        print(f"📂 Modelo: {self.modelo_path}")
        print(f"📡 Interfaces: {len(self.interface_list)} ativas")
        for iface in self.interface_list:
            friendly = self.get_friendly_interface_name(iface)
            print(f"   - {friendly}")
        if self.filtro:
            print(f"🔍 Filtro BPF: {self.filtro}")
        print(f"🔒 Bloqueio ativo: {'SIM' if self.bloquear else 'NÃO'}")
        print(f"✅ Whitelist: {len(self.whitelist)} IPs")
        print(f"📁 Logs: {self.log_dir}")
        print("="*80 + "\n")

        self.running = True
        self.inicio = datetime.now()

        self.sniffer_threads = []
        for iface in self.interface_list:
            thread = threading.Thread(target=self._sniff_thread_func, args=(iface,))
            thread.daemon = True
            thread.start()
            self.sniffer_threads.append(thread)

        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.parar()

    def parar(self):
        if not self.running:
            return

        print("\n" + "="*80)
        print("⏹️ A PARAR CAPTURA...")
        print("="*80)

        self.running = False
        time.sleep(1)

        print(f"📦 Total pacotes: {self.contador}")
        print(f"✅ Normais: {self.contador - self.anomalias}")
        print(f"⚠️ Anomalias: {self.anomalias}")
        print(f"🔒 Bloqueios realizados: {self.bloqueios}")
        print(f"🚫 IPs bloqueados: {len(self.ips_bloqueados)}")
        print(f"✅ IPs na whitelist: {len(self.whitelist)}")

        if self.portas_tcp:
            print("\n📊 TOP PORTAS TCP:")
            for porta, count in sorted(self.portas_tcp.items(), key=lambda x: x[1], reverse=True)[:10]:
                servico = self._obter_servico(porta)
                print(f"   Porta {porta}: {count} pacotes ({servico})")

        if self.portas_udp:
            print("\n📊 TOP PORTAS UDP:")
            for porta, count in sorted(self.portas_udp.items(), key=lambda x: x[1], reverse=True)[:10]:
                servico = self._obter_servico(porta)
                print(f"   Porta {porta}: {count} pacotes ({servico})")

        print(f"\n📡 RESUMO DE INTERFACES:")
        print(f"   🟢 ATIVAS ({len(self.interface_ativas)}):")
        for iface in sorted(self.interface_ativas):
            friendly = self.get_friendly_interface_name(iface)
            print(f"      - {friendly}: {self.interface_stats[iface]} pacotes")

        if self.interface_inativas:
            print(f"   🔴 INATIVAS ({len(self.interface_inativas)}):")
            for iface in sorted(self.interface_inativas):
                friendly = self.get_friendly_interface_name(iface)
                print(f"      - {friendly}")
        else:
            print(f"   ✅ Todas as interfaces geraram tráfego!")

        if self.contador > 0:
            taxa = (self.anomalias / self.contador) * 100
            print(f"\n📊 Taxa de anomalias: {taxa:.2f}%")

        if self.ips_bloqueados:
            print("\n🚫 IPs BLOQUEADOS:")
            for ip in self.ips_bloqueados:
                print(f"   - {ip} ({self.contagem_ips[ip]} anomalias)")

        self.salvar_log()
        print(f"\n📁 Log guardado em: {self.log_file}")
        print("="*80)
        print("✅ IPS parado com sucesso!")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='IPS com nomes amigáveis e filtros BPF')
    parser.add_argument('--interface', '-i',
                       help='Interface de rede (ex: "Wi-Fi", "Ethernet") - Se não especificar, captura em TODAS')
    parser.add_argument('--modelo', '-m', help='Caminho do modelo .pkl')
    parser.add_argument('--no-bloqueio', action='store_true', help='Desativa bloqueio')
    parser.add_argument('--filtro', '-f', help='Filtro BPF (ex: "icmp", "tcp port 80", "udp port 53")')

    args = parser.parse_args()

    print("="*80)
    print("🔧 SISTEMA IPS COM NOMES AMIGÁVEIS E FILTROS")
    print("="*80)

    ips = IPSRealtime(
        modelo_path=args.modelo,
        interface=args.interface,
        filtro=args.filtro,
        bloquear=not args.no_bloqueio
    )

    ips.iniciar()

if __name__ == "__main__":
    main()