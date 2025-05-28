
"""
This is for running simulation files in parallel.
"""
import multiprocessing
import multiprocessing.pool
import subprocess
import os


def process_files():
    path_of_this_file = os.path.split(__file__)[0]
    os.chdir(path_of_this_file)
    
    pool = multiprocessing.pool.ThreadPool(7)  # Number of processors to be used
    
    
    filename = 'inf_quantities.py'
    path_here = os.path.abspath('.')
    script_file = os.path.join(path_here, filename)
    
    # enter the data path
    os.chdir("Data")


    path = os.path.abspath('.')
    for folder in os.listdir("."): # folder is the name of each folder
        if folder[-5:] ==".xlsx" or folder[-4:]==".txt" or folder[-5:]==".opju":
            continue
        folder_path = os.path.join(path, folder)
        cmd = ["python", script_file, str(folder_path)]
        pool.apply_async(subprocess.check_call, (cmd,))  # supply command to system
                           
    pool.close() 
    pool.join()


if __name__ == '__main__':
    process_files()



