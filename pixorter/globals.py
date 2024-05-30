"""
Global-ish configuration options and state for use in parts of the script
"""

import re
from typing import Any, Dict

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "tif", "tiff", "gif", "heic"}

VIDEO_EXTENSIONS = {"mp4", "mpv", "mkv", "mov", "3gp"}

SUPPORTED_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS

YEAR_REGEX = r"(?P<year>(?:20|19)[0-9]{2})"
MONTH_REGEX = r"(?P<month>0[0-9]|1[0-2])"
DAY_REGEX = r"(?P<day>[0-2][0-9]|3[01])"
HOUR_REGEX = r"(?P<hour>[01][0-9]|2[0-3])"
MINUTE_REGEX = r"(?P<minute>[0-5][0-9])"
SECOND_REGEX = r"(?P<second>:[0-5][0-9])"

# TODO: MATCH AND CAPTURE SECONDS TOO IF POSSIBLE

HM_REGEX = rf"{HOUR_REGEX}[-_:HhT]?{MINUTE_REGEX}{SECOND_REGEX}?"

DATE_REGEXES = [rf"{YEAR_REGEX}[-_ ]?{MONTH_REGEX}[-_ ]?{DAY_REGEX}"]
# TODO: Add support for different dates formats (currently only yyyy-mm-dd)
# Also need to figure out how to decide between them when multiple match

FILENAME_REGEX_STRS = [
    rf"(?:{date_regex})[-_ ]?(?:{HM_REGEX})?" for date_regex in DATE_REGEXES
] + [rf"(?:{HM_REGEX})?[-_ ]?(?:{date_regex})" for date_regex in DATE_REGEXES]

FILENAME_REGEXES = [re.compile(x) for x in FILENAME_REGEX_STRS]

# Keep track of the picture currently being processed
# FOR USE IN LOGGING ONLY
# Use Dict so that the same object is always pointed to, would not work by simply reassigning
# Use Any to prevent circular import
_CURR_PICTURE: Dict[str, Any] = {"picture": None}
