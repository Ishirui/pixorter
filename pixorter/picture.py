"""
Module holding the definition for the Picture class.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .constants import VIDEO_EXTENSIONS


@dataclass
class Picture:
    """
    Main class representing a single image file.
    """

    source_path: Path
    snap_date: datetime

    @property
    def extension(self) -> str:
        ext = self.source_path.suffix.lower()
        match ext:
            case "jpeg":
                return "jpg"
            case "tiff":
                return "tif"
            case _:
                return ext

    @property
    def is_video(self) -> bool:
        return self.extension in VIDEO_EXTENSIONS

    def get_output_path(self, duplicate_count: int = 1) -> Path:
        """
        Get the canonical (output) Path for this Picture.
        This is the path the image file will get moved to upon script completion.
        """
        d = self.snap_date
        tag = "VID" if self.is_video else "IMG"
        ext = self.extension

        # pylint: disable-next=line-too-long
        ymdhms_str = f"{d.year}-{d.month}-{d.day}-{d.hour}h{d.minute}{f'm{d.second}s' if d.second else ''}"
        filename = f"{ymdhms_str}_{tag}{duplicate_count}.{ext}"

        folder = Path(f"{d.year}/{d.month}")
        return folder / filename
