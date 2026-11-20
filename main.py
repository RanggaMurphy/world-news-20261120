#!/usr/bin/env python3
"""Copy the entry image to the grader output directory.

Stdlib only: the image grader runs python:3.13-slim with no Pillow and no
system fonts, so this program must not import anything beyond the standard
library. The image itself lives in this repository as entry.png; all this
program does is copy it to MAKEFUN_OUTPUT_DIR.
"""

import os
import shutil
import sys


def _source_dir():
    """Where entry.png lives: the bot dir when the harness sets it, else
    the folder holding this file (the repository root)."""
    bot_dir = os.environ.get("MAKEFUN_BOT_DIR")
    if bot_dir:
        return bot_dir
    return os.path.dirname(os.path.abspath(__file__))


def main():
    src = os.path.join(_source_dir(), "entry.png")
    if not os.path.isfile(src):
        print("entry.png not found next to main.py: %s" % src, file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.dirname(
        os.path.abspath(__file__)
    )
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(out_dir, "entry.png"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
