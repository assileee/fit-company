from ast import List
from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError
from ..models_dto import Exercise, UserSchema, UserProfileSchema
from ..services.user_service import create_user as create_user_service, get_all_users as get_all_users_service, update_user_profile, get_user_profile
from ..database import db_session
from ..models_db import UserModel
from ..services.auth_service import admin_required, jwt_required

users_bp = Blueprint("users", __name__)

from pydantic import ValidationError

@users_bp.route("/users", methods=["POST"])
@admin_required
def create_user():
    try:
        user_data = request.get_json()
        user = UserSchema.model_validate(user_data)
        created_user = create_user_service(user)
        return jsonify(created_user.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": "Invalid user data", "details": e.errors()}), 400
    except Exception as e:
        # Log exception for debugging
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@users_bp.route("/users", methods=["GET"])
@admin_required
def get_all_users():
    try:
        users = get_all_users_service()
        return jsonify([user.model_dump() for user in users]), 200
    except Exception as e:
        return jsonify({"error": "Error retrieving users", "details": str(e)}), 500

@users_bp.route("/bootstrap/admin", methods=["POST"])
def create_bootstrap_admin():
    try:
        bootstrap_key = request.headers.get('X-Bootstrap-Key')
        BOOTSTRAP_KEY = "bootstrap-secret-key"  # Or import from config/env
        
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

@users_bp.route("/profile/onboarding", methods=["POST"])
@jwt_required
def onboard_user():
    try:
        user_email = g.user_email
        profile_data = request.get_json()
        profile = UserProfileSchema.model_validate(profile_data)
        updated_profile = update_user_profile(user_email, profile)
        if not updated_profile:
            return jsonify({"error": "User not found"}), 404
        return jsonify(updated_profile.model_dump()), 200
    except ValidationError as e:
        return jsonify({"error": "Invalid profile data", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "Error updating profile", "details": str(e)}), 500

@users_bp.route("/profile", methods=["GET"])
@jwt_required
def get_profile():
    try:
        user_email = g.user_email
        profile = get_user_profile(user_email)
        if not profile:
            return jsonify({"error": "User not found"}), 404
        return jsonify(profile.model_dump()), 200
    except Exception as e:
        return jsonify({"error": "Error retrieving profile", "details": str(e)}), 500

