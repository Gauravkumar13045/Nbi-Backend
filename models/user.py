from extensions import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    mobile = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    status = db.Column(db.String(100), nullable=False, unique=False, default="pending")
