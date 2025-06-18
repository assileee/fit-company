from flask import Blueprint, jsonify, request, g, current_app
import requests
import os

from ..services.auth_service import jwt_required

billing_bp = Blueprint('billing', __name__)

BILLING_SERVICE_CHECKOUT_ENDPOINT = os.getenv("BILLING_URL", "http://billing:5003") + "/billing/checkout"

@billing_bp.route("/billing/upgrade", methods=["POST"])
@jwt_required
def upgrade_membership():
    try:
        user_email = g.user_email
        current_app.logger.debug(f"Processing upgrade for user: {user_email}")

        # Simulate payment success
        payment_success = True  # Always succeeds for now

        if payment_success:
            # Notify monolith to upgrade membership
            response = requests.post(BILLING_SERVICE_CHECKOUT_ENDPOINT, json={"email": user_email})

            if response.status_code == 200:
                current_app.logger.info(f"User {user_email} upgraded to premium")
                return jsonify({"message": "Membership upgraded to premium"}), 200
            else:
                current_app.logger.error(f"Failed to upgrade user in monolith: {response.text}")
                return jsonify({"error": "Failed to upgrade user"}), 502

        return jsonify({"error": "Payment failed"}), 402

    except Exception as e:
        current_app.logger.error(f"Error during billing upgrade: {str(e)}")
        return jsonify({"error": str(e)}), 500
