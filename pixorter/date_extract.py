"""
Module containing different methods for extracting a picture's creation date:
    - Regex on the filename
    - EXIF data
    - File creation date
"""

import logging
import os
import platform
import re
from datetime import datetime
from pathlib import Path

from PIL.Image import ExifTags, Image
from PIL.Image import open as open_image
from pixorter import FILENAME_REGEXES

DATETIME_TAGS = {
    name: id
    for id, name in ExifTags.TAGS.items()
    if name in ("DateTime", "DateTimeOriginal", "DateTimeDigitized")
}


class NoMatchException(Exception):
    """Raised when an extraction method does not give any satisfactory result"""


def get_date_from_filename(filename: str) -> datetime:
    """Try to get datetime info from the filename using the regexes defined in constants.py"""
    match = None
    for regex in FILENAME_REGEXES:
        match = re.search(regex, filename)
        if match:
            break

    if not match:
        raise NoMatchException()

    datetime_parts = {
        k: int(match.group(k))
        for k in ("year", "month", "day", "hour", "minute", "second")
        if match.group(k)
    }
    return datetime(**datetime_parts)  # type: ignore


def get_date_from_exif(image: Image) -> datetime:
    """Try to get datetime info from the image's EXIF metadata"""
    exif = image.getexif()

    if exif is None:
        raise NoMatchException()

    datetime_str = None
    for tag_id in DATETIME_TAGS.values():
        datetime_str = datetime_str or exif.get(tag_id, default=None)

    if datetime_str is None:
        raise NoMatchException()

    # See https://stackoverflow.com/a/62077871
    return datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")


def get_date_from_attrs(path: Path) -> datetime:
    """
    Try to get the snap date from file attrs.
    Note that on Unix systems, there is no way to get file creation date from Python.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == "Windows":
        ctime = os.path.getctime(path)
    else:
        stat = os.stat(path)
        try:
            ctime = stat.st_birthtime  # type: ignore
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            ctime = stat.st_mtime

    return datetime.fromtimestamp(ctime)


def get_snap_date(img_path: Path) -> datetime:
    """
    Use all extraction methods to try to get an image's snap date.
    Here is the logic:

        1. Try to get it from EXIF
        2. Try to get it from filename
        3a. If only one worked, use the one that worked
        3b. If both worked, check whether they match:
            i. If they are equal, return here.
            ii. If they have the same date but different times, emit a warning and use the EXIF one.
            iii. If they do not match at all, raise an error.
                > This can be relaxed with a CLI option, where it will use the EXIF one.

        4. If none worked, error out.
            > This can be relaxed with a CLI option, emitting a warning and extract from file attrs.
    """
    img: Image = open_image(img_path)

    try:
        # 1.
        exif_datetime = get_date_from_exif(img)
    except NoMatchException:
        logging.debug("Could not extract snap_date from EXIF")
        exif_datetime = None
    else:
        logging.debug("Successfully Extracted EXIF snap_date: %s", exif_datetime)

    try:
        # 2.
        filename_datetime = get_date_from_filename(img_path.name)
    except NoMatchException:
        logging.debug("Could not extract snap_date from filename")
        filename_datetime = None
    else:
        logging.debug(
            "Successfully Extracted filename snap_date: %s", filename_datetime
        )

    # 3a.
    if (exif_datetime is not None) ^ (filename_datetime is not None):
        if exif_datetime is not None:
            logging.debug("Using EXIF snap_date")
            return exif_datetime

        logging.debug("Using filename snap_date")
        return filename_datetime  # type: ignore

    # 4.
    if exif_datetime is None and filename_datetime is None:
        msg = f"Could not determine snap_date for {img_path} !"
        logging.error(msg)
        # TODO: Implement CLI option for relaxing and using attr-based extraction
        raise NoMatchException(msg)

    # Make mypy happy
    assert exif_datetime is not None and filename_datetime is not None

    # 3b.
    if exif_datetime == filename_datetime:
        logging.debug("Both datetimes match.")
        return exif_datetime

    if exif_datetime.date() == filename_datetime.date():
        logging.warning(
            "EXIF and filename-based datetime only loosely match. Using EXIF."
        )
        return exif_datetime

    msg = "EXIF and filename-based datetime do not match !"
    # TODO: Implement CLI option for relaxing this
    logging.error(msg)
    raise NoMatchException(msg)
