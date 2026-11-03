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
%   Prepares ground-truth annotations and dispatches motion-signal
%   visualization according to the selected sensor configuration.

function plot_CONSULTA(pid, fecha, ground_truth, mocap_name, cfg)
%PLOT_CONSULTA Plot motion capture signals with prepared annotations.
    if nargin < 5 || isempty(cfg)
        cfg = motiva.construir_paths_visualizacion();
    end

    [tiempos, tabla_series] = motiva.prepare_annotation_plot_data(ground_truth);

    if strcmp(mocap_name, 'completo')
        motiva.plot_mocap_completo_C(pid, fecha, tiempos, tabla_series, cfg);
    elseif strcmp(mocap_name, 'sencillo')
        motiva.plot_mocap_sencillo_C(pid, fecha, tiempos, tabla_series, cfg);
    elseif strcmp(mocap_name, 'tobillos_gz')
        motiva.plot_tobillos_gz_C(pid, fecha, tiempos, tabla_series, cfg);
    end
end
