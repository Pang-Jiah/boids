
# Descropiption genenrate the data of Vicsek pairwise model
import numpy as np
import time
import os
import h5py
import progressbar
import sys


sys.path.insert(0, sys.path[0]+"\\..\\")
from Vicsek import *


if __name__=="__main__":
    path_of_this_file = os.path.split(__file__)[0]
    print(path_of_this_file)

    # Initialize parameters of Vicsek model:
    # Receive the parameters from cmd
    # print(sys.argv[:])
    number_of_particles = int(sys.argv[1])  # The number of particles
    number_of_influencers = int(sys.argv[2]) # The number of influencer
    eta = float(sys.argv[3])*np.pi # eta, the noise strength
    size_of_arena = float(sys.argv[4]) # The linear size of the squrae shape cell where simulations are carried out

    speed = 2 # Speed of the particles
    sensing_radius = float(sys.argv[7]) # The sensing radius that one particles can sense


    rng = np.random.default_rng() #
    # init Position 
    position = rng.random((number_of_particles, 2))*size_of_arena # random()-> float interval [0,1)
    # init orientation    (-pi, pi] 
    theta = modulo(rng.random((number_of_particles, 1))*2*np.pi) 
    # init Velocity  
    velocity = np.hstack((speed*np.cos(theta), speed*np.sin(theta)))
    
    # init interaction strength
    # leader is influencer
    Wx = np.ones((number_of_particles, number_of_particles))
    wLF = [float(sys.argv[6])] # for multiple leaders
    Wx[0:number_of_influencers,number_of_influencers:] = 0 # followers' effect on leader 
    Wx[0:number_of_influencers,0:number_of_influencers] = 0 #  leader on leader
    Wx[number_of_influencers:,number_of_influencers:] =0 # ; follower on follower
    followerIndex = np.arange(number_of_influencers,number_of_particles)
    
    for i in followerIndex: # follower on itself
        Wx[i,i]=1
    for i in range(number_of_influencers): # leader on itself
        Wx[number_of_influencers:,i] = wLF[i]  # leader's effect on followers # leader 之间没有相互影响
        Wx[i,i]=wLF[i] # leaders effect on itself

    # Initialize data and simulation
    number_of_steps = int(sys.argv[5]) # 2 power of 17
    fps = 20 
    time_resolution = 1/fps 


    ## Data initialization
    Data_theta = np.zeros((number_of_particles, number_of_steps), dtype=np.float16)
    Data_velocity = np.zeros((number_of_particles,2,number_of_steps), dtype=np.float16)
    Data_interaction_martix = np.zeros(((number_of_particles,number_of_particles)), dtype=np.float16)
    Data_position = np.zeros((number_of_particles,2,number_of_steps), dtype=np.float32)
    Data_pairwise_influence = np.zeros((number_of_particles,number_of_particles, number_of_steps),dtype=np.float16)
    Data_noises = np.zeros((number_of_particles,number_of_steps), dtype=np.float16)


    ## Intiallize progressbar
    bar_widgets = ['Progress: ',progressbar.Percentage(), ' ', progressbar.Bar('#'),' ', progressbar.Timer(),
           ' ', progressbar.ETA(), ' ', progressbar.FileTransferSpeed()]
    pbar = progressbar.ProgressBar(widgets=bar_widgets, max_value=number_of_steps).start()

    ## Intialize file
    ### Folder name
    time_now = time.localtime()
    timeStr = time.strftime("%Y-%m-%d_%H-%M-%S",time_now)
    folderName = timeStr + '_' + \
                str(number_of_particles) + 'particles_' + \
                str(number_of_influencers) + 'influencers_' + \
                str(wLF) + 'interaction_' + \
                str(number_of_steps) + 'steps_' + \
                str(format(eta/np.pi,'.3f')) + 'pi_noises_' + \
                str(sensing_radius) + 'radius_' + \
                str(size_of_arena) + 'size_' + \
                str(speed) + 'speed' 



    mypath = os.path.abspath(".")
    os.chdir(mypath)
    if not os.path.isdir(folderName):
        os.mkdir(folderName)
    os.chdir(folderName)
    ### File name 
    fileName = "Data-Vicsek_pairwise.hdf5"
    file = h5py.File(fileName, 'w-')


    Data_interaction_martix = Wx ## Store the data interaction matrix

    for i in range(number_of_steps):
        ## save the data
        # i represents the time step

        Data_theta[:,i]=theta.reshape((number_of_particles,))
        Data_velocity[:,:,i]=velocity.reshape((number_of_particles, 2,))
        Data_position[:,:,i]=position.reshape((number_of_particles, 2,))
        if i==0:
            Data_noises[:,i]=np.zeros(number_of_particles,) # The initial random state has no noise data
        else:
            Data_noises[:,i]=noises.reshape((number_of_particles,))

        # Ax is the adjacent matrix
        position, theta, Ax, noises, _, velocity, theta_influence= update(position=position,theta=theta, velocity=velocity,
                                      l=size_of_arena,n=number_of_particles,r=sensing_radius,Wx=Wx,eta=eta,
                                      speed=speed, time_resolution=time_resolution)
        
        Data_pairwise_influence[:,:,i] = theta_influence[:,:]
        pbar.update(i+1)



    # Save data
    file.create_dataset('orientation',          data=Data_theta,                compression='gzip', compression_opts=9)
    file.create_dataset('velocity',             data=Data_velocity,             compression='gzip', compression_opts=9)
    file.create_dataset('position',             data=Data_position,             compression='gzip', compression_opts=9)
    file.create_dataset('interaction_matrix',   data=Data_interaction_martix,   compression='gzip', compression_opts=9)
    file.create_dataset('influence',            data=Data_pairwise_influence,    compression='gzip', compression_opts=9)
    file.create_dataset('noises',               data=Data_noises,               compression='gzip', compression_opts=9)

    number_of_steps         = np.array([number_of_steps])
    time_resolution         = np.array([time_resolution])
    wLF                     = np.array([wLF])
    number_of_influencers   = np.array([number_of_influencers])
    noise_strength          = np.array([eta])
    number_of_particles     = np.array([number_of_particles])
    size_of_arena           = np.array([size_of_arena])
    sensing_radius            = np.array([sensing_radius])
    speed                   = np.array([speed])

    groupParameter = file.create_group("parameters")
    groupParameter.create_dataset('time_resolution',        data=time_resolution,       compression='gzip',   compression_opts=9)
    groupParameter.create_dataset('number_of_steps',        data=number_of_steps,       compression='gzip',   compression_opts=9)
    groupParameter.create_dataset('wLF',                    data=wLF,                   compression='gzip',   compression_opts=9)
    groupParameter.create_dataset('number_of_influencers',  data=number_of_influencers, compression='gzip',   compression_opts=9)
    groupParameter.create_dataset('noise_strength',         data=noise_strength,        compression='gzip',   compression_opts=9)
    groupParameter.create_dataset('number_of_particles',    data=number_of_particles,   compression='gzip',   compression_opts=9)
    groupParameter.create_dataset('size_of_arena',          data=size_of_arena,         compression='gzip',   compression_opts=9)
    groupParameter.create_dataset('sensing_radius',           data=sensing_radius,         compression='gzip',   compression_opts=9)
    groupParameter.create_dataset('speed',                  data=speed,         compression='gzip',   compression_opts=9)
    
    file.close()
    pbar.finish()
    print("Data collection accomplished")

    os.chdir("..") 