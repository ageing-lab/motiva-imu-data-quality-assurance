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
%   Classifies valid ground-truth events by phase identifier and returns
%   annotation indices for plotting.

function res = parse_gt(gt)

    if ismember('valido', gt.Properties.VariableNames)
        mask = gt.valido == true;
    else
        mask = true(height(gt), 1);
    end

    % Base outputs.
    [res.evIds, res.l_inicio_e] = unique(gt.evId);

    % Define event categories.
    categorias.inicio_s = 1;
    categorias.final_r  = 2;
    categorias.nula_r   = 3;
    categorias.pausa    = [4 5];
    categorias.esc_inicio_b = 7;

    categorias.pausa_brazos = 6;

    % deprecated event categories
    % categorias.brazos_inicio_sube = 1120;
    % categorias.brazos_final_sube = 1220;
    % categorias.brazos_inicio_baja = 2120;
    % categorias.brazos_final_baja = 2220;

    % categorias.piernas_inicio_inicio_s = 1119;
    % categorias.piernas_final_inicio_s = 1219;
    % categorias.piernas_inicio_cambio = 2119;
    % categorias.piernas_final_cambio = 2219;

    nombres = fieldnames(categorias);

    for i = 1:numel(nombres)
        nombre = nombres{i};
        valores = categorias.(nombre);

        res.(['l_' nombre]) = find(ismember(gt.phsId, valores) & mask);
    end
end
