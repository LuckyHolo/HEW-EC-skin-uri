from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ----------------ユーザー情報----------------
class User(db.Model):
    __name__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30),unique=True, nullable=False)
    language = db.Column(db.String(30), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.Datetime, nullable=False, default=datetime.now())

    # 関係定義


# ----------------ゲーム情報----------------
class Game(db.Model):
    __name__ = "games"

    id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.Datetime, nullable=False, default=datetime.now())

    # かんけい


