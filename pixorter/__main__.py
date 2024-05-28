"""
Main entrypoint for Pixorter.
"""

import argparse
import logging
from pathlib import Path

from .file_manip import copy, dry_run, hardlink, move, symlink
from .globals import _CURR_PICTURE
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


def setup_logging(level: int):
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(picture)s - %(message)s"
    )
    logging.getLogger().setLevel(level)


def main():
    """Main method for Pixorter"""
    args = parse_arguments()
    setup_logging(args.loglevel)

    logging.debug("Parsed arguments: %s", vars(args), extra=_CURR_PICTURE)

    if args.hardlinks:
        operation = hardlink
    elif args.symlinks:
        operation = symlink
    elif args.copies:
        operation = copy
    else:
        operation = move

    logging.info("Selected operation: %s.", operation.__name__, extra=_CURR_PICTURE)

    if args.dry_run:
        logging.info("Dry running ! No changes will be applied.", extra=_CURR_PICTURE)
        operation = dry_run

    pictures = collect_pictures(args.input_path)

    for src_path, dest_path in get_path_couples(pictures):
        abs_src_path = args.input_path.resolve() / src_path
        logging.debug(
            "Transformed %s -> %s", src_path, abs_src_path, extra=_CURR_PICTURE
        )

        abs_dest_path = args.output_path.resolve() / dest_path
        logging.debug(
            "Transformed %s -> %s", dest_path, abs_dest_path, extra=_CURR_PICTURE
        )

        operation(abs_src_path, abs_dest_path)
