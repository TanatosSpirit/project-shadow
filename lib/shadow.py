import math
def shadow(data, vehicle_state):

    # vehicle_state = {
    #     'time': [0],
    #     'delta_time': [0],
    #     'delta_path': [0],
    #     'path': [0],
    #     'Global_position_X': [0],
    #     'Global_position_Y': [0]
    # }

    # if data['Source'] == 'PATH1':
    #     time_body.append(data[i]['Time Stamp'])
    #     PATH1_Speed.append(data[i]['PATH1_Speed'])

    wheel_offset = -8
    gain = -40.75

    if data['Source'] == 'WHEEL_1':

        GradM = (data['WH_1_Position'] + wheel_offset) / gain
        vehicle_state['GradM'] = GradM

    elif data['Source'] == 'ANSCU_WS':
        vehicle_state['time'].append(data['Time Stamp'])

        d_t = vehicle_state['time'][-1] - vehicle_state['time'][len(vehicle_state['time'])-2]

        vehicle_state['delta_time'].append(d_t)

        speed_LRW = data['ANSCU_LRW']
        speed_RRW = data['ANSCU_RRW']

        linear_speed = (speed_LRW + speed_RRW) / 2

        ds = linear_speed * d_t
        vehicle_state['delta_path'].append(ds)

        vehicle_state['path'].append(vehicle_state['path'][-1] + ds)

        d_course = ds * vehicle_state['GradM'] * math.pi / 180
        vehicle_state['delta_course'].append(d_course)


        d_x = ds * math.cos(vehicle_state['course'][-1] + (d_course / 2))
        d_y = ds * math.sin(vehicle_state['course'][-1] + (d_course / 2))

        vehicle_state['course'].append(vehicle_state['course'][-1] + d_course)

        vehicle_state['Global_position_X'].append(vehicle_state['Global_position_X'][-1] + d_x)
        vehicle_state['Global_position_Y'].append(vehicle_state['Global_position_Y'][-1] + d_y)


    # pose_obj = []
    # rcs_value = []
    # id_obj = []
    # time = []
    # gradM = []
    # # print(data)
    # if data['Source'] == 'Radar':
    #     for j in range(int(data['Obj_NofObjects'])):
    #         # Ось oX радара направлена вперед по продольной оси автомобиля
    #         # Ось oY радара направлена влево по поперечной оси автомобиля
    #         # Поэтому преобразуем данные с радара к виду, удобному для отображения
    #         x = -data['Obj_List'][j]['Obj_DistLat']
    #         y = data['Obj_List'][j]['Obj_DistLong']
    #
    #         # ЭПР объекта
    #         rcs = data['Obj_List'][j]['Obj_RCS']
    #
    #         # ID объекта
    #         id = data['Obj_List'][j]['Obj_ID']
    #
    #         # if id==4:
    #             # print(x,y)
    #         pose_obj.append([x, y])
    #         rcs_value.append(rcs)
    #         id_obj.append(id)

    # elif data['Source'] == 'Body':
    #     pass
    #     # time.append(data['Time Stamp'])
    #     # gradM.append(data['PATH1_GradM'])
