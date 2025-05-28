import h5py
import numpy as np
import os
import time
import sys 




sys.path.insert(0, sys.path[0]+"\\..\\")
from Vicsek import *
from SURD import surd
from SURD import mysurd
from information_processor import *
from h5py_process import H5PY_Processor

# import progressbar


def calculate_information_theoretic_quantities(distribution,collection_index):
    '''
    calculate the information-theoretic quantities using the package "dit"
    
    '''
    global informationList
    mutual_information = multivariate_Mutual_Information(distribution=distribution, var1='XY', var2='Z') # mutual information
    tdmi = time_Delayed_Mutual_Information(distribution=distribution,var1='X', var2='Z') #TDMI
    te = transfer_Entropy(distribution=distribution,var1='X', var2='Z',cvar='Y') #TE
    imi0, shared0,synergistic0 = intrinsic_Mutual_Information(distribution=distribution,var1='X',var2='Z',cvar='Y') #IMI
    imi1, shared1,synergistic1 = intrinsic_Mutual_Information(distribution=distribution,var1='Y',var2='Z',cvar='X')

    informationList["total_mutul_information"][collection_index]= mutual_information
    informationList["TDMI"][collection_index]= tdmi
    informationList["TE"][collection_index]= te
    informationList["IMI_unique0"][collection_index],informationList["IMI_redundance0"][collection_index],informationList["IMI_synergy0"][collection_index] = imi0, shared0, synergistic0
    informationList["IMI_unique1"][collection_index],informationList["IMI_redundance1"][collection_index],informationList["IMI_synergy1"][collection_index] = imi1, shared1, synergistic1
    
    #  normlized by the total mutual information
    informationList["nTDMI"][collection_index]= tdmi/mutual_information
    informationList["nTE"][collection_index]= te/mutual_information
    informationList["nIMI_unique0"][collection_index],informationList["nIMI_redundance0"][collection_index],informationList["nIMI_synergy0"][collection_index] = imi0/mutual_information, shared0/mutual_information, synergistic0/mutual_information
    informationList["nIMI_unique1"][collection_index],informationList["nIMI_redundance1"][collection_index],informationList["nIMI_synergy1"][collection_index] = imi1/mutual_information, shared1/mutual_information, synergistic1/mutual_information
    
    # AMI
    distribution.set_rv_names((0, 1, 2))
    Imin0,Imin1,redundant,synergy = I_Min(distribution=distribution)
    informationList["I_min_unique0"][collection_index],informationList["I_min_unique1"][collection_index],informationList["I_min_redundance"][collection_index],informationList["I_min_synergy"][collection_index] = Imin0,Imin1,redundant,synergy
    informationList["nI_min_unique0"][collection_index],informationList["nI_min_unique1"][collection_index],informationList["nI_min_redundance"][collection_index],informationList["nI_min_synergy"][collection_index] = Imin0/mutual_information, Imin1/mutual_information, redundant/mutual_information, synergy/mutual_information



def obtain_time_series(target_index:int, position:np.ndarray, theta:np.ndarray, sensing_radius:float, start_point:int, end_point:int, size_of_arena:float):
    '''
    obtain the time series for 

    \mathsf{\left \{\theta_x(t), \theta_y(t), \theta_y(t+\tau) | for\ every\ x\ in\ the\ neighborhood\ of\ y \right \}}


    Parameters:
    ---
    target_index: the index of y particle
    position: position of particles
    sensing radius: the sensing radius
    theta: moving orientation


    Return:
    ---
    xt: time series of theta_x(t) 
    yt: time series of theta_y(t)
    yt_tau: time series of theta_y(t+\tau)
    '''
    l = size_of_arena

    # obtain the position of the target particle
    target_pos = position[target_index, :, :]  # (2 x T)

    # compute the difference between target particle and other particles (dimension: N x 2 x T）
    dpos = position[:, :, :] - target_pos[np.newaxis, :, :]

    # periodical condition

    # dpos = np.where(
    #     np.abs(dpos) > l/2,
    #     np.sign(dpos) * (np.abs(dpos)-l),
    #     dpos
    # )
    dpos = dpos - l * np.sign(dpos) * (np.abs(dpos) > l/2)
    # Compute the distance (dimension: N x T）
    distances = np.linalg.norm(dpos, axis=1)
    
    # Find the neighbour 
    neighbor_mask = (distances > 0) & (distances <= sensing_radius)
    
    # obtain the indexes of the neighbors 
    particle_indices, time_indices = np.where(neighbor_mask)

    # consider the time index 
    valid_time_mask = np.logical_and((start_point<=time_indices), (time_indices< end_point - 1))
    particle_indices = particle_indices[valid_time_mask]
    time_indices = time_indices[valid_time_mask]
    
    # obtain the data 
    xt = theta[particle_indices, time_indices]
    yt = theta[target_index, time_indices]
    yt_tau = theta[target_index, time_indices + 1]

    return xt, yt, yt_tau, len(xt)



if __name__ == "__main__":
    # enter the absolute path of this python filep
    path_of_this_file = os.path.split(__file__)[0]
    os.chdir(path_of_this_file)



    # Parameters setting
    number_of_bins = 8
    folder = sys.argv[1] # receieve the path
    print(f"START {folder}") 
    os.chdir(folder)

    start_point = 1000 # start from the 1000th steps. This is to make sure everything reach stationary state

    # read the data 
    f = H5PY_Processor("Data-Vicsek_collective.hdf5","r")


    theta               = f.f["orientation"][:,:]
    position            = f.f["position"][:,:]
    # f.search_Deep(path='/')

    groupParameter = f.f["parameters"]
    time_resolution         = groupParameter["time_resolution"][:][0]
    number_of_steps         = groupParameter["number_of_steps"][:][0]
    wLF                     = groupParameter["wLF"][:][:]
    number_of_influencers   = groupParameter["number_of_influencers"][:][0]
    eta                     = groupParameter["noise_strength"][:][0]
    number_of_particles     = groupParameter["number_of_particles"][:][0]
    size_of_arena           = groupParameter["size_of_arena"][:][0]
    sensing_radius            = groupParameter["sensing_radius"][:][0]
    speed                   = groupParameter["speed"][:][0]
    f.close()
    
    

    '''
    Theorectically speaking, there are as many particles as there are data to compute
    '''

    number_of_data_collection = number_of_particles
    if number_of_data_collection > 100:
        number_of_data_collection = 100

    collection_index = 0
    #  Calculation: unique0 is the information x gives to y
    # Imin is the AMI

    informationList = {
                    "total_mutul_information":np.ones(number_of_data_collection, dtype=np.float16)*16,
                    "TDMI": np.ones(number_of_data_collection, dtype=np.float16)*16,
                    "TE":np.ones(number_of_data_collection, dtype=np.float16)*16,

                    
                    "IMI_unique0":np.ones(number_of_data_collection, dtype=np.float16)*16, # the strategy of imi is not consistant
                    "IMI_redundance0":np.ones(number_of_data_collection, dtype=np.float16)*16,
                    "IMI_synergy0":np.ones(number_of_data_collection, dtype=np.float16)*16,

                    "IMI_unique1":np.ones(number_of_data_collection, dtype=np.float16)*16, # the strategy of imi is not consistant
                    "IMI_redundance1":np.ones(number_of_data_collection, dtype=np.float16)*16,
                    "IMI_synergy1":np.ones(number_of_data_collection, dtype=np.float16)*16,
                
                
                    "I_min_unique0":np.ones(number_of_data_collection, dtype=np.float16)*16,
                    "I_min_unique1":np.ones(number_of_data_collection, dtype=np.float16)*16,
                    "I_min_redundance":np.ones(number_of_data_collection, dtype=np.float16)*16,
                    "I_min_synergy":np.ones(number_of_data_collection, dtype=np.float16)*16,
                    
                    "surd_unique0":np.ones(number_of_data_collection, dtype=np.float16)*16,
                    "surd_unique1":np.ones(number_of_data_collection, dtype=np.float16)*16,
                    "surd_redundance":np.ones(number_of_data_collection, dtype=np.float16)*16,
                    "surd_synergy":np.ones(number_of_data_collection, dtype=np.float16)*16,
                    "surd_information_leak":np.ones(number_of_data_collection, dtype=np.float16)*16,

                    # normalized by mutual information
                    "nTDMI": np.ones(number_of_data_collection, dtype=np.float16)*16,
                    "nTE":np.ones(number_of_data_collection, dtype=np.float16)*16,
                    
                    "nIMI_unique0":np.ones(number_of_data_collection, dtype=np.float16)*16, # the strategy of imi is not consistant
                    "nIMI_redundance0":np.ones(number_of_data_collection, dtype=np.float16)*16,
                    "nIMI_synergy0":np.ones(number_of_data_collection, dtype=np.float16)*16,

                    "nIMI_unique1":np.ones(number_of_data_collection, dtype=np.float16)*16, # the strategy of imi is not consistant
                    "nIMI_redundance1":np.ones(number_of_data_collection, dtype=np.float16)*16,
                    "nIMI_synergy1":np.ones(number_of_data_collection, dtype=np.float16)*16,
                
                    "nI_min_unique0":np.ones(number_of_data_collection, dtype=np.float16)*16,
                    "nI_min_unique1":np.ones(number_of_data_collection, dtype=np.float16)*16,
                    "nI_min_redundance":np.ones(number_of_data_collection, dtype=np.float16)*16,
                    "nI_min_synergy":np.ones(number_of_data_collection, dtype=np.float16)*16,

                    "nsurd_unique0":np.ones(number_of_data_collection, dtype=np.float16)*16,
                    "nsurd_unique1":np.ones(number_of_data_collection, dtype=np.float16)*16,
                    "nsurd_redundance":np.ones(number_of_data_collection, dtype=np.float16)*16,
                    "nsurd_synergy":np.ones(number_of_data_collection, dtype=np.float16)*16,
   
                    "number_of_samples":np.ones(number_of_data_collection,)*16,
                }
            
    time_startall = time.time()  # start time. record the time assumption of calculation 
    
    
    # tranverse all the particles to obtain distribution

    for i in range(number_of_data_collection):
        collection_index = i

        # obtain the time series 
        xt, yt, yt_tau, number_of_samples= obtain_time_series(target_index=i, position=position,theta=theta, sensing_radius=sensing_radius, start_point=start_point, end_point=number_of_steps, size_of_arena=size_of_arena)
        
        # count the number of samples
        informationList["number_of_samples"][collection_index] = number_of_samples


        # calculate information (surd)
        ## obatin distribution

        bins = [np.linspace(start=-np.pi,stop=np.pi,num=number_of_bins+1),np.linspace(start=-np.pi,stop=np.pi,num=number_of_bins+1),np.linspace(start=-np.pi,stop=np.pi,num=number_of_bins+1)]

        s = (xt, yt) #source 
        a = yt_tau # target
        V = np.vstack([ a[:], [ s[j][:] for j in range(len(s)) ] ]).T
        # binning method: equidistant method
        h, _ = np.histogramdd( V, bins=bins )
        hist = h/h.sum()

        # print("hist shape is ", np.shape(hist))

        Rd, Sy, MI, info_leak = surd.surd(hist)

        red, unq0, unq1, syn, lea = mysurd.obtain_DI_twoSources(Rd, Sy, MI, info_leak)
        nred, nunq0, nunq1, nsyn, _= mysurd.obtain_NDI_twoSources(Rd, Sy, MI, info_leak)
        mutual_information = MI[(1, 2)]


        # save data
        informationList["surd_redundance"][collection_index] = red
        informationList["surd_unique0"][collection_index] = unq0
        informationList["surd_unique1"][collection_index] = unq1
        informationList["surd_synergy"][collection_index] = syn
        informationList["surd_information_leak"][collection_index] = lea

        informationList["nsurd_redundance"][collection_index] = nred
        informationList["nsurd_unique0"][collection_index] = nunq0
        informationList["nsurd_unique1"][collection_index] = nunq1
        informationList["nsurd_synergy"][collection_index] = nsyn


        
        # calculate information (dit) 
        ## obtain the distribution
        V_dit = np.vstack([  [ s[j][:] for j in range(len(s)) ] , a[:]]).T
        h_dit, _ = np.histogramdd( V_dit, bins=bins )
        hist_dit = h_dit/h_dit.sum()

        distribution = dit.Distribution.from_ndarray(hist_dit) 
        distribution.set_rv_names('XYZ')

        calculate_information_theoretic_quantities(distribution=distribution, collection_index=collection_index)

        # pbar.update(i+1)

    
    time_endall = time.time()  # record the stop instance
    time_sumall = time_endall - time_startall  # in the unit of second
    print("the time consumption for running one group:",time_sumall)
    print(collection_index+1, " data have been collected.")
        

    # Store the data
    file = h5py.File("Data-collective_inf-"+str(number_of_bins)+".hdf5", 'w')

    number_of_particles = np.array([number_of_particles])
    number_of_influencers = np.array([number_of_influencers])  
    wLF = np.array([wLF])
    eta = np.array([eta])
    number_of_data_collection = np.array([number_of_data_collection])
    number_of_data_collection_r = np.array([collection_index+1]) 

    file.create_dataset("number_of_particles",    data=number_of_particles,     compression='gzip',   compression_opts=9)
    file.create_dataset("number_of_influencers",  data=number_of_influencers,   compression='gzip',   compression_opts=9)
    file.create_dataset("wLF",                    data=wLF,                     compression='gzip',   compression_opts=9)
    file.create_dataset("eta",                    data=eta,                     compression='gzip',   compression_opts=9)
    file.create_dataset("number_of_data_collection",        data=number_of_data_collection,         compression='gzip',   compression_opts=9)
    file.create_dataset("number_of_data_collection_r",        data=number_of_data_collection_r,         compression='gzip',   compression_opts=9)
    
    for keys in informationList:
        file.create_dataset(keys, data=informationList[keys], compression='gzip', compression_opts=9)

    file.close()
    print(folder,"done")
