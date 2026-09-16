from functools import wraps
import jwt
from flask import request, jsonify, current_app
from models.user import User


def token_required(original_function):

    @wraps(original_function)
    def wrapper(*args, **kwargs):

        token = request.cookies.get("access_token")

        if not token:
            return jsonify({"error": "Authorization token is missing"}), 401

        parts = token.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"error": "Invalid Authorization header format"}), 401

        token = parts[1]

        try:

            decoded_token = jwt.decode(
                token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"]
            )

            user_id = decoded_token.get("sub")

            if not user_id:
                return jsonify({"error": "Invalid token payload"}), 401

            current_user = User.query.get(int(user_id))

            if not current_user:
                return jsonify({"error": "User associated with token not found"}), 401

            return original_function(current_user, *args, **kwargs)

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401

        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

    return wrapper
