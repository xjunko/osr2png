"""
    replay.py - ripped off from cmyui's common lib
"""
import os
from dataclasses import dataclass
from enum import IntEnum, IntFlag, unique
from pathlib import Path
from typing import Optional


@unique
class Mods(IntFlag):
    NOMOD = 0
    NOFAIL = 1 << 0
    EASY = 1 << 1
    TOUCHSCREEN = 1 << 2  # old: 'NOVIDEO'
    HIDDEN = 1 << 3
    HARDROCK = 1 << 4
    SUDDENDEATH = 1 << 5
    DOUBLETIME = 1 << 6
    RELAX = 1 << 7
    HALFTIME = 1 << 8
    NIGHTCORE = 1 << 9
    FLASHLIGHT = 1 << 10
    AUTOPLAY = 1 << 11
    SPUNOUT = 1 << 12
    AUTOPILOT = 1 << 13
    PERFECT = 1 << 14
    KEY4 = 1 << 15
    KEY5 = 1 << 16
    KEY6 = 1 << 17
    KEY7 = 1 << 18
    KEY8 = 1 << 19
    FADEIN = 1 << 20
    RANDOM = 1 << 21
    CINEMA = 1 << 22
    TARGET = 1 << 23
    KEY9 = 1 << 24
    KEYCOOP = 1 << 25
    KEY1 = 1 << 26
    KEY3 = 1 << 27
    KEY2 = 1 << 28
    SCOREV2 = 1 << 29
    MIRROR = 1 << 30

    # XXX: needs some modification to work..
    # KEY_MOD = KEY1 | KEY2 | KEY3 | KEY4 | KEY5 | KEY6 | KEY7 | KEY8 | KEY9 | KEYCOOP
    # FREE_MOD_ALLOWED = NOFAIL | EASY | HIDDEN | HARDROCK | \
    #                 SUDDENDEATH | FLASHLIGHT | FADEIN | \
    #                 RELAX | AUTOPILOT | SPUNOUT | KEY_MOD
    # SCORE_INCREASE_MODS = HIDDEN | HARDROCK | DOUBLETIME | FLASHLIGHT | FADEIN
    SPEED_CHANGING = DOUBLETIME | NIGHTCORE | HALFTIME

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        # NM returns NM
        if self.value == Mods.NOMOD:
            return "NM"

        # Filter DT if NC
        value: int = self.value

        if value & Mods.NIGHTCORE:
            value -= Mods.DOUBLETIME

        mod_dict = {
            Mods.NOFAIL: "NF",
            Mods.EASY: "EZ",
            Mods.TOUCHSCREEN: "TD",
            Mods.HIDDEN: "HD",
            Mods.HARDROCK: "HR",
            Mods.SUDDENDEATH: "SD",
            Mods.DOUBLETIME: "DT",
            Mods.RELAX: "RX",
            Mods.HALFTIME: "HT",
            Mods.NIGHTCORE: "NC",
            Mods.FLASHLIGHT: "FL",
            Mods.AUTOPLAY: "AU",
            Mods.SPUNOUT: "SO",
            Mods.AUTOPILOT: "AP",
            Mods.PERFECT: "PF",
            Mods.KEY4: "K4",
            Mods.KEY5: "K5",
            Mods.KEY6: "K6",
            Mods.KEY7: "K7",
            Mods.KEY8: "K8",
            Mods.FADEIN: "FI",
            Mods.RANDOM: "RN",
            Mods.CINEMA: "CN",
            Mods.TARGET: "TP",
            Mods.KEY9: "K9",
            Mods.KEYCOOP: "CO",
            Mods.KEY1: "K1",
            Mods.KEY3: "K3",
            Mods.KEY2: "K2",
            Mods.SCOREV2: "V2",
            Mods.MIRROR: "MR",
        }

        mod_str = []

        for m in (_m for _m in Mods if value & _m and _m != Mods.SPEED_CHANGING):
            mod_str.append(mod_dict[m])

        return "".join(mod_str)


class Mode(IntEnum):
    standard = 0
    taiko = 1
    ctb = 2
    mania = 3


@dataclass
class Accuracy:
    hit300: float
    hit100: float
    hit50: float
    hitgeki: float
    hitkatu: float
    hitmiss: float

    @property
    def value(self) -> float:
        # :troll:
        return (
            (
                (self.hit300) * 300.0
                + (self.hit100) * 100.0
                + (self.hit50) * 50.0
                + (self.hitmiss) * 0.0
            )
            / ((self.hit300 + self.hit100 + self.hit50 + self.hitmiss) * 300.0)
        ) * 100


class ReplayInfo:
    def __init__(self) -> None:
        self.mode: Optional[Mode] = None
        self.client_version: Optional[int] = None

        self.beatmap_md5: Optional[str] = None
        self.player_name: Optional[str] = None
        self.replay_md5: Optional[str] = None

        self.accuracy: Optional[Accuracy] = None
        self.score: Optional[int] = None
        self.max_combo: Optional[int] = None
        self.is_perfect: Optional[bool] = None
        self.mods: Optional[Mods] = None

        self.view: Optional[memoryview] = None

    @classmethod
    def from_file(cls, filepath: str | Path) -> "ReplayInfo":
        if not (path := Path(filepath)).exists():
            print("[Replay] Failed to load replay file, exiting!")
            os._exit(1)

        replay: "ReplayInfo" = cls()
        replay.view = memoryview(path.read_bytes())
        replay.parse()

        print("[Replay] Replay loaded!")

        return replay

    def parse(self) -> None:
        self.mode = Mode.from_bytes(self.read_byte(), "little")

        self.client_version = self.read_int()
        self.beatmap_md5 = self.read_string()
        self.player_name = self.read_string()
        self.replay_md5 = self.read_string()

        self.accuracy = Accuracy(
            hit300=self.read_short(),  # type: ignore
            hit100=self.read_short(),  # type: ignore
            hit50=self.read_short(),  # type: ignore
            hitgeki=self.read_short(),  # type: ignore
            hitkatu=self.read_short(),  # type: ignore
            hitmiss=self.read_short(),  # type: ignore
        )  # suck my dick

        self.score = self.read_int()
        self.max_combo = self.read_short()
        self.is_perfect = self.read_byte() == 0x01
        self.mods = Mods(self.read_int())

    # read FNs
    def read_byte(self, length: int = 1) -> bytes:
        if (
            self.view
        ):  # NOTE: fuckin lint kept saying "oh no this might be none ohhhh nooo!!!!"
            val = self.view[:length].tobytes()
            self.view = self.view[length:]
            return val

        return b""

    def read_short(self) -> Optional[int]:
        return int.from_bytes(self.read_byte(2), "little", signed=True)

    def read_int(self) -> int:
        return int.from_bytes(self.read_byte(4), "little", signed=True)

    def read_uleb128(self) -> int:
        val = shift = 0

        while True:
            b = self.read_byte()[0]

            val |= (b & 127) << shift
            if (b & 128) == 0x00:
                break
            shift += 7

        return val

    def read_string(self) -> str:
        if self.read_byte() == 0x00:
            return ""

        return self.read_byte(length=self.read_uleb128()).decode()


if __name__ == "__main__":
    replay = ReplayInfo.from_file("replay.osr")
    print(replay.mode)
    print(replay.max_combo)
