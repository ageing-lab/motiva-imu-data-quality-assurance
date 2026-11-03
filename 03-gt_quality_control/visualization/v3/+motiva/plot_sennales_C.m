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
%   Plots the three accelerometer and three gyroscope channels of an
%   IMU with annotated exercise events and interactive data tips.

function plot_sennales_C(disp, disp_name, t_etiquetas)

    % Get temporal event-category names: t_*.
    campos = fieldnames(t_etiquetas);
    es_tiempo = startsWith(campos, 't_');
    nombres_t = campos(es_tiempo);

    % Compute sample indices for each category.
    indices = struct();
    for i = 1:numel(nombres_t)
        nombre = nombres_t{i};
        indices.(nombre) = motiva.get_indices_plot(disp.tsmillis, t_etiquetas.(nombre));
    end

    % Map known event categories to plot styles.
    estilos = struct();
    estilos.t_inicio_s = 'go';
    estilos.t_inicio_e = 'ro';
    estilos.t_final_r  = 'ko';
    estilos.t_nula_r   = 'mo';
    estilos.t_pausa    = 'co';

    % deprecated sytles
    %estilos.t_esc_inicio_b = 'yo';
    %estilos.t_brazos_inicio_sube = 'gs';
    %estilos.t_brazos_final_sube = 'gd';
    %estilos.t_brazos_inicio_baja = 'ks';
    %estilos.t_brazos_final_baja = 'kd';
    %estilos.t_piernas_inicio_inicio_s = 'gs';
    %estilos.t_piernas_final_inicio_s = 'gd';
    %estilos.t_piernas_inicio_cambio = 'ks';
    %estilos.t_piernas_final_cambio = 'kd';

    % Fallback plot styles for additional categories.
    estilos_reserva = {'gd','cd','gs','ks','kd','gs','gd','ks','kd'};

    figure()

    subplot(3, 2, 1)
    plot_canal(disp.tsmillis, disp.ax, 'ax', disp_name, t_etiquetas, nombres_t, indices, estilos, estilos_reserva)

    subplot(3, 2, 2)
    plot_canal(disp.tsmillis, disp.gx, 'gx', disp_name, t_etiquetas, nombres_t, indices, estilos, estilos_reserva)

    subplot(3, 2, 3)
    plot_canal(disp.tsmillis, disp.ay, 'ay', disp_name, t_etiquetas, nombres_t, indices, estilos, estilos_reserva)

    subplot(3, 2, 4)
    plot_canal(disp.tsmillis, disp.gy, 'gy', disp_name, t_etiquetas, nombres_t, indices, estilos, estilos_reserva)

    subplot(3, 2, 5)
    plot_canal(disp.tsmillis, disp.az, 'az', disp_name, t_etiquetas, nombres_t, indices, estilos, estilos_reserva)

    subplot(3, 2, 6)
    plot_canal(disp.tsmillis, disp.gz, 'gz', disp_name, t_etiquetas, nombres_t, indices, estilos, estilos_reserva)

    % Enable data cursor mode.
    dcm = datacursormode(gcf);
    datacursormode on;

    dcm.UpdateFcn = @(obj, event_obj) { ...
        ['X: ', num2str(event_obj.Position(1), '%.0f'), ...
         ', Y: ', num2str(event_obj.Position(2), '%.5f')]};
end


function plot_canal(ts, y, nombre_canal, disp_name, t_etiquetas, nombres_t, indices, estilos, estilos_reserva)

    hold off
    plot(ts, y, 'b')
    hold on

    % Plot all event categories.
    k_reserva = 1;
    for i = 1:numel(nombres_t)
        nombre = nombres_t{i};
        idx = indices.(nombre);

        if isempty(idx)
            continue
        end

        if isfield(estilos, nombre)
            estilo = estilos.(nombre);
        else
            estilo = estilos_reserva{min(k_reserva, numel(estilos_reserva))};
            k_reserva = k_reserva + 1;
        end

        plot(ts(idx), y(idx), estilo, 'DisplayName', nombre)
    end

    % Label event IDs at t_inicio_e when both fields are present.
    if isfield(t_etiquetas, 't_inicio_e') && isfield(t_etiquetas, 'evIds')
        idx_e = indices.t_inicio_e;

        if ~isempty(idx_e)
            str = cellstr(num2str(t_etiquetas.evIds));
            text(ts(idx_e), y(idx_e), str, 'FontWeight', 'bold', 'FontSize', 15);
        end
    end

    title([nombre_canal ' of ' disp_name])
    %legend('show')
    hold off

end
