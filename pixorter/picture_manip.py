"""Contains top-level methods for manipulating Picture objects"""

import logging
from pathlib import Path
from typing import Generator, Iterable, Set

from .date_extract import get_snap_date
from .file_manip import walk_dir
from .globals import _CURR_PICTURE, SUPPORTED_EXTENSIONS
from .picture import Picture


def collect_pictures(root_path: Path) -> Generator[Picture, None, None]:
    for file in walk_dir(root_path):
        logging.debug("Considering file %s", file, extra=_CURR_PICTURE)
        if file.suffix in SUPPORTED_EXTENSIONS:
            snap_date = get_snap_date(file)
            logging.debug("Extracted snap date: %s", snap_date, extra=_CURR_PICTURE)
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
        logging.info("Considering picture %s...", picture, extra=_CURR_PICTURE)
        duplicate_count = 1
        while (output_path := picture.get_output_path(duplicate_count)) in used_paths:
            duplicate_count += 1
        logging.debug("Got duplicate_count=%s", duplicate_count, extra=_CURR_PICTURE)

        yield picture.source_path, output_path
        _CURR_PICTURE["picture"] = None
