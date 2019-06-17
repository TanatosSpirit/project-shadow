import can
import canmatrix.formats
import os
import os.path


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

    logData = []
    for i in range(len(log)):

        msg = log[i]
        absTime = msg.timestamp
        msgFrame = matrix.frameById(msg.arbitration_id)

        if msgFrame:  # If msg in CAN-matrix
            if msgFrame.name == 'ObjectListState':

                objListCount += 1
                objCount = -1
                instaObjList = {'Time Stamp': absTime}

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

                    logData[objListCount]['Obj_List'].append(obj)

            elif msgFrame.name == 'PATH1':
                pass

    print('Loaded')
               
    return logData
