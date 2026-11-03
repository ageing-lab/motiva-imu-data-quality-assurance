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
%   Constructs ground-truth annotation filenames and resolves their
%   directories for processed or raw recordings.

function [gt_fname, path] = get_gtfile_path(pid, fecha, hora, rueda, is_ppr, directorio, cfg)
    % Return the ground-truth filename and directory for the selected source, version, and wave.
    % Create cfg with construir_paths_visualizacion(...).
    if nargin < 7 || isempty(cfg)
        cfg = motiva.construir_paths_visualizacion();
    end

    gt_fname = string(pid) + "_" + string(fecha) + "_" + string(hora) + "_" + string(rueda) + ".txt";

    if is_ppr
        path = cfg.app_dir;
        if nargin >= 6 && ~isempty(directorio)
            path = fullfile(path, directorio);
        end

        [~, name, ext] = fileparts(gt_fname);
        gt_fname = name + "_ppr2" + ext;
    else
        % Keep support for reading raw files, now under
        % repo|pendientes/app/raw/<wave> instead of the former absolute path.
        path = cfg.app_raw_dir;
        if nargin >= 6 && ~isempty(directorio)
            path = fullfile(path, directorio);
        end
    end
end
