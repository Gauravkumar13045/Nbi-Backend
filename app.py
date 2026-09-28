from flask import Flask
from routes.auth import auth_bp
from flask_cors import CORS
import os
from dotenv import load_dotenv
from extensions import db, mail
from models import user
from models import otp
from routes.protected import protected_bp
from routes.account import account_bp

load_dotenv()

app = Flask(__name__)
allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

CORS(
    app,
    resources={r"/*": {"origins": allowed_origins}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 1800,
}

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

if not app.config["JWT_SECRET_KEY"]:
    raise RuntimeError("JWT_SECRET_KEY is missing from .env")


db.init_app(app)
mail.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(protected_bp, url_prefix="/api")
app.register_blueprint(account_bp, url_prefix="/api")

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return "Backend is Running sucessfully 🚀🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
