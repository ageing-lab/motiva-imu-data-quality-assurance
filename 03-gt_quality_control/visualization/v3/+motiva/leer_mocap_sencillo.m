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
%   Provides a compatibility wrapper for loading the five-sensor
%   motion-capture configuration.

function [cintura, brazoD, brazoI, abzD, abzI, musloD, musloI, tobD, tobI] = leer_mocap_sencillo(pid, fecha, verbose, cfg)
%LEER_MOCAP_SENCILLO Load the five-sensor setup (compatibility wrapper).
    if nargin < 4 || isempty(cfg)
        cfg = motiva.construir_paths_visualizacion();
    end
    [cintura, brazoD, brazoI, abzD, abzI, musloD, musloI, tobD, tobI] = ...
        motiva.leer_mocap(pid, fecha, verbose, cfg, 'sencillo');
end
