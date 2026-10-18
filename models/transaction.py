from datetime import datetime

from extensions import db


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)

    sender_account_id = db.Column(
        db.Integer, db.ForeignKey("accounts.id"), nullable=True
    )

    receiver_account_id = db.Column(
        db.Integer, db.ForeignKey("accounts.id"), nullable=True
    )

    amount = db.Column(db.Numeric(15, 2), nullable=False)

    transaction_type = db.Column(db.String(20), nullable=False)

    transaction_status = db.Column(db.String(20), nullable=False, default="completed")

    reference_id = db.Column(db.String(50), unique=True, nullable=False)

    description = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
