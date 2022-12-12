from typing import TYPE_CHECKING

from PIL import Image, ImageFilter

from app.generation.common import vector
from app.generation.text.text import TEXT_DEFAULT_SCALE, TextAlignment, TextComponent

if TYPE_CHECKING:
    from app.generation.canvas import Canvas

import app.utils


def generate(canvas: "Canvas") -> None:
    print("[Style::Default] Generating!")

    # Background
    if canvas.settings.background_blur:
        # If blur
        canvas.assets.background = canvas.assets.background.filter(
            ImageFilter.GaussianBlur(radius=canvas.settings.background_blur)
        )

    canvas.canvas.paste(canvas.assets.background)

    # Dim
    dim = Image.new(
        "RGBA",
        size=(
            int(
                canvas.settings.resolution.x
                - (canvas.settings.background_border * canvas.settings.scale)
            ),
            int(
                canvas.settings.resolution.y
                - (canvas.settings.background_border * canvas.settings.scale)
            ),
        ),
        color=(0, 0, 0, int(255 * canvas.settings.background_dim)),
    )

    canvas.canvas.paste(
        dim,
        (
            int((canvas.settings.resolution.x - dim.width) / 2),
            int((canvas.settings.resolution.y - dim.height) / 2),
        ),
        mask=dim,
    )

    # Avatar
    canvas.assets.avatar = app.utils.resize_image_to_resolution_but_keep_ratio(
        canvas.assets.avatar,
        vector.Vector2(
            x=200.0 * canvas.settings.scale, y=200.0 * canvas.settings.scale
        ),
    )

    avatar_with_border = Image.new(
        "RGBA",
        (int(205 * canvas.settings.scale), int(205 * canvas.settings.scale)),
        (220, 220, 220, 255),
    )

    avatar_with_border.paste(
        canvas.assets.avatar,
        (
            int((avatar_with_border.width - canvas.assets.avatar.width) / 2),
            int((avatar_with_border.height - canvas.assets.avatar.height) / 2),
        ),
        mask=canvas.assets.avatar,
    )

    canvas.canvas.paste(
        avatar_with_border,
        (
            int((canvas.settings.resolution.x - avatar_with_border.width) / 2),
            int((canvas.settings.resolution.y - avatar_with_border.height) / 2),
        ),
    )

    # Text

    # Title
    canvas.assets.font.draw_text(
        f"{canvas.context.beatmap.artist} - {canvas.context.beatmap.title}",
        alignment=TextAlignment.centre,
        offset=[0, -550],
    )

    # Diff
    canvas.assets.font.draw_text(
        f"[{canvas.context.beatmap.difficulty}]",
        alignment=TextAlignment.centre,
        offset=[0, -400],
    )

    # Acc
    canvas.assets.font.draw_text(
        f"{canvas.context.replay.accuracy.value:.2f}%",  # type: ignore
        alignment=TextAlignment.right,
        offset=[-120, -100],
    )

    # Mods
    canvas.assets.font.draw_text(
        f"{canvas.context.replay.mods}",  # type: ignore
        alignment=TextAlignment.right,
        offset=[-120, 60],
    )

    # Star
    canvas.assets.default.star = app.utils.resize_image_to_resolution_but_keep_ratio(
        canvas.assets.default.star,
        vector.Vector2(x=60.0 * canvas.settings.scale, y=60.0 * canvas.settings.scale),
    )

    star_text_position = canvas.assets.font.draw_text(
        f"{canvas.context.info.difficulty.stars:.2f}",  # type: ignore
        alignment=TextAlignment.left,
        offset=[120, -100],
    )

    canvas.canvas.paste(
        canvas.assets.default.star,
        [star_text_position.x, star_text_position.y],  # type: ignore
        mask=canvas.assets.default.star,
    )

    # PP
    canvas.assets.font.draw_text(
        f"{canvas.context.info.pp:.2f}pp",  # type: ignore
        alignment=TextAlignment.left,
        offset=[120, 60],
    )

    # Miss (if theres any)
    if canvas.context.replay.accuracy and canvas.context.replay.accuracy.hitmiss:
        canvas.assets.default.miss = (
            app.utils.resize_image_to_resolution_but_keep_ratio(
                canvas.assets.default.miss,
                vector.Vector2(
                    x=120 * canvas.settings.scale, y=120 * canvas.settings.scale
                ),
            )
        )

        # If theres message we can make the miss text smaller (by like 0.85)
        miss_text_scale: float = 1.0
        if canvas.settings.message:
            miss_text_scale = 0.75

        canvas.assets.font.draw_text(
            f"{canvas.context.replay.accuracy.hitmiss}xMiss",  # type: ignore
            alignment=TextAlignment.centre,
            offset=[0, 240],
            text_size=int(TEXT_DEFAULT_SCALE * miss_text_scale),
            color=(255, 0, 0),
            outline_color=(139, 0, 0),
            outline_stroke=4,
            shadow_color=None,
        )

    if canvas.settings.message:
        y_offset: float = 0.0

        if canvas.context.replay.accuracy and canvas.context.replay.accuracy.hitmiss:
            y_offset += 100.0

        canvas.assets.font.draw_text(
            canvas.settings.message,  # type: ignore
            alignment=TextAlignment.centre,
            offset=[0, int(240 + y_offset)],
            text_size=int(TEXT_DEFAULT_SCALE * 1.4),
        )
