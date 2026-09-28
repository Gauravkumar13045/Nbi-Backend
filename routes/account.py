from flask import Blueprint, jsonify, request

from utils.decorators import token_required
from services.account_service import create_account

account_bp = Blueprint("account", __name__)


@account_bp.route("/account", methods=["POST"])
@token_required
def create_new_account(current_user):

    data = request.get_json()

    if not data:
        return jsonify({"error": "Data not found"}), 400

    account = create_account(
        user_id=current_user.id,
        account_type=data["account_type"],
        branch_code=data["branch_code"],
        ifsc_code=data["ifsc_code"],
    )

    return (
        jsonify(
            {
                "message": "Account created successfully",
                "account": {
                    "id": account.id,
                    "user_id": account.user_id,
                    "account_number": account.account_number,
                    "ifsc_code": account.ifsc_code,
                    "balance": float(account.balance),
                    "currency": account.currency,
                    "account_status": account.account_status,
                    "account_type": account.account_type,
                    "branch_code": account.branch_code,
                },
            }
        ),
        201,
    )
