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
%   Tests configurable data roots, directory validation, and
%   ground-truth annotation filename construction.

function tests = test_configuration
%TEST_CONFIGURATION Verify configurable roots, paths, and validation.
tests = functiontests(localfunctions);
end

function testSeparateRoots(testCase)
fixture = makeRoots();
cleanup = onCleanup(@() rmdir(fixture, 's'));
pendingRoot = fullfile(fixture, 'incoming');
repoRoot = fullfile(fixture, 'published');
mkdir(fullfile(pendingRoot, 'pending', 'app', 'v2', 'wave-2'));
mkdir(fullfile(repoRoot, 'repo', 'devices', 'wave-2'));

cfg = motiva.construir_paths_visualizacion('origen', 'pending', ...
    'version', 'v2', 'wave', 'wave-2', ...
    'root_pending', pendingRoot, 'root_repo', repoRoot);

verifyEqual(testCase, cfg.app_dir, fullfile(pendingRoot, 'pending', 'app', 'v2', 'wave-2'));
verifyEqual(testCase, cfg.dispositivos_dir, fullfile(repoRoot, 'repo', 'devices', 'wave-2'));
verifyEqual(testCase, cfg.app_raw_dir, fullfile(pendingRoot, 'pending', 'app', 'raw', 'wave-2'));
end

function testMissingDirectoriesAreRejected(testCase)
fixture = makeRoots();
cleanup = onCleanup(@() rmdir(fixture, 's'));
verifyError(testCase, @() motiva.construir_paths_visualizacion( ...
    'base_dir', fixture), 'MATLAB:assertion:failed');
end

function testGroundTruthFilenames(testCase)
cfg.app_dir = fullfile('root', 'repo', 'app', 'v2', 'wave-1');
cfg.app_raw_dir = fullfile('root', 'repo', 'app', 'raw', 'wave-1');
[name, directory] = motiva.get_gtfile_path(12, 20260102, 1030, 'A', true, '', cfg);
verifyEqual(testCase, string(name), "12_20260102_1030_A_ppr2.txt");
verifyEqual(testCase, directory, cfg.app_dir);
[name, directory] = motiva.get_gtfile_path(12, 20260102, 1030, 'A', false, '', cfg);
verifyEqual(testCase, string(name), "12_20260102_1030_A.txt");
verifyEqual(testCase, directory, cfg.app_raw_dir);
end

function folder = makeRoots()
folder = tempname;
mkdir(folder);
end
