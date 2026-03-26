from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import re
import time

app = Flask(__name__)
CORS(app)  # frontend can talk to server

# pattern to extract data from ADB
PATTERN = re.compile(
    r"rssi=(-?\d+)\s+"
    r"rsrp=(-?\d+)\s+"
    r"rsrq=(-?\d+)\s+"
    r"rssnr=(-?\d+)"
)

def get_network_data():
    """Get the latest network data from the phone"""
    try:
        output = subprocess.check_output(
            ["adb", "shell", "dumpsys", "telephony.registry"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        
        for line in output.splitlines():
            if "mSignalStrength=" not in line:
                continue
                
            match = PATTERN.search(line)
            if match:
                rssi, rsrp, rsrq, rssnr = map(int, match.groups())
                return {
                    "rssi": rssi,
                    "rsrp": rsrp,
                    "rsrq": rsrq,
                    "rssnr": rssnr,
                    "timestamp": time.time()
                }
        
        # If no data found
        return {"error": "No signal data found"}
        
    except Exception as e:
        return {"error": str(e)}

@app.route('/api/data')
def get_data():
    """Endpoint for frontend to get network data"""
    data = get_network_data()
    return jsonify(data)

@app.route('/')
def index():
    """Serve the dashboard"""
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)