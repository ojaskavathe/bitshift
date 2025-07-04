import json
import nmap3

nmap = nmap3.Nmap()
scan_results = nmap.scan_top_ports("192.168.137.0/24")

for ip, data in scan_results.items():
    if not isinstance(data, dict):
        print("hehe")
