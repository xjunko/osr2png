from enum import IntEnum
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from app.generation.common import CanvasSettings, vector
from app.utils import CACHE_FOLDER

#
TEXT_DEFAULT_SCALE: int = 55


class TextAlignment(IntEnum):
    left = 1
    centre = 2
    right = 3


class TextComponent:
    def __init__(self, canvas: Image.Image, settings: CanvasSettings) -> None:
        self.settings = settings
        self.canvas = canvas
        self.font = self.make_font(size=TEXT_DEFAULT_SCALE)
        self.draw = ImageDraw.Draw(canvas)

    def make_font(self, size: float = TEXT_DEFAULT_SCALE) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(
            str(CACHE_FOLDER / "font.ttf"),
            size=int(size * self.settings.scale),
        )

    def draw_text(
        self,
        text: str,
        color: tuple[int, int, int] = (255, 255, 255),
        shadow_color: tuple[int, int, int] | None = (0, 0, 0),
        outline_color: tuple[int, int, int] | None = (0, 0, 0),
        outline_stroke: int = 2,
        alignment: TextAlignment = TextAlignment.left,
        text_size: int = TEXT_DEFAULT_SCALE,
        offset: list[int] = [0, 0],
    ) -> vector.Vector2:
        font = self.font
        font_size = text_size * self.settings.scale
        pos_x, pos_y = [_ * self.settings.scale for _ in offset]

        # Truncate
        if len(text) > 80:
            text = text[:80] + "..."

        # Special case
        if text_size != TEXT_DEFAULT_SCALE:
            font = self.make_font(font_size)

        # Make sure text fits the screen
        while (
            font.getsize(text)[0] > self.settings.resolution.x
            and font_size > 20 * self.settings.scale
        ):
            font_size -= 1
            font = self.make_font(font_size)

        # Font size
        text_width, text_height = self.draw.textsize(text, font=font)

        # Text alignment
        if alignment == TextAlignment.left:
            pos_x = (self.settings.resolution.x - text_width + text_width) / 2 + pos_x
            pos_y = (self.settings.resolution.y + pos_y) / 2
        elif alignment == TextAlignment.centre:
            pos_x = (self.settings.resolution.x - text_width) / 2 + pos_x
            pos_y = (self.settings.resolution.y + pos_y) / 2
        else:
            pos_x = (self.settings.resolution.x - text_width - text_width) / 2 + pos_x
            pos_y = (self.settings.resolution.y + pos_y) / 2

        # Shadow Position
        shadow_x, shadow_y = [
            position + 5 * self.settings.scale for position in [pos_x, pos_y]
        ]

        if shadow_color:  # Can be nullable to disable shadow
            self.draw.text((shadow_x, shadow_y), text, fill=shadow_color, font=font)

        extra_args: dict[str, Any] = {}

        if outline_color:
            extra_args |= {"stroke_width": outline_stroke, "stroke_fill": outline_color}

        self.draw.text((pos_x, pos_y), text, fill=color, font=font, **extra_args)

        # Return position next to text
        return vector.Vector2(
            x=int(pos_x + text_width + 5 * self.settings.scale), y=int(pos_y)
        )
