from enum import IntEnum
from PIL import Image, ImageDraw, ImageFont

from objects.settings import Settings
from objects.api import ASSETS_FOLDER


class TextAlignment(IntEnum):
    left = 1
    centre = 2
    right = 3


class TextComponent:
    def __init__(self, canvas: Image.Image, settings: Settings) -> None:
        self.settings = settings
        self.canvas = canvas
        self.font = self.make_font(size=55)
        self.draw = ImageDraw.Draw(canvas)

    def make_font(self, size: int = 55) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(
            str(ASSETS_FOLDER / self.settings.font),
            size=int(size * self.settings.scale),
        )

    def draw_text(
        self,
        text: str,
        color: tuple = (255, 255, 255),
        shadow_color: tuple = (0, 0, 0),
        alignment: TextAlignment = TextAlignment.left,
        text_size: int = 55,
        offset: list = [0, 0],
    ) -> None:
        font = self.font
        font_size = text_size * self.settings.scale
        pos_x, pos_y = [_ * self.settings.scale for _ in offset]

        # Truncate
        if len(text) > 80:
            text = text[:80] + "..."

        # Make sure text fits the screen
        while (
            font.getsize(text)[0] > self.settings.resolution[0]
            and font_size > 20 * self.settings.scale
        ):
            font_size -= 1
            font = self.make_font(font_size)

        # Font size
        text_width, text_height = self.draw.textsize(text, font=font)

        # Text alignment
        if alignment == TextAlignment.left:
            pos_x = (self.settings.resolution[0] - text_width + text_width) / 2 + pos_x
            pos_y = (self.settings.resolution[1] + pos_y) / 2
        elif alignment == TextAlignment.centre:
            pos_x = (self.settings.resolution[0] - text_width) / 2 + pos_x
            pos_y = (self.settings.resolution[1] + pos_y) / 2
        else:
            pos_x = (self.settings.resolution[0] - text_width - text_width) / 2 + pos_x
            pos_y = (self.settings.resolution[1] + pos_y) / 2

        # Shadow Position
        shadow_x, shadow_y = [
            position + 5 * self.settings.scale for position in [pos_x, pos_y]
        ]

        if shadow_color:  # Can be nullable to disable shadow
            self.draw.text((shadow_x, shadow_y), text, fill=shadow_color, font=font)

        self.draw.text((pos_x, pos_y), text, fill=color, font=font)

        # Return position next to text
        return [int(pos_x + text_width + 5 * self.settings.scale), int(pos_y)]
