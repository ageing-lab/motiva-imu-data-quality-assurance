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
%   Identifies exercise-series boundaries and counts repetitions from
%   valid ground-truth event annotations.

function tabla_series = delimitar_series(gt_table)
    tabla_validos = gt_table((gt_table.valido == true) & ((gt_table.phsId == 1) | (gt_table.phsId == 2)), :);
    tabla_series = tabla_validos(tabla_validos.phsId == 1, {'evId', 'ts'});
    nombresColumnas = {'evId', 'gt_inicio'};
    tabla_series.Properties.VariableNames = nombresColumnas;

    gt_final = [];
    outcome_real = [];
    reps = 0;
    for i=2:length(tabla_validos.phsId)
        if(tabla_validos.phsId(i) == 1)
            gt_final = [gt_final; tabla_validos.ts(i-1)];
	    outcome_real = [outcome_real; reps];
	    reps = 0;
        else
            reps = reps + 1;
        end
    end
    reps = reps + 1;

    gt_final = [gt_final; tabla_validos.ts(length(tabla_validos.phsId))];
    outcome_real = [outcome_real; reps];

    tabla_series.gt_final = gt_final;
    tabla_series.outcome_real = outcome_real;
end
