from typing import TYPE_CHECKING

from PIL import Image, ImageFilter, ImageOps

import app.utils
from app.generation.common import vector
from app.generation.text.text import TEXT_DEFAULT_SCALE, TextAlignment, TextComponent

if TYPE_CHECKING:
    from app.generation.canvas import Canvas

__all__: list[str] = ["generate"]


# Internals
def _generate_background(canvas: "Canvas") -> None:
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
            int(canvas.settings.resolution.x),
            int(canvas.settings.resolution.y),
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

    canvas.canvas.paste(
        dim,
        (
            int((canvas.settings.resolution.x - dim.width) / 2),
            int(160 * canvas.settings.scale),
        ),
        mask=dim,
    )


def _generate_line(canvas: "Canvas") -> None:
    # Line
    top_space: int = int(160 * canvas.settings.scale)

    top_line_back = Image.new(
        "RGBA",
        (int(canvas.settings.resolution.x), int(6 * canvas.settings.scale)),
        (0, 0, 0, 255),
    )

    top_line = Image.new(
        "RGBA",
        (int(canvas.settings.resolution.x), int(5 * canvas.settings.scale)),
        (255, 255, 255, 255),
    )

    top_line_bloom = Image.new(
        "RGBA",
        (int(canvas.settings.resolution.x), int(100 * canvas.settings.scale)),
    )

    _top_line_bloom_line = top_line.resize(
        (int(canvas.settings.resolution.x), int(10 * canvas.settings.scale)),
    )

    top_line_bloom.paste(
        _top_line_bloom_line,
        (
            int((top_line_bloom.width - _top_line_bloom_line.width) / 2),
            int((top_line_bloom.height - _top_line_bloom_line.height) / 2),
        ),
        mask=_top_line_bloom_line,
    )

    top_line_bloom = top_line_bloom.filter(ImageFilter.GaussianBlur(10))

    canvas.canvas.paste(
        top_line_bloom,
        (0, int(top_space - top_line_bloom.height / 2)),
        mask=top_line_bloom,
    )

    canvas.canvas.paste(
        top_line_back,
        (0, int(top_space - top_line_back.height / 2)),
        mask=top_line_back,
    )

    canvas.canvas.paste(
        top_line,
        (0, int(top_space - top_line.height / 2)),
        mask=top_line,
    )


def _generate_avatar(canvas: "Canvas") -> None:
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
            int(40 * canvas.settings.scale),
            int(220 * canvas.settings.scale),
        ),
    )


def _generate_text(canvas: "Canvas") -> None:
    # Text
    canvas.assets.font.draw_text(
        f"{canvas.context.replay.player_name}",
        alignment=TextAlignment.centre,
        offset=[0, -650],
        outline_stroke=4,
        outline_color=(0, 0, 0),
        shadow_color=None,
        text_size=int(TEXT_DEFAULT_SCALE * 1.2),
        bloom_color=(255, 255, 255),
    )

    # Artist
    canvas.assets.font.draw_text(
        f"{canvas.context.beatmap.artist}",
        alignment=TextAlignment.centre,
        offset=[100, -320],
        shadow_color=None,
        text_size=int(TEXT_DEFAULT_SCALE * 0.9),
        bloom_color=(255, 255, 255),
        text_canvas_size=[800 * canvas.settings.scale, 800 * canvas.settings.scale],
    )

    # Title
    canvas.assets.font.draw_text(
        f"{canvas.context.beatmap.title}",
        alignment=TextAlignment.centre,
        offset=[100, -160],
        shadow_color=None,
        text_size=int(TEXT_DEFAULT_SCALE * 0.9),
        color=(255, 255, 100),
        bloom_color=(255, 255, 100),
        text_canvas_size=[800 * canvas.settings.scale, 800 * canvas.settings.scale],
    )

    # Diff
    canvas.assets.font.draw_text(
        f"[{canvas.context.beatmap.difficulty}] +{canvas.context.replay.mods!r} | {canvas.context.replay.max_combo}/{canvas.context.beatmap.max_combo}x",
        alignment=TextAlignment.centre,
        offset=[100, 50],
        shadow_color=None,
        text_size=int(TEXT_DEFAULT_SCALE * 0.9),
        bloom_color=(255, 255, 255),
        text_canvas_size=[800 * canvas.settings.scale, 800 * canvas.settings.scale],
    )

    # PP
    canvas.assets.font.draw_text(
        f"{canvas.context.info.pp:.0f}pp",  # type: ignore
        alignment=TextAlignment.centre,
        offset=[0, 350],
        shadow_color=None,
        text_size=int(TEXT_DEFAULT_SCALE * 1.2),
        bloom_color=(255, 255, 255),
    )

    # Acc
    canvas.assets.font.draw_text(
        f"{canvas.context.replay.accuracy.value:.2f}%",  # type: ignore
        alignment=TextAlignment.centre,
        offset=[350, 300],
        shadow_color=None,
        text_size=int(TEXT_DEFAULT_SCALE * 0.9),
        bloom_color=(255, 255, 255),
    )

    # Judge
    judge_text: str = "FC"
    judge_color: tuple[int, int, int] = (255, 255, 100)

    # NOTE: If missed for sure.
    if canvas.context.replay.accuracy and canvas.context.replay.accuracy.hitmiss:
        judge_text = f"{canvas.context.replay.accuracy.hitmiss}xMiss"
        judge_color = (255, 0, 0)

    # HACK: If there's no misses but combo doesnt reach >= 60% of the max beatmap combo,
    # HACK: Just show "?"
    if (canvas.context.replay.max_combo / canvas.context.beatmap.max_combo) <= 0.6 and judge_text == "FC":  # type: ignore
        judge_text = "?"
        judge_color = (255, 255, 0)

    canvas.assets.font.draw_text(
        judge_text,  # type: ignore
        alignment=TextAlignment.centre,
        offset=[350, 450],
        shadow_color=None,
        text_size=int(TEXT_DEFAULT_SCALE * 0.9),
        color=judge_color,
        bloom_color=judge_color,
    )


def generate(canvas: "Canvas") -> None:
    print("[Style::Akatsuki] Generating!")

    _generate_background(canvas)
    _generate_line(canvas)
    _generate_avatar(canvas)
    _generate_text(canvas)
