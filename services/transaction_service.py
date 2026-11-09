from models.transaction import Transaction
from models.user import User
from models.account import Account
from sqlalchemy import or_
from decimal import Decimal, InvalidOperation
import secrets
from extensions import db


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
        .limit(8)
        .all()
    )
    return transactions


def validate_transactions(user_id, account_id, amount, transaction_type):
    try:
        amount = Decimal(str(amount))
    except (InvalidOperation, ValueError, TypeError):
        return {"error": "Invalid amount"}, 400

    if not amount.is_finite() or amount <= 0:
        return {"error": "Amount must be greater than zero"}, 400

    if amount != amount.quantize(Decimal("0.01")):
        return {"error": "Amount cannot have more than two decimal places"}, 400

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return {"error": "User Not Found"}, 404

    account = Account.query.filter_by(id=account_id, user_id=user.id).first()
    if not account:
        return {"error": "Account Not Found"}, 404

    if (account.account_status or "").lower() != "active":
        return {"error": "Account is not active"}, 400

    if not isinstance(transaction_type, str):
        return {"error": "Invalid transaction type"}, 400

    normalized_transaction_type = transaction_type.strip().lower()
    allowed_types = {"credit", "debit"}

    if normalized_transaction_type not in allowed_types:
        return {"error": "Invalid transaction type"}, 400

    return {
        "valid": True,
        "account": account,
        "amount": amount,
        "transaction_type": normalized_transaction_type,
    }, 200


def create_transaction(user_id, account_id, amount, transaction_type, description=None):
    validation_result, status_code = validate_transactions(
        user_id=user_id,
        account_id=account_id,
        amount=amount,
        transaction_type=transaction_type,
    )

    if status_code != 200:
        return validation_result, status_code

    account = (
        Account.query.filter_by(id=account_id, user_id=user_id)
        .with_for_update()
        .first()
    )

    if not account:
        db.session.rollback()
        return {"error": "Account Not Found"}, 404

    if (account.account_status or "").lower() != "active":
        db.session.rollback()
        return {"error": "Account is not active"}, 400

    amount = validation_result["amount"]
    transaction_type = validation_result["transaction_type"]

    try:
        current_balance = Decimal(str(account.balance))

        if transaction_type == "credit":
            account.balance = current_balance + amount
            sender_account_id = None
            receiver_account_id = account.id

        elif transaction_type == "debit":
            if current_balance < amount:
                db.session.rollback()
                return {"error": "Insufficient Balance"}, 400

            account.balance = current_balance - amount
            sender_account_id = account.id
            receiver_account_id = None
        else:
            db.session.rollback()
            return {"error": "Invalid transaction type"}, 400

        transaction = Transaction(
            sender_account_id=sender_account_id,
            receiver_account_id=receiver_account_id,
            amount=amount,
            transaction_type=transaction_type,
            transaction_status="completed",
            reference_id=f"TXN-{secrets.token_hex(12).upper()}",
            description=description,
        )

        db.session.add(transaction)
        db.session.commit()

        return {
            "message": "Transaction created successfully",
            "transaction": {
                "id": transaction.id,
                "reference_id": transaction.reference_id,
                "transaction_type": transaction.transaction_type,
                "amount": str(transaction.amount),
                "transaction_status": transaction.transaction_status,
                "balance": str(account.balance),
                "description": transaction.description,
            },
        }, 201

    except Exception:
        db.session.rollback()
        return {"error": "Transaction Failed"}, 500


def transfer_money(
    user_id, sender_account_id, receiver_account_id, amount, description=None
):

    try:
        amount = Decimal(str(amount))
    except (InvalidOperation, ValueError, TypeError):
        return {"error": "Invalid amount"}, 400

    if not amount.is_finite() or amount <= 0:
        return {"error": "Amount must be greater than zero"}, 400

    if amount != amount.quantize(Decimal("0.01")):
        return {"error": "Amount cannot have more than two decimal places"}, 400

    if isinstance(sender_account_id, bool) or isinstance(receiver_account_id, bool):
        return {"error": "Invalid account ID"}, 400

    try:
        sender_id = int(sender_account_id)
        receiver_id = int(receiver_account_id)
    except (ValueError, TypeError, OverflowError):
        return {"error": "Invalid account ID"}, 400

    if str(sender_account_id).strip() != str(sender_id) or str(
        receiver_account_id
    ).strip() != str(receiver_id):
        return {"error": "Invalid account ID"}, 400

    if sender_id <= 0 or receiver_id <= 0:
        return {"error": "Invalid account ID"}, 400

    if sender_id == receiver_id:
        return {"error": "Sender and receiver accounts must be different"}, 400

    try:
        accounts = (
            Account.query.filter(Account.id.in_([sender_id, receiver_id]))
            .order_by(Account.id)
            .with_for_update()
            .all()
        )

        accounts_by_id = {account.id: account for account in accounts}

        sender = accounts_by_id.get(sender_id)
        receiver = accounts_by_id.get(receiver_id)

        if sender is None or receiver is None:
            db.session.rollback()
            return {"error": "Sender or receiver account not found"}, 404

        if sender.user_id != user_id:
            db.session.rollback()
            return {"error": "You cannot transfer from this account"}, 403

        if (sender.account_status or "").lower() != "active" or (
            receiver.account_status or ""
        ).lower() != "active":
            db.session.rollback()
            return {"error": "Both accounts must be active"}, 400

        if sender.currency != receiver.currency:
            db.session.rollback()
            return {"error": "Account currencies must match"}, 400

        sender_balance = Decimal(str(sender.balance))
        receiver_balance = Decimal(str(receiver.balance))

        if sender_balance < amount:
            db.session.rollback()
            return {"error": "Insufficient balance"}, 400

        max_balance = Decimal("9999999999999.99")

        if receiver_balance + amount > max_balance:
            db.session.rollback()
            return {"error": "Receiver balance limit exceeded"}, 400

        sender.balance = sender_balance - amount
        receiver.balance = receiver_balance + amount

        transaction = Transaction(
            sender_account_id=sender.id,
            receiver_account_id=receiver.id,
            amount=amount,
            transaction_type="transfer",
            transaction_status="completed",
            reference_id=f"TXN-{secrets.token_hex(12).upper()}",
            description=description,
        )

        db.session.add(transaction)
        db.session.commit()

        return {
            "message": "Transfer completed successfully",
            "transaction": {
                "id": transaction.id,
                "reference_id": transaction.reference_id,
                "sender_account_id": transaction.sender_account_id,
                "receiver_account_id": transaction.receiver_account_id,
                "amount": str(transaction.amount),
                "transaction_type": transaction.transaction_type,
                "transaction_status": transaction.transaction_status,
                "description": transaction.description,
            },
            "balances": {
                "sender": str(sender.balance),
                "receiver": str(receiver.balance),
            },
        }, 201

    except Exception:
        db.session.rollback()
        return {"error": "Transfer failed. No changes were committed."}, 500
