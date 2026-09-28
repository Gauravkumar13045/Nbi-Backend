from datetime import datetime
from extensions import db


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    account_number = db.Column(db.String(20), unique=True, nullable=False)

    account_type = db.Column(db.String(30), nullable=False)

    balance = db.Column(db.Numeric(15, 2), nullable=False, default=0)

    currency = db.Column(db.String(3), nullable=False, default="INR")

    account_status = db.Column(db.String(20), nullable=False, default="active")

    branch_code = db.Column(db.String(20), nullable=False)

    ifsc_code = db.Column(db.String(20), nullable=False)

    opened_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    last_transaction_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    closed_at = db.Column(db.DateTime, nullable=True)
