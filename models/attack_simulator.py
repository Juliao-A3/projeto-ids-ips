"""
IDS/IPS — Simulador de Ataques
================================
Simula ataques na interface loopback para testar o IDS.
Usa Scapy para gerar tráfego real sem precisar de uma segunda máquina.

⚠️  Usar APENAS em ambiente de teste local!

Uso:
    # Testar um ataque específico:
    sudo python attack_simulator.py --attack ddos
    sudo python attack_simulator.py --attack portscan
    sudo python attack_simulator.py --attack slowloris
    sudo python attack_simulator.py --attack ftp_patator
    sudo python attack_simulator.py --attack ssh_patator

    # Testar todos os ataques em sequência:
    sudo python attack_simulator.py --attack all

    # Em paralelo com o IDS (em dois terminais):
    Terminal 1: sudo python ids_realtime.py --interface lo --model best_model.pkl
    Terminal 2: sudo python attack_simulator.py --attack all
"""

import time
import random
import argparse
from scapy.all import (
    IP, TCP, UDP, Raw,
    send, sendp, Ether,
    RandShort, RandIP
)

# ─────────────────────────────────────────────
# Configuração
# ─────────────────────────────────────────────

TARGET_IP   = "127.0.0.1"   # loopback — mesma máquina
IFACE       = "lo"           # interface loopback


# ─────────────────────────────────────────────
# Cores terminal
# ─────────────────────────────────────────────

class Color:
    GREEN  = '\033[92m'
    YELLOW = '\033[93m'
    RED    = '\033[91m'
    BLUE   = '\033[94m'
    BOLD   = '\033[1m'
    RESET  = '\033[0m'

def log(msg, color=Color.BLUE):
    print(f"{color}{msg}{Color.RESET}")


# ─────────────────────────────────────────────
# 1. DDoS — flood de pacotes UDP
# ─────────────────────────────────────────────

def simulate_ddos(packets=1000):
    log("\n[*] Simulando DDoS (UDP Flood)...", Color.RED)
    log(f"    → {packets} pacotes para {TARGET_IP}:80", Color.YELLOW)

    for i in range(packets):
        src_ip = f"10.0.{random.randint(0,255)}.{random.randint(1,254)}"
        pkt = IP(src=src_ip, dst=TARGET_IP) / \
              UDP(sport=RandShort(), dport=80) / \
              Raw(load=b"X" * random.randint(512, 1400))
        send(pkt, verbose=False, iface=IFACE)

        if i % 100 == 0:
            log(f"    → {i}/{packets} pacotes enviados...", Color.YELLOW)

    log("[✓] DDoS concluído!", Color.GREEN)


# ─────────────────────────────────────────────
# 2. PortScan — SYN scan em portas sequenciais
# ─────────────────────────────────────────────

def simulate_portscan(start_port=1, end_port=1024):
    log("\n[*] Simulando PortScan (SYN Scan)...", Color.RED)
    log(f"    → Portas {start_port} a {end_port} em {TARGET_IP}", Color.YELLOW)

    src_ip = "10.0.0.1"
    for port in range(start_port, end_port + 1):
        pkt = IP(src=src_ip, dst=TARGET_IP) / \
              TCP(sport=RandShort(), dport=port, flags="S")
        send(pkt, verbose=False, iface=IFACE)

        if port % 100 == 0:
            log(f"    → Porta {port}/{end_port} escaneada...", Color.YELLOW)

    log("[✓] PortScan concluído!", Color.GREEN)


# ─────────────────────────────────────────────
# 3. DoS Slowloris — conexões TCP lentas
# ─────────────────────────────────────────────

def simulate_slowloris(connections=200, duration=30):
    log("\n[*] Simulando DoS Slowloris...", Color.RED)
    log(f"    → {connections} conexões lentas para {TARGET_IP}:80", Color.YELLOW)
    log(f"    → Duração: {duration} segundos", Color.YELLOW)

    src_ip = "10.0.0.2"
    start  = time.time()
    sent   = 0

    while time.time() - start < duration:
        for _ in range(connections):
            # SYN
            pkt = IP(src=src_ip, dst=TARGET_IP) / \
                  TCP(sport=random.randint(1024, 65535),
                      dport=80, flags="S",
                      window=64240)
            send(pkt, verbose=False, iface=IFACE)
            sent += 1

            # Envia headers HTTP incompletos lentamente
            pkt2 = IP(src=src_ip, dst=TARGET_IP) / \
                   TCP(sport=random.randint(1024, 65535),
                       dport=80, flags="PA") / \
                   Raw(load=b"GET / HTTP/1.1\r\nHost: target\r\n")
            send(pkt2, verbose=False, iface=IFACE)
            sent += 1

        elapsed = time.time() - start
        log(f"    → {sent} pacotes enviados ({elapsed:.0f}s/{duration}s)...", Color.YELLOW)
        time.sleep(2)   # pausa característica do Slowloris

    log("[✓] Slowloris concluído!", Color.GREEN)


# ─────────────────────────────────────────────
# 4. FTP-Patator — brute force FTP (porta 21)
# ─────────────────────────────────────────────

def simulate_ftp_patator(attempts=500):
    log("\n[*] Simulando FTP-Patator (Brute Force FTP)...", Color.RED)
    log(f"    → {attempts} tentativas para {TARGET_IP}:21", Color.YELLOW)

    # Wordlist simulada de credenciais
    users     = ["admin", "root", "ftp", "user", "test", "guest"]
    passwords = ["123456", "password", "admin", "root", "ftp123", "test"]
    src_ip    = "10.0.0.3"

    for i in range(attempts):
        user = random.choice(users)
        pwd  = random.choice(passwords)

        # SYN para estabelecer "conexão"
        sport = random.randint(1024, 65535)
        pkt_syn = IP(src=src_ip, dst=TARGET_IP) / \
                  TCP(sport=sport, dport=21, flags="S")
        send(pkt_syn, verbose=False, iface=IFACE)

        # Envia credenciais (simulado)
        payload = f"USER {user}\r\nPASS {pwd}\r\n".encode()
        pkt_data = IP(src=src_ip, dst=TARGET_IP) / \
                   TCP(sport=sport, dport=21, flags="PA") / \
                   Raw(load=payload)
        send(pkt_data, verbose=False, iface=IFACE)

        # FIN — encerra conexão
        pkt_fin = IP(src=src_ip, dst=TARGET_IP) / \
                  TCP(sport=sport, dport=21, flags="FA")
        send(pkt_fin, verbose=False, iface=IFACE)

        if i % 50 == 0:
            log(f"    → {i}/{attempts} tentativas...", Color.YELLOW)

    log("[✓] FTP-Patator concluído!", Color.GREEN)


# ─────────────────────────────────────────────
# 5. SSH-Patator — brute force SSH (porta 22)
# ─────────────────────────────────────────────

def simulate_ssh_patator(attempts=500):
    log("\n[*] Simulando SSH-Patator (Brute Force SSH)...", Color.RED)
    log(f"    → {attempts} tentativas para {TARGET_IP}:22", Color.YELLOW)

    users     = ["root", "admin", "ubuntu", "ec2-user", "pi", "user"]
    passwords = ["root", "toor", "password", "ubuntu", "raspberry", "123456"]
    src_ip    = "10.0.0.4"

    for i in range(attempts):
        user = random.choice(users)
        pwd  = random.choice(passwords)

        sport = random.randint(1024, 65535)

        # SYN
        pkt_syn = IP(src=src_ip, dst=TARGET_IP) / \
                  TCP(sport=sport, dport=22, flags="S", window=64240)
        send(pkt_syn, verbose=False, iface=IFACE)

        # SSH banner + tentativa de auth (simulado)
        payload = f"SSH-2.0-OpenSSH_8.0\r\nauth {user}:{pwd}\r\n".encode()
        pkt_data = IP(src=src_ip, dst=TARGET_IP) / \
                   TCP(sport=sport, dport=22, flags="PA") / \
                   Raw(load=payload)
        send(pkt_data, verbose=False, iface=IFACE)

        # FIN
        pkt_fin = IP(src=src_ip, dst=TARGET_IP) / \
                  TCP(sport=sport, dport=22, flags="FA")
        send(pkt_fin, verbose=False, iface=IFACE)

        if i % 50 == 0:
            log(f"    → {i}/{attempts} tentativas...", Color.YELLOW)

    log("[✓] SSH-Patator concluído!", Color.GREEN)


# ─────────────────────────────────────────────
# 6. Tráfego BENIGN — para comparação
# ─────────────────────────────────────────────

def simulate_benign(packets=200):
    log("\n[*] Simulando tráfego BENIGN...", Color.GREEN)

    ports = [80, 443, 53, 8080, 8443]
    for i in range(packets):
        src_ip = f"192.168.1.{random.randint(1, 50)}"
        port   = random.choice(ports)

        pkt = IP(src=src_ip, dst=TARGET_IP) / \
              TCP(sport=random.randint(1024, 65535),
                  dport=port, flags="S")
        send(pkt, verbose=False, iface=IFACE)

        pkt2 = IP(src=src_ip, dst=TARGET_IP) / \
               TCP(sport=random.randint(1024, 65535),
                   dport=port, flags="PA") / \
               Raw(load=b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
        send(pkt2, verbose=False, iface=IFACE)

    log("[✓] Tráfego BENIGN concluído!", Color.GREEN)


# ─────────────────────────────────────────────
# Execução
# ─────────────────────────────────────────────

ATTACKS = {
    "ddos":        simulate_ddos,
    "portscan":    simulate_portscan,
    "slowloris":   simulate_slowloris,
    "ftp_patator": simulate_ftp_patator,
    "ssh_patator": simulate_ssh_patator,
    "benign":      simulate_benign,
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulador de ataques para testar o IDS")
    parser.add_argument(
        "--attack", "-a",
        required=True,
        choices=list(ATTACKS.keys()) + ["all"],
        help="Tipo de ataque a simular"
    )
    args = parser.parse_args()

    log("="*55, Color.BOLD)
    log("  IDS/IPS — Simulador de Ataques", Color.BOLD)
    log("  ⚠️  Usar APENAS em ambiente de teste!", Color.YELLOW)
    log("="*55, Color.BOLD)
    log(f"\n  Alvo:      {TARGET_IP}", Color.BLUE)
    log(f"  Interface: {IFACE}\n", Color.BLUE)

    if args.attack == "all":
        log("[*] Iniciando simulação completa...\n", Color.BLUE)
        log("[1/6] Tráfego normal primeiro...", Color.BLUE)
        simulate_benign(200)
        time.sleep(2)

        log("[2/6] DDoS...", Color.BLUE)
        simulate_ddos(500)
        time.sleep(2)

        log("[3/6] PortScan...", Color.BLUE)
        simulate_portscan(1, 512)
        time.sleep(2)

        log("[4/6] Slowloris...", Color.BLUE)
        simulate_slowloris(100, 15)
        time.sleep(2)

        log("[5/6] FTP-Patator...", Color.BLUE)
        simulate_ftp_patator(300)
        time.sleep(2)

        log("[6/6] SSH-Patator...", Color.BLUE)
        simulate_ssh_patator(300)

        log("\n[✓] Simulação completa concluída!", Color.GREEN)
    else:
        ATTACKS[args.attack]()