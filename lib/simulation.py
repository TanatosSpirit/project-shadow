from lib.shadow import shadow

def sim(data):
    time_body = []
    time_radar = []
    PATH1_Speed = []
    speedInfo = []
    speed_RRW = []
    for i in range(len(data)):
        # pose_obj, rcs_value, id_obj = shadow(data[i])
        if data[i]['Source'] == 'PATH1':
            time_body.append(data[i]['Time Stamp'])
            PATH1_Speed.append(data[i]['PATH1_Speed'])
        elif data[i]['Source'] == 'ANSCU_WS':
            time_radar.append(data[i]['Time Stamp'])
            speedInfo.append(data[i]['ANSCU_LRW'])
            speed_RRW.append(data[i]['ANSCU_RRW'])

    return time_body, PATH1_Speed, time_radar, speedInfo, speed_RRW