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
%   Converts ground-truth event annotations into timestamp markers and
%   exercise-series boundaries for signal visualization.

function [times, series_table] = prepare_annotation_plot_data(ground_truth)
%PREPARE_ANNOTATION_PLOT_DATA Prepare annotations for motion signal plots.
%   [TIMES, SERIES_TABLE] = PREPARE_ANNOTATION_PLOT_DATA(GROUND_TRUTH)
%   extracts event timestamps and series boundaries without drawing figures.

    markers = motiva.parse_gt(ground_truth);
    series_table = motiva.delimitar_series(ground_truth);

    times = struct();
    fields = fieldnames(markers);

    for i = 1:numel(fields)
        name = fields{i};
        if startsWith(name, 'l_')
            indices = markers.(name);
            base = extractAfter(name, 2);
            times.(['t_' base]) = ground_truth.ts(indices);
        end
    end

    times.evIds = markers.evIds;
end
