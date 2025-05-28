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



def calculate_information_theoretic_quantities(distribution,):
    '''
    calculate all the information-theoretic quantities and influence quantities for pairwise interaction
    
    '''
    global informationList
    # influence quantities
    informationList["A_at"] = defined_influence_at(influence=influence, x= 0, z=1, adjacent_matrix=np.ones((number_of_particles, number_of_particles, number_of_steps)), start_point=start_point, stop_point=number_of_steps-1)
    informationList["A_ta"] = defined_influence_ta(influence=influence, x= 0, z=1, adjacent_matrix=np.ones((number_of_particles, number_of_particles, number_of_steps)), start_point=start_point, stop_point=number_of_steps-1)
    # information quantities
    mutual_information = multivariate_Mutual_Information(distribution=distribution, var1='XY', var2='Z')
    tdmi = time_Delayed_Mutual_Information(distribution=distribution,var1='X', var2='Z')
    te = transfer_Entropy(distribution=distribution,var1='X', var2='Z',cvar='Y')
    imi0, shared0,synergistic0 =intrinsic_Mutual_Information(distribution=distribution,var1='X',var2='Z',cvar='Y')
    imi1, shared1,synergistic1 = intrinsic_Mutual_Information(distribution=distribution,var1='Y',var2='Z',cvar='X')

    informationList["total_mutul_information"] = mutual_information
    informationList["TDMI"] = tdmi
    informationList["TE"] = te
    informationList["IMI_unique0"] ,informationList["IMI_redundance0"] ,informationList["IMI_synergy0"] = imi0, shared0, synergistic0
    informationList["IMI_unique1"] ,informationList["IMI_redundance1"] ,informationList["IMI_synergy1"] = imi1, shared1,synergistic1
    
    # n_mutual means normalized by total joint mutual infomration which is I(X,Y;Z)
    informationList["nTDMI"]= tdmi/mutual_information
    informationList["nTE"]= te/mutual_information
    informationList["nIMI_unique0"],informationList["nIMI_redundance0"],informationList["nIMI_synergy0"] = imi0/mutual_information, shared0/mutual_information, synergistic0/mutual_information
    informationList["nIMI_unique1"],informationList["nIMI_redundance1"],informationList["nIMI_synergy1"] = imi1/mutual_information, shared1/mutual_information, synergistic1/mutual_information
    
    # AMI
    distribution.set_rv_names((0,1,2))
    Imin0,Imin1,redundant,synergy = I_Min(distribution=distribution)
    informationList["I_min_unique0"] ,informationList["I_min_unique1"] ,informationList["I_min_redundance"] ,informationList["I_min_synergy"]  = Imin0,Imin1,redundant,synergy
    informationList["nI_min_unique0"] ,informationList["nI_min_unique1"] ,informationList["nI_min_redundance"] ,informationList["nI_min_synergy"]  = Imin0/mutual_information, Imin1/mutual_information, redundant/mutual_information, synergy/mutual_information



if __name__ == "__main__":
    # enter the absolute path of this python filep
    path_of_this_file = os.path.split(__file__)[0]
    os.chdir(path_of_this_file)


    # Parameters setting
    number_of_bins = 8
    start_point = 1000 # start from the 1000th steps. This is to make sure everything reach stationary state


    folder = sys.argv[1] # receieve the path
    print(folder,"start")
    os.chdir(folder)



    f = H5PY_Processor("Data-Vicsek_pairwise.hdf5","r")
    velocity            = f.f["velocity"][:,:,:] # The last dimension is "time"
    theta               = f.f["orientation"][:,:]
    interaction_matrix  = f.f["interaction_matrix"][:,:]
    position            = f.f["position"][:,:]
    influence           = f.f["influence"][:,:,:] 

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
    
    
    followerList = np.arange(number_of_influencers,number_of_particles)

    count = 0
    #  Calculation: unique0 is the information influencer (leader, x) gives to follower,y
    # Imin is the AMI

    informationList = {
        "A_at":16,
        "A_ta":16, 

        "total_mutul_information":16,
        "TDMI": 16,
        "TE":16,

        "IMI_unique0":16, # the strategy of imi is not consistant
        "IMI_redundance0":16,
        "IMI_synergy0":16,

        "IMI_unique1":16, # the strategy of imi is not consistant
        "IMI_redundance1":16,
        "IMI_synergy1":16,
    
        "I_min_unique0":16,
        "I_min_unique1":16,
        "I_min_redundance":16,
        "I_min_synergy":16,
        
        "surd_unique0":16,
        "surd_unique1":16,
        "surd_redundance":16,
        "surd_synergy":16,
        "surd_information_leak":16,

        # normalized by mutual information
        "nTDMI": 16,
        "nTE":16,
        
        "nIMI_unique0":16, # the strategy of imi is not consistant
        "nIMI_redundance0":16,
        "nIMI_synergy0":16,

        "nIMI_unique1":16, # the strategy of imi is not consistant
        "nIMI_redundance1":16,
        "nIMI_synergy1":16,
    
        "nI_min_unique0":16,
        "nI_min_unique1":16,
        "nI_min_redundance":16,
        "nI_min_synergy":16,

        "nsurd_unique0":16,
        "nsurd_unique1":16,
        "nsurd_redundance":16,
        "nsurd_synergy":16,

        }      
     
    time_startall = time.time()  # Record the start poit
    
    
    # obatin the distribution
    ## obtain time series
    dt = 1
    xt = theta[0,start_point:-dt] # 0 is the leader 
    yt = theta[1,start_point:-dt] # 1 is the follower
    yt_tau = theta[1,start_point+dt:]
    
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
    informationList["surd_redundance"] = red
    informationList["surd_unique0"] = unq0
    informationList["surd_unique1"]= unq1
    informationList["surd_synergy"] = syn
    informationList["surd_information_leak"] = lea

    informationList["nsurd_redundance"] = nred
    informationList["nsurd_unique0"] = nunq0
    informationList["nsurd_unique1"] = nunq1
    informationList["nsurd_synergy"] = nsyn

    # calculate information (dit)
    ## obtain the distribution
    V_dit = np.vstack([  [ s[j][:] for j in range(len(s)) ] , a[:]]).T
    h_dit, _ = np.histogramdd( V_dit, bins=bins )
    hist_dit = h_dit/h_dit.sum()

    distribution = dit.Distribution.from_ndarray(hist_dit) 
    # print(f"distribution is {distribution}")
    distribution.set_rv_names('XYZ')

    calculate_information_theoretic_quantities(distribution=distribution)


    time_endall = time.time()  # record the stop instance
    time_sumall = time_endall - time_startall  # in the unit of second
    print("the time consumption for running one group:",time_sumall)


    # Store the data
    file = h5py.File("Data-pairwise_inf-"+str(number_of_bins)+".hdf5", 'w')
    number_of_particles = np.array([number_of_particles])
    number_of_influencers = np.array([number_of_influencers])  
    wLF = np.array([wLF])
    eta = np.array([eta])
    file.create_dataset("number_of_particles",    data=number_of_particles,     compression='gzip',   compression_opts=9)
    file.create_dataset("number_of_influencers",  data=number_of_influencers,   compression='gzip',   compression_opts=9)
    file.create_dataset("wLF",                    data=wLF,                     compression='gzip',   compression_opts=9)
    file.create_dataset("eta",                    data=eta,                     compression='gzip',   compression_opts=9)
    
    for keys in informationList:
        file.create_dataset(keys, data=np.array([informationList[keys]]), compression='gzip', compression_opts=9)
    
    file.close()
    print(folder,"done")
