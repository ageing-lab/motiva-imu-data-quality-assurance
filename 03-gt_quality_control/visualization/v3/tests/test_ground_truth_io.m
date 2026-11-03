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
%   Tests reading line-delimited JSON ground-truth annotations
%   from a temporary sample file.

function tests = test_ground_truth_io
%TEST_GROUND_TRUTH_IO Verify reading a minimal JSONL annotation fixture.
tests = functiontests(localfunctions);
end

function testReadJsonLines(testCase)
folder = tempname;
mkdir(folder);
cleanup = onCleanup(@() rmdir(folder, 's'));
filename = '12_20260102_1030_A_ppr2.txt';
fid = fopen(fullfile(folder, filename), 'w');
assert(fid ~= -1, 'Could not create JSONL fixture');
fprintf(fid, '{"evId":10,"phsId":1,"ts":1000,"valido":true}\n');
fprintf(fid, '{"evId":10,"phsId":2,"ts":2000,"valido":true}\n');
fclose(fid);
gt = motiva.leer_groundTruth(folder, filename);
verifyEqual(testCase, height(gt), 2);
verifyEqual(testCase, gt.evId, [10; 10]);
verifyEqual(testCase, gt.ts, [1000; 2000]);
end
