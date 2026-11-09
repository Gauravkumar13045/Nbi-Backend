from flask import Blueprint, jsonify, request

from services.transaction_service import (
    get_user_transactions,
    create_transaction,
    transfer_money,
)
from utils.decorators import token_required

transaction_bp = Blueprint("transaction", __name__)


@transaction_bp.route("/transactions", methods=["GET"])
@token_required
def get_transactions(current_user):

    transactions = get_user_transactions(current_user.id)

    if transactions is None:
        return jsonify({"error": "User not found"}), 404

    return (
        jsonify(
            {
                "transactions": [
                    {
                        "id": transaction.id,
                        "sender_account_id": transaction.sender_account_id,
                        "receiver_account_id": transaction.receiver_account_id,
                        "amount": str(transaction.amount),
                        "transaction_type": transaction.transaction_type,
                        "transaction_status": transaction.transaction_status,
                        "reference_id": transaction.reference_id,
                        "description": transaction.description,
                        "created_at": transaction.created_at.isoformat(),
                    }
                    for transaction in transactions
                ]
            }
        ),
        200,
    )


@transaction_bp.route("/transactions/withdraw", methods=["POST"])
@token_required
def create_new_transaction(current_user):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON body"}), 400

    account_id = data.get("account_id")
    amount = data.get("amount")
    transaction_type = data.get("transaction_type")
    description = data.get("description")

    if account_id is None or amount is None or transaction_type is None:
        return (
            jsonify({"error": "account_id, amount and transaction_type are required"}),
            400,
        )

    if not isinstance(transaction_type, str):
        return jsonify({"error": "Invalid transaction type"}), 400

    if description is not None and not isinstance(description, str):
        return jsonify({"error": "Invalid description"}), 400

    if transaction_type.strip().lower() != "debit":
        return jsonify({"error": "Only debit transactions are allowed"}), 400

    result, status_code = create_transaction(
        user_id=current_user.id,
        account_id=account_id,
        amount=amount,
        transaction_type="debit",
        description=description,
    )

    return jsonify(result), status_code


@transaction_bp.route("/transactions/transfer", methods=["POST"])
@token_required
def transfer_new_money(current_user):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON body"}), 400

    sender_account_id = data.get("sender_account_id")
    receiver_account_id = data.get("receiver_account_id")
    amount = data.get("amount")
    description = data.get("description")

    if sender_account_id is None or receiver_account_id is None or amount is None:
        return (
            jsonify(
                {
                    "error": "sender_account_id, receiver_account_id and amount are required"
                }
            ),
            400,
        )

    if description is not None and not isinstance(description, str):
        return jsonify({"error": "Invalid description"}), 400

    result, status_code = transfer_money(
        user_id=current_user.id,
        sender_account_id=sender_account_id,
        receiver_account_id=receiver_account_id,
        amount=amount,
        description=description,
    )

    return jsonify(result), status_code
