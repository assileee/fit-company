from flask import Flask, request, jsonify
from coach_service import generate_wod

app = Flask(__name__)

@app.route("/api/coach/wod", methods=["POST"])
def generate_wod_endpoint():
    try:
        data = request.get_json()
        user_email = data.get("user_email")
        excluded_ids = data.get("excluded_ids", [])

        if not user_email:
            return jsonify({"error": "user_email is required"}), 400

        wod = generate_wod(user_email=user_email, excluded_ids=excluded_ids)
        return jsonify({"exercises": wod}), 200

    except Exception as e:
        return jsonify({"error": "Failed to generate WOD", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
