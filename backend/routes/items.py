from flask import Blueprint, jsonify, request, render_template
from models import db, Item, ItemFavorite

account_bp = Blueprint('account', __name__)
items_bp = Blueprint('items', __name__)

# ----------------全てのアイテム取得（GET)----------------
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

# ----------------お気に入り追加（POST)----------------
@items_bp.route("/api/items/favorite/<int:user_id>/<int:item_id>", methods=["POST"])
def add_favorite_item(user_id, item_id):
    existing = ItemFavorite.query.filter_by(user_id=user_id, item_id=item_id).first()
    if existing:
        return jsonify({"message": "既にお気に入りに追加されています"}), 400

    fav = ItemFavorite(user_id=user_id, item_id=item_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({"message": "お気に入りに追加しました！"}), 201


# ----------------お気に入りアイテム一覧（GET）----------------
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


# ----------------お気に入りアイテム削除（DELETE）----------------
@items_bp.route("/api/items/favorite/<int:user_id>/<int:item_id>", methods=["DELETE"])
def delete_favorite_item(user_id, item_id):
    favorite = ItemFavorite.query.filter_by(user_id=user_id, item_id=item_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "お気に入りから削除しました"}), 200
    else:
        return jsonify({"message": "お気に入りに追加されていません"}), 404
    
