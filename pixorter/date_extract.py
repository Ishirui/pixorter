"""
Module containing different methods for extracting a picture's creation date:
    - Regex on the filename
    - EXIF data
    - File creation date
"""

import re
from datetime import datetime

from pixorter import FILENAME_REGEXES


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
