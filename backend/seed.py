from app import app, db
from models import Game, Item
from datetime import datetime, timezone


# 初期値

with app.app_context():
    print("🌱 Starting database seeding...")

    # --------------------------------------
    db.session.query(Item).delete()
    db.session.query(Game).delete()
    db.session.commit()
    # データリセット、不要だったらコメントアウト

    game = Game(game_name="League of Legends")
    db.session.add(game)
    db.session.commit()
    print(f"✅ Added game: {game.game_name}")

    items = [
        Item(
            item_name="Ahri - Spirit Blossom",
            item_price=1350,
            game_id=game.id,
            category_1="Champion Skin",
            description="Oye.",
            img_url="/statics/images/skins/ahri_spirit_blossom.jpg",
            item_link="https://leagueoflegends.com/ahri",
        ),
        Item(
            item_name="Yasuo - Nightbringer",
            item_price=1820,
            game_id=game.id,
            category_1="Champion Skin",
            description="Syalala.",
            img_url="/statics/images/skins/yasuo_nightbringer.jpg",
            item_link="https://leagueoflegends.com/yasuo",
        ),
        Item(
            item_name="Lux - Elementalist",
            item_price=3250,
            game_id=game.id,
            category_1="Champion Skin",
            description="Oye.",
            img_url="/statics/images/skins/lux_elementalist.jpg",
            item_link="https://leagueoflegends.com/lux",
        ),
        Item(
            item_name="Ezreal - Pulsefire",
            item_price=1350,
            game_id=game.id,
            category_1="Champion Skin",
            description="Yahoo.",
            img_url="/statics/images/skins/ezreal_pulsefire.jpg",
            item_link="https://leagueoflegends.com/ezreal",
        ),
        Item(
            item_name="Jinx - Star Guardian",
            item_price=1820,
            game_id=game.id,
            category_1="Champion Skin",
            description="Nonono.",
            img_url="/statics/images/skins/jinx_star_guardian.jpg",
            item_link="https://leagueoflegends.com/jinx",
        ),
        Item(
            item_name="Zed - PROJECT",
            item_price=1350,
            game_id=game.id,
            category_1="Champion Skin",
            description="Ouyea.",
            img_url="/statics/images/skins/zed_project.jpg",
            item_link="https://leagueoflegends.com/zed",
        ),
        Item(
            item_name="Akali - K/DA",
            item_price=1350,
            game_id=game.id,
            category_1="Champion Skin",
            description="We rockin'.",
            img_url="/statics/images/skins/akali_kda.jpg",
            item_link="https://leagueoflegends.com/akali",
        ),
        Item(
            item_name="Lee Sin - God Fist",
            item_price=1820,
            game_id=game.id,
            category_1="Champion Skin",
            description="Kick.",
            img_url="/statics/images/skins/leesin_godfist.jpg",
            item_link="https://leagueoflegends.com/leesin",
        ),
        Item(
            item_name="Thresh - Dark Star",
            item_price=1350,
            game_id=game.id,
            category_1="Champion Skin",
            description="Da Void.",
            img_url="/statics/images/skins/thresh_darkstar.jpg",
            item_link="https://leagueoflegends.com/thresh",
        ),
        Item(
            item_name="Vayne - PROJECT",
            item_price=1820,
            game_id=game.id,
            category_1="Champion Skin",
            description="Mamamia.",
            img_url="/statics/images/skins/vayne_project.jpg",
            item_link="https://leagueoflegends.com/vayne",
        ),
    ]

    db.session.add_all(items)
    db.session.commit()
    print(f"✅ Added {len(items)} items for {game.game_name}!")

    print("🌸 Seeding completed successfully!")
