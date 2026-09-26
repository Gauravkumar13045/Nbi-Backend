from flask import request, jsonify, Blueprint, current_app, make_response
import re
from models.user import User
from extensions import db, mail
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
from models.otp import Otp
from routes.otp_sender import generate_and_send_otp
import jwt

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


@auth_bp.route("/resend-otp", methods=["POST"])
def resend_otp():
    responce = request.get_json(silent=True)
    if not responce:
        return jsonify({"error": "Invalid JSON data"}), 400

    email = responce.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "User not Found"}), 400

    if user.status == "active":
        return jsonify({"error": "User already Existed"})

    generate_and_send_otp(user=user, email=email)

    db.session.commit()

    return (
        jsonify(
            {
                "message": "OTP sent to your email!",
                "email": email,
            }
        ),
        200,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    Login_data = request.get_json(silent=True)

    if not Login_data:
        return jsonify({"error": "Invalid Login Data"}), 400

    email = Login_data.get("email")
    password = Login_data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and Password required"}), 400

    password_pattern = (
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    )
    email_pattern = r"^[a-zA-Z0-9._%+-]+" r"@[a-zA-Z0-9.-]+" r"\.[a-zA-Z]{2,}$"
    mobile_pattern = r"^[6-9]\d{9}$"

    if not (re.fullmatch(email_pattern, email) or re.fullmatch(mobile_pattern, email)):
        return (
            jsonify({"error": "Invalid Email or Mobile Number ", "field": "email"}),
            400,
        )
    if not re.fullmatch(password_pattern, password):
        return jsonify({"error": "Invalid Password"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User Not Found"}), 404

    if user.status == "active":

        password_correct = check_password_hash(user.password_hash, password)

        if not password_correct:
            return jsonify({"error": "Invalid Password !! Try again"}), 401

        generate_and_send_otp(user=user, email=email)
        db.session.commit()
        return jsonify({"message": "OTP sent to your email!", "email": email}), 200

    if user.status == "pending":
        return jsonify({"error": "Account Not Activated Yet"}), 403


@auth_bp.route("/verify-login-otp", methods=["POST"])
def verify_login_otp():

    response = request.get_json(silent=True)

    if not response:
        return jsonify({"error": "Invalid Json"}), 400

    email = response.get("email")
    otp = response.get("otp")

    if not email or not otp:
        return jsonify({"error": "Email and Otp Required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "User Not Found"}), 404

    if user.status == "pending":
        return jsonify({"error": "Account Not Activated !! Please verify again"}), 400

    otp_record = Otp.query.filter_by(user_id=user.id).first()

    if not otp_record:
        return jsonify({"error": "OTP Not Found !! Please request a new OTP"}), 404

    if not str(otp).isdigit() or len(str(otp)) != 6:
        return jsonify({"error": "Enter a valid 6 digit OTP"}), 400

    if datetime.utcnow() > otp_record.expires_at:

        db.session.delete(otp_record)
        db.session.commit()

        return jsonify({"error": "OTP Expired !! Please request a new OTP"}), 400

    if not check_password_hash(otp_record.otp_hash, str(otp)):
        return jsonify({"error": "Invalid OTP !! Try again"}), 400

    access_token = jwt.encode(
        {
            "sub": str(user.id),
            "email": user.email,
            "type": "access",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        },
        current_app.config["JWT_SECRET_KEY"],
        algorithm="HS256",
    )

    db.session.delete(otp_record)
    db.session.commit()

    response = make_response(
        jsonify(
            {
                "message": "Login Successful",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            }
        ),
        200,
    )

    response.set_cookie(
        "access_token",
        access_token,
        samesite="Lax",
        httponly=True,
        secure=False,
        max_age=900,
    )
    return response


@auth_bp.route("/logout", methods=["POST"])
def logout():

    response = make_response(jsonify({"message": "Logout successful"}), 200)

    response.delete_cookie("access_token", samesite="Lax")

    return response
