from flask import Flask
from routes.auth import auth_bp
from flask_cors import CORS
import os
from dotenv import load_dotenv
from extensions import db, mail
from models import user
from models import otp

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")


db.init_app(app)
mail.init_app(app)

app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return "Backend is Running sucessfully 🚀🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
