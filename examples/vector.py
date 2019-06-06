import numpy as np
import matplotlib.pyplot as plt
def plotv(M):
    rows,cols = M.T.shape
    print(rows,cols)

    #Get absolute maxes for axis ranges to center origin
    #This is optional
    maxes = 1.1*np.amax(abs(M), axis = 0)
    colors = ['b','r','k']
    fig = plt.figure()
    fig.suptitle('Vectors', fontsize=10, fontweight='bold')

    ax = fig.add_subplot(111)
    fig.subplots_adjust(top=0.85)
    ax.set_title('Vector operations')

    ax.set_xlabel('x')
    ax.set_ylabel('y')

    for i,l in enumerate(range(0,cols)):
        # print(i)
        plt.axes().arrow(0,0,M[i,0],M[i,1],head_width=0.2,head_length=0.1,zorder=3)

        ax.text(M[i,0],M[i,1], str(M[i]), style='italic',
            bbox={'facecolor':'red', 'alpha':0.5, 'pad':0.5})

    plt.plot(0,0,'ok') #<-- plot a black point at the origin
    # plt.axis('equal')  #<-- set the axes to the same scale
    plt.xlim([-maxes[0],maxes[0]]) #<-- set the x axis limits
    plt.ylim([-maxes[1],maxes[1]]) #<-- set the y axis limits

    plt.grid(b=True, which='major') #<-- plot grid lines
    plt.show()

r = np.random.randint(4,size=[2,2])
print(r[0,:])
print(r[1,:])
r12 = np.add(r[0,:],r[1,:])
print(r12)
plotv(np.vstack((r,r12)))