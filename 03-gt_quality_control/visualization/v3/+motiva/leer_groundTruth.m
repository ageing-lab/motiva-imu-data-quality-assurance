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
%   Reads line-delimited JSON ground-truth annotations and converts
%   their records into a MATLAB table.

function tableData = leer_groundTruth(path, gt_fname)
    % Split the ground-truth file into individual lines.
    disp(['Reading ground-truth file: ' gt_fname]);
    txtContent = fileread(fullfile(path, gt_fname));
    lines = strsplit(txtContent, '\n');

    % Decode each JSON object (one per line) and
    % store the records in a structure array.
    structArray = [];

    for i = 1:numel(lines) - 1
        try
            current_line = jsondecode(lines{i});
            fields = fieldnames(current_line);
            for j = 1:length(fields)
                % Convert empty fields to NaN.
                if isempty(current_line.(fields{j}))
                    current_line.(fields{j}) = NaN;
                % Convert character strings to numeric values.
                elseif ischar(current_line.(fields{j}))
                    current_line.(fields{j}) = str2num(current_line.(fields{j}));
                end
            end
            structArray = [structArray, current_line];
        catch ME
            fprintf('\n[ERROR] Failed to decode JSON on line %d:\n%s\n', i, lines{i});
            fprintf('Error message: %s\n', ME.message);
            rethrow(ME); % Rethrow the error to stop execution.
        end

    end

    % Convert the structure array into a table.
    tableData = struct2table(structArray);
end
