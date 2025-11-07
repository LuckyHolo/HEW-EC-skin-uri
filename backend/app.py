from flask import Flask, render_template, jsonify
from flask_cors import CORS
from models import db, User, Item, Game, Cart, CartItem, ItemFavorite  # 試す
from config import Config 

app = Flask(__name__, static_folder='statics')
CORS(app)

# app.config.from_object(Config)

# db.init_app(app)

# with app.app_context():
#     db.create_all()


# --- ROUTES (?) ---

@app.route("/")
def index():
    banner_games = [
        {'name': 'Lee Sin', 'img': 'images/skins/leesin_godfist.jpg'},
        {'name': 'Thresh', 'img': 'images/skins/thresh_darkstar.jpg'},
        {'name': 'Lux', 'img': 'images/skins/lux_elementalist.jpg'},
    ]
    return render_template("index.html", banner_games=banner_games)

# @app.route("/account")
# def account():
#     return render_template("account.html")

# @app.route("/items")
# def items_all():
#     items = Item.query.order_by(Item.id.desc()).all()
#     return render_template("items.html")


# # プレースホルダ
# @app.route("/api/items", methods=["GET"])
# def get_items():
#     items = Item.query.all()
#     return jsonify([
#         {
#             "id": item.id,
#             "name": item.item_name,
#             "price": item.item_price,
#             "img_url": item.img_url,
#             "availability": item.availability
#         }
#         for item in items
#     ])


# # プレースホルダ（２）
# @app.route("/api/items/favorite/<int:user_id>/<int:item_id>", methods=["POST"])
# def add_favorite_item(user_id, item_id):
#     existing = ItemFavorite.query.filter_by(user_id=user_id, item_id=item_id).first()
#     if existing:
#         return jsonify({"message": "既にお気に入りに追加されています"}), 400

#     fav = ItemFavorite(user_id=user_id, item_id=item_id)
#     db.session.add(fav)
#     db.session.commit()
#     return jsonify({"message": "お気に入りに追加しました！"}), 201


# # プレースホルダ（３）
# @app.route("/api/items/favorites/<int:user_id>", methods=["GET"])
# def get_favorite_items(user_id):
#     favorites = ItemFavorite.query.filter_by(user_id=user_id).all()
#     return jsonify([
#         {
#             "item_id": f.item_id,
#             "item_name": f.item.item_name,
#             "item_price": f.item.item_price,
#             "img_url": f.item.img_url
#         }
#         for f in favorites
#     ])


if __name__ == "__main__":
    app.run(port=8000, debug=True)
