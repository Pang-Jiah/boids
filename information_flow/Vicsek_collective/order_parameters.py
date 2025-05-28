import numpy as np
import sys


sys.path.insert(0, sys.path[0]+"\\..\\")
from h5py_process import *



def v_a(N, speed, theta):
    '''
    calculate the va

    parameter:
    N: number of agents
    v: speed
    Ve: velocity nx2xnumber of steps
    '''
    
    vel_x = speed*np.cos(theta, dtype=np.float64)
    vel_y = speed*np.sin(theta, dtype=np.float64)



    average_vel_x = np.sum(vel_x,axis=0)/(N*speed)
    average_vel_y = np.sum(vel_y,axis=0)/(N*speed)



    abs_va = np.hypot(average_vel_x, average_vel_y)
    v_aList = abs_va.reshape(1,-1)

 
    return v_aList




def A_a_pant(influence_A:np.ndarray,):
    '''
    calculate total flowing influence in a group at time 𝑡 
    
    Description:
    ---
    first assemble on the particles and take absolute value and average on paticles (and then average on time (This is left to another program))


    pant: 
    p for assemble on the 'p'articles 
    a for take absolute value
    n for average on paticles
    t for average on time
    '''
    

    A_p = influence_A
    A_pa = np.abs(A_p,dtype=np.float64)
    A_pan = np.average(A_pa, axis=0)

    return A_pan





def A_a_pant_step(influence:np.ndarray,):
    '''
    calculate total flowing influence in a group at time 𝑡 
    
    Description:
    ---
    first assemble on the particles and take absolute value and average on paticles (and then average on time (This is left to another program))
    step means i only calculate one step

    pant: 
    p for assemble on the 'p'articles 
    a for take absolute value
    n for average on paticles
    t for average on time



    '''

    A_p = np.sum(influence, axis=1, dtype=np.float64)
    A_pa = np.abs(A_p)
    A_pan_step = np.average(A_pa)

    return A_pan_step






def A_a_apnt_step(influence:np.ndarray,):
    '''
    
    
    Description:
    ---
    first assemble on the particles and take absolute value and average on paticles (and then average on time (This is left to another program))
    step means i only calculate one step

    pant: 
    p for assemble on the 'p'articles 
    a for take absolute value
    n for average on paticles
    t for average on time



    '''
    A_a = np.abs(influence, dtype=np.float64)
    A_ap = np.sum(A_a, axis=1)
    A_apn_step = np.average(A_ap)

    return A_apn_step




    
