"""Collection of functions for manipulating files (move, copy, walk a directory etc.)"""

import logging
import shutil
from pathlib import Path
from typing import Generator


def walk_dir(directory: Path) -> Generator[Path, None, None]:
    for folder, _, files in directory.walk():
        for file in files:
            yield folder / file


def op_common(src_file: Path, dest_file: Path):
    """Common things to do for every operation type"""
    if dest_file.exists():
        raise ValueError(f"Destination file {dest_file} already exists !")

    if not src_file.is_file() or dest_file.is_file():
        raise ValueError(
            f"Only allowing operations between files. Offending: {src_file} -> {dest_file}"
        )

    # Make sure the parent directories tree exist
    dest_file.parent.mkdir(parents=True, exist_ok=True)


def move(src_file: Path, dest_file: Path):
    op_common(src_file, dest_file)
    logging.info("Moving %s -> %s...", src_file, dest_file)
    shutil.move(src_file, dest_file)


def copy(src_file: Path, dest_file: Path):
    op_common(src_file, dest_file)
    logging.info("Copying %s |-> %s...", src_file, dest_file)
    shutil.copy(src_file, dest_file)


def symlink(src_file: Path, dest_file: Path):
    op_common(src_file, dest_file)
    logging.info("Symlinking %s <- %s...", src_file, dest_file)
    dest_file.symlink_to(src_file)


def hardlink(src_file: Path, dest_file: Path):
    op_common(src_file, dest_file)
    logging.info("Hardlinking %s <-| %s...", src_file, dest_file)
    dest_file.hardlink_to(src_file)


def dry_run(src_file: Path, dest_file: Path):
    op_common(src_file, dest_file)
    logging.info("Running operation %s -> %s", src_file, dest_file)
