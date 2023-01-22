"""
    main.py - the start of everything
"""

__author__ = "xJunko"
__discord__ = "FireRedz#0537"

import argparse
import sys
from pathlib import Path

import app.utils
from app.gazo import Replay2Picture
from app.generation.common import CanvasStyle, vector
from app.version import Version

#
CURRENT_VERSION = Version.from_str("0|7|4")


def main(argv: list[str]) -> int:
    """Ensure shit is okay to run"""
    for early_task in [app.utils.ensure_directories, app.utils.ensure_default_assets]:
        if ret_code := early_task():
            return ret_code

    """ command-line arguments """
    parser = argparse.ArgumentParser(
        description="An open-source osu! thumbnail generator for lazy circle clickers."
    )

    # Info
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"osr2png v{CURRENT_VERSION}",
    )

    # Source
    parser.add_argument(
        "-r",
        "--replay",
        help="[Optional] The path of the .osr file",
    )
    parser.add_argument(
        "-b",
        "--beatmap",
        help="[Optional] The path of the .osu file, if using a custom beatmap.",
    )

    # Image Gen
    parser.add_argument(
        "-m",
        "--message",
        help="[Optional] The extra text at the bottom",
        type=str,
        default="",
    )

    parser.add_argument(
        "-s",
        "--style",
        help="Style of Image, [{}]".format(
            " ".join([f"{n.value}: {n.name}" for n in CanvasStyle])
        ),
        type=int,
        default=1,
    )
    parser.add_argument(
        "-width",
        "--width",
        help="[Optional] The width of the image.",
        type=int,
        default=1920,
    )
    parser.add_argument(
        "-height",
        "--height",
        help="[Optional] The width of the image.",
        type=int,
        default=1080,
    )

    parser.add_argument(
        "-dim",
        "--background-dim",
        help="[Optional] The dim of beatmap background.",
        type=float,
        default=0.6,
    )

    parser.add_argument(
        "-blur",
        "--background-blur",
        help="[Optional] The blur of beatmap background.",
        type=float,
        default=5,
    )

    parser.add_argument(
        "-border",
        "--background-border",
        help="[Optional] The border of beatmap background's dim.",
        type=float,
        default=25,
    )

    args = parser.parse_args()

    if not args.replay and not args.beatmap:
        parser.print_help()
        parser.error(
            "You didnt give me shit, please pass `.osr` or `.osu` file into the params."
        )

    if args.replay:
        replay_path: Path = Path(args.replay)
        beatmap_path: Path | None = None

        if args.beatmap:
            beatmap_path = Path(args.beatmap)

        replay = Replay2Picture.from_replay_file(
            replay_path=Path(replay_path), beatmap_file=beatmap_path
        )
    else:
        # Generate from beatmap file only, SS everything.
        # TODO:
        parser.error("Beatmap only ImageGen is not supported yet.")
        replay = Replay2Picture()

    # Common
    replay.calculate()
    replay.generate(
        style=args.style,
        resolution=vector.Vector2(x=args.width, y=args.height),  # type: ignore
        background_blur=args.background_blur,
        background_dim=args.background_dim,
        background_border=args.background_border,
        message=args.message,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
