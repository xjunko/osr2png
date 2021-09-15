import logging
import argparse
import requests
from pathlib import Path
from autologging import TRACE, logged, traced

#
from gen.canvas import Canvas

#
from objects.api import osuAPI, ASSETS_FOLDER
from objects.replay import Replay
from objects.settings import Settings


class Version:
    major: int
    minor: int
    patch: int
    message: str

    def __init__(self) -> None:
        self.major = self.minor = self.patch = 0
        self.message = ""

    def __repr__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __gt__(self, other: object) -> bool:
        return [self.major, self.minor, self.patch] > [
            other.major,
            other.minor,
            other.patch,
        ]

    def __lt__(self, other: object) -> bool:
        return [self.major, self.minor, self.patch] < [
            other.major,
            other.minor,
            other.patch,
        ]

    @classmethod
    def from_str(cls: object, version_str: str) -> object:
        items = version_str.strip().split("|")
        numbers = [int(x) for x in items[0].strip().split(".")]
        message = items[1] if len(items) > 1 else ""

        version = cls()
        version.major = numbers[0]
        version.minor = numbers[1]
        version.patch = numbers[2]
        version.message = message

        return version


@logged
@traced
class osr2png:
    def __init__(self, replay_path: str, ignore_updates: bool = False) -> None:
        # Check version first
        if ignore_updates:
            print("[osr2png] Ignoring version updates!")
        else:
            self.check_version()

        #
        self.settings = Settings.make_settings(replay_path)

    def check_version(self) -> None:
        # check our version
        if not (path := ASSETS_FOLDER / "version.txt").exists():
            print(
                "[osr2png] No version file found, if you dont care about updating then ignore this."
            )
            return
        else:
            # check against git version
            local_version = Version.from_str(path.read_text())
            print(
                f"[osr2png] Running on version: {local_version} - checking git version!"
            )

            try:
                git_version = Version.from_str(
                    requests.get(
                        "https://raw.githubusercontent.com/FireRedz/osr2png/master/assets/version.txt"
                    ).content.decode()
                )
            except:
                return print(f"[osr2png] Cannot get the git version, ignoring updates!")

            print(f"[osr2png] Git version is {git_version}!")

            # git version is newer
            if git_version > local_version:
                print("[osr2png] Your osr2png is outdated!")
                print(
                    "[osr2png] Please check `https://github.com/FireRedz/osr2png/releases/latest` for newer releases!"
                )

                if git_version.message:
                    print(f"[osr2png] Version message from git: {git_version.message}")

    def generate(self) -> None:
        image = Canvas(self.settings)
        image.generate()
        image.save()


if __name__ == "__main__":
    # Logging
    if (runtime_log := Path("runtime.log")).exists():
        runtime_log.unlink()
    logging.basicConfig(filename="runtime.log", level=TRACE)

    # ok commandline time
    parser = argparse.ArgumentParser(
        prog="osr2png", description="Generates video thumbnail from replay file!"
    )
    parser.add_argument("replay", type=str, help=".osr file path")
    parser.add_argument(
        "--ignore-update",
        help="Enable this if you dont want the thing bitching about updates.",
        action="store_true",
    )
    args = parser.parse_args()

    # real shit
    app = osr2png(replay_path=args.replay, ignore_updates=args.ignore_update)
    # app.generate()
