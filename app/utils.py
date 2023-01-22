from pathlib import Path

import requests
from PIL import Image

from app.generation.common.vector import Vector2

CACHE_FOLDER: Path = Path.cwd() / ".cache"
AVATAR_FOLDER: Path = CACHE_FOLDER / "avatar"
API_KEY_FILE: Path = Path.cwd() / "apikey.txt"


def ensure_directories() -> int:
    for required_dir in [CACHE_FOLDER, AVATAR_FOLDER]:
        required_dir.mkdir(exist_ok=True, parents=True)

    return 0


def ensure_default_assets() -> int:
    session: requests.Session = requests.Session()

    # Default
    default_assets_and_url: dict[str, str] = {
        "default_avatar.png": "https://a.ppy.sh/",
        "default_background.png": "https://assets.ppy.sh/contests/154/winners/Dreamxiety.png",
        "default_star.png": "https://cdn.discordapp.com/attachments/703552229680087042/1051736349163651072/0PTTQK8.png",
        "default_miss.png": "https://cdn.discordapp.com/attachments/703552229680087042/1051757293479403530/zfaT6fg.png",
        "font.ttf": "https://cdn.discordapp.com/attachments/703552229680087042/1066692446798483466/font.ttf",
    }

    for filename, url in default_assets_and_url.items():
        if not (file_path := CACHE_FOLDER / filename).exists():
            print(f"[Startup] Getting default assets: {filename},", end="")

            # Download the motherfucking file
            with session.get(url) as res:
                if res.status_code != 200 and len(res.content) < 2048:
                    print(" failed!")
                    print(
                        f"[Startup] Might want to put your own files in place there, `{file_path.resolve()}`."
                    )

                print(" success!")
                file_path.write_bytes(res.content)

    return 0


""" Image crap """


def resize_image_to_resolution_but_keep_ratio(
    img: Image.Image, resolution: Vector2
) -> Image.Image:
    ratio = resolution.x / img.width

    return img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)


def get_player_avatar(name: str) -> Path:
    session: requests.Session = requests.Session()

    if not (avatar_path := AVATAR_FOLDER / name).exists():
        if not API_KEY_FILE.exists():
            print(
                f"[API] Error: Failed to get user avatar because API_KEY_FILE ({API_KEY_FILE}) did not exists."
            )
            print(
                f"[API] Solution: Please make that file and put your api key into it."
            )

            return CACHE_FOLDER / "default_avatar.png"

        API_KEY = API_KEY_FILE.read_text()

        with session.get(
            "https://osu.ppy.sh/api/get_user", params={"k": API_KEY, "u": name}
        ) as res:
            if not res.status_code != 200:
                print("[API] Error: Failed to get user data from osu! /api/.")
                print("[API] Using default avatar.")

            user_id: int = res.json()[0].get("user_id", -1)

            # Download
            print(f"[API] Downloading {name}'s avatar,", end="")
            with session.get(f"https://a.ppy.sh/{user_id}") as avatar_res:
                if avatar_res.status_code != 200 and len(avatar_res.content) < 2000:
                    print(" failed.")
                    return CACHE_FOLDER / "default_avatar.png"

                print(" success!")
                avatar_path.write_bytes(avatar_res.content)

    return avatar_path
