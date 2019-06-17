from lib.reader import read_can_log
from lib.shadow import shadow

import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.cm as cm

class Visualizer:
    def __init__(self, settings):
        self.settings = settings

    def get_data(self):
        path = self.settings['log']
        dbc = self.settings['dbc']

        return read_can_log(path, dbc)

    def show(self):
        data = self.get_data()
        colorRCSmin = self.settings['colorRCSmin']
        colorRCSmax = self.settings['colorRCSmax']

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.minorticks_on()
        ax.grid(which='major', linestyle='-')
        ax.grid(which='minor', linestyle=':')

        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 100)

        spdAnnot = fig.text(0.15, 0.97, '')
        cmap = cm.rainbow

        norm = colors.Normalize(vmin=colorRCSmin, vmax=colorRCSmax)

        MAX_OBJ = 100
        idAnnot = []

        for i in range(MAX_OBJ):
            idAnnot.append(ax.annotate(0, xy=(0, 0), horizontalalignment='center', verticalalignment='center', fontsize=8))

        objects = ax.scatter([0, 0], [0, 0], c=[colorRCSmin, colorRCSmax], marker='s', cmap=cmap)

        fig.subplots_adjust(right=0.85)
        cbar_ax = fig.add_axes([0.9, 0.1, 0.01, 0.8])
        fig.colorbar(objects, cax=cbar_ax)

        def animate(i):

            pose_obj, rcs_value, id_obj = shadow(data[i])


            # Настройка графиков
            objects.set_offsets(pose_obj)
            objects.set_facecolor(cmap(norm(rcs_value)))
            objects.set_sizes([20 ** 2] * len(pose_obj))

            spdAnnot.set_text('Speed = {:.2f} m/s'.format(0))

            for i in range(len(rcs_value)):
                idAnnot[i].set_text(id_obj[i])
                idAnnot[i].set_position((pose_obj[i][0], pose_obj[i][1]))

            for i in range(len(rcs_value), MAX_OBJ):
                idAnnot[i].set_text(0)
                idAnnot[i].set_position((0, 0))

        ani = animation.FuncAnimation(fig, animate, interval=10, frames=len(data))

        plt.show()



