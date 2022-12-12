import os
import platform
import sys
from pathlib import Path

from PyInstaller.__main__ import run as run_pyinstaller

#
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

OS_NAME: str = sys.platform
IS_LINUX: bool = OS_NAME == "linux"


def main() -> int:
    output_folder: Path = Path.cwd() / "build"
    output_file: Path = output_folder / ("osr2png" + ["", ".exe"][not IS_LINUX])

    print(f"Building osr2png for {OS_NAME} {platform.machine()}.")
    print(f"Final file: {output_file}")

    opts = [
        f"--name=osr2png",
        "--upx-exclude=vcruntime140.dll",
        "--noconfirm",
        "--onefile",
        "main.py",
    ]

    print(f"Running PyInstaller with {opts}")
    run_pyinstaller(opts)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
