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
%   Tests IMU CSV loading, timestamp construction, and five- and
%   nine-sensor mapping with synthetic recordings.

function tests = test_sensor_loading
%TEST_SENSOR_LOADING Verify IMU data, timestamps, and sensor mapping.
tests = functiontests(localfunctions);
end

function testSensorColumnsAndTimestamps(testCase)
folder = tempname;
mkdir(folder);
cleanup = onCleanup(@() rmdir(folder, 's'));
file = fullfile(folder, 'sample.csv');
writeSensor(file);
data = motiva.leer_sensor(file);
verifyEqual(testCase, data.Properties.VariableNames, ...
    {'seg_epoch', 'ms', 'ax', 'ay', 'az', 'gx', 'gy', 'gz', 'tsmillis'});
verifyEqual(testCase, data.tsmillis, [1700000000123; 1700000000456]);
verifyEqual(testCase, data.ax, [1; 2]);
verifyEqual(testCase, data.gz, [6; 7]);
end

function testFiveSensorModePreservesOutputPositions(testCase)
folder = tempname;
mkdir(folder);
cleanup = onCleanup(@() rmdir(folder, 's'));
cfg.dispositivos_dir = folder;
writeSensor(fullfile(folder, '12_20260102_1.csv'));
writeSensor(fullfile(folder, '12_20260102_8.csv'));
out = cell(1, 9);
[out{:}] = motiva.leer_mocap('12', '20260102', false, cfg, 'sencillo');
verifyTrue(testCase, istable(out{1}));
verifyTrue(testCase, istable(out{8}));
verifyEqual(testCase, out{1}.tsmillis, out{8}.tsmillis);
for index = [2 3 4 5 6 7 9]
    verifyEmpty(testCase, out{index});
end
wrapper = cell(1, 9);
[wrapper{:}] = motiva.leer_mocap_sencillo('12', '20260102', false, cfg);
for index = 1:9
    verifyEqual(testCase, wrapper{index}, out{index});
end
end

function testNineSensorModeReadsAdditionalSensors(testCase)
folder = tempname;
mkdir(folder);
cleanup = onCleanup(@() rmdir(folder, 's'));
cfg.dispositivos_dir = folder;
writeSensor(fullfile(folder, '12_20260102_2.csv'));
out = cell(1, 9);
[out{:}] = motiva.leer_mocap('12', '20260102', false, cfg, 'completo');
verifyTrue(testCase, istable(out{2}));
for index = [1 3 4 5 6 7 8 9]
    verifyEmpty(testCase, out{index});
end
end

function writeSensor(filename)
fid = fopen(filename, 'w');
assert(fid ~= -1, 'Could not create test sensor file');
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, 'seg_epoch,ms,ax,ay,az,gx,gy,gz\n');
fprintf(fid, '1700000000,123,1,2,3,4,5,6\n');
fprintf(fid, '1700000000,456,2,3,4,5,6,7\n');
end
