import logging
from pathlib import Path
from autologging import TRACE, logged, traced

#
from gen.canvas import Canvas

#
from objects.api import osuAPI
from objects.replay import Replay
from objects.settings import Settings


@logged
@traced
class osr2png:
    def __init__(self, replay_path: str) -> None:
        self.settings = Settings.make_settings(replay_path)

    def generate(self) -> None:
        image = Canvas(self.settings)
        image.generate()
        image.save()


if __name__ == "__main__":
    if (runtime_log := Path("runtime.log")).exists():
        runtime_log.unlink()

    logging.basicConfig(filename="runtime.log", level=TRACE)
    app = osr2png(replay_path="assets/replay.osr")
    app.generate()
