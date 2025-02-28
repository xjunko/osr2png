from __future__ import annotations  # Ensure this is the first line

import argparse
import sys
from pathlib import Path

# Attempt to import Gooey
try:
    from gooey import Gooey, GooeyParser
    gooey_available = True
except ImportError:
    gooey_available = False

import app.utils
from app.gazo import Replay2Picture
from app.generation.common import CanvasStyle, vector
from app.version import Version

CURRENT_VERSION = Version.from_str("0.8.1")

# Conditionally apply the Gooey decorator
if gooey_available:
    @Gooey(program_name="osr2png GUI")
    def main(argv: list[str] = None) -> int:
        return run_main(argv)
else:
    def main(argv: list[str] = None) -> int:
        return run_main(argv)

def run_main(argv: list[str] = None) -> int:
    """Ensure program is okay to run"""
    for early_task in [app.utils.ensure_directories, app.utils.ensure_default_assets]:
        if ret_code := early_task():
            return ret_code

    """Command-line arguments"""
    if gooey_available:
        parser = GooeyParser(
            description="An open-source osu! thumbnail generator for lazy circle clickers.",
        )
    else:
        parser = argparse.ArgumentParser(
            description="An open-source osu! thumbnail generator for lazy circle clickers.",
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
        **({"widget": "FileChooser"} if gooey_available else {}),
    )
    parser.add_argument(
        "-b",
        "--beatmap",
        help="[Optional] The path of the .osu file, if using a custom beatmap.",
        **({"widget": "FileChooser"} if gooey_available else {}),
    )

    # Where to save
    parser.add_argument(
        "-o",
        "--output",
        help="[Optional] Change generated image filename.",
        **({"widget": "FileSaver"} if gooey_available else {}),
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
            " ".join([f"{n.value}: {n.name}" for n in CanvasStyle]),
        ),
        type=int,
        default=1,
        choices=[n.value for n in CanvasStyle],  # Ensure choices align with CanvasStyle values
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
        help="[Optional] The height of the image.",
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

    # Misc options
    parser.add_argument(
        "-skip",
        "--skip-update",
        help="[Optional] Don't check for a new version on Github.",
        action="store_true",
    )

    args = parser.parse_args(argv)

    if not args.replay and not args.beatmap:
        parser.print_help()
        parser.error(
            "No argument passed, please provide a `.osr` or `.osu` file.",
        )

    if args.replay:
        # Check for update
        if not args.skip_update:
            try:
                app.utils.ensure_up_to_date(CURRENT_VERSION)
            except Exception:
                print("[Version] Failed to reach GitHub.")

        replay_path: Path = Path(args.replay)
        beatmap_path: Path | None = None

        if args.beatmap:
            beatmap_path = Path(args.beatmap)

        replay = Replay2Picture.from_replay_file(
            replay_path=replay_path,
            beatmap_file=beatmap_path,
        )
    else:
        # Generate from beatmap file only, SS everything.
        # TODO:
        parser.error("Beatmap-only ImageGen is not supported yet.")
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
        custom_filename=args.output,
    )

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
