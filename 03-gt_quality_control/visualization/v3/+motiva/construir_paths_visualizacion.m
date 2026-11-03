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
%   Builds and validates configurable paths to motion-capture recordings,
%   device files, and exercise annotations across repository and pending data.

function cfg = construir_paths_visualizacion(varargin)
    % Build and validate all data paths used by visualizar_sennales.
    %
    % Name-value options (existing names remain supported):
    %   'origen'       : 'repo', 'pendientes', or 'pending' (default 'repo')
    %   'version'      : 'v1' or 'v2' (default 'v2')
    %   'wave'         : 'wave-1' or 'wave-2' (default 'wave-1')
    %   'base_dir'     : common parent of repo/ and pending/ (optional)
    %   'root_pending' : parent containing pending/ or pendientes/ (optional)
    %   'root_repo'    : parent containing repo/ (optional)
    %
    % If no roots are supplied, search the script's parent directories for
    % repo/. Retain the legacy four-level fallback for compatibility.

    ip = inputParser;
    addParameter(ip, 'origen', 'repo', @(x) any(strcmp(string(x), ["repo", "pendientes", "pending"])));
    addParameter(ip, 'version', 'v2', @(x) any(strcmp(string(x), ["v1", "v2"])));
    addParameter(ip, 'wave', 'wave-1', @(x) any(strcmp(string(x), ["wave-1", "wave-2"])));
    addParameter(ip, 'base_dir', '', @(x) ischar(x) || isstring(x));
    addParameter(ip, 'root_pending', '', @(x) ischar(x) || isstring(x));
    addParameter(ip, 'root_repo', '', @(x) ischar(x) || isstring(x));
    parse(ip, varargin{:});

    cfg = ip.Results;
    cfg.origen = char(cfg.origen);
    cfg.version = char(cfg.version);
    cfg.wave = char(cfg.wave);
    cfg.base_dir = char(cfg.base_dir);
    cfg.root_pending = char(cfg.root_pending);
    cfg.root_repo = char(cfg.root_repo);

    if isempty(cfg.base_dir)
        script_dir = fileparts(fileparts(mfilename('fullpath'))); % Project root (parent of +motiva)
        candidate = script_dir;
        found = false;
        while true
            if isfolder(fullfile(candidate, 'repo'))
                cfg.base_dir = candidate;
                found = true;
                break;
            end
            parent = fileparts(candidate);
            if strcmp(parent, candidate)
                break;
            end
            candidate = parent;
        end
        if ~found
            cfg.base_dir = fullfile(script_dir, '..', '..', '..', '..');
        end
    end

    if isempty(cfg.root_repo)
        cfg.root_repo = cfg.base_dir;
    end
    if isempty(cfg.root_pending)
        cfg.root_pending = cfg.base_dir;
    end

    cfg.repo_dir = fullfile(cfg.root_repo, 'repo');
    if strcmp(cfg.origen, 'repo')
        cfg.origen_dir = cfg.repo_dir;
    else
        % Preserve the historical 'pendientes' layout while accepting the
        % newer 'pending' directory name. An explicit choice takes priority.
        cfg.origen_dir = fullfile(cfg.root_pending, cfg.origen);
    end
    cfg.app_dir = fullfile(cfg.origen_dir, 'app', cfg.version, cfg.wave);
    cfg.app_raw_dir = fullfile(cfg.origen_dir, 'app', 'raw', cfg.wave);
    cfg.dispositivos_dir = fullfile(cfg.repo_dir, 'devices', cfg.wave);

    assert(isfolder(cfg.app_dir), 'Application directory does not exist: %s', cfg.app_dir);
    assert(isfolder(cfg.dispositivos_dir), 'Device directory does not exist: %s', cfg.dispositivos_dir);
end
