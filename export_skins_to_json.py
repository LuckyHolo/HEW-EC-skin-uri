import json
from pathlib import Path

SKINS_DIR = Path("skins")
OUTPUT_FILE = Path("skins_files.json")

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

result = {}

for champion_dir in sorted(p for p in SKINS_DIR.iterdir() if p.is_dir()):
    files = sorted(
        f.name
        for f in champion_dir.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTS
    )

    if files:
        result[champion_dir.name] = files

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"✅ Export selesai → {OUTPUT_FILE}")
