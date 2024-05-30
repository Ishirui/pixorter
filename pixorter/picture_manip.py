"""Contains top-level methods for manipulating Picture objects"""

import logging
from pathlib import Path
from typing import Generator, Iterable, Set

from .date_extract import NoMatchException, get_snap_date
from .file_manip import walk_dir
from .globals import _CURR_PICTURE, SUPPORTED_EXTENSIONS
from .picture import Picture


def collect_pictures(root_path: Path) -> Generator[Picture, None, None]:
    """Create Picture objects for all Pictures under root_path/"""
    for file in walk_dir(root_path):
        logging.debug("Considering file %s", file)
        if file.suffix[1:] in SUPPORTED_EXTENSIONS:
            try:
                snap_date = get_snap_date(file)
            except NoMatchException:
                logging.error(
                    "Could not determine snap_date for %s ! Skipping...", file
                )
                continue

            logging.debug("Extracted snap date: %s", snap_date)
            yield Picture(source_path=file, snap_date=snap_date)


def get_path_couples(
    pictures: Iterable[Picture],
) -> Generator[tuple[Path, Path], None, None]:
    """
    Get all the src/dest paths for the pictures passed as input.
    The function makes sure no duplicate paths are returned (even if the snap datetimes are equal)
    """
    used_paths: Set[Path] = set()

    for picture in pictures:
        _CURR_PICTURE["picture"] = picture
        logging.info("Considering picture %s...", picture)
        duplicate_count = 1
        while (output_path := picture.get_output_path(duplicate_count)) in used_paths:
            duplicate_count += 1
        logging.debug("Got duplicate_count=%s", duplicate_count)

        yield picture.source_path, output_path
        _CURR_PICTURE["picture"] = None
