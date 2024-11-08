# nmap_scanner.py

import nmap3
import socket
import fcntl
import struct

interface = "wlan0"
subnet_mask = "24"

def get_local_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packed_iface = struct.pack('256s', interface.encode('utf_8'))
    packed_addr = fcntl.ioctl(sock.fileno(), 0x8915, packed_iface)[20:24]
    return socket.inet_ntoa(packed_addr)

def get_network_ip():
    ip_addr = get_local_ip()
    return ip_addr[:ip_addr.rfind(".")] + ".0"

def scan_network(ip_range=None):
    ip_range = ip_range or get_network_ip() + "/" + subnet_mask
    nmap = nmap3.NmapHostDiscovery()
    results = nmap.nmap_no_portscan(ip_range)
    
    # Remove non-IP keys
    for key in ["runtime", "stats", "task_results"]:
        results.pop(key, None)

    # Filter active hosts
    active_hosts = {}
    for ip, info in results.items():
        if info["state"]["state"] == "up":
            hostname = None
            if "hostname" in info and len(info["hostname"]) > 0:
                hostname = info["hostname"][0]["name"]
            active_hosts[ip] = {
                "hostname": hostname if hostname else "Unknown"
            }
    
    return active_hosts
