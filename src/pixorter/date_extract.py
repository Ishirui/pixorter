"""
Module containing different methods for extracting a picture's creation date:
    - Regex on the filename
    - EXIF / metadata
    - File creation date
"""

import json
import logging
import os
import platform
import re
from datetime import datetime
from pathlib import Path

from PIL.Image import ExifTags, Image
from PIL.Image import open as open_image

try:
    from ffmpeg import FFmpeg, FFmpegError  # type: ignore
except ImportError:
    pass


from .globals import FILENAME_REGEXES, IMAGE_EXTENSIONS, VIDEO_EXTENSIONS

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


def get_date_from_video_metadata(path: Path):
    """Try to get datetime info from the video's metadata"""
    ffprobe = FFmpeg(executable="ffprobe").input(
        path,
        print_format="json",
        show_streams=None,
    )

    try:
        media = json.loads(ffprobe.execute())
        datetime_str: str = media["streams"][0]["tags"]["creation_time"]
    except (KeyError, json.JSONDecodeError, FFmpegError) as exc:
        logging.error("Failed to get video metadata ! for %s. Error: %s", path, exc)
        raise NoMatchException() from exc

    datetime_str = datetime_str.split(".")[0]  # Remove trailing decimal

    try:
        return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError as e:
        logging.warning(
            "Invalid date found in video metadata ! (%s). Ignoring...", datetime_str
        )
        raise NoMatchException() from e


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

    try:
        # See https://stackoverflow.com/a/62077871
        return datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")
    except ValueError as e:
        logging.warning(
            "Invalid date found in EXIF data ! (%s). Ignoring...", datetime_str
        )
        raise NoMatchException() from e


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

    try:
        # 1.
        img_extension = img_path.suffix[1:]
        if img_extension in IMAGE_EXTENSIONS:
            img: Image = open_image(img_path)
            metadata_datetime = get_date_from_exif(img)
        elif img_extension in VIDEO_EXTENSIONS:
            metadata_datetime = get_date_from_video_metadata(img_path)
        else:
            raise NoMatchException("Unsupported extension !")
    except NoMatchException:
        logging.debug("Could not extract snap_date from EXIF / metadata")
        metadata_datetime = None
    else:
        logging.debug(
            "Successfully Extracted EXIF / metadata-based snap_date: %s",
            metadata_datetime,
        )

    try:
        # 2.
        filename_datetime = get_date_from_filename(img_path.name)
    except NoMatchException:
        logging.debug("Could not extract snap_date from filename")
        filename_datetime = None
    else:
        logging.debug(
            "Successfully Extracted filename snap_date: %s",
            filename_datetime,
        )

    # 3a.
    if (metadata_datetime is not None) ^ (filename_datetime is not None):
        if metadata_datetime is not None:
            logging.debug("Using EXIF / metadata-based snap_date")
            return metadata_datetime

        logging.debug("Using filename snap_date")
        return filename_datetime  # type: ignore

    # 4.
    if metadata_datetime is None and filename_datetime is None:
        msg = f"Could not determine snap_date for {img_path} !"
        # TODO: Implement CLI option for relaxing and using attr-based extraction
        raise NoMatchException(msg)

    # Make mypy happy
    assert metadata_datetime is not None and filename_datetime is not None

    # 3b.
    if metadata_datetime == filename_datetime:
        logging.debug("Both datetimes match.")
        return metadata_datetime

    if metadata_datetime.date() == filename_datetime.date():
        logging.warning(
            "EXIF / metadata-based and filename-based datetime only loosely match. "
            + "Using EXIF / metadata-based."
        )
        return metadata_datetime

    msg = "EXIF / metadata-based and filename-based datetime do not match !"
    # TODO: Implement CLI option for relaxing this
    logging.error(msg)
    raise NoMatchException(msg)
