
"""
This is for running simulations in parallel.
"""
import multiprocessing
import multiprocessing.pool
import subprocess
import os
import numpy as np    


def process_files():
    path_of_this_file = os.path.split(__file__)[0]
    os.chdir(path_of_this_file) # Enter the path of this file

    pool = multiprocessing.pool.ThreadPool(8)  # Number of processors to be used
    
    # The collective program
    filename = 'vicsek_collective.py'
    
    # Enter the folder where the data is located
    os.chdir("Data_40")

    number_of_particles = [40]  # argv[1] The number of particles 
    number_of_influencers = [0] # argv[2] The number of influencer 
    
    eta = np.arange(0.00, 2.01, .05) # argv[3].  eta, the noise strength . Pay attention that eta is in the unit of pi radians here
    size_of_arena = [3.16]  # argv[4]  Size of the arena #[3.16]-40 #[5]-100 #[7.07]-200  #[10]-400 #[15.81]-1000 #[31.6]-4000 # density is 4
    number_of_steps=[int(2**17)] # argv[5]
    wFL = [1] # argv[6] the interaction strength
    R = 1 # argv[7]

    # Varying the eta
    for arg3 in eta:
        script_file = os.path.join(path_of_this_file, filename)
        cmd = ["python", script_file, str(number_of_particles[0]), str(number_of_influencers[0]), str(arg3), str(size_of_arena[0]), str(number_of_steps[0]), str(wFL[0]), str(R)]
        pool.apply_async(subprocess.check_call, (cmd,))  # supply command to system
    
    pool.close()
    pool.join()
    

if __name__ == '__main__':
    process_files()