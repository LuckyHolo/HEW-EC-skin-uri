from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import User

account_bp = Blueprint('account', __name__)

@account_bp.route("/account")
@login_required
def account():
    user = current_user

    return render_template("account.html", user=user)
