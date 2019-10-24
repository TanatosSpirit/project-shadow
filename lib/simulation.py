from lib.shadow import shadow

def sim(data):
    # time_body = []
    # time_radar = []
    # PATH1_Speed = []
    # speedInfo = []
    # speed_RRW = []
    vehicle_state = {
        'time': [0],
        'delta_time': [0],
        'delta_path': [0],
        'delta_course': [0],
        'course': [0],
        'path': [0],
        'Global_position_X' : [0],
        'Global_position_Y': [0],
        'GradM': 10
    }

    for i in range(len(data)):
        # pose_obj, rcs_value, id_obj = shadow(data[i])
        shadow(data[i], vehicle_state)
        # if data[i]['Source'] == 'PATH1':
        #     time_body.append(data[i]['Time Stamp'])
        #     PATH1_Speed.append(data[i]['PATH1_Speed'])

    # return time_body, PATH1_Speed, time_radar, speedInfo, speed_RRW
    return vehicle_state
