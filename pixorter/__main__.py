"""
Main entrypoint for Pixorter.
"""

import argparse
import logging
from pathlib import Path

from .file_manip import copy, hardlink, move, symlink
from .picture_manip import collect_pictures, get_path_couples


def parse_arguments() -> argparse.Namespace:
    """Define all CLI arguments for the script"""
    parser = argparse.ArgumentParser(
        prog="Pixorter",
        description=__doc__,
    )

    parser.add_argument("input_path", type=Path)

    parser.add_argument("output_path", type=Path)

    copy_mode = parser.add_mutually_exclusive_group()
    copy_mode.add_argument("--hardlinks", action="store_true")
    copy_mode.add_argument("--symlinks", action="store_true")
    copy_mode.add_argument("--copies", action="store_true")

    parser.add_argument("--dry-run", action="store_true")

    parser.add_argument(
        "--loglevel",
        # pylint: disable-next=protected-access
        choices=logging._nameToLevel.keys(),
    )

    return parser.parse_args()


def main():
    """Main method for Pixorter"""
    args = parse_arguments()

    if args.hardlinks:
        operation = hardlink
    elif args.symlinks:
        operation = symlink
    elif args.copies:
        operation = copy
    else:
        operation = move

    pictures = collect_pictures(args.input_path)
    for src_path, dest_path in get_path_couples(pictures):
        abs_src_path = args.input_path.resolve() / src_path
        abs_dest_path = args.output_path.resolve() / dest_path

        operation(abs_src_path, abs_dest_path)
