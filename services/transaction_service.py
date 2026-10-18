from models.transaction import Transaction
from models.user import User
from models.account import Account
from sqlalchemy import or_


def get_user_transactions(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return None

    accounts = Account.query.filter_by(user_id=user.id).all()
    if not accounts:
        return []

    account_ids = [account.id for account in accounts]

    transactions = (
        Transaction.query.filter(
            or_(
                Transaction.sender_account_id.in_(account_ids),
                Transaction.receiver_account_id.in_(account_ids),
            )
        )
        .order_by(Transaction.created_at.desc())
        .limit(5)
        .all()
    )
    return transactions
