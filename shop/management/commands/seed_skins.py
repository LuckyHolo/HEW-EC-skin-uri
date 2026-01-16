import os
import json
import math
import random
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from django.utils.text import slugify
from shop.models import Product, Category, Game

BASE_SKINS_DIR = Path(settings.MEDIA_ROOT) / "skins"  

TIER_PRICES = {
    "Normal": 1000,
    "Epic": 1500,
    "Legendary": 2000,
    "Ultimate": 3500,
}
TIERS = list(TIER_PRICES.keys())

# filename -> (skin_name, image_name)
def filename_to_skin_and_image(champion_folder_name: str, filename: str):
    """Return (skin_name, image_name). filename is the raw filename with extension."""
    champion_slug = slugify(champion_folder_name).replace("-", "_")
    name_no_ext = os.path.splitext(filename)[0]
    name_lower = name_no_ext.lower()

    suffix = "_" + champion_slug
    if name_lower.endswith(suffix):
        skin_slug = name_lower[: -len(suffix)]
    else:
        skin_slug = name_lower

    skin_name = " ".join([part.capitalize() for part in skin_slug.split("_") if part])
    image_name_relative = f"skins/{champion_folder_name}/{filename}"
    return skin_name, image_name_relative


class Command(BaseCommand):
    help = "Seed skin products into the database from a folder structure: skins/<Champion>/*.jpg"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dir",
            "-d",
            help="Path to skins folder (default: BASE_DIR/skins)",
            default=str(BASE_SKINS_DIR),
        )
        parser.add_argument(
            "--bulk-size",
            type=int,
            default=500,
            help="How many objects to bulk_create at once",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force re-create duplicates (skip existing checks). Without --force duplicates are skipped.",
        )

    def handle(self, *args, **options):
        lol_game, _ = Game.objects.get_or_create(name="League of Legends")
        skins_dir = Path(options["dir"])
        bulk_size = options["bulk_size"]
        force = options["force"]

        if not skins_dir.exists() or not skins_dir.is_dir():
            self.stderr.write(self.style.ERROR(f"Folder tidak ditemukan: {skins_dir}"))
            return

        release_dates_path = skins_dir / "release_dates.json"
        release_map = {}
        if release_dates_path.exists():
            try:
                with open(release_dates_path, "r", encoding="utf-8") as f:
                    release_map = json.load(f)
                self.stdout.write(self.style.NOTICE("Loaded release_dates.json"))
            except Exception as e:
                self.stderr.write(self.style.WARNING(f"release_dates.json error: {e}"))

        champions_ja_path = skins_dir / "champions_ja.json"
        champion_ja_map = {}

        if champions_ja_path.exists():
            try:
                with open(champions_ja_path, "r", encoding="utf-8") as f:
                    champion_ja_map = json.load(f)
                self.stdout.write(self.style.NOTICE("Loaded champions_ja.json"))
            except Exception as e:
                self.stderr.write(self.style.WARNING(f"champions_ja.json error: {e}"))

        skins_ja_path = skins_dir / "skins_ja.json"
        skin_ja_map = {}

        if skins_ja_path.exists():
            try:
                with open(skins_ja_path, "r", encoding="utf-8") as f:
                    skin_ja_map = json.load(f)
                self.stdout.write(self.style.NOTICE("Loaded skins_ja.json"))
            except Exception as e:
                self.stderr.write(self.style.WARNING(f"skins_ja.json error: {e}"))


        category_skin, _ = Category.objects.get_or_create(name="Skin")

        to_create = []
        created = 0
        skipped = 0

        for champion_folder in sorted(p for p in skins_dir.iterdir() if p.is_dir()):
            champion_folder_name = champion_folder.name 
            champion_readable = " ".join([w.capitalize() for w in champion_folder_name.split("_")])
            champion_name_ja = champion_ja_map.get(
                champion_readable,
                champion_readable
            )


            for filename in sorted(os.listdir(champion_folder)):
                if filename.startswith("."):
                    continue
                if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                    continue

                skin_name, image_name = filename_to_skin_and_image(champion_folder_name, filename)
                skin_key = f"{champion_readable}|{skin_name}"

                skin_name_ja = skin_ja_map.get(
                    skin_key,
                    skin_name 
                )


                # 複数対策
                exists = Product.objects.filter(image_name=image_name).exists() or Product.objects.filter(
                    champion_name__iexact=champion_name_ja, 
                    skin_name__iexact=skin_name_ja
                ).exists()

                if exists and not force:
                    skipped += 1
                    continue

                tier = random.choice(TIERS)
                price = TIER_PRICES[tier]

                release_date = None
                key1 = f"{champion_readable}|{skin_name}"
                if key1 in release_map:
                    release_date = release_map[key1]
                elif image_name in release_map:
                    release_date = release_map[image_name]

                product_kwargs = dict(
                    champion_name=champion_name_ja,
                    skin_name=skin_name_ja,
                    description=f"{champion_name_ja} – {skin_name_ja} のスキン",
                    name=f"{champion_name_ja} – {skin_name_ja}",
                    price=price,
                    game=lol_game,
                    category=category_skin,
                    image_name=image_name,
                    release_date=release_date,
                )

                # 念のためバグ対策
                if hasattr(Product, "stock") or "stock" in [f.name for f in Product._meta.get_fields()]:
                    product_kwargs["stock"] = 0

                to_create.append(Product(**product_kwargs))

                if len(to_create) >= bulk_size:
                    with transaction.atomic():
                        Product.objects.bulk_create(to_create)
                    created += len(to_create)
                    to_create = []
                    self.stdout.write(self.style.NOTICE(f"Bulk created {created} so far..."))

        if to_create:
            with transaction.atomic():
                Product.objects.bulk_create(to_create)
            created += len(to_create)

        self.stdout.write(self.style.SUCCESS(f"Seeding selesai. created={created}, skipped={skipped}"))
        self.stdout.write(self.style.SUCCESS("Tip: jika ingin isi release_date, buat file skins/release_dates.json dengan mapping `\"Champion|Skin\": \"YYYY-MM-DD\"` atau `\"skins/Champion/filename.jpg\": \"YYYY-MM-DD\"`"))
