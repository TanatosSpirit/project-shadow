# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 15:06:38 2019

@author: lytov
"""
import matplotlib.pyplot as plt
import numpy as np

from calculation_of_target_state import *
from config_log import *
from matrix_operations import matrix


# Инициализация фильтра Калмана
is_initialized = False

x = matrix([[0.], [0.], [0.], [0.]])  # initial state (location x,y and velocity x,y)
P = matrix([[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1000., 0.], [0., 0., 0., 1000.]])   # initial uncertainty
F = matrix([[1., 0., 1, 0.], [0., 1., 0., 1], [0., 0., 1., 0.], [0., 0., 0., 1.]])  # next state function
H = matrix([[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]])  # measurement function
R = matrix([[0.0225, 0., 0., 0.], [0., 0.0225, 0., 0.], [0., 0., 0.0225, 0.], [0., 0., 0., 0.0225]])  # measurement uncertainty
I = matrix([[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]])  # identity matrix

def parse_data_log(path):
    log = []
    with open(path) as fp:
        fp.readline()
        line = fp.readline()
        while line:
            single_line = [float(x) for x in line.split()]
            log.append(single_line)
            line = fp.readline()

    return log

def main(data_log):
    data = np.array(parse_data_log(data_log))

    # Инициализация параметров
    phi = 0  # Угол курса автомобиля в системе координат земли.

    # Проекции положения автомобиля.
    vehicle_world_pose_x = 0
    vehicle_world_pose_y = 0

    target_global_velocity_ekf_x = 0
    target_global_velocity_ekf_y = 0

###############################################################################
    # листы для графиков
    x_time = []
    y_speed = []
    y_yaw_rate = []

    # графики зависимостей некоторых параметров от времени
    fig_graph, (ax1, ax2) = plt.subplots(2, 1, sharex='all', sharey='all',figsize=(8, 8))

    # настройка графиков
    x_lim = max(data[:, timestamp_col])

    # первый график
    y_min, y_max = min(data[:, vehicle_velocity_col]), max(data[:, vehicle_velocity_col])
    ax1.set_xlim(0, x_lim)
    ax1.set_ylim(y_min, y_max)
    ax1.set_title('Graph 1')
    ax1.set_ylabel('Linear vehicle_velocity (m/s)')
    data1, = ax1.plot([],[],color="blue")

    # второй график
    y_min, y_max = min(data[:, vehicle_yaw_rate_col]), max(data[:, vehicle_yaw_rate_col])
    ax2.set_xlim(0, x_lim)
    ax2.set_ylim(y_min, y_max)
    ax2.set_title('Graph 2')
    ax2.set_ylabel('vehicle_yaw_rate rate(d / s)')
    data2, = ax2.plot([], [], color="red")

    x_time.append(data[:, timestamp_col])

    y_speed.append(data[:, vehicle_velocity_col])
    data1.set_data(x_time, y_speed)

    y_yaw_rate.append(data[:, vehicle_yaw_rate_col])
    data2.set_data(x_time, y_yaw_rate)

    # График для положение автомобиля и объекта
    fig, ax = plt.subplots(figsize=(10, 10))

    ax.minorticks_on()
    ax.grid(which='major', linestyle='-')
    ax.grid(which='minor', linestyle=':')

    vehicle_pose, = ax.plot([], [], 'r.')
    target_pose, = ax.plot([], [], 'b.')
    target_pose_ekf, = ax.plot([], [], 'g.')

    # листы для графиков
    epsilon_graph= []
    epsilon_phi_graph = []
    epsilon_graph.append([0])
    epsilon_graph.append([0])
    epsilon_graph.append([0])
    epsilon_phi_graph.append([0])


###############################################################################

    vehicle_list_global_pose_x = []
    vehicle_list_global_pose_y = []

    target_list_global_pose_y = []
    target_list_global_pose_x = []

    target_list_global_pose_ekf_y = []
    target_list_global_pose_ekf_x = []

    for i in range(len(data)):
        if i > 2:
            dt = data[i, delta_time_col]  # s


            vehicle_velocity = data[i, vehicle_velocity_col]  # m/s


            vehicle_yaw_rate_0 = 0.85 * data[i-1, vehicle_yaw_rate_col]  # degree per second
            vehicle_yaw_rate_1 = 0.85 * data[i, vehicle_yaw_rate_col]  # degree per second

            target_radar_pose_x = data[i, target_x_col]
            target_radar_pose_y = data[i, target_y_col] - 0.5
            target_world_velocity = data[i, target_velocity_col]
            target_radar_course = data[i, target_course_col]
            target_radar_vx = data[i, target_vx_raw_col]
            target_radar_vy = data[i, target_vy_raw_col]

            # Расчет курса автомобиля в мировых координатах. Как уточнить поворот за время dt ?
            delta_phi_0_yaw = vehicle_yaw_rate_0 * dt * math.pi / 180
            delta_phi = vehicle_yaw_rate_1 * dt * math.pi / 180
            epsilon = (vehicle_yaw_rate_1 - vehicle_yaw_rate_0) / dt
            epsilon_graph.append([epsilon])
            delta_phi_0_eps = ((epsilon * dt * dt) / 2) * math.pi / 180
            epsilon_phi_graph.append([delta_phi_0_eps])
            phi = phi + delta_phi_0_yaw + delta_phi_0_eps

            cos_phi = math.cos(phi)
            sin_phi = math.sin(phi)

            # Отрисовка движения автомобиля в системе координат связанной с землей
            # Ноль ск в первом положении автомобиля в логе.
            vehicle_world_velocity_x = vehicle_velocity * cos_phi
            vehicle_world_velocity_y = vehicle_velocity * sin_phi

            vehicle_world_movement_x = vehicle_world_velocity_x * dt
            vehicle_world_movement_y = vehicle_world_velocity_y * dt

            # Положение автомобиля в глобальной системе координат
            vehicle_world_pose_x = vehicle_world_pose_x + vehicle_world_movement_x
            vehicle_world_pose_y = vehicle_world_pose_y + vehicle_world_movement_y

            # положение объекта в глобальной системе координат
            target_world_pose_x = vehicle_world_pose_x + (target_radar_pose_x * cos_phi - target_radar_pose_y * sin_phi)
            target_world_pose_y = vehicle_world_pose_y + (target_radar_pose_x * sin_phi + target_radar_pose_y * cos_phi)

            # Скорость объекта расчитана Астаховым и записана в лог
            target_world_velocity_x = target_world_velocity * math.cos(phi + target_radar_course)
            target_world_velocity_y = target_world_velocity * math.sin(phi + target_radar_course)

            # Пересчет относительной скорости объекта в скорость относительно земли
            vehicle_velocity_global_x = vehicle_velocity * cos_phi
            vehicle_velocity_global_y = vehicle_velocity * sin_phi

            target_velocity_abs, target_course_abs = 0.0, 0.0

            if data[i, target_handle_col] == -1:
                target_velocity_global_y, target_velocity_global_x = state_of_target(vehicle_velocity_global_y,
                                                                                     vehicle_velocity_global_x,
                                                                                     target_radar_vx,
                                                                                     target_radar_vy,
                                                                                     phi)

                target_velocity_abs, target_course_abs = state_of_target_instantaneous(data[i, target_x_col],
                                                                                       data[i, target_y_col] - 0.5,
                                                                                       target_radar_vy, target_radar_vx,
                                                                                       vehicle_yaw_rate_0, vehicle_velocity)

            target_abs_velocity_radar_x = target_velocity_abs * math.cos(target_course_abs + phi)
            target_abs_velocity_radar_y = target_velocity_abs * math.sin(target_course_abs + phi)

            # Отрисовка сырых векторов скоростей объекта
            target_velocity_radar_raw_x = target_radar_vx * math.cos(phi)
            target_velocity_radar_raw_y = target_radar_vy * math.sin(phi)


    ###############################################################################
            dt_2 = dt * dt
            dt_3 = dt_2 * dt
            dt_4 = dt_3 * dt
            noise_ax = 5
            noise_ay = 5
            if data[i, target_handle_col] != -1:
                # Реализация фильтра Калмана
                global is_initialized, x, F, P, H, R, I
                if not is_initialized:
                    x = matrix([[0.], [0.], [0.], [0.]])  # initial state (location x,y and velocity x,y)
                    P = matrix([[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1000., 0.], [0., 0., 0., 1000.]]) # initial uncertainty
                    x.value[0][0] = target_world_pose_x
                    x.value[1][0] = target_world_pose_y
                    is_initialized = True
                else:
                    # prediction
                    F.value[0][2] = dt
                    F.value[1][3] = dt

                    Q = matrix([[dt_4 / 4 * noise_ax, 0, dt_3 / 2 * noise_ax, 0],
                                [0, dt_4 / 4 * noise_ay, 0, dt_3 / 2 * noise_ay],
                                [dt_3 / 2 * noise_ax, 0, dt_2 * noise_ax, 0],
                                [0, dt_3 / 2 * noise_ay, 0, dt_2 * noise_ay]])

                    x = F * x
                    P = F * P * F.transpose() + Q

                    if data[i, target_handle_col] == 1:
                        # measurement update
                        Z = matrix([[target_world_pose_x], [target_world_pose_y], [target_world_velocity_x], [target_world_velocity_y]])
                        y = Z - (H * x)
                        S = H * P * H.transpose() + R
                        K = P * H.transpose() * S.inverse()

                        x = x + (K * y)
                        P = (I - (K * H)) * P

                    if len(target_list_global_pose_ekf_x) < 7000:
                        target_list_global_pose_ekf_x.append(x.value[0][0])
                        target_list_global_pose_ekf_y.append(x.value[1][0])
                        target_global_velocity_ekf_x = x.value[2][0]
                        target_global_velocity_ekf_y = x.value[3][0]
            else:
                is_initialized = False
    ###############################################################################



            if data[i,target_handle_col] == 1 and len(target_list_global_pose_x) < 7000:
                target_list_global_pose_x.append(target_world_pose_x)
                target_list_global_pose_y.append(target_world_pose_y)

            if i % 10 == 0:
                vehicle_list_global_pose_x.append(vehicle_world_pose_x)
                vehicle_list_global_pose_y.append(vehicle_world_pose_y)

            if data[i, target_handle_col] == -1 and i % 20 == 0:
                ax.arrow(vehicle_world_pose_x, vehicle_world_pose_y, vehicle_world_velocity_x, vehicle_world_velocity_y, head_width=0.5, head_length=1, alpha=0.6)

            if data[i, target_handle_col] == -1 and i % 20 == 0 and len(target_list_global_pose_ekf_x) < 700:
                ax.arrow(target_world_pose_x, target_world_pose_y, target_world_velocity_x, target_world_velocity_y, head_width=0.5,
                         head_length=1, alpha=0.6)

            if data[i, target_handle_col] == -1 and len(target_list_global_pose_ekf_x) < 700 and i % 20 == 0:
                ax.arrow(x.value[0][0], x.value[1][0], target_global_velocity_ekf_x, target_global_velocity_ekf_y, head_width=0.5,
                         head_length=1, alpha=0.6)

            # print("velocity_abs: ", target_velocity_abs,
            #         "; course_abs: ", target_course_abs,
            #         "; velocity_global: ", target_velocity_global,
            #         "; course_global: ", target_angel_global)

    vehicle_pose.set_data(vehicle_list_global_pose_x, vehicle_list_global_pose_y)
    # target_pose.set_data(target_list_global_pose_x, target_list_global_pose_y)
    target_pose_ekf.set_data(target_list_global_pose_ekf_x, target_list_global_pose_ekf_y)

    # Определение границ графика траектории
    x_min, x_max = min(vehicle_list_global_pose_x)-10, max(vehicle_list_global_pose_x)+10
    y_min, y_max = min(vehicle_list_global_pose_y)-10, max(vehicle_list_global_pose_y)+10
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    # fig_graph2, (ax3, ax4) = plt.subplots(2, 1, sharex='all', sharey='all', figsize=(8, 8))
    #
    # # настройка графиков
    # x_lim = max(data[:, timestamp_col])
    #
    # # первый график
    # y_min, y_max = min(data[:, vehicle_velocity_col]), max(data[:, vehicle_velocity_col])
    # ax3.set_xlim(0, x_lim)
    # ax3.set_ylim(y_min, y_max)
    # ax3.set_title('Graph 1')
    # ax3.set_ylabel('Linear vehicle_velocity (m/s)')
    # data3, = ax3.plot([], [], color="blue")
    #
    # # второй график
    # y_min, y_max = min(data[:, vehicle_yaw_rate_col]), max(data[:, vehicle_yaw_rate_col])
    # ax4.set_xlim(0, x_lim)
    # ax4.set_ylim(y_min, y_max)
    # ax4.set_title('Graph 2')
    # ax4.set_ylabel('vehicle_yaw_rate rate(d / s)')
    # data4, = ax4.plot([], [], color="red")
    #
    # # x_time.append(data[:, timestamp_col])
    #
    # data3.set_data(x_time, target_list_global_pose_ekf_x)
    #
    # data4.set_data(x_time, target_list_global_pose_ekf_y)

    ###########################
    ### debug углового ускорения

    # графики зависимостей некоторых параметров от времени
    fig_graph_1, (ax3, ax4) = plt.subplots(2, 1, sharex='all', sharey='all', figsize=(8, 8))


    # # первый график
    # epsilon_graph_np = np.array(epsilon_graph)
    # y_min, y_max = min(epsilon_graph_np), max(epsilon_graph_np)
    # ax3.set_xlim(0, x_lim)
    # ax3.set_ylim(-1, 1)
    # ax3.set_title('Graph 3')
    # ax3.set_ylabel('Linear vehicle_velocity (m/s)')
    # data3, = ax3.plot([], [], color="blue")

    # второй график
    epsilon_graph_np = np.array(epsilon_graph)
    y_min, y_max = min(epsilon_graph_np), max(epsilon_graph_np)
    ax4.set_xlim(0, x_lim)
    ax4.set_ylim(y_min, y_max)
    ax4.set_title('Graph 4')
    ax4.set_ylabel('Epsilon (d / s^2)')
    data4, = ax4.plot([], [], color="red")

    # data3.set_data(x_time, epsilon_graph)

    data4.set_data(x_time, epsilon_graph)


    ###########################


    plt.show()


if __name__ == '__main__':
    log_1 = r'D:\workspace\python\project-shadow\data\NB080-mshdow.log'
    log_2 = r'D:\workspace\python\project-shadow\data\NB080-chita3_m3__.log'
    log_3 = r'D:\workspace\python\project-shadow\data\chita3_rel_speed.log'
    main(log_3)
