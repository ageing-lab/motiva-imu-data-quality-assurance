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
#   Audit MOTIVA inertial recordings and summarize effective recording time by VIVIFRAIL wheel.
#   
#   Read-only analysis; Python standard library only. Ground-truth directories are
#   optional. Visit durations are the mean effective duration across usable devices.

import argparse
import csv
import math
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

EXPECTED = {'1', '4', '5', '8', '9'}
NAME = re.compile(r'^(\d+)_(\d{8})_(\d+)\.csv$', re.I)
FIELDS = ['pid','date','device','filename','samples','valid_rows','bad_rows','nonfinite_rows','invalid_ms_rows','encoding','first_ts_ms','last_ts_ms','duration_s','effective_duration_s','median_dt_ms','mean_dt_ms','estimated_hz','positive_intervals','near_nominal_intervals','near_nominal_pct','estimated_missing_samples','estimated_missing_in_gaps','p05_dt_ms','p95_dt_ms','p99_dt_ms','duplicate_ts','backward_ts','gaps','gap_total_s','max_gap_ms','acc_saturation_samples','gyro_saturation_samples','constant_acc_runs','constant_gyro_runs','acc_jump_samples','gyro_jump_samples','warnings']

def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('dev_dir', type=Path, help='Directory with device CSV files, or parent of wave directory')
    p.add_argument('--wave', nargs='+', action='append', default=None, metavar='WAVE', help='One or more wave subdirectories; may be repeated (e.g. --wave wave-1 wave-2). Without this option, read CSVs directly from dev_dir')
    p.add_argument('--gt-dir', type=Path, action='append', default=[], help='Directory containing processed ground-truth files (searched recursively); may be repeated. Prefer app/v2 to avoid duplicate annotation versions')
    p.add_argument('--output', type=Path, default=Path('results/imu_qc'), help='Output directory')
    p.add_argument('--no-progress', action='store_true', help='Disable progress bar')
    p.add_argument('--gap-ms', type=float, default=250)
    p.add_argument('--expected-hz', type=float, default=20)
    p.add_argument('--interval-tolerance-ms', type=float, default=5, help='Absolute tolerance around nominal interval (default: +/-5 ms)')
    p.add_argument('--acc-range-g', type=float, help='Configured accelerometer full-scale magnitude in g, e.g. 16')
    p.add_argument('--gyro-range-dps', type=float, help='Configured gyroscope full-scale magnitude in degrees/s, e.g. 2000')
    p.add_argument('--saturation-fraction', type=float, default=0.98)
    p.add_argument('--constant-seconds', type=float, default=2)
    p.add_argument('--acc-jump', type=float, help='Threshold for norm of consecutive acceleration difference in m/s²')
    p.add_argument('--gyro-jump', type=float, help='Threshold for norm of consecutive angular-rate difference in rad/s')
    p.add_argument('--duration-tolerance-s', type=float, default=2)
    p.add_argument('--start-end-tolerance-ms', type=float, default=250)
    a = p.parse_args()
    if any(v <= 0 for v in (a.gap_ms, a.expected_hz, a.constant_seconds, a.duration_tolerance_s, a.start_end_tolerance_ms)):
        p.error('Time and sampling thresholds must be positive')
    for key in ('acc_range_g','gyro_range_dps','acc_jump','gyro_jump'):
        if getattr(a,key) is not None and getattr(a,key) <= 0: p.error(f'--{key.replace("_","-")} must be positive')
    if a.interval_tolerance_ms < 0: p.error('--interval-tolerance-ms must be non-negative')
    if not 0 < a.saturation_fraction <= 1: p.error('--saturation-fraction must be in (0, 1]')
    for directory in a.gt_dir:
        if not directory.is_dir(): p.error(f'Ground-truth directory not found: {directory}')
    return a

def open_text(path):
    # Attempt a small sample before streaming; no silent dropping of invalid bytes.
    with path.open('rb') as f: sample = f.read(8192)
    if sample.startswith((b'\xff\xfe', b'\xfe\xff')): return 'utf-16'
    for enc in ('utf-8-sig', 'cp1252'):
        try: sample.decode(enc); return enc
        except UnicodeDecodeError: pass
    return 'cp1252'

def norm_diff(a,b):
    return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))

def analyze(path, pid, date, device, args):
    r = {k:0 for k in FIELDS if k not in ('pid','date','device','filename','encoding','first_ts_ms','last_ts_ms','median_dt_ms','mean_dt_ms','estimated_hz','warnings')}
    r.update(pid=pid,date=date,device=device,filename=path.name,encoding='',first_ts_ms='',last_ts_ms='',median_dt_ms='',mean_dt_ms='',estimated_hz='',warnings='')
    issues = Counter()
    events = []
    ts_first = ts_last = previous_ts = None
    previous_acc = previous_gyro = None
    acc_run = gyro_run = 0
    acc_run_reported = gyro_run_reported = False
    intervals = []
    nominal_ms = 1000 / args.expected_hz
    effective_ms = 0
    acc_lim = args.acc_range_g * 9.80665 * args.saturation_fraction if args.acc_range_g else None
    gyro_lim = args.gyro_range_dps * math.pi / 180 * args.saturation_fraction if args.gyro_range_dps else None
    min_run = max(2, math.ceil(args.constant_seconds * args.expected_hz))
    def event(kind, rownum, detail):
        issues[kind] += 1
        events.append({'pid':pid,'date':date,'device':device,'filename':path.name,'row':rownum,'type':kind,'detail':detail})
    try:
        enc = open_text(path); r['encoding'] = enc
        with path.open('r', encoding=enc, newline='') as f:
            for rownum, row in enumerate(csv.reader(f, delimiter=';'), 1):
                r['samples'] += 1
                if len(row) != 8:
                    r['bad_rows'] += 1; event('wrong_column_count',rownum,f'{len(row)} columns'); continue
                try:
                    sec = int(row[0].strip()); ms = int(row[1].strip())
                    values = [float(x.strip()) for x in row[2:]]
                except ValueError:
                    r['bad_rows'] += 1; event('invalid_numeric',rownum,'Cannot parse timestamp or 6 channels'); continue
                if not 0 <= ms <= 999:
                    r['invalid_ms_rows'] += 1; event('invalid_millisecond_field',rownum,str(ms)); continue
                if not all(math.isfinite(x) for x in values):
                    r['nonfinite_rows'] += 1; event('nonfinite_channel',rownum,'NaN or infinity'); continue
                r['valid_rows'] += 1
                ts = 1000 * sec + ms
                acc, gyro = values[:3], values[3:]
                if ts_first is None: ts_first = ts
                ts_last = ts
                if acc_lim is not None and any(abs(x) >= acc_lim for x in acc):
                    r['acc_saturation_samples'] += 1
                    if r['acc_saturation_samples'] <= 10: event('acc_near_range',rownum,f'At least one axis >= {acc_lim:.3f} m/s²')
                if gyro_lim is not None and any(abs(x) >= gyro_lim for x in gyro):
                    r['gyro_saturation_samples'] += 1
                    if r['gyro_saturation_samples'] <= 10: event('gyro_near_range',rownum,f'At least one axis >= {gyro_lim:.3f} rad/s')
                if previous_ts is not None:
                    dt = ts - previous_ts
                    if dt == 0:
                        r['duplicate_ts'] += 1; event('duplicate_timestamp',rownum,'dt=0')
                    elif dt < 0:
                        r['backward_ts'] += 1; event('backward_timestamp',rownum,f'dt={dt} ms')
                    else:
                        intervals.append(dt)
                        r['positive_intervals'] += 1
                        if abs(dt - nominal_ms) <= args.interval_tolerance_ms:
                            r['near_nominal_intervals'] += 1
                        # Heuristic: rounded number of nominal periods between two samples, minus one.
                        # Counts possible missing samples, NOT proven losses.
                        missing = max(0, round(dt / nominal_ms) - 1)
                        r['estimated_missing_samples'] += missing
                        if dt > args.gap_ms:
                            r['estimated_missing_in_gaps'] += missing
                        if dt > args.gap_ms:
                            r['gaps'] += 1; r['gap_total_s'] += dt / 1000
                            r['max_gap_ms'] = max(r['max_gap_ms'],dt)
                            event('gap',rownum,f'dt={dt} ms')
                        else: effective_ms += dt
                    # Only compare consecutive valid samples with plausible spacing.
                    if 0 < dt <= args.gap_ms:
                        if args.acc_jump is not None and norm_diff(acc,previous_acc) > args.acc_jump:
                            r['acc_jump_samples'] += 1
                            if r['acc_jump_samples'] <= 10: event('acc_jump',rownum,f'difference={norm_diff(acc,previous_acc):.3f} m/s²')
                        if args.gyro_jump is not None and norm_diff(gyro,previous_gyro) > args.gyro_jump:
                            r['gyro_jump_samples'] += 1
                            if r['gyro_jump_samples'] <= 10: event('gyro_jump',rownum,f'difference={norm_diff(gyro,previous_gyro):.3f} rad/s')
                        acc_run = acc_run + 1 if acc == previous_acc else 1
                        gyro_run = gyro_run + 1 if gyro == previous_gyro else 1
                        if acc_run >= min_run and not acc_run_reported:
                            r['constant_acc_runs'] += 1; event('constant_acc_run',rownum,f'>={min_run} identical consecutive 3-axis readings'); acc_run_reported=True
                        if gyro_run >= min_run and not gyro_run_reported:
                            r['constant_gyro_runs'] += 1; event('constant_gyro_run',rownum,f'>={min_run} identical consecutive 3-axis readings'); gyro_run_reported=True
                        if acc_run == 1: acc_run_reported=False
                        if gyro_run == 1: gyro_run_reported=False
                    else:
                        acc_run = gyro_run = 1; acc_run_reported=gyro_run_reported=False
                else: acc_run = gyro_run = 1
                previous_ts, previous_acc, previous_gyro = ts, acc, gyro
    except (OSError, UnicodeError, csv.Error) as e:
        event('file_read_error',0,str(e))
    r['first_ts_ms'] = ts_first if ts_first is not None else ''
    r['last_ts_ms'] = ts_last if ts_last is not None else ''
    r['duration_s'] = round((ts_last-ts_first)/1000,3) if ts_first is not None else 0
    r['effective_duration_s'] = round(effective_ms/1000,3)
    if intervals:
        r['near_nominal_pct'] = round(100*r['near_nominal_intervals']/len(intervals), 4)
        sorted_dt = sorted(intervals)
        def percentile(q):
            pos = (len(sorted_dt)-1)*q
            lo = int(pos); hi = min(lo+1,len(sorted_dt)-1)
            return round(sorted_dt[lo]+(sorted_dt[hi]-sorted_dt[lo])*(pos-lo),3)
        r['p05_dt_ms'],r['p95_dt_ms'],r['p99_dt_ms'] = (percentile(q) for q in (0.05,0.95,0.99))
        r['median_dt_ms'] = round(median(intervals),3)
        r['mean_dt_ms'] = round(sum(intervals)/len(intervals),3)
        r['estimated_hz'] = round(1000/median(intervals),3)
    if r['valid_rows'] < 2: event('insufficient_samples',0,'Fewer than 2 usable rows')
    r['warnings'] = '|'.join(sorted(issues))
    # Disjoint distribution bins (ms): lower bound inclusive, upper bound exclusive.
    bounds = [0,25,40,45,55,60,75,args.gap_ms,float('inf')]
    # If gap threshold is <= 75 ms, use ordered standard bins plus final tail instead.
    if args.gap_ms <= 75: bounds = [0,25,40,45,55,60,75,float('inf')]
    hist = Counter()
    for dt in intervals:
        for low,high in zip(bounds,bounds[1:]):
            if low <= dt < high:
                hist[(low,high)] += 1
                break
    return r,events,hist


def read_gt_wheels(directories):
    """Map (wave, participant, date) to wheels from annotation filenames.

    When a directory contains wave-1/wave-2, use the wave for exact matching.
    Files without an identifiable wave are used only if their participant/date
    has a single wheel across all such files.
    """
    mapping = defaultdict(set)
    warnings = []
    pattern = re.compile(r'^(\d+)_(\d{8})_(\d{4})_([ABCD])_ppr2\.txt$', re.I)
    for directory in directories:
        for path in sorted(directory.rglob('*.txt')):
            match = pattern.fullmatch(path.name)
            if not match:
                warnings.append(f'Unrecognized annotation filename: {path}')
                continue
            pid, date, _, wheel = match.groups()
            wave_parts = [part for part in path.relative_to(directory).parts[:-1]
                          if re.fullmatch(r'wave-\d+', part, re.I)]
            if not wave_parts and re.fullmatch(r'wave-\d+', directory.name, re.I):
                wave_parts = [directory.name]
            if len(wave_parts) > 1:
                warnings.append(f'Ambiguous wave in annotation path: {path}')
                continue
            wave = wave_parts[0].lower() if wave_parts else ''
            mapping[(wave, pid, date)].add(wheel.upper())
    return mapping, warnings

def write_csv(path, rows, fields):
    with path.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)

def show_progress(done, total, started, enabled=True):
    """Single-line progress indicator, one update per processed file."""
    if not enabled or total == 0:
        return
    width = 30
    filled = round(width * done / total)
    elapsed = time.monotonic() - started
    eta = elapsed * (total - done) / done if done else 0
    bar = '#' * filled + '-' * (width - filled)
    sys.stderr.write(f'\rFiles [{bar}] {done}/{total} ({100 * done / total:5.1f}%) | ETA {eta:,.0f}s')
    sys.stderr.flush()
    if done == total:
        sys.stderr.write('\n')


def main():
    a = parse_args()
    waves = list(dict.fromkeys(w for group in a.wave for w in group)) if a.wave else []
    roots = [(wave, a.dev_dir / wave) for wave in waves] if waves else [('', a.dev_dir)]
    for wave, root in roots:
        if not root.is_dir(): raise SystemExit(f'Input directory not found: {root}')
    a.output.mkdir(parents=True,exist_ok=True)
    gt_wheels, gt_warnings = read_gt_wheels(a.gt_dir)
    by_visit=defaultdict(dict); bad_names=[]
    for wave, root in roots:
        for p in sorted(root.glob('*.csv')):
            m=NAME.fullmatch(p.name)
            if not m: bad_names.append(str(p));continue
            pid,date,dev=m.groups()
            key=(wave,pid,date)
            if dev in by_visit[key]:
                bad_names.append(f'DUPLICATE DEVICE KEY: {p}');continue
            by_visit[key][dev]=p
    if not by_visit: raise SystemExit('No matching device files in selected directories')
    records=[];events=[];visits=[]
    wheel_stats=defaultdict(lambda: {'visits': 0, 'participants': set(), 'seconds': 0.0})
    histograms=defaultdict(Counter)
    total_files = sum(len(files) for files in by_visit.values())
    processed_files = 0
    started = time.monotonic()
    progress_enabled = not a.no_progress
    show_progress(0, total_files, started, progress_enabled)
    for (wave,pid,date),files in sorted(by_visit.items()):
        current=[]
        for dev,path in sorted(files.items()):
            r, ev, hist=analyze(path,pid,date,dev,a)
            histograms[wave].update(hist)
            histograms['__all__'].update(hist)
            r['wave']=wave
            for item in ev: item['wave']=wave
            records.append(r);events.extend(ev);current.append(r)
            processed_files += 1
            show_progress(processed_files, total_files, started, progress_enabled)
        usable=[r for r in current if r['valid_rows']>=2 and r['first_ts_ms']!='']
        starts=[r['first_ts_ms'] for r in usable]
        ends=[r['last_ts_ms'] for r in usable]
        durations=[r['effective_duration_s'] for r in usable]
        start_spread=max(starts)-min(starts) if len(starts)>1 else 0
        end_spread=max(ends)-min(ends) if len(ends)>1 else 0
        duration_spread=max(durations)-min(durations) if len(durations)>1 else 0
        missing=sorted(EXPECTED-set(files),key=int)
        warnings=[]
        if missing: warnings.append('missing_devices')
        if len(usable)<len(files): warnings.append('unusable_device_files')
        if start_spread>a.start_end_tolerance_ms: warnings.append('start_time_mismatch')
        if end_spread>a.start_end_tolerance_ms: warnings.append('end_time_mismatch')
        if duration_spread>a.duration_tolerance_s: warnings.append('effective_duration_mismatch')
        visit_duration = sum(durations)/len(durations) if durations else 0
        matched_wheels = gt_wheels.get((wave.lower(),pid,date), set())
        if not matched_wheels:
            matched_wheels = gt_wheels.get(('',pid,date), set())
        if not a.gt_dir:
            wheel = ''
        elif len(matched_wheels) == 1:
            wheel = next(iter(matched_wheels))
            if durations:
                wheel_stats[wheel]['visits'] += 1
                wheel_stats[wheel]['participants'].add(pid)
                wheel_stats[wheel]['seconds'] += visit_duration
        else:
            wheel = ''
            warnings.append('wheel_not_found' if not matched_wheels else 'ambiguous_wheel')
        visits.append({'wave':wave,'pid':pid,'date':date,'wheel':wheel,'files':len(files),'usable_devices':len(usable),'missing_devices':'|'.join(missing),'start_spread_ms':start_spread,'end_spread_ms':end_spread,'effective_duration_spread_s':round(duration_spread,3),'estimated_visit_duration_s':round(visit_duration,3),'warnings':'|'.join(warnings)})
    write_csv(a.output/'device_quality.csv',records,['wave']+FIELDS)
    hist_rows=[]
    for wave,counts in sorted(histograms.items()):
        total=sum(counts.values())
        for (low,high),count in sorted(counts.items()):
            hist_rows.append({'wave':'ALL' if wave=='__all__' else (wave or 'direct'),
                              'dt_from_ms':low,'dt_to_ms_exclusive':high if math.isfinite(high) else 'inf',
                              'intervals':count,'percentage':round(100*count/total,5) if total else 0})
    write_csv(a.output/'interval_distribution.csv',hist_rows,['wave','dt_from_ms','dt_to_ms_exclusive','intervals','percentage'])
    write_csv(a.output/'visit_quality.csv',visits,['wave','pid','date','wheel','files','usable_devices','missing_devices','start_spread_ms','end_spread_ms','effective_duration_spread_s','estimated_visit_duration_s','warnings'])
    write_csv(a.output/'quality_events.csv',events,['wave','pid','date','device','filename','row','type','detail'])
    (a.output/'unrecognized_filenames.txt').write_text('\n'.join(bad_names)+ ('\n' if bad_names else ''),encoding='utf-8')
    if a.gt_dir:
        wheel_rows = [{'wheel': wheel, 'visits': stats['visits'],
                       'unique_participants': len(stats['participants']),
                       'effective_recording_hours': round(stats['seconds']/3600, 4)}
                      for wheel, stats in sorted(wheel_stats.items())]
        write_csv(a.output/'wheel_recording_hours.csv', wheel_rows,
                  ['wheel','visits','unique_participants','effective_recording_hours'])
        (a.output/'gt_filename_warnings.txt').write_text(
            '\n'.join(gt_warnings) + ('\n' if gt_warnings else ''), encoding='utf-8')
    print(f'Waves analyzed: {", ".join(waves) if waves else "direct directory"}')
    print(f'Visits: {len(visits)}; device files: {len(records)}; events logged: {len(events)}')
    print(f'Visits with warnings: {sum(bool(x["warnings"]) for x in visits)}; device files with warnings: {sum(bool(x["warnings"]) for x in records)}')
    print(f'Total estimated recording hours: {sum(v["estimated_visit_duration_s"] for v in visits)/3600:.3f}')
    if a.gt_dir:
        for row in wheel_rows:
            print(f'Wheel {row["wheel"]}: {row["visits"]} visits, '
                  f'{row["unique_participants"]} participants, '
                  f'{row["effective_recording_hours"]:.3f} h')
        unassigned = sum(not v['wheel'] for v in visits)
        print(f'Visits without unambiguous wheel assignment: {unassigned}')
        print(f'Unrecognized ground-truth filenames: {len(gt_warnings)}')
    total_intervals=sum(r['positive_intervals'] for r in records)
    total_near=sum(r['near_nominal_intervals'] for r in records)
    print(f'Near-nominal intervals (+/-{a.interval_tolerance_ms:g} ms): {total_near:,}/{total_intervals:,} ({100*total_near/total_intervals:.3f}%)' if total_intervals else 'No positive inter-sample intervals')
    print(f'Estimated missing samples (heuristic): {sum(r["estimated_missing_samples"] for r in records):,}')
    print(f'Reports: {a.output.resolve()}')
    if not a.acc_range_g or not a.gyro_range_dps: print('NOTE: Saturation checks require --acc-range-g and --gyro-range-dps.')
    if a.acc_jump is None or a.gyro_jump is None: print('NOTE: Jump checks require --acc-jump and --gyro-jump.')

if __name__ == '__main__': main()
