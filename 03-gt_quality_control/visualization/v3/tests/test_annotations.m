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
%   Tests annotation parsing, event filtering, and exercise-series
%   boundary preparation against synthetic ground-truth data.

function tests = test_annotations
%TEST_ANNOTATIONS Check annotation parsing and series preparation.
tests = functiontests(localfunctions);
end

function testAnnotationPreparationMatchesExistingFunctions(testCase)
gt = sampleGroundTruth();
[actualTimes, actualSeries] = motiva.prepare_annotation_plot_data(gt);
markers = motiva.parse_gt(gt);
expectedSeries = motiva.delimitar_series(gt);
verifyEqual(testCase, actualSeries, expectedSeries);
fields = fieldnames(markers);
for i = 1:numel(fields)
    name = fields{i};
    if startsWith(name, 'l_')
        target = ['t_' char(extractAfter(name, 2))];
        verifyTrue(testCase, isfield(actualTimes, target));
        verifyEqual(testCase, actualTimes.(target), gt.ts(markers.(name)));
    end
end
verifyEqual(testCase, actualTimes.evIds, markers.evIds);
verifyEqual(testCase, actualSeries.outcome_real, [2; 1]);
verifyEqual(testCase, actualSeries.gt_inicio, [1000; 4000]);
verifyEqual(testCase, actualSeries.gt_final, [3000; 5000]);
end

function testInvalidEventsExcludedFromCategoryMarkers(testCase)
gt = sampleGroundTruth();
gt.valido(2) = false;
[times, ~] = motiva.prepare_annotation_plot_data(gt);
verifyEqual(testCase, times.t_final_r, [3000; 5000]);
end

function gt = sampleGroundTruth()
gt = table([10; 10; 10; 11; 11], [1; 2; 2; 1; 2], ...
    [1000; 2000; 3000; 4000; 5000], true(5, 1), ...
    'VariableNames', {'evId', 'phsId', 'ts', 'valido'});
end
