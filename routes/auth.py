from flask import request, jsonify, Blueprint
import re
from models.user import User
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    username = data.get("username")
    email = data.get("email")
    mobile = data.get("mobile")
    password = data.get("password")
    confirm_password = data.get("confirmPassword")

    password_pattern = (
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    )
    email_pattern = r"^[a-zA-Z0-9._%+-]+" r"@[a-zA-Z0-9.-]+" r"\.[a-zA-Z]{2,}$"
    mobile_pattern = r"^[6-9]\d{9}$"
    username_pattern = r"(?=.{3,30}$)[A-Za-z0-9_]+(?: [A-Za-z0-9_]+)*"

    if not username or not email or not mobile or not password or not confirm_password:
        return jsonify({"error": "All fields required"}), 400

    if not re.fullmatch(username_pattern, username):
        return jsonify({"error": "Invalid username"}), 400
    if password != confirm_password:
        return jsonify({"error": "Password not matched"}), 400
    if not re.match(password_pattern, password):
        return jsonify({"error": "Weak Password"}), 400
    if not re.match(email_pattern, email):
        return jsonify({"error": "Invalid Email Address "}), 400
    if not re.fullmatch(mobile_pattern, mobile):
        return jsonify({"error": "Invalid Mobile Number"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists", "field": "username"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists", "field": "email"}), 400

    if User.query.filter_by(mobile=mobile).first():
        return (
            jsonify({"error": "Mobile number already exists", "field": "mobile"}),
            400,
        )

    password_hash = generate_password_hash(password)

    new_user = User(
        username=username, email=email, mobile=mobile, password_hash=password_hash
    )

    db.session.add(new_user)
    db.session.commit()
    print("Data Received")

    return (
        jsonify(
            {
                "message": "Signup validation successful",
                "user": {"username": username, "email": email, "mobile": mobile},
            }
        ),
        201,
    )
