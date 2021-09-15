"""

    THE MOTHERFUCKING OSU API 

"""
import os
import requests
from pathlib import Path
from PIL import Image

BASE_API: str = "https://osu.ppy.sh/api/"
BASE_ASSETS: str = "https://assets.ppy.sh/"
BASE_AVATAR: str = "https://a.ppy.sh/"
BASE_CPOL_API: str = "https://pp.osuck.net/"
CACHE_FOLDER: Path = Path("cache")
ASSETS_FOLDER: Path = Path("assets")


class osuAPI:
    def __init__(self, token: str, settings: object) -> None:
        self.token: str = token
        self.settings: object = settings
        self.session: requests.Session = requests.Session()

        #
        print(f"[osuAPI] Started, apikey is {token[:10]}... [Length: {len(token)}]!")
        self.check_api_shit()
        self.make_sure_folder_created()

    def check_api_shit(self) -> None:
        if len(self.token) < 40:
            print("[osuAPI] Invalid api key!")
            os._exit(1)

    def make_sure_folder_created(self) -> None:
        for required in [CACHE_FOLDER, ASSETS_FOLDER]:
            if not required.exists():
                required.mkdir()

    def make_request(
        self, base: str, endpoint: str, params: dict = {}, mode: int = 0
    ) -> dict:
        """
        # cba to use enums for this lole
        MODE 0: json
        MODE 1: bytes
        MODE 2: just return as it is
        """
        if base == BASE_API:
            params["k"] = self.token

        print(f"[osuAPI] Reaching {base+endpoint}, ", end="")

        with self.session.get(base + endpoint, params=params) as res:
            if not res or res.status_code != 200:
                print(f"Failed to reach {base+endpoint}: {res.content}")
                return None

            print("Success!")
            if mode == 0:
                return res.json()

            return {1: res.content, 2: res}[mode]

    def get_user_from_name(self, name: str) -> dict:
        if res := self.make_request(BASE_API, "get_user", {"u": name}):
            return res[0]

    def get_map_from_md5(self, md5: str) -> dict:
        if res := self.make_request(BASE_API, "get_beatmaps", {"h": md5}):
            return res[0]

    def get_beatmap_background(self, beatmap_id: int) -> Path:
        path = ASSETS_FOLDER / "default_bg.png"
        filepath = CACHE_FOLDER / f"{beatmap_id}.png"

        if filepath.exists() and self.settings.use_cache:
            return Image.open(filepath)

        if res := self.make_request(
            BASE_ASSETS, f"beatmaps/{beatmap_id}/covers/fullsize.jpg", mode=1
        ):
            filepath.write_bytes(res)
            path = filepath

        return Image.open(path)

    def get_avatar_image(self, user_id: int) -> Path:
        path = ASSETS_FOLDER / "default_avatar.png"
        filepath = CACHE_FOLDER / f"{user_id}.png"

        if filepath.exists() and self.settings.use_cache:
            return Image.open(filepath)

        if res := self.make_request(BASE_AVATAR, str(user_id), mode=1):
            filepath.write_bytes(res)
            path = filepath

        return Image.open(path)

    ## PP APIs
    def get_pp(
        self, map_id: int, mods: int, max_combo: int, hitmiss: int, accuracy: float
    ) -> dict:
        for endpoint in [self.get_pp_from_cpol]:
            if res := endpoint(
                id=map_id, mods=mods, combo=max_combo, miss=hitmiss, acc=accuracy
            ):
                return res

        # Defaults
        return {
            "stats": {"star": {"pure": "0.00"}},
            "mods": {"name": ""},
            "pp": {"current": "0.00"},
        }

    def get_pp_from_cpol(self, **kwargs: dict) -> dict:
        return self.make_request(BASE_CPOL_API, "pp", kwargs)
