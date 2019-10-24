from lib.reader import read_can_log
from lib.simulation import sim
from lib.shadow import shadow

import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.cm as cm

class Visualizer:
    def __init__(self, settings):
        self.settings = settings
        self.data = self.get_data()

    def get_data(self):
        path = self.settings['log']
        dbc = self.settings['dbc']

        return read_can_log(path, dbc)

    def show(self):

        # vehicle_state = {
        #     'time': [0],
        #     'delta_time': [0],
        #     'delta_path': [0],
        #     'delta_course': [0],
        #     'course': [0],
        #     'path': [0],
        #     'Global_position_X': [0],
        #     'Global_position_Y': [0],
        #     'GradM': 10
        # }
        vehicle_state = sim(self.data)

        fig_graph, ax1  = plt.subplots(1, 1, sharex='all', sharey='all', figsize=(9, 9))

        time = vehicle_state['time']
        Global_position_X = vehicle_state['Global_position_X']
        Global_position_Y = vehicle_state['Global_position_Y']

        # y_max = max(speed_RRW) if max(speed_RRW) > max(speed_LRW) else max(speed_LRW)
        y_min = min(Global_position_Y)
        y_max = max(Global_position_Y)

        x_min = min(Global_position_X)
        x_max = max(Global_position_X)

        ax1.set_xlim(x_min, x_max)
        ax1.set_ylim(y_min, y_max)
        ax1.set_title('Graph 1')
        ax1.set_ylabel('speed_LRW (ms)')
        ax1.plot(Global_position_X, Global_position_Y, color = 'blue')

        # y_min = min(delta_time)
        # y_max = max(delta_time)
        # ax2.set_xlim(0, time[-1])
        # ax2.set_ylim(y_min, y_max)
        # ax2.set_title('Graph 1')
        # ax2.set_ylabel('speed_RRW (ms)')
        # ax2.plot(time, delta_time, color='blue')


        if self.settings['Anim']:
            colorRCSmin = self.settings['colorRCSmin']
            colorRCSmax = self.settings['colorRCSmax']

            fig, ax = plt.subplots(figsize=(10, 10))
            ax.minorticks_on()
            ax.grid(which='major', linestyle='-')
            ax.grid(which='minor', linestyle=':')

            ax.set_xlim(-55, 55)
            ax.set_ylim(-10, 100)

            spdAnnot = fig.text(0.15, 0.97, '')
            timeAnnot = fig.text(0.70, 0.97, '')
            time_text = ax.text(0.70, 0.9, '', transform=ax.transAxes)
            spd_text = ax.text(0.70, 0.85, '', transform=ax.transAxes)
            cmap = cm.rainbow

            norm = colors.Normalize(vmin=colorRCSmin, vmax=colorRCSmax)

            MAX_OBJ = 100
            idAnnot = []

            for i in range(MAX_OBJ):
                idAnnot.append(ax.annotate(0, xy=(0, 0), horizontalalignment='center', verticalalignment='center', fontsize=8))
                idAnnot[i].set_animated(True)

            objects = ax.scatter([0, 0], [0, 0], c=[colorRCSmin, colorRCSmax], marker='s', cmap=cmap)


            fig.subplots_adjust(right=0.85)
            cbar_ax = fig.add_axes([0.9, 0.1, 0.01, 0.8])
            fig.colorbar(objects, cax=cbar_ax)

            def init():

                time_text.set_text('')
                spd_text.set_text('')

                for i in range(MAX_OBJ):
                    idAnnot[i].set_text('')
                    idAnnot[i].set_position(([], []))


                return (objects, time_text, spd_text) + tuple(idAnnot)

            data = self.data
            def animate(i):

                pose_obj, rcs_value, id_obj = shadow(data[i])


                # Настройка графиков
                objects.set_offsets(pose_obj)
                objects.set_facecolor(cmap(norm(rcs_value)))
                objects.set_sizes([20 ** 2] * len(pose_obj))

                # spdAnnot.set_text('Speed = {:.2f} m/s'.format(0))
                # timeAnnot.set_text('Time = {:.2f} s'.format(data[i]['Time Stamp']))
                time_text.set_text('Time = {:.2f} s'.format(self.data[i]['Time Stamp']))
                spd_text.set_text('Speed = {:.2f} m/s'.format(0))


                for i in range(len(rcs_value)):
                    idAnnot[i].set_text(id_obj[i])
                    idAnnot[i].set_position((pose_obj[i][0], pose_obj[i][1]))

                for i in range(len(rcs_value), MAX_OBJ):
                    idAnnot[i].set_text('')
                    idAnnot[i].set_position((0, 0))

                return (objects, time_text, spd_text) + tuple(idAnnot)

            ani = animation.FuncAnimation(fig, animate, init_func=init, interval=10, frames=len(self.data), blit=True)

            # ani.save('basic_animation.mp4', fps=30, extra_args=['-vcodec', 'libx264'])

        plt.show()



