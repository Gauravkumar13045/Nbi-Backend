from flask import Blueprint, jsonify, request

from utils.decorators import token_required
from services.account_service import create_account, get_user_accounts

account_bp = Blueprint("account", __name__)


@account_bp.route("/account", methods=["POST"])
@token_required
def create_new_account(current_user):

    data = request.get_json()

    if not data:
        return jsonify({"error": "Data not found"}), 400

    account_type = data.get("account_type")
    branch_code = data.get("branch_code")
    ifsc_code = data.get("ifsc_code")

    if not account_type or not branch_code or not ifsc_code:
        return (
            jsonify({"error": "Account type, branch code and IFSC code are required"}),
            400,
        )

    account = create_account(
        user_id=current_user.id,
        account_type=account_type,
        branch_code=branch_code,
        ifsc_code=ifsc_code,
        opening_balance=0,
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


@account_bp.route("/accounts", methods=["GET"])
@token_required
def get_accounts(current_user):

    accounts = get_user_accounts(current_user.id)

    return (
        jsonify(
            {
                "accounts": [
                    {
                        "id": account.id,
                        "account_number": account.account_number,
                        "account_type": account.account_type,
                        "balance": float(account.balance),
                        "currency": account.currency,
                        "account_status": account.account_status,
                        "branch_code": account.branch_code,
                        "ifsc_code": account.ifsc_code,
                    }
                    for account in accounts
                ]
            }
        ),
        200,
    )
