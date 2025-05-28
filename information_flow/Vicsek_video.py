'''
Generate video for the Vicsek model

'''

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import os
import h5py
import progressbar

from h5py_process import H5PY_Processor



def drawing(now):
    '''
    draw these figuers
    '''

    global pbar
    
    
    n = number_of_particles
    l = size_of_arena
    r = sense_radius
    v = speed

    pbar.update(now+1)
    plt.cla()

    titleName = 'n=' + str(n) + \
                ', $w_{lf}$=' +str(wLF) +  \
                ', step=' + str(number_of_steps)  + \
                ', $\\eta$=' +str(format(eta/np.pi,'.1f')) +"$\\pi$"+  \
                ', L=' +str(l) +  \
                ', r=' +str(r) +  \
                ', v=' + str(v)
                
    
    plt.title(titleName)
    plt.xlim((0, l))
    plt.ylim((0, l))
    nowstr = str(now)
    plt.xlabel("$t_n = $"+nowstr, size = 15) # 

    
    
    # draw the quivers

    if number_of_influencers>0:
        plt.quiver(position[0:number_of_influencers,0,now],position[0:number_of_influencers,1,now],np.cos(theta[0:number_of_influencers,now]),np.sin(theta[0:number_of_influencers,now]),color = 'r',width = 0.005) # init positionsition
    
    if n > number_of_influencers:
    #     plt.quiver(position[indexOfLeader+2:,0],position[indexOfLeader+2:,1],Ve[indexOfLeader+2:,0],Ve[indexOfLeader+2:,1],width = 0.005)
        plt.quiver(position[number_of_influencers:,0,now], position[number_of_influencers:,1,now], np.cos(theta[number_of_influencers:,now]), np.sin(theta[number_of_influencers:,now]), width = 0.005)
    # plt.quiver(position[:,0],position[:,1], self.Ve[:,0], self.Ve[:,1])

    # 编号 serial number
    # for i in range(np.shape(position)[0]):
    #     plt.text(position[i,0,now]-0.1, position[i,1,now]+0.1, str(i), color="brown")
    
    # pass
    
    #绘制轨迹 draw the previous trajectory
    # trajL = 15 # trajectory length
    # scatterSize = np.ones((n,trajL))*0.5 # trajectory size
    # if now > trajL:
    #     plt.scatter(position[:,0,now-trajL:now], position[:,1,now-trajL:now], marker='.', s=scatterSize[:,:])#画轨迹点
    # else:
    #     plt.scatter(position[:,0,:now], position[:,1,:now], marker='.', s=scatterSize[:,:now])#画轨迹点
    # pass




if __name__=="__main__":
    # enter the absolute path of this python file
    path_of_this_file = os.path.split(__file__)[0]
    os.chdir(path_of_this_file)
    

    # enter the file where you store the data
    os.chdir("Video")



    noThroughList = []
    for folder in os.listdir("."): # folder is the name of each folder
        if folder in noThroughList or folder[-5:] ==".xlsx" or folder[-4:]==".txt" or folder[-5:]==".opju":
            continue
        print(f"START_{folder}")
        os.chdir(folder)
        #Read data
        f = H5PY_Processor("Data-Vicsek_collective.hdf5","r")
        # f = H5PY_Processor("Data-Vicsek_pairwise.hdf5","r")
        velocity            = f.f["velocity"][:,:,:] # The last dimension is "time"
        theta               = f.f["orientation"][:,:]
        interaction_matrix  = f.f["interaction_matrix"][:,:]
        position            = f.f["position"][:,:]

        groupParameter = f.f["parameters"]
        time_resolution         = groupParameter["time_resolution"][:][0]
        number_of_steps         = groupParameter["number_of_steps"][:][0]
        wLF                     = groupParameter["wLF"][:][:]
        number_of_influencers   = groupParameter["number_of_influencers"][:][0]
        eta                     = groupParameter["noise_strength"][:][0]
        number_of_particles     = groupParameter["number_of_particles"][:][0]
        size_of_arena           = groupParameter["size_of_arena"][:][0]
        sense_radius            = groupParameter["sensing_radius"][:][0]
        speed                   = groupParameter["speed"][:][0]
        f.close()


        # parameter initialize
        fps = 1 
        timeResolution = 1/fps

        start_point = 1000 # the time step you want to start
        stop_point = 1100 # the time step you end
        widgets = ['Progress: ',progressbar.Percentage(), ' ', progressbar.Bar('@'),' ', progressbar.Timer(),
           ' ', progressbar.ETA(), ' ', progressbar.FileTransferSpeed()]
        pbar = progressbar.ProgressBar(widgets=widgets, max_value=stop_point).start()

        fig = plt.figure() #


        ani = animation.FuncAnimation(fig=fig, func=drawing, frames=stop_point, interval=int(1/fps*1000), blit=False, repeat=False) #
        ani.save('./Vicsek.mp4',fps=fps)
        pbar.finish()
        print(":) \"Video is saved successfully.\"")
        plt.close()#
        os.chdir("..")
    pass