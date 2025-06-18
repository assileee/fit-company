import logging
import os
import sys
from flask import Flask, request, jsonify
from pydantic import ValidationError

from .models_dto import UserSchema
from .database import init_db, db_session
from .models_db import UserModel
from .services.user_service import create_user as create_user_service
from .blueprints import user_bp, auth_bp, workout_bp
from .blueprints.billing_blueprint import billing_bp 

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

# Force stdout to be unbuffered
sys.stdout.reconfigure(line_buffering=True)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/')
app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(workout_bp, url_prefix='/workouts')
app.register_blueprint(billing_bp, url_prefix='/')


BOOTSTRAP_KEY = os.environ.get("BOOTSTRAP_KEY", "bootstrap-secret-key")

@app.route("/health")
def health():
    return {"status": "UP"}

@app.route("/bootstrap/admin", methods=["POST"])
def create_bootstrap_admin():
    try:
        bootstrap_key = request.headers.get('X-Bootstrap-Key')
        if not bootstrap_key or bootstrap_key != BOOTSTRAP_KEY:
            return jsonify({"error": "Invalid bootstrap key"}), 401

        db = db_session()
        admin_exists = db.query(UserModel).filter(UserModel.role == "admin").first() is not None
        db.close()

        if admin_exists:
            return jsonify({"error": "Admin user already exists"}), 409

        admin_data = request.get_json()
        admin_data["role"] = "admin"
        admin_user = UserSchema.model_validate(admin_data)
        created_admin = create_user_service(admin_user)

        return jsonify(created_admin.model_dump()), 201

    except ValidationError as e:
        return jsonify({"error": "Invalid admin data", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "Error creating admin", "details": str(e)}), 500

# 🔔 New route to handle premium membership upgrade
@app.route("/internal/users/upgrade", methods=["POST"])
def upgrade_user_to_premium():
    try:
        user_email = request.json.get("email")
        db = db_session()
        user = db.query(UserModel).filter_by(email=user_email).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        user.fitness_goal = "premium"  # Or you can add a separate 'membership' column in the model
        db.commit()
        return jsonify({"message": f"User {user_email} upgraded to premium"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

def run_app():
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    run_app()
