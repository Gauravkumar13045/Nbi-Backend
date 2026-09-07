from flask import request, jsonify, Blueprint
import re
from models.user import User
from extensions import db, mail
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from models.otp import Otp
from routes.otp_sender import generate_and_send_otp

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

    existing_user = User.query.filter(
        (User.email == email) | (User.username == username) | (User.mobile == mobile)
    ).first()

    if existing_user:

        if existing_user.status == "active":

            if existing_user.email == email:
                return (
                    jsonify({"error": "Email already registered", "field": "email"}),
                    400,
                )

            if existing_user.username == username:
                return (
                    jsonify({"error": "Username already exists", "field": "username"}),
                    400,
                )

            if existing_user.mobile == mobile:
                return (
                    jsonify(
                        {"error": "Mobile number already registered", "field": "mobile"}
                    ),
                    400,
                )

        elif existing_user.status == "pending":

            generate_and_send_otp(existing_user, existing_user.email)

        db.session.commit()

        return (
            jsonify(
                {
                    "message": "OTP sent to your email!",
                    "email": existing_user.email,
                }
            ),
            200,
        )

    password_hash = generate_password_hash(password)

    new_user = User(
        username=username, email=email, mobile=mobile, password_hash=password_hash
    )

    db.session.add(new_user)
    db.session.flush()

    generate_and_send_otp(new_user, email)

    db.session.commit()

    return (
        jsonify(
            {
                "message": "OTP sent to your email!",
                "email": email,
                "user": {"username": username, "email": email, "mobile": mobile},
            }
        ),
        201,
    )


@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    otp_data = request.get_json(silent=True)
    if not otp_data:
        return jsonify({"error": "Invalid JSON data"}), 400

    otp = otp_data.get("otp")
    email = otp_data.get("email")

    if not email or not otp:
        return jsonify({"error": "Email and OTP are required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    otp_record = Otp.query.filter_by(user_id=user.id).first()

    if not otp_record:
        return jsonify({"error": "OTP not found. Please signup again"}), 404

    if not str(otp).isdigit() or len(str(otp)) != 6:
        return jsonify({"error": "Enter a valid 6 digit OTP"}), 400

    if datetime.utcnow() > otp_record.expires_at:
        db.session.delete(otp_record)
        db.session.commit()
        return jsonify({"error": "OTP Expired: Please Resend New OTP"}), 400

    if not check_password_hash(otp_record.otp_hash, str(otp)):
        return jsonify({"error": "Invalid OTP. Please try again"}), 400

    user.status = "active"

    db.session.delete(otp_record)

    db.session.commit()

    return jsonify({"message": "OTP verified successfully. Account activated!"}), 200
