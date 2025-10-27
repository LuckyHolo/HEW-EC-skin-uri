from flask import Blueprint, jsonify, request
from models import db, Item, ItemFavorite

# bikin blueprint baru
items_bp = Blueprint('items', __name__)

# ------------------------------
# すべてのアイテムを取得 (GET)
# ------------------------------
@items_bp.route("/api/items", methods=["GET"])
def get_items():
    items = Item.query.all()
    return jsonify([
        {
            "id": item.id,
            "name": item.item_name,
            "price": item.item_price,
            "img_url": item.img_url,
            "availability": item.availability
        }
        for item in items
    ])


# ------------------------------
# お気に入りに追加 (POST)
@items_bp.route("/api/items/favorite/<int:user_id>/<int:item_id>", methods=["POST"])
def add_favorite_item(user_id, item_id):
    existing = ItemFavorite.query.filter_by(user_id=user_id, item_id=item_id).first()
    if existing:
        return jsonify({"message": "既にお気に入りに追加されています"}), 400

    fav = ItemFavorite(user_id=user_id, item_id=item_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({"message": "お気に入りに追加しました！"}), 201


# ------------------------------
# お気に入りアイテム一覧 (GET)
# ------------------------------
@items_bp.route("/api/items/favorites/<int:user_id>", methods=["GET"])
def get_favorite_items(user_id):
    favorites = ItemFavorite.query.filter_by(user_id=user_id).all()
    return jsonify([
        {
            "item_id": f.item_id,
            "item_name": f.item.item_name,
            "item_price": f.item.item_price,
            "img_url": f.item.img_url
        }
        for f in favorites
    ])
