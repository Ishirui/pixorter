"""
Module holding the definition for the Picture class.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from pixorter import VIDEO_EXTENSIONS


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
        d = self.snap_date
        tag = "VID" if self.is_video else "IMG"
        ext = self.extension

        ymdhm_str = f"{d.year}-{d.month}-{d.day}-{d.hour}h{d.minute}"
        filename = f"{ymdhm_str}_{tag}{duplicate_count}.{ext}"

        folder = Path(f"{d.year}/{d.month}")
        return folder / filename
