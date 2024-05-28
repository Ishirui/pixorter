"""Collection of functions for manipulating files (move, copy, walk a directory etc.)"""

import logging
import shutil
from pathlib import Path
from typing import Generator

from .globals import _CURR_PICTURE


def walk_dir(directory: Path) -> Generator[Path, None, None]:
    for folder, _, files in directory.walk():
        for file in files:
            yield folder / file


def move(src_file: Path, dest_file: Path):
    if not src_file.is_file() or not dest_file.is_file():
        raise ValueError(
            f"Only allowing moves between files. Offending: {src_file:s} -> {dest_file}"
        )

    logging.info("Moving %s -> %s...", src_file, dest_file, extra=_CURR_PICTURE)
    shutil.move(src_file, dest_file)


def copy(src_file: Path, dest_file: Path):
    if not src_file.is_file() or not dest_file.is_file():
        raise ValueError(
            f"Only allowing copies between files. Offending: {src_file} -> {dest_file}"
        )

    logging.info("Copying %s |-> %s...", src_file, dest_file, extra=_CURR_PICTURE)
    shutil.copy(src_file, dest_file)


def symlink(src_file: Path, dest_file: Path):
    if not src_file.is_file() or not dest_file.is_file():
        raise ValueError(
            f"Only allowing symlink creation between files. Offending: {src_file} -> {dest_file}"
        )

    logging.info("Symlinking %s <- %s...", src_file, dest_file, extra=_CURR_PICTURE)
    dest_file.symlink_to(src_file)


def hardlink(src_file: Path, dest_file: Path):
    if not src_file.is_file() or not dest_file.is_file():
        raise ValueError(
            f"Only allowing hardlinking between files. Offending: {src_file} -> {dest_file}"
        )

    logging.info("Hardlinking %s <-| %s...", src_file, dest_file, extra=_CURR_PICTURE)
    dest_file.hardlink_to(src_file)


def dry_run(src_file: Path, dest_file: Path):
    if not src_file.is_file() or not dest_file.is_file():
        logging.error(
            "Would throw an error ! %s or %s is not a file.",
            src_file,
            dest_file,
            extra=_CURR_PICTURE,
        )

    logging.info("Running operation %s -> %s", src_file, dest_file, extra=_CURR_PICTURE)
