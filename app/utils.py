from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import requests
from PIL import Image

from app.generation.common.vector import Vector2
from app.objects import api
from app.version import Version

API_KEY_FILE: Path = Path.cwd() / "apikey.txt"
CACHE_FOLDER: Path = Path.cwd() / ".cache"
AVATAR_FOLDER: Path = CACHE_FOLDER / "avatar"


def get_api_client() -> api.APIWrapper:
    return api.APIWrapper.from_file(API_KEY_FILE)


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
        "default_star.png": "https://raw.githubusercontent.com/xjunko/blobs/e1719872b7faad07b1b2400cea44055ce0051a71/osr2png/assets/default_star.png",
        "default_miss.png": "https://raw.githubusercontent.com/xjunko/blobs/e1719872b7faad07b1b2400cea44055ce0051a71/osr2png/assets/default_miss.png",
        "font.ttf": "https://raw.githubusercontent.com/xjunko/blobs/e1719872b7faad07b1b2400cea44055ce0051a71/osr2png/assets/font.ttf",
    }

    for filename, url in default_assets_and_url.items():
        if not (file_path := CACHE_FOLDER / filename).exists():
            print(f"[Startup] Getting default assets: {filename},", end="")

            # Download the motherfucking file
            with session.get(url) as res:
                if res.status_code != 200 and len(res.content) < 2048:
                    print(" failed!")
                    print(
                        f"[Startup] Might want to put your own files in place there, `{file_path.resolve()}`.",
                    )

                print(" success!")
                file_path.write_bytes(res.content)

    return 0


def ensure_up_to_date(current_version: Version) -> int:
    print(f"[Version] Current version: {current_version!r}")
    print(f"[Version] Checking github for a new version of osr2png,", end="")

    with requests.Session() as session:
        with session.get(
            "https://api.github.com/repos/xjunko/osr2png/releases/latest",
        ) as res:
            if res.status_code != 200:
                print(" failed!")
                return 0

            data: dict[Any, Any] = res.json()

            github_version = Version.from_str(data["tag_name"])

            print(" success!")

            # Compare our version with github's
            if github_version > current_version:
                print("[Version] You're using an older version of osr2png.")
                print("[Version] You can update it from here:", data["html_url"])
                time.sleep(3)
            else:
                print("[Version] You're using the latest version of osr2png.")

    return 0


""" Image crap """


def resize_image_to_resolution_but_keep_ratio(
    img: Image.Image,
    resolution: Vector2,
) -> Image.Image:
    ratio = resolution.x / img.width

    return img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)


def get_player_avatar(name: str) -> Path:
    api_client: api.APIWrapper = get_api_client()
    session: requests.Session = requests.Session()

    if not (avatar_path := AVATAR_FOLDER / name).exists():
        if not (user_id := api_client.get_player_id(name)):
            return CACHE_FOLDER / "default_avatar.png"

        # Download
        print(f"[API] Downloading {name}'s avatar,", end="")
        with session.get(f"https://a.ppy.sh/{user_id}") as avatar_res:
            if avatar_res.status_code != 200 and len(avatar_res.content) < 2000:
                print(" failed.")
                return CACHE_FOLDER / "default_avatar.png"

            print(" success!")
        avatar_path.write_bytes(avatar_res.content)

    return avatar_path
