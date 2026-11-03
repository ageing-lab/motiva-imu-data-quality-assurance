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
#   Subtract 3600 seconds from the first field of every CSV file in a directory.
#   Usage: python3 correct_timestamps_english.py DIRECTORY [--dry-run]
#   WARNING: without --dry-run, the original CSV files are modified.

import argparse
import os
from pathlib import Path
import tempfile


def correct_file(path: Path, dry_run: bool = False) -> int:
    """Validate and transform a CSV while preserving all other fields exactly."""
    temporary = None
    rows = 0
    try:
        with path.open('r', encoding='utf-8', newline='') as source:
            if not dry_run:
                with tempfile.NamedTemporaryFile(
                    mode='w', encoding='utf-8', newline='',
                    dir=path.parent, prefix=f'.{path.name}.', suffix='.tmp',
                    delete=False
                ) as destination:
                    temporary = Path(destination.name)
                    for line_number, line in enumerate(source, 1):
                        content = line.rstrip('\r\n')
                        line_ending = line[len(content):]
                        first, separator, remainder = content.partition(';')
                        if not separator:
                            raise ValueError(f'line {line_number}: missing separator ;')
                        try:
                            value = int(first)
                        except ValueError as exc:
                            raise ValueError(f'line {line_number}: non-integer timestamp: {first!r}') from exc
                        destination.write(f'{value - 3600};{remainder}{line_ending}')
                        rows += 1
            else:
                for line_number, line in enumerate(source, 1):
                    first, separator, _ = line.rstrip('\r\n').partition(';')
                    if not separator:
                        raise ValueError(f'line {line_number}: missing separator ;')
                    try:
                        int(first)
                    except ValueError as exc:
                        raise ValueError(f'line {line_number}: non-integer timestamp: {first!r}') from exc
                    rows += 1

        if temporary is not None:
            os.chmod(temporary, path.stat().st_mode)
            os.replace(temporary, path)
        return rows
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description='Subtract 3600 seconds from the first column of all CSV files found recursively.')
    parser.add_argument('directory', type=Path, help='Root directory containing CSV files')
    parser.add_argument('--dry-run', action='store_true', help='Validate files without modifying them')
    args = parser.parse_args()
    if not args.directory.is_dir():
        parser.error(f'Not a valid directory: {args.directory}')

    files = sorted(p for p in args.directory.rglob('*') if p.is_file() and p.suffix.lower() == '.csv')
    total_rows = 0
    errors = 0
    for path in files:
        try:
            rows = correct_file(path, args.dry_run)
            total_rows += rows
            print(f'OK: {path} ({rows} records)')
        except (OSError, UnicodeError, ValueError) as exc:
            errors += 1
            print(f'ERROR: {path}: {exc}')

    action = 'validated' if args.dry_run else 'corrected'
    print(f'\nFiles {action}: {len(files) - errors}; records: {total_rows}; errors: {errors}')
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
