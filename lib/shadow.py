def shadow(data):
    pose_obj = []
    rcs_value = []
    id_obj = []

    for j in range(int(data['a_Obj_NoOfObj'])):
        # Ось oX радара направлена вперед по продольной оси автомобиля
        # Ось oY радара направлена влево по поперечной оси автомобиля
        # Поэтому преобразуем данные с радара к виду, удобному для отображения
        x = -data['Obj_List'][j]['b_Obj_DistLat']
        y = data['Obj_List'][j]['b_Obj_DistLong']

        # ЭПР объекта
        rcs = data['Obj_List'][j]['b_Obj_RCS']

        # ID объекта
        id = data['Obj_List'][j]['b_obj_ID']

        pose_obj.append([x, y])
        rcs_value.append(rcs)
        id_obj.append(id)

    return pose_obj, rcs_value, id_obj