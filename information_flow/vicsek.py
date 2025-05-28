'''
Function for Vicsek model simulation

'''
import numpy as np

def modulo(x):
    '''contrain the angle of orientation within (-pi, pi]'''
    
#     x = x%(2*np.pi)
#     if x > np.pi:
#         x = x - 2*np.pi
    
    return x - 2 * np.pi * np.ceil((x - np.pi) / (2 * np.pi))



def alignment(number_of_particles:int, theta:np.ndarray, WxA:np.ndarray):
        '''
        Compute the alignment (influence).
        
        Parameters:
        ---
        number_of_particles: The number of the particles
        theta: the orientation of particels
        WxA: interaction matrix .* adjacent matrix
        
        Return:
        ---
        thetaASum: the combined influence one particle receieves from the surrounding neighbors
        theta_influnce: the influence one particle receieves from the surrounding neighbors

        '''
        n = number_of_particles

        #dtattheta \in [-2pi,2pi]
        detatheta = -theta.reshape((n,1))+theta.reshape((1,n)) # i, j is \theta j - theta i
        
        #dtattheta \in （-pi,pi]
        # detatheta = detatheta*((detatheta<=np.pi)*(detatheta>-np.pi)) + (((detatheta-2*np.pi)*(detatheta>np.pi))) + (((detatheta+2*np.pi)*(detatheta<=-np.pi)))#也可以用取余来操作
        detatheta = modulo(detatheta)
        thetaA = WxA*detatheta 
        total_weight = np.sum(WxA,axis=1).reshape((n,1))

        thetaA = np.divide(thetaA, total_weight, where = total_weight>0) #\inc\theta_ij
        thetaASum = np.sum(thetaA,axis=1) #\inc\theta_i
        
        #influence
        theta_influence = thetaA
        
        return thetaASum, theta_influence



def update(position:np.ndarray, theta:np.ndarray, velocity:np.ndarray, l:float, n:int, r:float, Wx:np.ndarray, eta:float, speed:float, time_resolution:float):
        '''
        Description
        ---
        
        Calculate the position and orientation of the particles at t+ \inc t  
        
        Parameters:
        ---
        position: the position of particles at t (N x 2)
        theta: the orientation of particles at t (N x 1)
        velocity: the velocity of particles at t (N x 2)
        l: the width of the cell 
        n: the number of partcles (N)
        r: sensing radius
        Wx: interaction matrix
        eta: noise strength
        speed: the speed of partcles
        time-resolution: can be roughly interpretated as \inc t


        '''

        dx = np.subtract.outer(position[:, 0], position[:, 0])
        dy = np.subtract.outer(position[:, 1], position[:, 1]) 


        ## periodic boundary 
        # we have several way to achieve the periodic boundary condition
        # method 1
        # as we will use dx and dy to calculate the distance, therefore the sign of dx and dy does not matter.
        # dx = (abs(dx)>(l/2))*(l-abs(dx))+(abs(dx)<=(l/2))*abs(dx) 
        # dy = (abs(dy)>(l/2))*(l-abs(dy))+(abs(dy)<=(l/2))*abs(dy)
        
        #This is really time consumming on allocating space, therefore we decompose the calculation
        # in oder to accelerate the speed, we decompose this formulation into following small ones 
        # method 2
        # abs_dx = abs(dx)
        # dx10  = (abs_dx>(l/2))
        # dx11 = (l-abs_dx)
        # dx1 = np.where(dx10,dx11,0)
        # dx20 = np.logical_not(dx10)
        # dx2 = np.where(dx20,dx,0)
        # dx = dx1 + dx2

        # abs_dy = abs(dy)
        # dy10  = (abs_dy>(l/2))
        # dy11 = (l-abs_dy)
        # dy1 = np.where(dy10,dy11,0)

        # dy20 = np.logical_not(dy10)
        # dy2 = np.where(dy20,dy,0)

        # dy = dy1 + dy2


        # method 3
        # same logic
        dx = dx - l * np.sign(dx) * (np.abs(dx) > l/2)
        dy = dy - l * np.sign(dy) * (np.abs(dy) > l/2)

        distance = np.hypot(dx, dy)
        Ax = (distance >= 0) * (distance <= r) # adjacent matrix
        WxA = Ax * Wx # combine adjacent matrix and interaction matrix
        # noise
        rng = np.random.default_rng()
        noises = rng.random((n,1))*eta - eta/2 #[-eta/2, eta/2)

        # calculate
        dTheta, theta_influence  = alignment(number_of_particles=n, theta=theta,  WxA=WxA)#alignment                
        theta = theta + dTheta.reshape((n,1))
        
        # add noises
        theta = theta + noises

        # interval range of angle->(-pi,pi]
        theta = modulo(theta)

        # speed remains unchanged
        # velocity
        velocity = np.hstack((speed*np.cos(theta), speed*np.sin(theta))) 

        # position
        position  = position + velocity * time_resolution #
        position = np.mod(position, l)
        
        return position, theta, Ax, noises, dTheta, velocity, theta_influence