from flask import Flask, request, jsonify
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Configuration
WINDOW_SIZE = 10
THRESHOLD = 0.15

# Initialize BP history with default values
bp_data = pd.DataFrame([{
    'timestamp': datetime.now(),
    'systolic_bp': 120,
    'diastolic_bp': 70
} for _ in range(WINDOW_SIZE)])

@app.route("/")
def home():
    return "🩺 Real-time BP Alert API is live!"

@app.route("/bp_alert", methods=["POST"])
def bp_alert():
    global bp_data

    data = request.get_json()
    user_sys = data.get("systolic_bp")
    user_dia = data.get("diastolic_bp")

    # Add new reading
    new_row = pd.DataFrame([{
        'timestamp': datetime.now(),
        'systolic_bp': user_sys,
        'diastolic_bp': user_dia
    }])
    bp_data = pd.concat([bp_data, new_row], ignore_index=True)

    # Get last N rows
    recent_data = bp_data.tail(WINDOW_SIZE)
    mean_sys = recent_data['systolic_bp'].mean()
    mean_dia = recent_data['diastolic_bp'].mean()

    dev_sys = abs(user_sys - mean_sys) / (mean_sys + 1e-5)
    dev_dia = abs(user_dia - mean_dia) / (mean_dia + 1e-5)

    alert = dev_sys > THRESHOLD or dev_dia > THRESHOLD

    return jsonify({
        "mean_systolic": round(mean_sys, 2),
        "mean_diastolic": round(mean_dia, 2),
        "systolic_deviation": round(dev_sys * 100, 2),
        "diastolic_deviation": round(dev_dia * 100, 2),
        "alert": alert
    })
