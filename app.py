# app.py

from flask import Flask, render_template, request, jsonify
from rfid_handler import rfid_handler
from nmap_scanner import get_local_ip, get_network_ip, scan_network
from arpspoof.arpspoof import Spoofer

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

#RFID
@app.route('/start_scan', methods=['POST'])
def start_scan():
    rfid_handler.start_scanning()
    return jsonify({"status": "success", "message": "Started scanning."})

@app.route('/stop_scan', methods=['POST'])
def stop_scan():
    rfid_handler.stop_scanning()
    return jsonify({"status": "success", "message": "Stopped scanning."})

@app.route('/get_scan', methods=['GET'])
def get_scan():
    latest = rfid_handler.get_latest_scan()
    if latest:
        return jsonify({"status": "success", "data": latest})
    else:
        return jsonify({"status": "no_data", "message": "No data scanned yet."})

@app.route('/write', methods=['POST'])
def write_card():
    data_to_write = request.json.get("data")
    result = rfid_handler.authenticate_and_write(data_to_write, 4)
    if "successfully" in result:
        return jsonify({"status": "success", "message": result})
    else:
        return jsonify({"status": "error", "message": result})

# NMAP
@app.route('/network_scan')
def network_scan_page():
    return render_template('network_scan.html')

@app.route('/get_ip_info', methods=['GET'])
def get_ip_info():
    local_ip = get_local_ip()
    network_ip = get_network_ip()
    return jsonify({"local_ip": local_ip, "network_ip": network_ip})

@app.route('/scan_network', methods=['POST'])
def scan_network_route():
    results = scan_network()
    return jsonify({"status": "success", "data": results})

# Spoof
@app.route('/arp_spoofing')
def arp_spoofing():
    return render_template('arp_spoofing.html')

@app.route('/start_arp_spoofing', methods=['POST'])
def start_arp_spoofing():
    data = request.json
    target_ip = data['target_ip']
    attacker_mac = data['attacker_mac']
    gateway_mac = data['gateway_mac']
    gateway_ip = data['gateway_ip']
    target_mac = data['target_mac']
    interval = data['interval']
    disassociate = data['disassociate']
    ipforward = data['ipforward']
    
    # Assuming 'eth0' as the network interface, change as needed
    spoofer = Spoofer(
        interface='wlan0',
        attackermac=attacker_mac,
        gatewaymac=gateway_mac,
        gatewayip=gateway_ip,
        targetmac=target_mac,
        targetip=target_ip,
        interval=interval,
        disassociate=disassociate,
        ipforward=ipforward
    )
    
    try:
        spoofer.execute()
        return jsonify({"status": "success", "message": f"ARP spoofing started for IP {target_ip}."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
