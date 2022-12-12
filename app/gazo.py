from pathlib import Path
from typing import Any, Optional

from rosu_pp_py import PerformanceAttributes

from app.generation.canvas import Canvas, CanvasSettings, CanvasStyle, Vector2
from app.objects.beatmap import Beatmap
from app.objects.replay import ReplayInfo

#
OUTPUT_FOLDER: Path = Path.cwd() / "outputs"
OUTPUT_FOLDER.mkdir(exist_ok=True)


class Replay2Picture:
    def __init__(self) -> None:
        self.replay: ReplayInfo
        self.beatmap: Beatmap
        self.info: PerformanceAttributes

    def calculate(self) -> None:
        print("[Replay2Picture] Calculating PP,", end="")

        self.info = self.beatmap.calculate_pp(
            mods=self.replay.mods,  # type: ignore
            acc=self.replay.accuracy.value,  # type: ignore
            combo=self.replay.max_combo,  # type: ignore
            misses=self.replay.accuracy.hitmiss,  # type: ignore
        )

        print(" done!")

    def generate(self, style: int = 1, **kwargs: dict[Any, Any]) -> Path:
        settings: CanvasSettings = CanvasSettings(
            style=CanvasStyle(style),
            context=self,
            **kwargs,
        )

        canvas: Canvas = Canvas.from_settings(settings=settings)

        image = canvas.generate()
        filename: str = "[{name}] - ({artist} - {title} [{diff}]).png".format(
            name=canvas.context.replay.player_name,
            artist=canvas.context.beatmap.artist,
            title=canvas.context.beatmap.title,
            diff=canvas.context.beatmap.difficulty,
        )

        result_image_path = OUTPUT_FOLDER / filename
        image.save(fp=result_image_path, format="png")

        return result_image_path

    @classmethod
    def from_replay_file(
        cls, replay_path: Path, beatmap_file: Optional[Path] = None
    ) -> "Replay2Picture":
        print(f"[Replay2Picture] File: `{replay_path.name}`")

        self: "Replay2Picture" = cls()
        self.replay = ReplayInfo.from_file(replay_path)

        if not beatmap_file and self.replay.beatmap_md5:
            print("[Replay2Picture] No Beatmap file passed, getting from osu!")
            self.beatmap = Beatmap.from_md5(self.replay.beatmap_md5)
        elif beatmap_file:
            print("[Replay2Picture] Beatmap file passed, using that instead.")
            self.beatmap = Beatmap.from_osu_file(beatmap_file)

        return self

    @classmethod
    def from_beatmap_file(cls, beatmap_file: Path) -> "Replay2Picture":
        ...
