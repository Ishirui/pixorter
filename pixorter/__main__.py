"""
Main entrypoint for Pixorter.
"""

import argparse
import logging
from pathlib import Path

from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

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
        default="WARNING",
    )

    output = parser.parse_args()
    output.input_path = output.input_path.resolve()
    output.output_path = output.output_path.resolve()

    return output


def setup_logging(level: int):
    """Setup logging for the script (message format, extra args etc.)"""
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(picture)s - %(message)s"
    )

    # See stackoverflow.com/questions/17558552/how-do-i-add-custom-field-to-python-log-format-string
    old_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.picture = _CURR_PICTURE["picture"]
        return record

    logging.setLogRecordFactory(record_factory)

    logging.getLogger().setLevel(level)


def main():
    """Main method for Pixorter"""
    args = parse_arguments()
    setup_logging(args.loglevel)

    logging.debug("Parsed arguments: %s", vars(args))

    if args.hardlinks:
        operation = hardlink
    elif args.symlinks:
        operation = symlink
    elif args.copies:
        operation = copy
    else:
        operation = move

    logging.info("Selected operation: %s.", operation.__name__)

    if args.dry_run:
        logging.info("Dry running ! No changes will be applied.")
        operation = dry_run

    # Discover existing pictures
    # Convert to list so we can see the execution now and get the total n° of pics for later
    with logging_redirect_tqdm():
        pictures = list(
            tqdm(collect_pictures(args.input_path), desc="Discovering Pictures...")
        )
        n_pictures = len(pictures)
        logging.info("Found %s pictures", n_pictures)

        for src_path, dest_path in tqdm(
            get_path_couples(pictures), total=n_pictures, desc="Moving Pictures"
        ):
            abs_src_path = args.input_path.resolve() / src_path
            logging.debug("Transformed %s -> %s", src_path, abs_src_path)

            abs_dest_path = args.output_path.resolve() / dest_path
            logging.debug("Transformed %s -> %s", dest_path, abs_dest_path)

            try:
                operation(abs_src_path, abs_dest_path)
            # pylint: disable-next=broad-exception-caught
            except Exception as exc:
                logging.exception("Could not handle image %s !", src_path, exc_info=exc)


main()
