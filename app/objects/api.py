""" api.py - v1 and v2 api wrapper """
from __future__ import annotations

from pathlib import Path
from typing import Self

import requests
from ossapi import Ossapi
from ossapi import UserLookupKey

# Errors
MISSING_FILE = "[Error] Failed to read api key file [apikey.txt], create it."
EMPTY_FILE = "[API] No values found in api key file [apikey.txt]."
SOLUTION_API_V1 = (
    "[API] For API v1: https://osu.ppy.sh/p/api \n"
    + "Solution: Put your api key on the first line in 'apikey.txt'"
)
SOLUTION_API_V2 = (
    "[API] For API v2: https://osu.ppy.sh/home/account/edit#oauth \n"
    + "Solution: Put your client_id and client_secret on separate lines in 'apikey.txt'"
)


class LegacyAPI:
    def __init__(self, key: str) -> None:
        self.session: requests.Session = requests.Session()
        self.key: str = key

    def get_player_id(self, name: str) -> int | None:
        with self.session.get(
            f"https://osu.ppy.sh/api/get_user",
            params={"k": self.key, "u": name},
        ) as res:
            if not res or res.status_code != 200:
                print("[API] Failed to get player id from osu! v1 api!")
                return None

            return res.json()[0].get("user_id", -1)

        return -1

    def get_beatmap_id_from_md5(self, md5: str) -> int:
        with self.session.get(
            f"https://osu.ppy.sh/api/get_beatmaps",
            params={"k": self.key, "h": md5},
        ) as res:
            if not res or res.status_code != 200:
                print("[API] Failed to get beatmap id from osu! v1 api!")
                return None

            return res.json()[0].get("beatmap_id", -1)


class ModernAPI(LegacyAPI):
    def __init__(self, client_id: str, client_secret: str) -> None:
        self.client: Ossapi = Ossapi(client_id, client_secret)

    def get_player_id(self, name: str) -> int | None:
        user = self.client.user(name, key=UserLookupKey.USERNAME)
        return user.id if user else None

    def get_beatmap_id_from_md5(self, md5: str) -> int:
        return self.client.beatmap(checksum=md5).id


class APIWrapper:
    def __init__(self) -> None:
        ...

    @classmethod
    def from_api_v1_key(cls, key: str) -> Self:
        return LegacyAPI(key)

    @classmethod
    def from_api_v2_key(cls, client_id: str, client_secret: str) -> Self:
        return ModernAPI(client_id, client_secret)

    @classmethod
    def from_file(cls, file: Path) -> Self | None:
        if not file.exists():
            print(MISSING_FILE)
            print(SOLUTION_API_V1)
            print(SOLUTION_API_V2)
            exit(1)

        # Read values
        lines: list[str] = [
            line for line in file.read_text().split("\n") if line.strip()
        ]

        # Empty file
        if not lines:
            print(EMPTY_FILE)
            print(SOLUTION_API_V1)
            print(SOLUTION_API_V2)
            exit(1)

        # V1
        if len(lines) == 1:
            return cls.from_api_v1_key(lines[0])

        # V2
        if len(lines) == 2:
            return cls.from_api_v2_key(lines[0], lines[1])

        # Invalid
        print("[API] Invalid api key file.")
        print(SOLUTION_API_V1)
        print(SOLUTION_API_V2)
        exit(1)
