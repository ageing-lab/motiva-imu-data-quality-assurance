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
%   Plots right- and left-ankle gyroscope Z-axis signals with
%   exercise-event annotations and interactive data cursors.

function plot_gz_C(dispD, dispI, evIds, t_inicio_e, t_inicio_s, t_final_r, t_nula_r, t_pausa)
    i_inicio_e_D = motiva.get_indices_plot(dispD.tsmillis, t_inicio_e);
    i_inicio_s_D = motiva.get_indices_plot(dispD.tsmillis, t_inicio_s);
    i_final_r_D = motiva.get_indices_plot(dispD.tsmillis, t_final_r);
    i_nula_r_D = motiva.get_indices_plot(dispD.tsmillis, t_nula_r);
    i_pausa_D = motiva.get_indices_plot(dispD.tsmillis, t_pausa);

    i_inicio_e_I = motiva.get_indices_plot(dispI.tsmillis, t_inicio_e);
    i_inicio_s_I = motiva.get_indices_plot(dispI.tsmillis, t_inicio_s);
    i_final_r_I = motiva.get_indices_plot(dispI.tsmillis, t_final_r);
    i_nula_r_I = motiva.get_indices_plot(dispI.tsmillis, t_nula_r);
    i_pausa_I = motiva.get_indices_plot(dispI.tsmillis, t_pausa);

    figure()
    subplot(2, 1, 1)
    plot(dispD.tsmillis, dispD.gz, 'b', ...
        dispD.tsmillis(i_inicio_s_D), dispD.gz(i_inicio_s_D), 'go', ...
        dispD.tsmillis(i_inicio_e_D), dispD.gz(i_inicio_e_D), 'ro', ...
        dispD.tsmillis(i_final_r_D), dispD.gz(i_final_r_D), 'ko', ...
        dispD.tsmillis(i_nula_r_D), dispD.gz(i_nula_r_D), 'mo', ...
        dispD.tsmillis(i_pausa_D), dispD.gz(i_pausa_D), 'co');
    str = cellstr(num2str(evIds));
    text(dispD.tsmillis(i_inicio_e_D), dispD.gz(i_inicio_e_D), str, 'FontWeight', 'bold', 'FontSize', 15);
    title(['gz of right ankle']);

    subplot(2, 1, 2)
    plot(dispI.tsmillis, dispI.gz, 'b', ...
        dispI.tsmillis(i_inicio_s_I), dispI.gz(i_inicio_s_I), 'go', ...
        dispI.tsmillis(i_inicio_e_I), dispI.gz(i_inicio_e_I), 'ro', ...
        dispI.tsmillis(i_final_r_I), dispI.gz(i_final_r_I), 'ko', ...
        dispI.tsmillis(i_nula_r_I), dispI.gz(i_nula_r_I), 'mo', ...
        dispI.tsmillis(i_pausa_I), dispI.gz(i_pausa_I), 'co');
    str = cellstr(num2str(evIds));
    text(dispI.tsmillis(i_inicio_e_I), dispI.gz(i_inicio_e_I), str, 'FontWeight', 'bold', 'FontSize', 15);
    title(['gz of left ankle']);

    % Enable data cursor mode.
    dcm = datacursormode(gcf);
    datacursormode on; % Enable data-point selection.

    % Customize data-tip display.
    dcm.UpdateFcn = @(obj, event_obj) {['X: ', num2str(event_obj.Position(1), '%.0f'), ...
                                    ', Y: ', num2str(event_obj.Position(2), '%.5f')]};
end
