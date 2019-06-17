import can
import canmatrix.formats
import matplotlib.animation as animation

import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.cm as cm

import conf

def run():
    log = []

    reader = can.LogReader(conf.log['radar'])
    print('Log loading...')
    for m in reader:
        log.append(m)

    readed_dbc = canmatrix.formats.loadp(conf.db)
    matrix = next(iter(readed_dbc.values()))

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

    fig_graph, (ax1, ax2) = plt.subplots(2, 1, sharex='all', sharey='all',figsize=(8, 8))

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.minorticks_on()
    ax.grid(which='major', linestyle='-')
    ax.grid(which='minor', linestyle=':')

    spdAnnot = fig.text(0.15, 0.97, '')

    cmap = cm.rainbow
    norm = colors.Normalize(vmin=conf.colorRCSmin, vmax=conf.colorRCSmax)

    MAX_OBJ = 100

    idAnnot = []
    for i in range(MAX_OBJ):
        idAnnot.append(ax.annotate(0, xy=(0, 0), horizontalalignment='center', verticalalignment='center', fontsize=8))

    scat = ax.scatter([0, 0], [0, 0], c=[conf.colorRCSmin, conf.colorRCSmax], marker='s', cmap=cmap)

    fig.subplots_adjust(right=0.85)
    cbar_ax = fig.add_axes([0.9, 0.1, 0.01, 0.8])
    fig.colorbar(scat, cax=cbar_ax)

    vehicle_pose, = ax.plot([], [], 'r.', markersize=10)

    # object_list_x = []
    # object_list_y = []

    # frame = 50
    # for i in range(int(logData[frame]['a_Obj_NoOfObj'])):
    #     object_list_x.append(logData[frame]['Obj_List'][i]['b_Obj_DistLat'])
    #     object_list_y.append(logData[frame]['Obj_List'][i]['b_Obj_DistLong'])

    # vehicle_pose.set_data(object_list_x, object_list_y)

    # Определение границ графика
    # x_min, x_max = min(object_list_x)-10, max(object_list_x)+10
    # y_min, y_max = min(object_list_y)-10, max(object_list_y)+10
    # ax.set_xlim(x_min, x_max)
    # ax.set_ylim(y_min, y_max)

    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 100)

    def animate(i):

        object_list_x = []
        object_list_y = []

        offsets = []
        rcs_value = []


        for j in range(int(logData[i]['a_Obj_NoOfObj'])):
            # object_list_x.append(-logData[i]['Obj_List'][j]['b_Obj_DistLat'])
            # object_list_y.append(logData[i]['Obj_List'][j]['b_Obj_DistLong'])
            # object_list_x.append(logData[i]['Obj_List'][j]['b_Obj_DistLong'])
            # object_list_y.append(logData[i]['Obj_List'][j]['b_Obj_DistLat'])
            # offsets.append([-logData[i]['Obj_List'][j]['b_Obj_DistLat'], logData[i]['Obj_List'][j]['b_Obj_DistLong']])
            offsets.append([-logData[i]['Obj_List'][j]['b_Obj_DistLat'], logData[i]['Obj_List'][j]['b_Obj_DistLong']])
            rcs_value.append(logData[i]['Obj_List'][j]['b_Obj_RCS'])

            idAnnot[j].set_text(logData[i]['Obj_List'][j]['b_obj_ID'])
            idAnnot[j].set_position((-logData[i]['Obj_List'][j]['b_Obj_DistLat'], logData[i]['Obj_List'][j]['b_Obj_DistLong']))
            # idAnnot[j].set_position((logData[i]['Obj_List'][j]['b_Obj_DistLong'], logData[i]['Obj_List'][j]['b_Obj_DistLat']))

        for i in range(j+1, MAX_OBJ):
            idAnnot[i].set_text(0)
            idAnnot[i].set_position((0, 0))

        # vehicle_pose.set_data(object_list_x, object_list_y)
        scat.set_offsets(offsets)
        scat.set_facecolor(cmap(norm(rcs_value)))
        scat.set_sizes([20**2] * len(offsets))

        spdAnnot.set_text('Speed = {:.2f} m/s'.format(0))


        # return [vehicle_pose]


    ani = animation.FuncAnimation(fig,animate,interval=10,frames=len(logData))
    plt.show()

run()