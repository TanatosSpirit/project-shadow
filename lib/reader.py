import can
import canmatrix.formats
import os
import os.path
import numpy as np


def read_can_log(path, dbc):
    log = []

    print('Data loading from log...')

    reader = can.LogReader(path)
    
    for m in reader:
        log.append(m)

    if not os.path.isfile(dbc[-1]):
        s = "canconvert.exe --merge="
        s += dbc[0]
        s += ' '
        s += dbc[1]
        s += ' '
        s += dbc[2]
        # for i in range(n):
        #     s += str(i)
        os.system(s)

    common_dbc = canmatrix.formats.loadp(dbc[-1])
    matrix = next(iter(common_dbc.values()))

    objListCount = -1
    objCount = -1

    lenLogData = -1
    logData = []
    for i in range(len(log)):
        msg = log[i]
        absTime = msg.timestamp
        msgFrame = matrix.frameById(msg.arbitration_id)

        if msgFrame:  # If msg in CAN-matrix
            if msgFrame.name == 'Obj_0_Status':

                lenLogData += 1
                objListPose = lenLogData
                objListCount += 1
                objCount = -1
                instaObjList = {'Time Stamp': absTime,
                                'Source'    : 'Radar'}

                msgDecoded = matrix.decode(msg.arbitration_id, msg.data, False)
                for signal, value in msgDecoded.items():
                    instaObjList[signal] = value

                instaObjList['Obj_List'] = []

                logData.append(instaObjList)

            elif msgFrame.name == 'Obj_1_General':
                if objListCount >= 0:  # Prevent bug if log starts from 'Obj_1_General' message
                    objCount += 1
                    obj = {}

                    msgDecoded = matrix.decode(msg.arbitration_id, msg.data, False)
                    for signal, value in msgDecoded.items():
                        if signal != 'Time Stamp':
                            obj[signal] = value

                    logData[objListPose]['Obj_List'].append(obj)

            elif (msgFrame.name == 'Obj_2_Quality' or
                  msgFrame.name == 'Obj_3_Extended' or
                  msgFrame.name == 'Obj_4_Warning'):

                if objCount >= 0:  # Prevent bug if log starts from messages above
                    msgDecoded = matrix.decode(msg.arbitration_id, msg.data, False)
                    # Search necessary Obj_ID
                    for obj in logData[objListPose]['Obj_List']:
                        if msgDecoded['Obj_ID'] == obj['Obj_ID']:
                            for signal, value in msgDecoded.items():
                                if signal != 'Time Stamp':
                                    obj[signal] = value

            # elif msgFrame.name == 'SpeedInformation':
            #     speed = 1
            #     if objCount >= 0: # Prevent bug if log starts from messages above
            #         msgDecoded = matrix.decode(msg.arbitration_id, msg.data, False)
            #         for signal, value in msgDecoded.items():
            #             if signal == 'RadarDevice_SpeedDirection':
            #                 if value == 0:
            #                     speed = 0
            #                 elif value == 2:
            #                     speed *= -1
            #             elif signal == 'RadarDevice_Speed':
            #                 speed *= value
            #
            #         logData[objListPose]['SpeedInformation'] = speed

            elif msgFrame.name == 'PATH1':

                lenLogData += 1

                instaObjList = {'Time Stamp': absTime,
                                'Source': 'PATH1'}


                # msgDecoded = matrix.decode(msg.arbitration_id, msg.data, False)

                PATH1_GradM = 0.01 * np.int32(((((msg.data[1] & 0xFF) << 8) | (msg.data[0] & 0xFF)) - 32800))
                PATH1_Yaw = 0.001 * np.int32((((msg.data[4] & 0x03) << 16) | ((msg.data[3] & 0xFF) << 8) | (msg.data[2] & 0xFF)) - 131000);
                PATH1_Speed = 0.01 * np.uint16(((msg.data[5] & 0xFF) << 6) | ((msg.data[4] >> 2) & 0x3F))

                instaObjList['PATH1_GradM'] = PATH1_GradM
                instaObjList['PATH1_Yaw'] = PATH1_Yaw
                instaObjList['PATH1_Speed'] = PATH1_Speed

                # for signal, value in msgDecoded.items():
                #     instaObjList[signal] = value

                logData.append(instaObjList)

            elif msgFrame.name == 'ANSCU_WS':

                lenLogData += 1

                instaObjList = {'Time Stamp': absTime,
                                'Source': 'ANSCU_WS'}

                ANSCU_LFW = 0.0009765625 * np.uint16(((msg.data[1] & 0xFF) << 8) | (msg.data[0] & 0xFF))
                ANSCU_RFW = 0.0009765625 * np.uint16(((msg.data[3] & 0xFF) << 8) | (msg.data[2] & 0xFF))
                ANSCU_LRW = 0.0009765625 * np.uint16(((msg.data[5] & 0xFF) << 8) | (msg.data[4] & 0xFF))
                ANSCU_RRW = 0.0009765625 * np.uint16(((msg.data[7] & 0xFF) << 8) | (msg.data[6] & 0xFF))

                instaObjList['ANSCU_LFW'] = ANSCU_LFW
                instaObjList['ANSCU_RFW'] = ANSCU_RFW
                instaObjList['ANSCU_LRW'] = ANSCU_LRW
                instaObjList['ANSCU_RRW'] = ANSCU_RRW

                logData.append(instaObjList)

    print('Loaded')
               
    return logData
