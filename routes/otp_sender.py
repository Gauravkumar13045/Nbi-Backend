import secrets
from datetime import datetime, timedelta

from flask_mail import Message
from werkzeug.security import generate_password_hash

from extensions import db, mail
from models.otp import Otp


def generate_and_send_otp(user, email):

    Otp.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    db.session.flush()

    otp = secrets.randbelow(900000) + 100000

    otp_hash = generate_password_hash(str(otp))

    expires_at = datetime.utcnow() + timedelta(minutes=5)

    otp_record = Otp(user_id=user.id, otp_hash=otp_hash, expires_at=expires_at)

    db.session.add(otp_record)

    msg = Message(subject="NBI Bank - Verify Your Email Address", recipients=[email])

    msg.html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
    </head>

    <body style="
        margin:0;
        padding:0;
        background-color:white;
        font-family:Arial, sans-serif;
    ">

        <div style="
            max-width:600px;
            margin:40px auto;
            background:#ffffff;
            border-radius:12px;
            overflow:hidden;
            box-shadow:0 4px 20px rgba(0,0,0,0.9);
        ">

            <!-- Header -->
            <div style="
                background:#d8b45c;
                padding:30px;
                text-align:center;
                color:black;
            ">

                <table cellpadding="0" cellspacing="0" style="margin:0 auto;">
                    <tr>
                        <td>

                            <img
                                src="https://res.cloudinary.com/dug0cvjfs/image/upload/v1788261391/cc75a133-3c03-4a93-9fe1-af14d9203462.png"
                                height="70"
                                alt="NBI Logo"
                            />

                        </td>
                    </tr>
                </table>

            </div>


            <!-- Content -->
            <div style="
                padding:40px 35px;
                text-align:center;
            ">

                <h2 style="
                    color:#222;
                    margin-top:0;
                ">
                    Verify Your Email Address
                </h2>


                <p style="
                    color:#666;
                    font-size:16px;
                    line-height:1.6;
                ">
                    Welcome to NBI Bank!
                    <br>
                    Use the verification code below to complete
                    your account registration.
                </p>


                <!-- OTP Box -->
                <div style="
                    background:#f1f5ff;
                    border:2px dashed #0b3d91;
                    border-radius:10px;
                    padding:20px;
                    margin:30px 0;
                ">

                    <p style="
                        margin:0 0 8px;
                        color:#666;
                        font-size:14px;
                    ">
                        YOUR VERIFICATION CODE
                    </p>


                    <div style="
                        font-size:32px;
                        font-weight:bold;
                        letter-spacing:8px;
                        color:#0b3d91;
                    ">
                        {otp}
                    </div>

                </div>


                <!-- Expiry -->
                <p style="
                    color:#555;
                    font-size:15px;
                ">
                    ⏱ This code will expire in
                    <strong>5 minutes</strong>.
                </p>


                <!-- Security Warning -->
                <div style="
                    background:#fff8e6;
                    border-left:4px solid #f0a500;
                    padding:15px;
                    margin-top:25px;
                    text-align:left;
                    border-radius:6px;
                ">

                    <strong style="color:#8a5a00;">
                        Security Notice
                    </strong>


                    <p style="
                        margin:8px 0 0;
                        color:#666;
                        font-size:14px;
                        line-height:1.5;
                    ">
                        Never share your OTP with anyone.
                        NBI Bank will never ask for your OTP,
                        password, or banking credentials.
                    </p>

                </div>

            </div>


            <!-- Footer -->
            <div style="
                background:#f4f6f8;
                padding:20px;
                text-align:center;
                color:#888;
                font-size:13px;
            ">

                <strong style="color:#555;">
                    NBI Bank Security Team
                </strong>

                <p style="margin:8px 0 0;">
                    This is an automated security message.
                    Please do not reply to this email.
                </p>

            </div>

        </div>

    </body>
    </html>
    """

    mail.send(msg)

    return otp_record
