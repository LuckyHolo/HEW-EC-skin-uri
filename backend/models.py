from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

# ----------------ユーザー情報----------------
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30),unique=True, nullable=False)
    language = db.Column(db.String(30), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # 関係定義
    payment_methods = db.relationship('PaymentMethod', backref='user', lazy=True, cascade="all, delete-orphan")
    carts = db.relationship('Cart', backref='user', lazy=True, cascade="all, delete-orphan")
    purchases = db.relationship('PurchaseHistory', backref='user', lazy=True, cascade="all, delete-orphan")
    streamers = db.relationship('Streamer', backref='user', lazy=True, cascade="all, delete-orphan")
    favorites = db.relationship('Favorite', backref='user', lazy=True, cascade="all, delete-orphan")
    item_favorites = db.relationship('ItemFavorite', backref='user', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} name={self.user_name}>"    


# ----------------ゲーム情報----------------
class Game(db.Model):
    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # 関係定義
    items = db.relationship('Item', backref='game', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Game id={self.id} name={self.game_name}>"

# ----------------アイテム情報----------------
class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(200), nullable=False)
    item_price = db.Column(db.Integer, nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    category_1 = db.Column(db.String(100))
    category_2 = db.Column(db.String(100))
    category_3 = db.Column(db.String(100))
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    availability = db.Column(db.Boolean, nullable=False, default=True)
    description = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(255), nullable=False)
    item_link = db.Column(db.String(255), nullable=False)

    # 関係定義
    cart_items = db.relationship('CartItem', backref='item', lazy=True, cascade="all, delete-orphan")
    purchase_history = db.relationship('PurchaseHistory', backref='item', lazy=True, cascade="all, delete-orphan")
    favorites = db.relationship('ItemFavorite', backref='item', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Item id={self.id} name={self.item_name}>"

# ----------------支払い方法----------------
class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    card_token = db.Column(db.String(255))
    validity_date = db.Column(db.Date)
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    address = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<PaymentMethod id={self.id} user_id={self.user_id}>"

# ----------------購入履歴----------------
class PurchaseHistory(db.Model):
    __tablename__ = 'purchase_histories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    purchase_price = db.Column(db.Integer)
    purchase_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<PurchaseHistory id={self.id} user_id={self.user_id} item_id={self.item_id}>"

# ----------------ストリーマー----------------
class Streamer(db.Model):
    __tablename__ = 'streamers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    channel_name = db.Column(db.String(100))
    platform = db.Column(db.String(50))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # 関係定義
    streams = db.relationship('Stream', backref='streamer', lazy=True, cascade="all, delete-orphan")
    favorites = db.relationship('Favorite', backref='streamer', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Streamer id={self.id} channel_name={self.channel_name}>"

# ----------------ストリーム----------------
class Stream(db.Model):
    __tablename__ = 'streams'

    id = db.Column(db.Integer, primary_key=True)
    streamer_id = db.Column(db.Integer, db.ForeignKey('streamers.id'), nullable=False)
    stream_title = db.Column(db.String(200))
    stream_url = db.Column(db.String(255))
    start_time = db.Column(db.DateTime(timezone=True), nullable=True)
    end_time = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Stream id={self.id} streamer_id={self.streamer_id} stream_title={self.stream_title}>"

# ----------------お気に入り（ストリーマー）----------------
class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    streamer_id = db.Column(db.Integer, db.ForeignKey('streamers.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Favorite user_id={self.user_id} streamer_id={self.streamer_id}>"

# ----------------お気に入り（アイテム）----------------
class ItemFavorite(db.Model):
    __tablename__ = 'item_favorites'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'item_id', name='unique_user_item_favorite'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<ItemFavorite user_id={self.user_id} item_id={self.item_id}>"

# ----------------カート----------------
class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # 関係定義
    cart_items = db.relationship('CartItem', backref='cart', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Cart id={self.id} user_id={self.user_id}>"

# ----------------カートアイテム----------------
class CartItem(db.Model):
    __tablename__ = 'cart_items'
    __table_args__ = (
        db.UniqueConstraint('cart_id', 'item_id', name='unique_cart_item'),
    )

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<CartItem id={self.id} cart_id={self.cart_id} item_id={self.item_id}>"




