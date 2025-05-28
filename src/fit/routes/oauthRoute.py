from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError
from ..models_dto import LoginSchema, TokenSchema
from ..services.auth_service import authenticate_user, create_access_token
import datetime

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/oauth/token", methods=["POST"])
def login():
    try:
        content_type = request.headers.get('Content-Type', '')
        if 'application/x-www-form-urlencoded' in content_type:
            login_data = {
                "email": request.form.get("username"),
                "password": request.form.get("password")
            }
        else:
            login_data = request.get_json()

        login_schema = LoginSchema(**login_data)  # Fixed for Pydantic v1

        user = authenticate_user(login_schema.email, login_schema.password)
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        access_token_expires = datetime.timedelta(minutes=30)
        token_data = {
            "sub": user.email,
            "name": user.name,
            "role": user.role,
            "iss": "fit-api",
            "iat": datetime.datetime.now(datetime.timezone.utc),  # Fixed UTC timezone
        }

        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )

        token = TokenSchema(
            access_token=access_token,
            token_type="bearer"
        )

        response_data = token.dict()  # Fixed for Pydantic v1
        response_data["onboarded"] = user.onboarded

        return jsonify(response_data), 200

    except ValidationError as e:
        return jsonify({"error": "Invalid login data", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "Error logging in", "details": str(e)}), 500
