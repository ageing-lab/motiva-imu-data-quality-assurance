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
%   Loads an IMU CSV recording, assigns accelerometer and gyroscope
%   channel names, and computes millisecond epoch timestamps.

function datos = leer_sensor(sensor_fname, varargin)
    %% Load the contents of a sensor file into a table.
    % Create an inputParser object.
    p = inputParser;
    need_correction = false;

    % Define required arguments.
    addRequired(p, 'sensor_fname');

    % Define optional arguments.
    addParameter(p, 'verbose', false, @(x) islogical(x) || isnumeric(x));

    % Parse the arguments.
    parse(p, sensor_fname, varargin{:});

    % Retrieve the parsed argument values.
    sensor_fname = p.Results.sensor_fname;
    verbose = p.Results.verbose;

    if(verbose == true)
        disp(['Reading sensor file: ' sensor_fname]);
    end
    datos = readtable(sensor_fname);
    % Rename the table variables (columns).
    nombresColumnas = {'seg_epoch', 'ms', 'ax', 'ay', 'az', 'gx', 'gy', 'gz'};
    datos.Properties.VariableNames = nombresColumnas;

    timestampMillis = [];
    if (need_correction)
        timestampMillis = (datos.seg_epoch - 3600) * 1000 + datos.ms;
    else
        timestampMillis = datos.seg_epoch * 1000 + datos.ms;
    end
    

    % Add milliseconds since the Unix epoch as a table variable.
    nombre_nueva_columna = 'tsmillis';
    datos.(nombre_nueva_columna) = timestampMillis;
end
