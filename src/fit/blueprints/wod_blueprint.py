from flask import Blueprint, jsonify
from ..services.rabbitmq_service import rabbitmq_service
from ..services.user_service import get_all_users

wod_bp = Blueprint('wod_bp', __name__)

@wod_bp.route("/generate", methods=["POST"])
def generate_wods_for_all_users():
    users = get_all_users()
    count = 0

    for user in users:
        message = {
            "user_email": user.email,
            "exercise_ids": []  # Empty for now
        }
        if rabbitmq_service.publish_message(message):
            count += 1

    return jsonify({
        "status": "success",
        "queued_messages": count
    }), 200
