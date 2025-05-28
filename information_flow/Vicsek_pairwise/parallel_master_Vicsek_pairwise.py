
"""
This is for running simulation files in parallel.
"""
import multiprocessing
import multiprocessing.pool
import subprocess
# import sys
import os
import numpy as np
# import platform


def process_files():
    path_of_this_file = os.path.split(__file__)[0]
    os.chdir(path_of_this_file)


    pool = multiprocessing.pool.ThreadPool(8)  # Number of processors to be used

    # The pairwise interaction program
    filename = 'Vicsek_pairwise.py'
    # Enter the folder where the data is located
    os.chdir("data")



    # =========== pairwise interaction ===========
    number_of_particles = [2]  # num of particles argv[1]
    number_of_influencers =  [1] # number of influencer argv[2]

    eta = np.arange(0, 2.01, .2)  #eta, the noise strength argv[3] attention that actual eta is the value times pi
    size_of_arena = [5] #argv[4] #density is 4 # attention to the sensing radius
    number_of_steps=[int(2**17)]#[131072] #argv[5] #
    wFL = [1.0,1.1, 1.2, 1.3, 1.4, 1.5, 1.7, 1.9, 2.0,3.0,4.0,5.0,7.0,9.0,10.0,15,20,25,30,40,50,60,70,80,90,100] # argv[6] the interaction strength leader gives to the follower

    times = 1 # how many rounds to run the simuation 
    R = 5 # argv[7] the sensing radius

    for _ in range(times):
        for arg6 in wFL:
            for arg3 in eta:
                script_file = os.path.join(path_of_this_file, filename)
                cmd = ["python", script_file, str(number_of_particles[0]), str(number_of_influencers[0]), str(arg3), str(size_of_arena[0]), str(number_of_steps[0]), str(arg6), str(R)]
                pool.apply_async(subprocess.check_call, (cmd,))  # supply command to system
    pool.close()
    pool.join()




if __name__ == '__main__':
    process_files()