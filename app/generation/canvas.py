from dataclasses import dataclass
from typing import TYPE_CHECKING

from PIL import Image

import app.utils
from app.generation import styles
from app.generation.common import CanvasSettings, CanvasStyle
from app.generation.common.vector import Vector2
from app.generation.text.text import TextComponent

if TYPE_CHECKING:
    from app.gazo import Replay2Picture


@dataclass
class DefaultAssets:
    avatar: Image.Image
    background: Image.Image
    star: Image.Image
    miss: Image.Image

    @classmethod
    def load_default_assets(cls, settings: CanvasSettings) -> "DefaultAssets":
        avatar = Image.open(app.utils.CACHE_FOLDER / "default_avatar.png").convert(
            "RGBA"
        )
        background = Image.open(
            app.utils.CACHE_FOLDER / "default_background.png"
        ).convert("RGBA")

        star = Image.open(app.utils.CACHE_FOLDER / "default_star.png").convert("RGBA")
        miss = Image.open(app.utils.CACHE_FOLDER / "default_miss.png").convert("RGBA")

        # Resize background to fit image
        background = app.utils.resize_image_to_resolution_but_keep_ratio(
            background, settings.resolution
        )

        return cls(avatar=avatar, background=background, star=star, miss=miss)


@dataclass
class Assets:
    default: DefaultAssets

    #
    font: TextComponent

    #
    background: Image.Image
    avatar: Image.Image


class Canvas:
    def __init__(self) -> None:
        self.settings: CanvasSettings
        self.context: Replay2Picture
        self.assets: Assets

        self.canvas: Image.Image

    def generate(self) -> Image.Image:
        # Generate with style
        if self.settings.style == CanvasStyle.default:
            styles.default.generate(self)

        # Convert to RGB format
        self.canvas = self.canvas.convert("RGB")

        return self.canvas

    @classmethod
    def from_settings(cls, settings: CanvasSettings) -> "Canvas":
        canvas: "Canvas" = cls()
        canvas.settings = settings
        canvas.context = settings.context

        # Set up canvas
        canvas.canvas = Image.new(
            mode="RGBA", size=(canvas.settings.resolution.x, canvas.settings.resolution.y)  # type: ignore | cope
        )

        # Load Assets
        default = DefaultAssets.load_default_assets(settings=canvas.settings)
        background = app.utils.resize_image_to_resolution_but_keep_ratio(
            Image.open(canvas.context.beatmap.get_beatmap_background()),
            canvas.settings.resolution,
        )

        avatar = Image.open(app.utils.get_player_avatar(canvas.context.replay.player_name)).convert("RGBA")  # type: ignore

        canvas.assets = Assets(
            default=default,
            background=background,
            avatar=avatar,  # type: ignore
            font=TextComponent(canvas.canvas, canvas.settings),
        )

        return canvas
