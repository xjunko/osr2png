from __future__ import annotations

from pathlib import Path

import requests
from rosu_pp_py import Beatmap as PPBeatmap
from rosu_pp_py import Performance
from rosu_pp_py import PerformanceAttributes

import app.utils

#
CACHE_FOLDER: Path = app.utils.CACHE_FOLDER / "osu"
SOMETHING_FUCKED_UP: str = "SOMETHING FUCKED UP"

#
CACHE_FOLDER.mkdir(exist_ok=True, parents=True)

# URL(s)
OSU_RAW_URL: str = "https://osu.ppy.sh/osu/{id}"
OSU_BACKGROUND_URL: str = "https://assets.ppy.sh/beatmaps/{set_id}/covers/fullsize.jpg"
KITSU_MD5_URL: str = "https://osu.direct/api/md5/{md5}"

# Internal
USER_AGENT: str = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"


class Beatmap:
    data: dict[str, dict[str, str]]

    def __init__(
        self,
        data: dict[str, dict[str, str]] = {},
        beatmap_path: Path | None = None,
    ) -> None:
        self.data: dict[str, dict[str, str]] = data
        self.http: requests.Session = requests.Session()
        self.path = beatmap_path

        self.http.headers.update({"User-Agent": USER_AGENT})  # Set header

    @property
    def id(self) -> int:
        return int(self.data.get("Metadata", {}).get("BeatmapID", 0))

    @property
    def set_id(self) -> int:
        return int(self.data.get("Metadata", {}).get("BeatmapSetID", 0))

    @property
    def artist(self) -> str:
        return self.data.get("Metadata", {}).get("Artist", SOMETHING_FUCKED_UP)

    @property
    def title(self) -> str:
        return self.data.get("Metadata", {}).get("Title", SOMETHING_FUCKED_UP)

    @property
    def difficulty(self) -> str:
        return self.data.get("Metadata", {}).get("Version", SOMETHING_FUCKED_UP)

    @property
    def max_combo(self) -> int:
        return int(self.data.get("Metadata", {}).get("MaxCombo", 0))

    """ calcs """

    def calculate_pp(
        self,
        mods: int,
        acc: float,
        combo: int,
        misses: int,
    ) -> PerformanceAttributes:
        if self.path and not self.path.exists():
            print(
                "[Beatmap] The fuck, cached beatmap file is gone... Try running the thing again?",
            )

        pp_bmap = PPBeatmap(path=str(self.path))
        pp_calc = Performance(mods=mods)

        # params
        pp_calc.set_accuracy(acc)
        pp_calc.set_combo(combo)
        pp_calc.set_misses(misses)

        return pp_calc.calculate(pp_bmap)

    """ files """

    def get_beatmap_background(self) -> Path:
        # Download background if doesnt exists
        if not (background_file := CACHE_FOLDER / f"{self.set_id}_bg.png").exists():
            print("[API] Getting beatmap background from osu! /assets/,", end="")
            with self.http.get(OSU_BACKGROUND_URL.format(set_id=self.set_id)) as res:
                if res.status_code != 200:
                    print(" failed.")
                    print(
                        "[API] Failed to get beatmap background, using the default one.",
                    )
                    return app.utils.CACHE_FOLDER / "default_background.png"

                print(" success!")
                background_file.write_bytes(res.content)

        return background_file

    """ factories """

    def get_id_from_md5_kitsu(self, md5: str) -> int:
        with self.http.get(KITSU_MD5_URL.format(md5=md5)) as res:
            if res.status_code != 200:
                print("[API] Failed to get beatmap id from kitsu!")
                return 0

            return res.json().get("BeatmapID", 0)

    def get_id_from_md5_osu(self, md5: str) -> int:
        return app.utils.API_CLIENT.get_beatmap_id_from_md5(md5)

    @classmethod
    def from_md5(cls, md5: str):
        beatmap: Beatmap = cls()

        current_id: int = 0

        for api_method in [
            beatmap.get_id_from_md5_osu,
            beatmap.get_id_from_md5_kitsu,
        ]:
            print(
                f"[API] Trying to get beatmap id from {api_method.__name__}, ",
                end="",
            )
            try:
                if (current_id := api_method(md5)) != 0:
                    print("success!")
                    break
            except Exception as err:
                print(f"failed. Reason: {err}")
                continue

        if current_id == 0:
            print("[API] Failed to get beatmap id from all sources!")
            return None

        bmap = cls.from_id(current_id)

        return bmap

    @classmethod
    def from_id(cls, id: int):
        beatmap: Beatmap = cls()

        # Get raw .osu file from osu, if not in cache
        if not (beatmap_file := CACHE_FOLDER / str(id)).exists():
            print("[API] Getting beatmap from osu! /osu/,", end="")

            with beatmap.http.get(OSU_RAW_URL.format(id=id)) as res:
                if res.status_code != 200:
                    print(" failed.")
                    print("[API] Failed to get beatmap file from osu!.")
                    print(
                        "[API] If this is a custom beatmap, please pass the beatmap path with `-b` param.",
                    )
                    exit(1)

                print(" success!")
                beatmap_file.write_bytes(res.content)
                beatmap.path = beatmap_file

        return beatmap.from_osu_file(beatmap_file)

    @classmethod
    def from_osu_file(cls, path: Path) -> Beatmap:
        beatmap: Beatmap = cls(beatmap_path=path)

        beatmap.data |= beatmap._parse_beatmap_file_from_path(path)
        return beatmap

    """ spooky shit """

    @staticmethod
    def _parse_beatmap_file_from_path(path: Path) -> dict[str, dict[str, str]]:
        """really quick and dirty beatmap parser"""

        data: dict[str, dict[str, str]] = {}
        category: str = ""

        # NOTE: in linux this works just fine
        #       but on windows thing just shits the bed, fuck you windows.
        for line in (
            path.read_bytes().decode(encoding="utf-8", errors="ignore").splitlines()
        ):
            if not line.strip():
                continue

            if line.startswith("["):
                category = line.replace("[", "").replace("]", "")
                data[category] = {}
                continue

            match category:
                case "General" | "Editor" | "Metadata" | "Difficulty":
                    items = line.split(":")
                    data[category][items[0]] = items[1]
        return data


if __name__ == "__main__":
    b = Beatmap.from_id(2690223)
    print(b.title)
    print(b.difficulty)
    print(b.calculate_pp(mods=16, acc=100.0, combo=532, misses=0))
