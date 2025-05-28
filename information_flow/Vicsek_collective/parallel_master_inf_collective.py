
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
    
    pool = multiprocessing.pool.ThreadPool(5)  # Number of processors to be used
    
    filename = 'information_quantities.py'
    path_here = os.path.abspath('.')
    script_file = os.path.join(path_here, filename)
    
    
    # enter the data path
    os.chdir("Data_40")

    path = os.path.abspath('.')

    # single parent folder
    for folder in os.listdir("."): # folder is the name of each folder
        if  folder[-5:] ==".xlsx" or folder[-4:]==".txt" or folder[-5:]==".opju":
            continue
        folder_path = os.path.join(path, folder)
        cmd = ["python", script_file, str(folder_path)]
        pool.apply_async(subprocess.check_call, (cmd,))  # supply command to system



    # two parent folders 

    # for root_folder in os.listdir("."): # folder is the name of each folder
    #     os.chdir(root_folder)
    #     root_folder_path = os.path.join(path, root_folder)
    #     for folder in os.listdir("."):
    #         if folder or folder[-5:] ==".xlsx" or folder[-4:]==".txt" or folder[-5:]==".opju":
    #             continue
    #         folder_path = os.path.join(root_folder_path, folder)
    #         cmd = ["python", script_file, str(folder_path)]
    #         pool.apply_async(subprocess.check_call, (cmd,))  # supply command to system
    #     os.chdir("..")
    
    
    
    
    pool.close() 
    pool.join()


if __name__ == '__main__':
    process_files()



