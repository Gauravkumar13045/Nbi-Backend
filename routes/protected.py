from flask import Blueprint, jsonify

from utils.decorators import token_required

protected_bp = Blueprint("protected", __name__)


@protected_bp.route("/me", methods=["GET"])
@token_required
def me(current_user):

    return (
        jsonify(
            {
                "message": "You are authenticated",
                "user": {
                    "id": current_user.id,
                    "username": current_user.username,
                    "email": current_user.email,
                    "mobile": current_user.mobile,
                    "status": current_user.status,
                },
            }
        ),
        200,
    )
