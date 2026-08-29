from flask import Flask
from routes.auth import auth_bp
from flask_cors import CORS
import os
from dotenv import load_dotenv
from extensions import db
from models import user

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)

app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return "Backend is Running sucessfully 🚀🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
