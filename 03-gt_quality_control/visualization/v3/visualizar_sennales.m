% SPDX-FileCopyrightText: 2023-2026 Antonio Cobo Sánchez de Rojas
% SPDX-FileCopyrightText: 2023-2026 Elena Villalba Mora
% SPDX-License-Identifier: AGPL-3.0-only
%
% Project: MOTIVA (PID2022-140214OB-C21)
% Associated dataset:
%   MOTIVA-IMU: A Multi-Sensor Inertial Motion Dataset of SPPB Tests and VIVIFRAIL Exercises in Older Adults
%
% Authors and affiliations:
%   Antonio Cobo Sánchez de Rojas
%     Employer: Centro de Investigación Biomédica en Red (CIBER)
%     Additional affiliation: Universidad Politécnica de Madrid (UPM)
%
%   Elena Villalba Mora
%     Employer: Universidad Politécnica de Madrid (UPM)
%     Additional affiliation: Centro de Investigación Biomédica en Red (CIBER)
%
% Institutional affiliations do not indicate institutional ownership
% of the software copyright.
%
% This file is part of the MOTIVA project.
% Licensed under the GNU Affero General Public License, version 3 only.
% This software is distributed WITHOUT ANY WARRANTY; without even the implied
% warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
% See the LICENSE file in the project root for license terms.
%
% Description:
%   Loads ground-truth annotations and IMU recordings for a selected
%   exercise session and displays annotated inertial signals.

function visualizar_sennales(pid, fecha, hora, rueda, is_ppr, directorio, varargin)
    %% Read the recording files for the selected session.
    % The path for ground-truth files is resolved by
    % leer_groundTruth.m

    % The path for sensor signals is resolved by
    % leer_mocap_sencillo.m

    % Read the ground-truth file.
    cfg = motiva.construir_paths_visualizacion(varargin{:});
    [gt_fname, gt_dir] = motiva.get_gtfile_path(pid, fecha, hora, rueda, is_ppr, directorio, cfg);

    ground_truth = motiva.leer_groundTruth(gt_dir, gt_fname);

    % Select the motion-capture mode ('sencillo' = five sensors, 'completo' = nine
    % sensors).
    % mocap_name = get_mocap_name(pid, fecha);
    % All recordings in the pilot acquisition use the five-sensor mode.
    mocap_name = 'sencillo';

    % Plot the signals for each device, sensor, and
    % axis
    motiva.plot_CONSULTA(pid, fecha, ground_truth, mocap_name, cfg);
end
