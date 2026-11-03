# MOTIVA-IMU Data Quality Assurance — Inertial Signal Visualizer (v3)

MATLAB tool for visualizing MOTIVA-IMU inertial recordings together with exercise ground-truth annotations. This version exposes **one public entry point**, `visualizar_sennales.m`, and organizes its implementation in the `+motiva` package.

## Directory structure

```text
visualization/v3/
├── visualizar_sennales.m       # Public entry point
├── +motiva/                    # Configuration, I/O, annotations, and plots
│   ├── construir_paths_visualizacion.m *
│   ├── get_gtfile_path.m *
│   ├── leer_groundTruth.m *
│   ├── leer_sensor.m *
│   ├── leer_mocap.m *
│   ├── delimitar_series.m *
│   ├── prepare_annotation_plot_data.m *
│   ├── plot_CONSULTA.m *
│   └── ...                     # Additional plotting helpers and wrappers
├── README.md
└── tests/
    ├── run_tests.m
    ├── test_configuration.m
    ├── test_sensor_loading.m
    ├── test_ground_truth_io.m
    └── test_annotations.m
```

## Requirements

- MATLAB with support for `table`, `readtable`, `jsondecode`, string arrays, and `matlab.unittest`.
The code has been tested with MATLAB R2025a; however, the minimum version required to run the entire codebase has not been experimentally determined.
- Access to the MOTIVA-IMU IMU recordings (CSV) and ground-truth annotations (text/JSONL). **Data are not included** in this folder.

The MATLAB environment, and its license is not included in the ‘MOTIVA-IMU Data Quality Assurance’ code distribution.

The program was developed for execution in a Linux environment and has been tested on Ubuntu 24.04 with Python, MATLAB, and the corresponding dependencies. 
It uses Unix-style file system paths and requires read and write permissions in the working directories. 
Compatibility with Windows and macOS has not been validated; running the program on these systems may require adjustments to paths, configuration, or dependencies. 
Minimum RAM and processor requirements have not been determined.

## Setup

Add the `visualization/v3` directory to the MATLAB search path:

```matlab
addpath('/path/to/data-quality-assurance/03-gt_quality_control/visualization/v3');
```

Do **not** add `+motiva` directly to the path: MATLAB resolves package functions automatically as `motiva.function_name`.

## Usage

The public function is:

```matlab
visualizar_sennales(pid, fecha, hora, rueda, is_ppr, directorio, ...)
```

| Argument | Description |
| --- | --- |
| `pid` | Participant identifier, as used in filenames |
| `fecha` | Recording date identifier, as used in filenames |
| `hora` | Recording time identifier, as used in filenames |
| `rueda` | Exercise-wheel identifier, as used in filenames |
| `is_ppr` | `true` to load a processed annotation file with `_ppr2` suffix; `false` to load the raw annotation file |
| `directorio` | Optional subdirectory within the selected annotation directory; use `''` for none |
| Name-value pairs | Optional data-source and path configuration (below) |

For example, using **illustrative identifiers**:

```matlab
visualizar_sennales('12', '20260102', '1030', 'A', true, '', ...
    'origen', 'repo', ...
    'version', 'v2', ...
    'wave', 'wave-1', ...
    'base_dir', '/path/to/data-root');
```

For separate working and repository roots:

```matlab
visualizar_sennales('12', '20260102', '1030', 'A', true, '', ...
    'origen', 'pending', ...
    'version', 'v2', ...
    'wave', 'wave-2', ...
    'root_pending', '/path/to/working-root', ...
    'root_repo', '/path/to/publication-root');
```

The second example reads annotations from the `pending` tree while continuing to read sensor data from the `repo` tree.

### Configuration options

| Option | Accepted values / meaning | Default |
| --- | --- | --- |
| `origen` | `repo`, `pending`, or `pendientes` | `repo` |
| `version` | `v1` or `v2` | `v2` |
| `wave` | `wave-1` or `wave-2` | `wave-1` |
| `base_dir` | Common parent of `repo/` and `pending/` (or `pendientes/`) | Auto-detected if possible |
| `root_pending` | Parent of `pending/` or `pendientes/` | `base_dir` |
| `root_repo` | Parent of `repo/` | `base_dir` |

The program checks that the selected processed-annotation directory and device directory exist. Explicitly setting the roots is recommended for reproducibility; automatic discovery and a legacy relative-path fallback are also implemented.

### Expected data layout

```text
<root_repo>/
└── repo/
    ├── devices/
    │   ├── wave-1/
    │   │   └── <pid>_<fecha>_<sensor-id>.csv
    │   └── wave-2/
    │       └── <pid>_<fecha>_<sensor-id>.csv
    └── app/
        ├── raw/
        │   ├── wave-1/
        │   │   └── <pid>_<fecha>_<hora>_<rueda>.txt
        │   └── wave-2/
        │       └── <pid>_<fecha>_<hora>_<rueda>.txt
        ├── v1/wave-1/
        │    └── <pid>_<fecha>_<hora>_<rueda>_ppr2.txt
        └── v2/
            ├── wave-1/
            │   └── <pid>_<fecha>_<hora>_<rueda>_ppr2.txt
            └── wave-2/
                └── <pid>_<fecha>_<hora>_<rueda>_ppr2.txt

<root_pending>/
└── pending/
    ├── devices/
    │   ├── wave-1/
    │   │   └── <pid>_<fecha>_<sensor-id>.csv
    │   └── wave-2/
    │       └── <pid>_<fecha>_<sensor-id>.csv
    └── app/
        ├── raw/
        │   ├── wave-1/
        │   │   └── <pid>_<fecha>_<hora>_<rueda>.txt
        │   └── wave-2/
        │       └── <pid>_<fecha>_<hora>_<rueda>.txt
        ├── v1/wave-1/
        │    └── <pid>_<fecha>_<hora>_<rueda>_ppr2.txt
        └── v2/
            ├── wave-1/
            │   └── <pid>_<fecha>_<hora>_<rueda>_ppr2.txt
            └── wave-2/
                └── <pid>_<fecha>_<hora>_<rueda>_ppr2.txt
```

The `wave-1` and `wave-2` folders are selected with the `wave` option. When `origen='pendientes'`, the corresponding folder must actually be named `pendientes`; the code does not automatically translate that option to `pending`.

**Sensor CSVs:** the loader expects eight columns representing epoch seconds, milliseconds, three accelerometer axes (`ax`, `ay`, `az`), and three gyroscope axes (`gx`, `gy`, `gz`). It computes `tsmillis` from the first two columns.

**Annotations:** annotation files are read as JSON records and used to delimit exercise series and plot annotated events. The processed filename includes the `_ppr2` suffix when `is_ppr=true`.

## Visualization behavior

The public entry point currently sets the motion-capture mode to **`sencillo` (five sensors)**. Although internal functions for nine-sensor (`completo`) recordings exist, automatic selection of that mode is **not enabled** by the public entry point. Plotting and annotation-processing logic remain internal to `+motiva`.

## Automated tests

From MATLAB:

```matlab
cd('/path/to/data-quality-assurance/03-gt_quality_control/visualization/v3/tests');
results = run_tests();
```

The tests cover configuration and paths, sensor loading, ground-truth reading, and annotation preparation. They use synthetic temporary fixtures rather than actual participant recordings.

**Validation status:** the presence of automated tests does not establish that they pass on every MATLAB release or that generated plots match the original version. Run the suite in your MATLAB environment and visually compare representative recordings before relying on the software for research outputs.

## Scope and maintenance

When modifying the visualizer, keep `visualizar_sennales.m` as the stable public API, place implementation code inside `+motiva`, and extend `tests/` for changes to parsing, configuration, or signal processing.

## Copyright and authorship

Copyright © 2023–2026 **Antonio Cobo Sánchez de Rojas** and **Elena Villalba Mora**.

The authors and copyright holders are:

- **Antonio Cobo Sánchez de Rojas**
  Employed by Centro de Investigación Biomédica en Red (CIBER).
  Also affiliated with Universidad Politécnica de Madrid (UPM)
  as an “investigador colaborador preferente”.

- **Elena Villalba Mora**
  Employed by Universidad Politécnica de Madrid (UPM).
  Also affiliated with Centro de Investigación Biomédica en Red (CIBER)
  as “personal adscrito”.

Institutional affiliations are provided for identification purposes and do not indicate institutional ownership of the software copyright.

See [AUTHORS.md](../../../AUTHORS.md) for author information.

## License

This visualizer is part of **MOTIVA-IMU Data Quality Assurance** and is distributed under the **GNU Affero General Public License, version 3 only (AGPLv3; SPDX identifier: `AGPL-3.0-only`)**.

See [LICENSE](../../../LICENSE) for the software copyright and licensing notice, the warranty disclaimer, and the complete license text.
