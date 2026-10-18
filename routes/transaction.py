from flask import Blueprint, jsonify

from services.transaction_service import get_user_transactions
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
