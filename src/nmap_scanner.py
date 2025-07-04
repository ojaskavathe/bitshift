# nmap_scanner.py

import nmap3
import socket
import fcntl
import struct
import json

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
    results = nmap.nmap_portscan_only(ip_range)
    
    # Remove non-IP keys
    for key in ["runtime", "stats", "task_results"]:
        results.pop(key, None)

    # Filter active hosts
    active_hosts = {}
    for ip, info in results.items():
        if "state" in info and info["state"].get("state") == "up":
            if "hostname" in info and info["hostname"]:
                hostname = info["hostname"][0].get("name", "Unknown")
            else:
                hostname = "Unknown"
            active_hosts[ip] = {
                "hostname": hostname
            }

    return active_hosts

def scan_open_ports(ip_range=None):
    ip_range = get_network_ip() + "/" + subnet_mask
    print(ip_range)
    nmap = nmap3.Nmap() 
    scan_results = nmap.scan_top_ports(ip_range)

    open_ports_info = {}

    for ip, data in scan_results.items():
        if isinstance(data, dict):
            open_ports = []

            for port_info in data.get('ports', []):
                if port_info['state'] == 'open':
                    open_ports.append({
                        'port': port_info['portid'],
                        'name': port_info['service']['name']
                    })

            if open_ports:
                open_ports_info[ip] = open_ports
        else:
            print(f"Warning: Scan result for IP {ip} is in an unexpected format.")

    return open_ports_info
