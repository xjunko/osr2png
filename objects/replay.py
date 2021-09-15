"""

    piss simple replay parser to get metadata
    imagine importing someone else replay lib

"""
import os
from pathlib import Path
from enum import IntEnum
from dataclasses import dataclass


class Mode(IntEnum):
    standard = 0
    taiko = 1
    ctb = 2
    mania = 3


@dataclass
class Accuracy:
    hit300: int
    hit100: int
    hit50: int
    hitgeki: int
    hitkatu: int
    hitmiss: int

    @property
    def value(self) -> float:
        # god here we go
        return (
            (
                (self.hit300) * 300
                + (self.hit100) * 100
                + (self.hit50) * 50
                + (self.hitmiss) * 0
            )
            / ((self.hit300 + self.hit100 + self.hit50 + self.hitmiss) * 300)
        ) * 100


class Replay:
    def __init__(self) -> None:
        self.mode: Mode = None
        self.client_version: int = None

        self.beatmap_md5: str = None
        self.player_name: str = None
        self.replay_md5: str = None

        self.accuracy: Accuracy = None
        self.score: int = None
        self.max_combo: int = None
        self.is_perfect: bool = None
        self.mods: int = None

        self.view: memoryview = None

    @classmethod
    def from_file(cls: object, filepath: str) -> object:
        if not (path := Path(filepath)).exists():
            print("[Replay] File did not exists, exiting!")
            os._exit(1)

        replay = cls()
        replay.view = memoryview(path.read_bytes())
        replay.parse()

        print("[Replay] Replay loaded!")
        return replay

    def parse(self) -> None:
        self.mode = self.read_byte()
        self.client_version = self.read_int()
        self.beatmap_md5 = self.read_string()
        self.player_name = self.read_string()
        self.replay_md5 = self.read_string()

        self.accuracy = Accuracy(
            hit300=self.read_short(),
            hit100=self.read_short(),
            hit50=self.read_short(),
            hitgeki=self.read_short(),
            hitkatu=self.read_short(),
            hitmiss=self.read_short(),
        )

        self.score = self.read_int()
        self.max_combo = self.read_short()
        self.is_perfect = self.read_byte() == 0x01
        self.mods = self.read_int()

    # read FNs
    def read_byte(self, length: int = 1) -> bytes:
        val = self.view[:length].tobytes()
        self.view = self.view[length:]
        return val

    def read_short(self) -> int:
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
