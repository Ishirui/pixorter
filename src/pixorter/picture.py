"""
Module holding the definition for the Picture class.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import ClassVar

from .globals import VIDEO_EXTENSIONS


@dataclass
class Picture:
    """
    Main class representing a single image file.
    """

    # Class var
    _root_path: ClassVar[Path] = Path("/")

    source_path: Path
    snap_date: datetime

    def __str__(self) -> str:
        return f"{self.source_path.relative_to(self._root_path)} ({self.snap_date})"

    def __repr__(self) -> str:
        return f"Picture({self.source_path!r}, {self.snap_date!r})"

    @property
    def extension(self) -> str:
        ext = self.source_path.suffix.lower()[1:]
        if ext == "jpeg":
            return "jpg"

        if ext == "tiff":
            return "tif"

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
