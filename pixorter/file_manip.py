"""Collection of functions for manipulating files (move, copy, walk a directory etc.)"""

import shutil
from pathlib import Path
from typing import Generator


def walk_dir(directory: Path) -> Generator[Path, None, None]:
    for folder, _, files in directory.walk():
        for file in files:
            yield folder / file


def move(src_file: Path, dest_file: Path):
    if not src_file.is_file() or not dest_file.is_file():
        raise ValueError("Only allowing moves between files")

    shutil.move(src_file, dest_file)


def copy(src_file: Path, dest_file: Path):
    if not src_file.is_file() or not dest_file.is_file():
        raise ValueError("Only allowing copies between files")

    shutil.copy(src_file, dest_file)


def symlink(src_file: Path, dest_file: Path):
    if not src_file.is_file() or not dest_file.is_file():
        raise ValueError("Only allowing symlink creation between files")

    dest_file.symlink_to(src_file)


def hardlink(src_file: Path, dest_file: Path):
    if not src_file.is_file() or not dest_file.is_file():
        raise ValueError("Only allowing hardlinking between files")

    dest_file.hardlink_to(src_file)
