#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2023-2026 Antonio Cobo Sánchez de Rojas
# SPDX-FileCopyrightText: 2023-2026 Elena Villalba Mora
# SPDX-License-Identifier: AGPL-3.0-only
#
# Project: MOTIVA (PID2022-140214OB-C21)
# Associated dataset:
#   MOTIVA-IMU: A Multi-Sensor Inertial Motion Dataset of SPPB Tests and VIVIFRAIL Exercises in Older Adults
#
# Authors and affiliations:
#   Antonio Cobo Sánchez de Rojas
#     Employer: Centro de Investigación Biomédica en Red (CIBER)
#     Additional affiliation: Universidad Politécnica de Madrid (UPM)
#
#   Elena Villalba Mora
#     Employer: Universidad Politécnica de Madrid (UPM)
#     Additional affiliation: Centro de Investigación Biomédica en Red (CIBER)
#
# Institutional affiliations do not indicate institutional ownership
# of the software copyright.
#
# This file is part of the MOTIVA project.
# Licensed under the GNU Affero General Public License, version 3 only.
# This software is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the LICENSE file in the project root for license terms.
#
# Description:
#   Moves motion data files from the pending directory to the dataset
#   repository, preserving their organization by acquisition wave.
#   Supports individual files, entire waves, batch operations from
#   a list, and dry-run execution.

import argparse
import shlex
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MoveRequest:
    wave: str
    filename: str | None = None  # None means: all files in the wave


def source_directory(root: Path, wave: str) -> Path:
    return root / "pending" / "app" / "v2" / wave


def destination_directory(root: Path, wave: str) -> Path:
    return root / "repo" / "app" / "v2" / wave


def validate_filename(name: str) -> None:
    """Prevent accidental or unsafe paths in the input list file."""
    path = Path(name)

    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Filename not allowed: {name}")

    if len(path.parts) != 1:
        raise ValueError(
            f"Specify only the filename, not a full path: {name}"
        )


def move_file(root_pending: Path, root_repo: Path, wave: str, filename: str, dry_run: bool = False) -> bool:
    validate_filename(filename)

    source = source_directory(root_pending, wave) / filename
    destination_dir = destination_directory(root_repo, wave)
    destination = destination_dir / filename

    if not source.exists():
        print(f"NOT FOUND: {source}")
        return False

    if not source.is_file():
        print(f"NOT A FILE: {source}")
        return False

    if destination.exists():
        raise FileExistsError(f"File already exists at destination: {destination}")

    print(f"MOVE: {source} -> {destination}")

    if not dry_run:
        destination_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))

    return True


def move_entire_wave(root_pending: Path, root_repo: Path, wave: str, dry_run: bool = False) -> int:
    source_dir = source_directory(root_pending, wave)

    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")

    files = sorted(f for f in source_dir.iterdir() if f.is_file())

    if not files:
        print(f"No files in: {source_dir}")
        return 0

    moved = 0
    for file in files:
        if move_file(root_pending, root_repo, wave, file.name, dry_run=dry_run):
            moved += 1

    return moved


def parse_list_line(line: str, default_wave: str | None) -> MoveRequest | None:
    """
    Supported formats in the list file:

      # comments and blank lines are ignored
      file.txt                        # requires a default wave argument
      wave-2 file.txt
      wave-2/file.txt
      wave-2 *                        # all files in wave-2
      wave-2 ALL                      # all files in wave-2
      wave-2 TODO                     # all files in wave-2 (legacy alias)

    shlex is used to support quoted filenames containing spaces.
    """
    line = line.strip()

    if not line or line.startswith("#"):
        return None

    parts = shlex.split(line)

    if len(parts) == 1:
        value = parts[0]

        if "/" in value:
            wave, name = value.split("/", 1)
            name = None if name in {"*", "ALL", "TODO"} else name
            return MoveRequest(wave=wave, filename=name)

        if default_wave is None:
            raise ValueError(
                f"Line '{line}' does not specify a wave. Provide a wave argument or write 'wave filename'."
            )

        name = None if value in {"*", "ALL", "TODO"} else value
        return MoveRequest(wave=default_wave, filename=name)

    if len(parts) == 2:
        wave, name = parts
        name = None if name in {"*", "ALL", "TODO"} else name
        return MoveRequest(wave=wave, filename=name)

    raise ValueError(f"Invalid line format: {line}")


def read_requests_from_list(list_path: Path, default_wave: str | None) -> list[MoveRequest]:
    requests: list[MoveRequest] = []

    with list_path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            try:
                request = parse_list_line(line, default_wave)
            except Exception as e:
                raise ValueError(f"Error in {list_path}, line {line_number}: {e}") from e

            if request is not None:
                requests.append(request)

    return requests


def remove_duplicates(requests: list[MoveRequest]) -> list[MoveRequest]:
    seen: set[tuple[str, str | None]] = set()
    result: list[MoveRequest] = []

    for request in requests:
        key = (request.wave, request.filename)
        if key in seen:
            continue
        seen.add(key)
        result.append(request)

    return result


def execute_requests(root_pending: Path, root_repo: Path, requests: list[MoveRequest], dry_run: bool = False) -> int:
    total_moved = 0

    for request in remove_duplicates(requests):
        if request.filename is None:
            total_moved += move_entire_wave(root_pending, root_repo, request.wave, dry_run=dry_run)
        else:
            if move_file(root_pending, root_repo, request.wave, request.filename, dry_run=dry_run):
                total_moved += 1

    return total_moved


def main():
    parser = argparse.ArgumentParser(
        description="Move files from pending/app/v2/<wave> to repo/app/v2/<wave>."
    )

    parser.add_argument(
        "wave",
        nargs="?",
        help="Default wave. Without --lista, all files in this wave are moved."
    )

    parser.add_argument(
        "--lista",
        help="File containing the list of files or waves to move."
    )

    parser.add_argument(
        "--root_pending",
        default="../..",
        help="Project root directory. Default: ../.."
    )

    parser.add_argument(
        "--root_repo",
        default="../..",
        help="Project root directory. Default: ../.."
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be moved without moving anything."
    )

    args = parser.parse_args()
    root_pending = Path(args.root_pending).resolve()
    root_repo = Path(args.root_repo).resolve()

    if args.lista:
        requests = read_requests_from_list(Path(args.lista), args.wave)
    else:
        if not args.wave:
            parser.error("You must specify a wave or use --lista.")
        requests = [MoveRequest(wave=args.wave, filename=None)]

    total = execute_requests(root_pending, root_repo, requests, dry_run=args.dry_run)

    if args.dry_run:
        print(f"DRY-RUN: {total} file(s) would be moved.")
    else:
        print(f"TOTAL MOVED: {total}")


if __name__ == "__main__":
    main()
