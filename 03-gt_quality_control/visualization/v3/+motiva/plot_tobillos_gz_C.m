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
%   Loads the five-sensor recording and plots the gyroscope Z-axis
%   signals of both ankles with ground-truth markers.

function plot_tobillos_gz_C(pid, fecha, t_etiquetas, tabla_series, cfg)
    if nargin < 5 || isempty(cfg)
        cfg = motiva.construir_paths_visualizacion();
    end

    [cintura, brazoD, brazoI, abzD, abzI, musloD, musloI, tobD, tobI] = motiva.leer_mocap_sencillo(pid, fecha, false, cfg);

    if ~isempty(tobD) && ~isempty(tobI)
        motiva.plot_gz_C(tobD, tobI, t_etiquetas.evIds, ...
            t_etiquetas.t_inicio_e, ...
            t_etiquetas.t_inicio_s, ...
            t_etiquetas.t_final_r, ...
            t_etiquetas.t_nula_r, ...
            t_etiquetas.t_pausa);
    end
end
