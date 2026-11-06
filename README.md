# MOTIVA-IMU Data Quality Assurance

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24001182.svg)](https://doi.org/10.5281/zenodo.24001182)

Tools for preparing, inspecting, and quality-checking the **MOTIVA-IMU** dataset, including inertial motion-capture recordings and exercise annotations (*ground truth*).

The repository is organized into three stages: file preparation and integrity, inertial signal integrity, and ground-truth quality control. It also includes a MATLAB visualization tool for inspecting signals alongside their annotations.

## Repository structure

```text
data-quality-assurance/
├── 01-data_preparation-file_integrity/
│   ├── prepare-raw-files.py
│   └── correct_timestamps.py
├── 02-inertial_signal_integrity/
│   └── check_imu_quality.py
├── 03-gt_quality_control/
│   ├── check_gt_quality.py
│   ├── move-app-files.py
│   └── visualization/v3/
│       ├── visualizar_sennales.m
│       ├── +motiva/
│       ├── tests/
│       └── README.md
├── .gitignore
├── AUTHORS.md
├── CITATION.cff
├── LICENSE
└── README.md
```

Directories named `deprecated/` and `results/` may be present locally, but are excluded from version control by `.gitignore`.

## Requirements

- **Python 3** for the preparation and quality-control scripts. The five Python scripts use only the Python standard library. The code has been tested with Python 3.14.4. 
The minimum version required to run the entire codebase has not been experimentally determined; therefore, Python 3.10 or later is recommended as a conservative baseline.
- **MATLAB** for the signal visualization tool and its `matlab.unittest` tests. Visualization requires a MATLAB installation supporting tables, readtable, jsondecode, and string arrays; running the tests requires matlab.unittest. 
The code has been tested with MATLAB R2025a; however, the minimum version required to run the entire codebase has not been experimentally determined.

The program was developed for execution in a Linux environment and has been tested on Ubuntu 24.04 with Python, MATLAB, and the corresponding dependencies. 
It uses Unix-style file system paths and requires read and write permissions in the working directories. 
Compatibility with Windows and macOS has not been validated; running the program on these systems may require adjustments to paths, configuration, or dependencies. 
Minimum RAM and processor requirements have not been determined.

The Python interpreter, the MATLAB environment, and their respective licenses are not included in the ‘MOTIVA-IMU Data Quality Assurance’ code distribution.
No dataset files are bundled with this repository. Provide the input directories on your local system.

## 1. Data preparation and file integrity

**Directory:** `01-data_preparation-file_integrity/`

### `prepare-raw-files.py`

Transfers pending device recordings and application annotations into their expected locations. Device CSVs are copied without modifying their content. Application annotation files are copied into the raw repository directory and processed JSONL versions are generated with `"valido": true`.

The script discovers `wave-*` directories, avoids overwriting different destination content, and supports a preview mode.

```bash
python3 01-data_preparation-file_integrity/prepare-raw-files.py \
  --root-pending /path/to/working-root \
  --root-repo /path/to/publication-root \
  --dry-run
```

Remove `--dry-run` only after checking the planned operations. The script **removes successfully transferred source files** from the pending directories.

Expected directory conventions include:

```text
<working-root>/pending/devices/wave-*/
<working-root>/pending/app/raw/wave-*/
<publication-root>/repo/devices/wave-*/
<publication-root>/repo/app/raw/wave-*/
```

Processed annotations are written under `pending/app/v1/wave-1/` and/or `pending/app/v2/wave-*/`, as appropriate.

### `correct_timestamps.py`

Recursively processes CSV files and subtracts **3600 seconds** from the first semicolon-delimited field, preserving the remaining fields.

```bash
python3 01-data_preparation-file_integrity/correct_timestamps.py \
  /path/to/device-csv-directory --dry-run
```

**Warning:** without `--dry-run`, the script modifies the original CSVs. It is **not idempotent**: running it twice applies the correction twice. Use it only when the input timestamps require that correction.

## 2. Inertial signal integrity

**Directory:** `02-inertial_signal_integrity/`

`check_imu_quality.py` performs a **read-only** audit of IMU CSV recordings. Checks and summaries include sample counts, invalid rows, timestamp ordering, duplicate timestamps, sampling intervals, recording gaps, and configurable signal-quality indicators. Optional ground-truth directories support recording-level comparisons and VIVIFRAIL wheel recording-time summaries.

```bash
python3 02-inertial_signal_integrity/check_imu_quality.py \
  /path/to/repo/devices \
  --wave wave-1 wave-2 \
  --gt-dir /path/to/repo/app/v2 \
  --output 02-inertial_signal_integrity/results/imu_qc
```

The default expected sampling frequency is **20 Hz**; other thresholds can be adjusted using command-line options. The `--gt-dir` argument is optional. Generated reports include per-device and per-visit CSV summaries, quality events, and interval statistics.

Run `python3 02-inertial_signal_integrity/check_imu_quality.py --help` for the complete set of options.

## 3. Ground-truth quality control

**Directory:** `03-gt_quality_control/`

### `check_gt_quality.py`

Performs a **non-destructive** audit of versioned JSONL annotation files. It checks annotation consistency, compares expected set-start counts for supported VIVIFRAIL wheels (**B, C, D**), identifies potentially duplicated nearby annotations, and reports invalid annotations.

```bash
python3 03-gt_quality_control/check_gt_quality.py \
  /path/to/repo/app/v2 \
  --output 03-gt_quality_control/results/gt_qc_results
```

The default proximity threshold for candidate duplicate annotations is **550 ms**. Exercise IDs and phase IDs can be excluded from that check using `--exclude-evid` and `--exclude-phsid`.

Generated reports include:

- `gt_file_quality.csv`
- `gt_set_counts.csv`
- `gt_duplicate_candidates.csv`
- `gt_invalid_annotations.csv`
- `gt_quality_events.csv`
- `gt_quality_summary.txt`

A flagged candidate is **not automatically an erroneous annotation**; review the reported cases before changing the ground truth.

### `move-app-files.py`

Moves selected processed annotation files from `pending/app/v2/<wave>/` to `repo/app/v2/<wave>/`. It supports whole-wave transfers, selection via a list file (`--lista`), and `--dry-run`.

```bash
python3 03-gt_quality_control/move-app-files.py wave-2 \
  --root_pending /path/to/working-root \
  --root_repo /path/to/publication-root \
  --dry-run
```

The destination must not already contain the file. Remove `--dry-run` to perform the move.

### MATLAB visualization

The modular visualizer is located in `03-gt_quality_control/visualization/v3/`. Its public entry point is `visualizar_sennales.m`; implementation functions are grouped in the `+motiva/` package.

In MATLAB:

```matlab
addpath('/path/to/data-quality-assurance/03-gt_quality_control/visualization/v3');

visualizar_sennales('12', '20260102', '1030', 'A', true, '', ...
    'origen', 'pending', 'version', 'v2', 'wave', 'wave-2', ...
    'root_pending', '/path/to/working-root', ...
    'root_repo', '/path/to/publication-root');
```

The values above are illustrative. See [the visualizer documentation](03-gt_quality_control/visualization/v3/README.md) for configuration details and usage examples.

Automated MATLAB tests are provided in the visualizer's `tests/` directory:

```matlab
cd('/path/to/data-quality-assurance/03-gt_quality_control/visualization/v3/tests');
results = run_tests();
```

The tests have not been verified here against a live MATLAB installation or representative real recordings.

## Reproducibility and safety

- Run `--dry-run` first for scripts that support it and **modify or move files**.
- Keep an independent backup of source recordings and annotations before destructive operations.
- Store generated reports under `results/`; these directories are ignored by Git.
- Review quality-control reports before accepting, rejecting, or editing any recording or annotation.
- Check script-specific `--help` output for parameters and defaults; thresholds should be reported when using results in research.

## Scope

This repository contains supporting scripts for dataset preparation, quality assurance, and visualization. The quality-control checks provide evidence for reviewing data quality; they do not by themselves establish that every recording or annotation is correct.

## License

This software is distributed under the **GNU Affero General Public License, version 3 only (AGPLv3; SPDX identifier: `AGPL-3.0-only`)**.

See [LICENSE](LICENSE) for the software copyright and licensing notice, the warranty disclaimer, and the complete license text.

## Copyright and authorship

Copyright © 2023–2026 **Antonio Cobo Sánchez de Rojas** and **Elena Villalba Mora**.

The authors and copyright holders of this software are:

- **Antonio Cobo Sánchez de Rojas** — Centro de Investigación Biomédica en Red (CIBER).
- **Elena Villalba Mora** — Universidad Politécnica de Madrid (UPM).

Institutional affiliations are provided for identification purposes and do not indicate institutional ownership of the software copyright.

The software was developed as part of the MOTIVA research project (PID2022-140214OB-C21).

See [AUTHORS.md](AUTHORS.md) for author information and [LICENSE](LICENSE) for the copyright notice and complete GNU AGPLv3 license text.
Copyright notices in individual source files identify the authors as the copyright holders.

## Citation

If you use these software in your research, please acknowledge the MOTIVA-IMU project and cite the associated publication and the following archived release:

Cobo, A., & Villalba-Mora, E. (2026). *MOTIVA-IMU Data Quality Assurance* (Version 1.0.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.24001183

Citation metadata are also provided in the [CITATION.cff](CITATION.cff) file.


This citation request is separate from the legal obligations of AGPLv3; the license does not itself require citation of a scientific publication.

## Funding

This software is part of the **MOTIVA Project (Grant Number ID PID2022-140214OB-C21)** funded by **MCIN/AEI/10.13039/501100011033** and **FEDER/UE** and was supported by **CIBER - Consorcio Centro de Investigación Biomédica en Red - (CB06/01/0051), Instituto de Salud Carlos III, Ministerio de Ciencia e Innovación**.
