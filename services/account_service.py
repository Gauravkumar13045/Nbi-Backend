from extensions import db
from models.account import Account
from secrets import randbelow


def create_account(user_id, account_type, branch_code, ifsc_code):
    while True:
        account_number = str(randbelow(90000000000000) + 10000000000000)
        existing_account = Account.query.filter_by(
            account_number=account_number
        ).first()

        if not existing_account:
            break

    account = Account(
        user_id=user_id,
        account_number=account_number,
        ifsc_code=ifsc_code,
        balance=10000,
        currency="INR",
        account_status="active",
        account_type=account_type,
        branch_code=branch_code,
    )
    db.session.add(account)
    db.session.commit()

    return account
