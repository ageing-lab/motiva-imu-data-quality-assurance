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
#   Safely transfer pending MOTIVA recordings and prepare application annotations.
#
#   Sources:
#       <root_pending>/pending/devices/<wave>/*
#       <root_pending>/pending/app/raw/<wave>/*.txt
#
#   Destinations:
#       <root_repo>/repo/devices/<wave>/*
#       <root_repo>/repo/app/raw/<wave>/*.txt
#       <root_pending>/pending/app/v1/wave-1/*_ppr2.txt
#       <root_pending>/pending/app/v2/<wave>/*_ppr2.txt
#
#   Sources are removed only after all destinations for that file have been verified.
#   Existing destinations are never overwritten. Identical destinations are accepted
#   so that interrupted runs can be resumed safely.

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

RAW_NAME = re.compile(r"^(?P<pid>\d+)_(?P<date>\d{8})(?P<time>\d{4})_(?P<wheel>[A-D])\.txt$", re.I)
PREPARED_NAME = re.compile(r"^(?P<pid>\d+)_(?P<date>\d{8})_(?P<time>\d{4})_(?P<wheel>[A-D])\.txt$", re.I)


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.digest()


def same_content(left, right):
    return left.stat().st_size == right.stat().st_size and sha256(left) == sha256(right)


def staged_copy(source, destination):
    """Stage a copy in the destination filesystem, without publishing it."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.motiva-stage-', dir=destination.parent)
    temp = Path(name)
    try:
        with os.fdopen(fd, 'wb') as output, source.open('rb') as input_file:
            shutil.copyfileobj(input_file, output, 1024 * 1024)
            output.flush()
            os.fsync(output.fileno())
        shutil.copystat(source, temp)
        return temp
    except BaseException:
        temp.unlink(missing_ok=True)
        raise


def staged_jsonl(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.motiva-stage-', dir=destination.parent)
    temp = Path(name)
    try:
        with source.open('r', encoding='utf-8-sig') as input_file, os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as output:
            for number, line in enumerate(input_file, 1):
                if not line.strip():
                    raise ValueError(f'{source}:{number}: empty JSONL line')
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(f'{source}:{number}: invalid JSON: {error}') from error
                if not isinstance(obj, dict):
                    raise ValueError(f'{source}:{number}: expected a JSON object')
                obj['valido'] = True
                output.write(json.dumps(obj, ensure_ascii=False) + '\n')
            output.flush()
            os.fsync(output.fileno())
        return temp
    except BaseException:
        temp.unlink(missing_ok=True)
        raise


def publish_without_overwrite(temp, destination):
    """Atomically create a destination; never replace an existing file."""
    try:
        os.link(temp, destination)
    except FileExistsError:
        if not same_content(temp, destination):
            raise FileExistsError(f'Existing destination differs: {destination}')
    finally:
        temp.unlink(missing_ok=True)


def process_one(source, destinations, dry_run=False):
    """Prepare all outputs first, then publish; retain source on any failure."""
    if not destinations:
        return
    if len(set(destinations)) != len(destinations):
        raise ValueError(f'Duplicate destination for {source}')
    if any(source.resolve() == target.resolve() for target, _ in destinations):
        raise ValueError(f'Source and destination are the same: {source}')
    if dry_run:
        print(f'PLAN {source}')
        for target, mode in destinations:
            print(f'  -> {target} [{mode}]')
        return
    staged = []
    published = []
    try:
        # Verify all outputs before publishing any of them.
        for target, mode in destinations:
            temp = staged_copy(source, target) if mode == 'copy' else staged_jsonl(source, target)
            staged.append((temp, target))
            if target.exists() and not same_content(temp, target):
                raise FileExistsError(f'Existing destination differs: {target}')
        for temp, target in staged:
            existed = target.exists()
            publish_without_overwrite(temp, target)
            if not existed:
                published.append(target)
        # Verify each output once more before removing the source.
        for temp, target in staged:
            if not target.is_file():
                raise OSError(f'Missing destination after publication: {target}')
        source.unlink()
        print(f'OK {source}')
        for target, _ in destinations:
            print(f'  -> {target}')
    except Exception:
        # Remove only files published in this invocation, not pre-existing ones.
        for target in reversed(published):
            target.unlink(missing_ok=True)
        raise
    finally:
        for temp, _ in staged:
            temp.unlink(missing_ok=True)


def waves_in(directory):
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.iterdir() if p.is_dir() and re.fullmatch(r'wave-\d+', p.name))


def process_devices(pending, repo, dry_run):
    source_root = pending / 'devices'
    count = 0
    failures = 0
    for wave_dir in waves_in(source_root):
        for source in sorted(wave_dir.iterdir()):
            if not source.is_file():
                continue
            count += 1
            target = repo / 'devices' / wave_dir.name / source.name
            try:
                process_one(source, [(target, 'copy')], dry_run)
            except Exception as error:
                failures += 1
                print(f'ERROR {source}: {error}', file=sys.stderr)
    return count, failures


def destination_raw_name(filename):
    match = RAW_NAME.fullmatch(filename)
    if match:
        return f"{match['pid']}_{match['date']}_{match['time']}_{match['wheel']}.txt"
    if PREPARED_NAME.fullmatch(filename):
        return filename
    raise ValueError(f'Unexpected RAW filename format: {filename}')


def process_raw_app(pending, repo, dry_run):
    source_root = pending / 'app' / 'raw'
    count = 0
    failures = 0
    for wave_dir in waves_in(source_root):
        wave = wave_dir.name
        for source in sorted(wave_dir.iterdir()):
            if not source.is_file():
                continue
            count += 1
            try:
                new_name = destination_raw_name(source.name)
                prepared_name = Path(new_name).stem + '_ppr2.txt'
                targets = [(repo / 'app' / 'raw' / wave / new_name, 'copy')]
                if wave == 'wave-1':
                    targets.append((pending / 'app' / 'v1' / wave / prepared_name, 'jsonl'))
                targets.append((pending / 'app' / 'v2' / wave / prepared_name, 'jsonl'))
                process_one(source, targets, dry_run)
            except Exception as error:
                failures += 1
                print(f'ERROR {source}: {error}', file=sys.stderr)
    return count, failures


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root-pending', '--root_pending', dest='root_pending', type=Path, default=Path('../..'),
                        help='Parent directory containing pending/')
    parser.add_argument('--root-repo', '--root_repo', dest='root_repo', type=Path, default=Path('../..'),
                        help='Parent directory containing repo/')
    parser.add_argument('--dry-run', action='store_true', help='Preview operations without writing files')
    args = parser.parse_args()
    pending = args.root_pending.resolve() / 'pending'
    repo = args.root_repo.resolve() / 'repo'
    if not pending.is_dir():
        parser.error(f'Pending directory not found: {pending}')
    if not (pending / 'devices').is_dir() and not (pending / 'app' / 'raw').is_dir():
        parser.error('Neither pending/devices nor pending/app/raw exists')
    device_count, device_failures = process_devices(pending, repo, args.dry_run)
    raw_count, raw_failures = process_raw_app(pending, repo, args.dry_run)
    print(f'Summary: {device_count} device files, {raw_count} application files; '
          f'{device_failures + raw_failures} failures')
    return 1 if device_failures + raw_failures else 0


if __name__ == '__main__':
    sys.exit(main())
