# backend/scapy_module/sniffer_realtime.py
# IPS com análise por FLUXO (80+ features), deteção de ataques e explicação

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
from backend.scapy_module.extractor import FlowExtractor, Flow
from backend.scapy_module.detector_ataques import detector
from backend.scapy_module.explicador import explicador
from scapy.all import sniff, IP, TCP, UDP, ICMP, get_if_list
import signal

class IPSRealtime:
    """
    Sistema de Prevenção de Intrusão com análise por FLUXO (80+ features)
    Com deteção de ataques e explicação de decisões
    """
    
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
            modelos = list(models_dir.glob("modelo_fluxo_*.pkl")) + list(models_dir.glob("modelo_principal.pkl"))
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
        
        # Detetar modo legado
        self.modo_legado = self._detetar_modo_legado()
        
        # Criar extractor com modo adequado
        self.flow_extractor = FlowExtractor(timeout=60, modo_legado=self.modo_legado)
        
        # ========== INTEGRAR DETECTOR E EXPLICADOR ==========
        self.detector = detector
        self.explicador = explicador
        # Carregar o modelo no explicador
        self.explicador._carregar_modelo(self.modelo_path)
        # ===================================================
        
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
        
        # Estatísticas
        self.contador_fluxos = 0
        self.anomalias = 0
        self.bloqueios = 0
        self.ultimos_fluxos = deque(maxlen=100)
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
            '192.168.1.1', '192.168.0.1', '10.212.255.176'
        }
        
        self.log_dir = PROJECT_PATH / "data" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / f"ips_{datetime.now().strftime('%Y%m%d')}.json"
        self.sessoes_log = self.log_dir / "sessoes.json"
        self.carregar_logs()
        
        # Estatísticas por protocolo
        self.stats = {'TCP': 0, 'UDP': 0, 'ICMP': 0, 'OUTROS': 0}
        self.portas_tcp = defaultdict(int)
        self.portas_udp = defaultdict(int)
    
    def _detetar_modo_legado(self):
        """Deteta se o modelo carregado é o antigo (14 features)"""
        if hasattr(self.predictor, 'feature_names') and self.predictor.feature_names:
            if len(self.predictor.feature_names) <= 14:
                print("📋 Modo LEGADO ativado (14 features)")
                return True
        print("📋 Modo FLUXO ativado (78 features)")
        return False
    
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
            'total_fluxos': self.contador_fluxos,
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
                'fluxos': self.contador_fluxos,
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
        servicos = {
            20: "FTP Data", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
            53: "DNS", 80: "HTTP", 110: "POP3", 123: "NTP", 143: "IMAP",
            443: "HTTPS", 445: "SMB", 465: "SMTPS", 587: "SMTP", 993: "IMAPS",
            995: "POP3S", 3389: "RDP", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt"
        }
        return servicos.get(porta, "Desconhecido")
    
    def processar_fluxo(self, flow, iface=None):
        """
        Processa um fluxo completo (após finalizado)
        """
        self.contador_fluxos += 1
        
        # Extrair features do fluxo
        features = flow.get_features()
        feature_values = list(features.values())
        
        # Classificar com o modelo
        try:
            pred, score = self.predictor.predict_flow(flow)
            
            # Detetar tipo de ataque
            tipo_ataque = self.detector.detectar(flow) if pred == -1 else None
            
            # Obter explicação se for anomalia
            explicacao = None
            if pred == -1:
                try:
                    explicacao = self.explicador.explicar(feature_values, list(features.keys()))
                except:
                    explicacao = {'contribuicoes': [], 'metodo': 'erro'}
            
            # Determinar IP principal do fluxo
            main_ip = flow.src_ip
            
            # Preparar info para WebSocket
            fluxo_info = {
                'tipo': 'anomalia' if pred == -1 else 'normal',
                'timestamp': datetime.now().isoformat(),
                'src_ip': flow.src_ip,
                'dst_ip': flow.dst_ip,
                'src_port': flow.src_port,
                'dst_port': flow.dst_port,
                'protocolo': self._get_protocol_name(flow.protocol),
                'duration': features.get('Flow Duration', 0),
                'packets': flow.total_packets,
                'bytes': flow.total_bytes,
                'contador': self.contador_fluxos,
                'interface': self.get_friendly_interface_name(iface) if iface else "Desconhecida",
                'score': float(score),
                'tipo_ataque': tipo_ataque,
                'explicacao': explicacao
            }
            
            if pred == -1:  # anomalia
                self.anomalias += 1
                fluxo_info['cor'] = 'red'
                fluxo_info['bloqueado'] = False
                
                if main_ip and main_ip not in self.whitelist:
                    self.contagem_ips[main_ip] += 1
                    
                    if self.bloquear:
                        self.bloquear_ip(main_ip)
                        fluxo_info['bloqueado'] = True
                
                self._mostrar_alerta_fluxo(flow, fluxo_info)
            else:
                fluxo_info['cor'] = 'green'
                fluxo_info['bloqueado'] = False
                if self.contador_fluxos % 100 == 0:
                    self._mostrar_normal_fluxo(flow, fluxo_info)
            
            if self.callback:
                self.callback(fluxo_info)
            
            self.ultimos_fluxos.append(fluxo_info)
            
            if self.contador_fluxos % 100 == 0:
                self._mostrar_estatisticas()
                
        except Exception as e:
            print(f"❌ Erro ao processar fluxo: {e}")
    
    def _get_protocol_name(self, proto_num):
        """Converte número do protocolo para nome"""
        if proto_num == 6:
            return "TCP"
        elif proto_num == 17:
            return "UDP"
        elif proto_num == 1:
            return "ICMP"
        else:
            return f"OUTRO({proto_num})"
    
    def _mostrar_alerta_fluxo(self, flow, fluxo_info):
        """Mostra alerta de anomalia para fluxo"""
        cor_vermelho = '\033[91m'
        cor_amarelo = '\033[93m'
        cor_azul = '\033[94m'
        cor_reset = '\033[0m'
        
        interface_info = f" [📡 {fluxo_info['interface']}]" if fluxo_info['interface'] != "Desconhecida" else ""
        
        # Mostrar tipo de ataque se disponível
        tipo_info = f" [{fluxo_info['tipo_ataque']}]" if fluxo_info['tipo_ataque'] else ""
        
        if fluxo_info['bloqueado']:
            print(f"{cor_amarelo}🔒 BLOQUEADO #{fluxo_info['contador']}{interface_info}{tipo_info} [{fluxo_info['protocolo']}]{cor_reset}")
        else:
            print(f"{cor_vermelho}⚠️ ANOMALIA #{fluxo_info['contador']}{interface_info}{tipo_info} [{fluxo_info['protocolo']}]{cor_reset}")
        
        print(f"   IP: {flow.src_ip}:{flow.src_port} → {flow.dst_ip}:{flow.dst_port}")
        print(f"   Duração: {fluxo_info['duration']:.3f}s | Pacotes: {flow.total_packets} | Bytes: {flow.total_bytes}")
        print(f"   Score: {fluxo_info['score']:.4f}")
        
        # Mostrar explicação
        if fluxo_info.get('explicacao') and fluxo_info['explicacao'].get('contribuicoes'):
            print(f"   📊 Principais fatores:")
            for c in fluxo_info['explicacao']['contribuicoes'][:3]:
                print(f"      - {c['feature']}: {c['importance']:.2%}")
        
        if flow.src_ip in self.contagem_ips:
            print(f"   Anomalias deste IP: {self.contagem_ips[flow.src_ip]}")
    
    def _mostrar_normal_fluxo(self, flow, fluxo_info):
        """Mostra fluxo normal (resumido)"""
        interface_info = f" [📡 {fluxo_info['interface']}]" if fluxo_info['interface'] != "Desconhecida" else ""
        print(f"✅ Normal #{fluxo_info['contador']}{interface_info}: {flow.src_ip}:{flow.src_port} → {flow.dst_ip}:{flow.dst_port} [{fluxo_info['protocolo']}]")
    
    def _mostrar_estatisticas(self):
        """Mostra estatísticas a cada 100 fluxos"""
        taxa = (self.anomalias / self.contador_fluxos) * 100 if self.contador_fluxos > 0 else 0
        
        print("\n" + "="*80)
        print(f"📊 ESTATÍSTICAS ({self.contador_fluxos} fluxos)")
        print("="*80)
        print(f"📦 Total: {self.contador_fluxos}")
        print(f"✅ Normais: {self.contador_fluxos - self.anomalias}")
        print(f"⚠️ Anomalias: {self.anomalias} ({taxa:.2f}%)")
        print(f"🔒 Bloqueios: {self.bloqueios}")
        print(f"🚫 IPs bloqueados: {len(self.ips_bloqueados)}")
        print(f"✅ IPs na whitelist: {len(self.whitelist)}")
        
        print(f"\n📡 INTERFACES DE REDE:")
        print(f"   Total de interfaces: {len(self.interface_list)}")
        print(f"   🟢 ATIVAS ({len(self.interface_ativas)}):")
        for iface in sorted(self.interface_ativas):
            friendly = self.get_friendly_interface_name(iface)
            print(f"      - {friendly}: {self.interface_stats[iface]} fluxos")
        
        if self.interface_inativas:
            print(f"   🔴 INATIVAS ({len(self.interface_inativas)}):")
            for iface in sorted(self.interface_inativas):
                friendly = self.get_friendly_interface_name(iface)
                print(f"      - {friendly}")
        else:
            print(f"   ✅ Todas as interfaces geraram tráfego!")
        
        if self.ips_bloqueados:
            print("\n🚫 IPs BLOQUEADOS:")
            for ip in list(self.ips_bloqueados)[:5]:
                print(f"   - {ip} ({self.contagem_ips[ip]} anomalias)")
        
        print("="*80 + "\n")
    
    def _packet_handler(self, pkt, iface):
        """
        Handler de pacotes - agrupa em fluxos
        """
        if not self.running:
            return
        
        # Atualizar estatísticas de interface
        if iface:
            self.interface_stats[iface] += 1
            self.interface_ativas.add(iface)
            if iface in self.interface_inativas:
                self.interface_inativas.remove(iface)
        
        # Processar pacote no extrator de fluxos
        flow = self.flow_extractor.process_packet(pkt, time.time())
        
        # Se um fluxo foi completado, processá-lo
        completed_flows = self.flow_extractor.get_completed_flows()
        for completed_flow in completed_flows:
            self.processar_fluxo(completed_flow, iface)
    
    def _sniff_thread_func(self, iface):
        """Função executada na thread para capturar pacotes"""
        try:
            friendly = self.get_friendly_interface_name(iface)
            print(f"   🔵 Iniciada captura em: {friendly}")
            sniff(
                iface=iface, 
                prn=lambda pkt: self._packet_handler(pkt, iface),
                filter=self.filtro,
                store=False,
                stop_filter=lambda x: not self.running
            )
        except Exception as e:
            if self.running:
                print(f"   ❌ Erro em {friendly}: {e}")
    
    def iniciar(self):
        print("\n" + "="*80)
        print("🚀 IPS EM TEMPO REAL (ANÁLISE POR FLUXO + DETECÇÃO DE ATAQUES)")
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
        print(f"🔴 Pressiona CTRL+C para parar")
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
        
        # Processar fluxos restantes
        remaining_flows = self.flow_extractor.get_completed_flows()
        for flow in remaining_flows:
            self.processar_fluxo(flow)
        
        print(f"📦 Total fluxos: {self.contador_fluxos}")
        print(f"✅ Normais: {self.contador_fluxos - self.anomalias}")
        print(f"⚠️ Anomalias: {self.anomalias}")
        print(f"🔒 Bloqueios realizados: {self.bloqueios}")
        print(f"🚫 IPs bloqueados: {len(self.ips_bloqueados)}")
        print(f"✅ IPs na whitelist: {len(self.whitelist)}")
        
        if self.contador_fluxos > 0:
            taxa = (self.anomalias / self.contador_fluxos) * 100
            print(f"\n📊 Taxa de anomalias: {taxa:.2f}%")
        
        if self.ips_bloqueados:
            print("\n🚫 IPs BLOQUEADOS:")
            for ip in self.ips_bloqueados:
                print(f"   - {ip} ({self.contagem_ips[ip]} anomalias)")
        
        self.salvar_log()
        print(f"\n📁 Log guardado em: {self.log_file}")
        
        if self.ips_bloqueados:
            print("\n" + "="*80)
            resposta = input("❓ Deseja LIMPAR (remover) todos os IPs bloqueados? (s/n): ").strip().lower()
            if resposta == 's':
                self.limpar_todas_regras()
            else:
                print("🔒 Regras de bloqueio mantidas no firewall")
                print("📋 IPs continuam bloqueados (podes desbloquear manualmente depois)")
        
        print("="*80)
        print("✅ IPS parado com sucesso!")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='IPS com análise por fluxo e deteção de ataques')
    parser.add_argument('--interface', '-i', 
                       help='Interface de rede (ex: "Wi-Fi", "Ethernet") - Se não especificar, captura em TODAS')
    parser.add_argument('--modelo', '-m', help='Caminho do modelo .pkl')
    parser.add_argument('--no-bloqueio', action='store_true', help='Desativa bloqueio')
    parser.add_argument('--filtro', '-f', help='Filtro BPF (ex: "icmp", "tcp port 80", "udp port 53")')
    
    args = parser.parse_args()
    
    print("="*80)
    print("🔧 SISTEMA IPS COM ANÁLISE POR FLUXO E DETECÇÃO DE ATAQUES")
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