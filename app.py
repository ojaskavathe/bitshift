# app.py

from flask import Flask, render_template, request, jsonify
from rfid_handler import rfid_handler

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
