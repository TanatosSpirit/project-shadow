def shadow(data):
    pose_obj = []
    rcs_value = []
    id_obj = []
    time = []
    gradM = []
    # print(data)
    if data['Source'] == 'Radar':
        for j in range(int(data['Obj_NofObjects'])):
            # Ось oX радара направлена вперед по продольной оси автомобиля
            # Ось oY радара направлена влево по поперечной оси автомобиля
            # Поэтому преобразуем данные с радара к виду, удобному для отображения
            x = -data['Obj_List'][j]['Obj_DistLat']
            y = data['Obj_List'][j]['Obj_DistLong']

            # ЭПР объекта
            rcs = data['Obj_List'][j]['Obj_RCS']

            # ID объекта
            id = data['Obj_List'][j]['Obj_ID']

            # if id==4:
                # print(x,y)
            pose_obj.append([x, y])
            rcs_value.append(rcs)
            id_obj.append(id)

    # elif data['Source'] == 'Body':
    #     pass
    #     # time.append(data['Time Stamp'])
    #     # gradM.append(data['PATH1_GradM'])

    return pose_obj, rcs_value, id_obj