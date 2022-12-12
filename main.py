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
from app.version import Version

#
CURRENT_VERSION = Version.from_str("0|6|1")


def main(argv: list[str]) -> int:
    """Ensure shit is okay to run"""
    for early_task in [app.utils.ensure_directories, app.utils.ensure_default_assets]:
        if ret_code := early_task():
            return ret_code

    """ command-line arguments """
    parser = argparse.ArgumentParser(
        description="An open-source osu! thumbnail generator for lazy circle clickers."
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
        "-s",
        "--style",
        help="[TODO] Style of Image | Unimplemented!",
        type=int,
        default=1,
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
    replay.generate(style=args.style)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
