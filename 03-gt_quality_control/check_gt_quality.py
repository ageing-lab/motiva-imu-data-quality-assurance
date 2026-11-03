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
#   Non-destructive MOTIVA ground-truth annotation quality audit.
#   
#   Reads versioned newline-delimited JSON annotations recursively, checks expected
#   set-start counts by VIVIFRAIL wheel, and flags close consecutive annotations.
#   Uses only the Python standard library. All reports and messages are in English.

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

NAME = re.compile(r'^(?P<pid>\d+)_(?P<date>\d{8})_(?P<hhmm>\d{4})_(?P<wheel>[BCD])_ppr2\.txt$', re.I)
DEFAULT_EXCLUDED_EVID = (0, 1, 2, 3, 4, 5, 10, 11, 111, 112)
ACTIVITIES = {
    0:'Neutral posture', 1:'SPPB side-by-side stand', 2:'SPPB semi-tandem',
    3:'SPPB tandem', 4:'SPPB 3-m walk', 5:'SPPB chair stands',
    6:'Walk in line', 7:'Heel-to-toe walking', 8:'Obstacle course',
    9:'Figure-eight walking', 10:'Balloon walking', 11:'Stair ascent/descent',
    12:'Bottle lifting', 13:'Ball squeezing', 14:'Towel twisting',
    15:'Leg extension', 16:'Assisted chair rise', 17:'Simulated squats',
    18:'Chair rise', 19:'Leg stretching', 20:'Arm stretching',
    21:'Arm stretching with chair', 111:'Stair ascent (derived)',
    112:'Stair descent (derived)'
}
BASE = {0:1, 1:1, 2:1, 3:1, 4:2, 5:1}
EXPECTED = {
    'B': {**BASE, 7:3, 12:3, 13:3, 17:3, 20:9, 21:9},
    'C': {**BASE, 8:8, 9:3, 12:3, 14:3, 18:3, 20:9, 19:18},
    'D': {**BASE, 14:3, 12:3, 18:3, 11:3, 10:3, 9:3, 20:9, 19:18},
}
EXPECTED_D_EARLY = {**BASE, 14:3, 12:3, 18:3, 11:3, 10:2, 9:2, 20:9, 19:36}


def arguments():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('gt_dir', type=Path, help='Annotation directory; searched recursively (e.g. app/v2)')
    p.add_argument('--output', type=Path, default=Path('results/gt_qc_results'), help='Directory for generated reports')
    p.add_argument('--duplicate-threshold-ms', type=float, default=550, help='Flag adjacent eligible annotations with 0 <= dt < threshold')
    p.add_argument('--exclude-evid', type=int, nargs='*', default=list(DEFAULT_EXCLUDED_EVID), metavar='ID', help='Exercise IDs excluded from close-annotation detection; pass with no values to exclude none')
    p.add_argument('--exclude-phsid', type=int, nargs='*', default=[], metavar='ID', help='Annotation phase IDs excluded from close-annotation detection; none excluded by default')
    p.add_argument('--wheel', nargs='+', choices=('B','C','D'), default=['B','C','D'], help='VIVIFRAIL wheels to analyze')
    p.add_argument('--include-invalid', action='store_true', help='Include annotations marked valido=false in close-annotation detection (not set-count comparison)')
    a = p.parse_args()
    if a.duplicate_threshold_ms <= 0 or not math.isfinite(a.duplicate_threshold_ms):
        p.error('--duplicate-threshold-ms must be a positive finite number')
    if not a.gt_dir.is_dir():
        p.error(f'Annotation directory does not exist: {a.gt_dir}')
    if a.output.resolve() == a.gt_dir.resolve():
        p.error('Output directory must differ from the input directory')
    return a


def integer(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        n = float(value)
        return int(n) if math.isfinite(n) and n.is_integer() else None
    except (ValueError, TypeError, OverflowError):
        return None


def valid_flag(value):
    if value is None:
        return True  # Files without valido (e.g. raw) are not the recommended input.
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() not in ('false', '0', 'no')
    return bool(value)


def write_report(path, fields, records):
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(records)


def expected_counts(wheel, date):
    if wheel == 'D' and date < '20240604':
        return EXPECTED_D_EARLY
    return EXPECTED[wheel]


def audit_file(path, meta, args):
    annotations = []
    events = []
    invalid = []
    count = Counter()
    lines = 0
    base = {'wave':meta['wave'], 'pid':meta['pid'], 'date':meta['date'],
            'wheel':meta['wheel'], 'filename':str(path.relative_to(args.gt_dir))}
    with path.open('r', encoding='utf-8-sig') as stream:
        for lineno, line in enumerate(stream, 1):
            if not line.strip():
                continue
            lines += 1
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                events.append({**base,'line':lineno,'type':'invalid_json','detail':str(exc)})
                continue
            if not isinstance(item, dict):
                events.append({**base,'line':lineno,'type':'not_json_object','detail':'Expected an object'})
                continue
            ev = integer(item.get('evId'))
            ph = integer(item.get('phsId'))
            ts = integer(item.get('ts'))
            sn = integer(item.get('sNum'))
            rn = integer(item.get('rNum'))
            ok = valid_flag(item.get('valido'))
            if ev is None or ph is None or ts is None:
                events.append({**base,'line':lineno,'type':'missing_or_invalid_fields',
                               'detail':'evId, phsId, and ts must be integers'})
                continue
            entry = {'line':lineno, 'evId':ev, 'phsId':ph, 'ts':ts, 'sNum':sn,
                     'rNum':rn, 'valid':ok, 'extraId':integer(item.get('extraId'))}
            annotations.append(entry)
            if ph == 3:
                invalid.append({**base, **{k:entry[k] for k in ('line','evId','phsId','ts','sNum','rNum')},'valido':ok})
            if ok and ph == 1:
                count[ev] += 1
    return base, annotations, count, invalid, events, lines


def duplicate_candidates(base, annotations, args):
    """Compare adjacent eligible annotations within an exercise/set segment.

    Segments reset on an exercise change or a valid set-start (phsId=1).
    The latter is included as the first item of its new segment.
    Consecutive eligible annotations are compared in original file order.
    """
    result = []
    previous = None
    current_ev = None
    excluded_ev = set(args.exclude_evid)
    excluded_ph = set(args.exclude_phsid)
    for a in annotations:
        if a['evId'] != current_ev or (a['phsId'] == 1 and a['valid']):
            previous = None
            current_ev = a['evId']
        if (a['evId'] in excluded_ev or a['phsId'] in excluded_ph or
                (not a['valid'] and not args.include_invalid)):
            continue
        if previous is not None:
            delta = a['ts'] - previous['ts']
            if 0 <= delta < args.duplicate_threshold_ms:
                result.append({**base, 'first_line':previous['line'], 'second_line':a['line'],
                    'first_evid':previous['evId'], 'second_evid':a['evId'],
                    'first_phsid':previous['phsId'], 'second_phsid':a['phsId'],
                    'same_phsid':previous['phsId'] == a['phsId'],
                    'first_timestamp_ms':previous['ts'], 'second_timestamp_ms':a['ts'],
                    'delta_ms':delta, 'first_snum':previous['sNum'],
                    'second_snum':a['sNum'], 'first_rnum':previous['rNum'],
                    'second_rnum':a['rNum'], 'first_extraid':previous['extraId'],
                    'second_extraid':a['extraId']})
        previous = a
    return result


def main():
    args = arguments()
    args.output.mkdir(parents=True, exist_ok=True)
    files = sorted(args.gt_dir.rglob('*.txt'))
    summaries, counts, duplicates, invalids, events = [], [], [], [], []
    unmatched = []
    for path in files:
        match = NAME.fullmatch(path.name)
        if not match:
            unmatched.append(str(path.relative_to(args.gt_dir)))
            continue
        meta = match.groupdict()
        meta['wheel'] = meta['wheel'].upper()
        if meta['wheel'] not in args.wheel:
            continue
        try:
            datetime.strptime(meta['date'] + meta['hhmm'], '%Y%m%d%H%M')
        except ValueError:
            unmatched.append(str(path.relative_to(args.gt_dir)) + ' (invalid date/time)')
            continue
        meta['wave'] = next((part for part in path.relative_to(args.gt_dir).parts[:-1]
                             if re.fullmatch(r'wave-\d+', part, re.I)), '')
        try:
            base, entries, observed, invalid, issues, nlines = audit_file(path, meta, args)
        except (OSError, UnicodeError) as exc:
            events.append({'wave':meta['wave'], 'pid':meta['pid'], 'date':meta['date'],
                           'wheel':meta['wheel'], 'filename':str(path.relative_to(args.gt_dir)),
                           'line':0,'type':'file_read_error','detail':str(exc)})
            continue
        invalids.extend(invalid)
        events.extend(issues)
        candidates = duplicate_candidates(base, entries, args)
        duplicates.extend(candidates)
        expected = expected_counts(meta['wheel'], meta['date'])
        mismatches = 0
        for ev in sorted(set(expected) | set(observed)):
            exp, obs = expected.get(ev, 0), observed.get(ev, 0)
            status = 'match' if exp == obs else ('unexpected_exercise' if exp == 0 else
                      'missing_exercise' if obs == 0 else 'set_count_mismatch')
            mismatches += (status != 'match')
            counts.append({**base,'evId':ev,'activity':ACTIVITIES.get(ev,'Unknown'),
                           'expected_sets':exp,'observed_sets':obs,'difference':obs-exp,
                           'status':status})
        summaries.append({**base,'nonempty_lines':nlines,'parsed_annotations':len(entries),
                          'invalid_phsid3':len(invalid),'excluded_by_valido':sum(not a['valid'] for a in entries),
                          'set_count_discrepancies':mismatches,'duplicate_candidates':len(candidates),
                          'same_phsid_candidates':sum(x['same_phsid'] for x in candidates),
                          'structural_events':len(issues)})
    write_report(args.output/'gt_file_quality.csv',
        ['wave','pid','date','wheel','filename','nonempty_lines','parsed_annotations',
         'invalid_phsid3','excluded_by_valido','set_count_discrepancies',
         'duplicate_candidates','same_phsid_candidates','structural_events'], summaries)
    write_report(args.output/'gt_set_counts.csv',
        ['wave','pid','date','wheel','filename','evId','activity','expected_sets','observed_sets','difference','status'], counts)
    write_report(args.output/'gt_duplicate_candidates.csv',
        ['wave','pid','date','wheel','filename','first_line','second_line','first_evid','second_evid',
         'first_phsid','second_phsid','same_phsid','first_timestamp_ms','second_timestamp_ms',
         'delta_ms','first_snum','second_snum','first_rnum','second_rnum','first_extraid','second_extraid'], duplicates)
    write_report(args.output/'gt_invalid_annotations.csv',
        ['wave','pid','date','wheel','filename','line','evId','phsId','ts','sNum','rNum','valido'], invalids)
    write_report(args.output/'gt_quality_events.csv',
        ['wave','pid','date','wheel','filename','line','type','detail'], events)
    (args.output/'unrecognized_filenames.txt').write_text('\n'.join(unmatched) + ('\n' if unmatched else ''), encoding='utf-8')
    summary = [
        f'Files analyzed: {len(summaries)}', f'Unrecognized filenames: {len(unmatched)}',
        f'Parsed annotations: {sum(x["parsed_annotations"] for x in summaries)}',
        f'Files with set-count discrepancies: {sum(x["set_count_discrepancies"] > 0 for x in summaries)}',
        f'Set-count discrepancies: {sum(x["set_count_discrepancies"] for x in summaries)}',
        f'Close-annotation candidates: {len(duplicates)}',
        f'Candidates with matching phsId: {sum(x["same_phsid"] for x in duplicates)}',
        f'phsId=3 annotations: {len(invalids)}',
        f'Structural/read events: {len(events)}',
        f'Duplicate threshold: {args.duplicate_threshold_ms:g} ms',
        f'Excluded evId: {sorted(set(args.exclude_evid))}',
        f'Excluded phsId: {sorted(set(args.exclude_phsid))}',
        'NOTE: Close timestamps are review candidates, not confirmed duplicates.',
        'NOTE: Set-count expectations reproduce the original wheel/date rules.',
        'NOTE: This tool does not modify input files.',
    ]
    (args.output/'gt_quality_summary.txt').write_text('\n'.join(summary) + '\n', encoding='utf-8')
    print('\n'.join(summary))
    print(f'Reports: {args.output.resolve()}')


if __name__ == '__main__':
    main()
