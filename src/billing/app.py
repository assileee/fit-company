from flask import Flask, jsonify, request
import os
import requests

app = Flask(__name__)

MONOLITH_URL = os.getenv("MONOLITH_URL", "http://monolith:5000")

fake_payment_db = {}

@app.route('/billing/checkout', methods=['POST'])
def checkout():
    user_email = request.json.get('email')
    if not user_email:
        return jsonify({"error": "Email is required"}), 400

    fake_payment_db[user_email] = 'pending'
    
    # Simulate successful payment immediately
    fake_payment_db[user_email] = 'paid'

    # Call monolith to upgrade user
    try:
        response = requests.post(
            f"{MONOLITH_URL}/internal/users/upgrade",
            json={"email": user_email},
            timeout=5
        )
        monolith_status = response.status_code
        monolith_response = response.json()
        upgrade_status = "success" if monolith_status == 200 else "failed"
    except Exception as e:
        monolith_response = {"error": str(e)}
        upgrade_status = "failed"

    return jsonify({
        "status": "paid",
        "monolith_update": upgrade_status,
        "monolith_response": monolith_response
    }), 200

@app.route('/billing/status/<email>', methods=['GET'])
def check_status(email):
    status = fake_payment_db.get(email, 'not_found')
    return jsonify({"email": email, "status": status}), 200

def run_app():
    app.run(host="0.0.0.0", port=5003, debug=True)

if __name__ == "__main__":
    run_app()
