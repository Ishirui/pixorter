"""
Module containing different methods for extracting a picture's creation date:
    - Regex on the filename
    - EXIF data
    - File creation date
"""

import os
import platform
import re
from datetime import datetime
from pathlib import Path

from PIL.Image import ExifTags, Image
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
        for k in ("year", "month", "day", "hour", "minute")
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
