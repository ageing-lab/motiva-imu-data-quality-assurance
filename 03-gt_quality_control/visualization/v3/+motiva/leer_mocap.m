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
%   Loads available IMU recordings for five- or nine-sensor configurations
%   while preserving the original sensor output positions.

function [cintura, brazoD, brazoI, abzD, abzI, musloD, musloI, tobD, tobI] = leer_mocap(pid, fecha, verbose, cfg, modo)
%LEER_MOCAP Load available IMU recordings using a shared sensor mapping.
%   MODO is 'sencillo' (five sensors) or 'completo' (nine sensors).
%   Missing sensor files yield empty outputs.

    if nargin < 4 || isempty(cfg)
        cfg = motiva.construir_paths_visualizacion();
    end
    if nargin < 5 || isempty(modo)
        modo = 'sencillo';
    end

    if strcmp(modo, 'sencillo')
        sensor_ids = [1, 4, 5, 8, 9];
    elseif strcmp(modo, 'completo')
        sensor_ids = 1:9;
    else
        error('leer_mocap:InvalidMode', ...
            'Unknown motion capture mode: %s', char(modo));
    end

    % Keep the nine original output positions, including absent sensors.
    sensor_data = cell(1, 9);
    for i = sensor_ids
        sensor_file = fullfile(char(cfg.dispositivos_dir), ...
            sprintf('%s_%s_%d.csv', pid, fecha, i));
        if exist(char(sensor_file), 'file') == 2
            sensor_data{i} = motiva.leer_sensor(sensor_file, 'verbose', verbose);
        end
    end

    [cintura, brazoD, brazoI, abzD, abzI, musloD, musloI, tobD, tobI] = ...
        deal(sensor_data{:});
end
