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
%   Loads and plots lower-back, forearm, and ankle signals for the
%   five-device motion-capture configuration.

function plot_mocap_sencillo_C(pid, fecha, t_etiquetas, tabla_series, cfg)
    if nargin < 5 || isempty(cfg)
        cfg = motiva.construir_paths_visualizacion();
    end
    [cintura, brazoD, brazoI, abzD, abzI, musloD, musloI, tobD, tobI] = motiva.leer_mocap_sencillo(pid, fecha, false, cfg);

    % Plot the available sensors in the five-device configuration.
    if ~isempty(cintura)
        motiva.plot_dispositivo_C(cintura, 'cintura', t_etiquetas, tabla_series);
    end
    
    if ~isempty(abzD)
        motiva.plot_dispositivo_C(abzD, 'abzD', t_etiquetas, tabla_series);
    end
    if ~isempty(abzI)
        motiva.plot_dispositivo_C(abzI, 'abzI', t_etiquetas, tabla_series);
    end
    
    if ~isempty(tobD)
        motiva.plot_dispositivo_C(tobD, 'tobD', t_etiquetas, tabla_series);
    end
    if ~isempty(tobI)
        motiva.plot_dispositivo_C(tobI, 'tobI', t_etiquetas, tabla_series);
    end
end
