# vicsek model simulation [1]
# Under developing
# authority: Pang Jiahuan
# start time: 2022/11/7
# last time: 2022/11/28
# end time: ~
# python: 3.6

'''
vicsek model version description:
    vicsek model is developed into the boids model

the improvement in contrast with last version:
    leader control ( Linear, Rotational, sin-like); periodical boundary improved 
    
'''
#consideration：
#   ·。python version: 3.8->3.6 (numpy 在python3.8 下的一些函数竟然在 python3.6中也好使？虽然代码上没有了相应的提示符 weird)
#   ·。fps and velocity
#   ·。第一帧数据没缺失，但是画面缺失-》frameNumber有两个0，且第一个0不显示画面
#   ·。为什么有些代码突然就不好使了呢 #仔细排查seperation 和 cohesion 和alignment
#   ·。nan问题 
#   ·。注意dx
#   ·。矩阵乘发法问题
#   ·。seperation needs to be reconsidered

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import time
import os
import h5py
import progressbar

class Vicsek():
    '''
    class of Vicsek model, each class is a group of Vicsek model

    Parameters
    --
    sizeOfArena: float ( default: )
        the linear size of the squrae shape cell where simulations are carried out. 
    number: int  ( default: )
        the number of units. 
    leaderNum: int  ( default: )
        the number of leader. 
    wLF: float  ( default: )
        the interaction that leaders exert on followers. 
    speed: float ( default: )
        speed of the units(constant temporarily).
    senseRadiu: float ( default: )
        the radius that an unit can feel.
    noises: float ( default: )
        the strength of noises
    name: str (default: vicsek)
        name of viscek model.

    >>> hello vicsek

    '''
    '''
    Notation
    --
        # l: the simulations are carried out in a square shape cell of linear size L 1x1 场地大小
        # n: n units 1x1 个数
        # v: value of the velocities of the units  1x1 速度大小
        # Theta: directions nx1 角度(每个unit运动的不同)
        # Ve: velocities of the units nx2
        # Po: matrix of the positions of the units n x 2 x stepNum 位置矩阵
        # r: the radius that an unit can feel 1x1 所感知的半径
        # yeta: the strength of the noises 1x1 噪声
        # Wx: the matrix of interaction strength nxn 
    大小写规范问题:小写为数值，大写开头为矩阵

    '''
    def __init__(self, sizeOfArena: float, number: int, leaderNum: int, wLF: float, speed: float, senseRadius: float,noises: float, name: str = "vicsek" ) -> None:
        self.name = name
        print(name,"is born")
        
        #####
        self.parameters_Init(sizeOfArena=sizeOfArena,number = number,leaderNum = leaderNum,wLF = wLF,speed = speed, senseRadius = senseRadius, noises = noises) #init parameters
        
        pass
    

    def parameters_Init(self, sizeOfArena: float, number:int, leaderNum: int, wLF: float, speed: float, senseRadius: float, noises: float) -> None:
        '''
        Init parameters

        Parameters
        --
        sizeOfArena: float ( default: )
           the linear size of the squrae shape cell where simulations are carried out. 
        number: int  ( default: )
            the number of units. 
        leaderNum: int  ( default: )
            the number of leader. 
        wLF: float  ( default: )
            the interaction that leaders exert on followers. 
        speed: float ( default: )
            speed of the units(constant temporarily).
        senseRadiu: float ( default: )
            the radius that an unit can feel.
        noises: float ( default: )
            the strength of noises.

        '''
        self.l = sizeOfArena
        self.n = number
        self.v = speed
        self.r = senseRadius
        self.yeta = noises
        # init Position P
        rng = np.random.default_rng()
        self.Po = rng.random((self.n,2))*self.l # random()-> float interval [0,1]
        # init angle   Theta        0~2*pi but what is 
        self.Theta = rng.random((self.n,1))*2*np.pi 
        # init Velocity  V    
        self.Ve = np.hstack((self.v*np.cos(self.Theta),self.v*np.sin(self.Theta)))
        # init interaction strength
        self.Wx = np.ones((self.n,self.n))
        self.leaderNum = leaderNum -1 # self.leaderNum is the max labels of leaders. 
                                      # If there is one leader,  self.leaderNum = 1-1=0, meaning that [0] is a leader.
                                      # If there are three, self.leaderNum = 3-1 = 2, meaning that [0][1][2] are leaders. 
        self.wLF =wLF
        self.Wx[:,0:self.leaderNum+1] = wLF # leader's effect on followers
        self.Wx[0:self.leaderNum+1,:] = 0 # followers' effect on leader
        self.Wx[0:self.leaderNum+1,0:self.leaderNum+1] = 0

        # force the first leader's initial position and velocity
        # temporarily for rotation
        self.leader_Init(leaderIndex = self.leaderNum)
        

        pass


#================== simulation part

    def start(self,stepNum) -> None:
        '''
        start the simulation
        
        Parameters:
        stepNum: int (default:)
            the number of steps.
        '''
        self.simulation_Init(stepNum) # init file and folder 

        fig = plt.figure() #


        ani = animation.FuncAnimation(fig=fig, func=self._move, frames=self.stepNum-1, interval=20, blit=False, repeat=False) # frams-1是因为frame会传两个参数0


        
        
        
        ani.save('./vicsek.gif',fps=20)
        
        self.pbar.finish()
        print(":) \"Video is saved successfully.\"",self.name,"said")
        self.data_Save()
        print(":) \"Data is saved successfully.\"",self.name,"said")
        # plt.show()
        plt.close()# 否则一次画太多的图了

    def _move(self, frameNumber):
        '''
        update the animation

        Parameters:
        ---
            frameNumber: 
                the number of the frame, 
        '''
        Po, Theta, Ax = self.update()
        leaderNum = self.leaderNum
        Ve = self.Ve
    
        colorBoard = ['b','c','m','y','r','g','k','olive','purple','turquoise','lightpink']
        n = self.n
        PoA = np.hstack(((Po[:,0]*Ax[:,0]).reshape(n,1), (Po[:,1]*Ax[:,0]).reshape(n,1)))
        # print(self.now)
        self.ThetaSaved[:,self.now] = Theta.reshape((self.n, ))
        self.pbar.update(self.now+1)
        self.now +=1
        plt.cla()

        titleName = 'n=' + str(self.n) + \
                    ', n_L=' + str(self.leaderNum+1) +\
                    ', w_lf=' +str(self.wLF) +  \
                    ', step=' + str(self.stepNum)  + \
                    ', noises=' +str(self.yeta) +  \
                    ', L=' +str(self.l) +  \
                    ', r=' +str(self.r) +  \
                    ', v=' + str(self.v)  
        plt.title(titleName)
        plt.xlim((0, self.l))
        plt.ylim((0, self.l))
        # 画与领导节点相邻的线
        for j in range(leaderNum+1):
            PoA = np.hstack(((Po[:,0]*Ax[:,j]).reshape(n,1), (Po[:,1]*Ax[:,j]).reshape(n,1)))
            for i in PoA:
                if i[0] !=0. and i[1] != 0.:
                    # plt.plot(np.array([PoA[0,0],i[0]]),np.array([PoA[0,1],i[1]]),color='blue')
                    plt.plot(np.array([PoA[j,0],i[0]]),np.array([PoA[j,1],i[1]]),color=colorBoard[j],linestyle='--',alpha = 0.5,linewidth=0.8)
        plt.quiver(Po[0:leaderNum+1,0],Po[0:leaderNum+1,1],Ve[0:leaderNum+1,0],Ve[0:leaderNum+1,1],color = 'r',width = 0.005) # init position
        plt.quiver(Po[leaderNum+1:,0],Po[leaderNum+1:,1],Ve[leaderNum+1:,0],Ve[leaderNum+1:,1],width = 0.005)
        # plt.quiver(Po[:,0],Po[:,1], self.Ve[:,0], self.Ve[:,1])
        pass


    def simulation_Init(self,stepNum):
        '''
        Init things which are used for simulation

        Parameters:
        --
        stepNum: int (default:)
            the number of steps.

        Section
        --
        >>> step (time) init
        >>> space init
        >>> progressbar init
        >>> file init: folder and hdf5 file 

        '''

        # step (time) init
        #------------
        # self.simulationTime = 10 # the duration of the simulation, unit: second
        # self.step = 0.1 # the duration of the step
        # self.stepNum = int(self.simulationTime/self.step)

        self.stepNum = stepNum
        self.now = 0 # record what the step is now, start from 0~(stepNum-1)
        

        # space init
        #----------------
        # space for data to be saved
        self.ThetaSaved = np.zeros((self.n, self.stepNum))


        # progressbar init
        #------------
        widgets = ['Progress: ',progressbar.Percentage(), ' ', progressbar.Bar('#'),' ', progressbar.Timer(),
           ' ', progressbar.ETA(), ' ', progressbar.FileTransferSpeed()]
        self.pbar = progressbar.ProgressBar(widgets=widgets, max_value=self.stepNum).start()
        # self.pbar = progressbar.ProgressBar().start()

        # file init
        #-----------
        # init folder
        now = time.localtime()
        timeStr = time.strftime("%Y-%m-%d_%H-%M-%S",now)
        self.folderName = timeStr + '_' + \
                    str(self.n) + 'units_' + \
                    str(self.leaderNum+1) + 'leaders_' + \
                    str(self.wLF) + 'interaction_' + \
                    str(self.stepNum) + 'stepNumber_' + \
                    str(self.yeta) + 'noises_' + \
                    str(self.l) + 'size_' + \
                    str(self.r) + 'radius_' + \
                    str(self.v) + 'speed'


        mypath = os.path.split(__file__)[0]
        os.chdir(mypath)
        if not os.path.isdir(self.folderName):
            os.mkdir(self.folderName)
        os.chdir(self.folderName) 


        # init file
        fileName = "vicsekData.hdf5"
        self.file = h5py.File(fileName, 'w-')


    def data_Save(self):
        '''
        save data
        '''
        stepNum = np.array([self.stepNum])
        self.file.create_dataset('angleSaved', data=self.ThetaSaved, compression='gzip', compression_opts=9)
        self.file.create_dataset('stepNum', data=stepNum, compression='gzip', compression_opts=9)
        self.file.close()
        os.chdir("..")
        pass





#=================== update data
    def alignment(self,WxA):
        '''
        Compute the alignment. Weighted average the velocity of adjacent units.
        
        Parameters:
        ---
        WxA: interaction matrix .* adjacent node matrix

        Return:
        ---
        The result direction of alignment, whose size is (n x 2) . Each row of the matrix, (x,y), is unitized. 
        '''
        Ve = self.Ve
        n = self.n
        # as |V| = 3, we can take Ve as the direction
        WAlignment = np.ones((n,2)) # aligment weight matrix
        VeA = np.matmul( WxA, WAlignment*Ve) # velocity

        # unitize
        VeASqrt = np.sqrt(((VeA*VeA).sum(axis=1)).reshape(n,1))
        VeA = np.divide(VeA,VeASqrt,where= VeASqrt!=0)
        return VeA

    def cohesion(self, WxA, dx, dy,di):
        '''
        Compute the cohension. Compute the direction which is towards the center of adjacent crowds.

        Parameters:
        ---
        WxA: interaction matrix .* adjacent node matrix

        Return:
        ---
        The result direction of cohesion, whose size is (n x 2) . Each row of the matrix, (x,y), is unitized. 
        '''
        n = self.n
        WCohesion = np.ones((n,n))
        dx = -dx # please pay attention to these direction
        dy = -dy

        dxC = ((WxA*WCohesion*dx).sum(axis = 1)/di).reshape(n,1)
        dyC = ((WxA*WCohesion*dy).sum(axis = 1)/di).reshape(n,1)

        VeC = np.hstack((dxC, dyC))
        # unitize
        VeCSqrt = np.sqrt(((VeC*VeC).sum(axis=1)).reshape(n,1))
        VeC = np.divide(VeC,VeCSqrt,where= VeCSqrt!=0)
        return VeC
        
    def seperation(self, WxA, dx, dy, distance):
        '''
        Compute the seperation. Compute the direction which is away from adjacent neighbours

        Parameters:
        ---
        WxA: 
            interaction matrix .* adjacent node matrix (n x n)
        dx:
            distance in x (n x n)
        dy:
            distance in y (n x n)
        distance: 
            distance between different units (n x n)


        Return:
        ---
        The result direction of seperation, whose size is(n x 2) . Each row of the matrix, (x,y), is unitized. 
        '''
        n = self.n
        WSeperation = np.divide(1, np.abs(distance)**3 , where= (np.abs(distance)**3)!=0) # seperation weight matrix (n x n)

        # dxS means dx Seperation
        dxS = ( WxA*WSeperation *dx).sum(axis = 1).reshape(n,1) # sum the weighted dx 
        dyS = ( WxA*WSeperation *dy).sum(axis = 1).reshape(n,1)
        # print("WSeperation:\n",WSeperation)

        VeS = np.hstack((dxS, dyS))
        # print(VeS)
        
        # # unitize
        VeSSqrt = np.sqrt(((VeS*VeS).sum(axis=1)).reshape(n,1))
        VeS = np.divide(VeS,VeSSqrt,where= VeSSqrt!=0)
        return VeS

    def update(self):
        '''
        # Main logic
        
        update the position.        
        
        Parameters:

        '''
        
        dx = np.subtract.outer(self.Po[:, 0], self.Po[:, 0])
        dy = np.subtract.outer(self.Po[:, 1], self.Po[:, 1]) 
        distance = np.hypot(dx, dy)
        # periodic boundary
        distanceTemp = np.zeros((self.n,self.n))
        distanceTemp += (dy > self.l/2) * (np.abs(dx)< self.l/2) * (np.hypot(0-dx,self.l-dy)<self.r)       *np.hypot(0-dx,self.l-dy)
        distanceTemp += (dy > self.l/2) * (dx< -self.l/2)        * (np.hypot(-self.l-dx,self.l-dy)<self.r) *np.hypot(-self.l-dx,self.l-dy)
        distanceTemp += (dy > self.l/2) * (dx> self.l/2)         * (np.hypot(self.l-dx,self.l-dy)<self.r)  *np.hypot(self.l-dx,self.l-dy)
        distanceTemp += (dy < self.l/2) * (dx> self.l/2)         * (np.hypot(self.l-dx,0-dy)<self.r)       *np.hypot(self.l-dx,0-dy)
        distanceTemp += distanceTemp.T
        distance = (distanceTemp==0)*distance + distanceTemp
        
        
        Ax = (distance >= 0) * (distance <= self.r) # >=0是包括自己 

        # print(Ax)
        di = np.maximum(Ax.sum(axis=1), 1) #.reshape(self.n,1)
        Dx = np.diag(di)
        # print(Dx)
        Lx = Dx-Ax
        Id = np.identity(self.n)

        #  weight matrix
        #  Wx is a nonnegative asymmetric matrix whose wij element determines the interaction strength that particle i exerts on particle j
        WxA = Ax * self.Wx
        # noise
        rng = np.random.default_rng()
        Noises = rng.random((self.n,1))*self.yeta - self.yeta/2 #[-yeta/2, yeta/2]


        '''
        When the past will not influence the futher, the influence of past will be replaced by noises. Four situations [3].  Defalt: situation D. 
        '''
        # A
        # ThetaRandom = rng.random((self.n,1))*2*np.pi
        # self.Ve[:,:]  = np.hstack((self.v*np.cos(ThetaRandom[:]),self.v*np.sin(ThetaRandom[:])))
        # B
        # ThetaRandom = rng.random((self.n,1))*2*np.pi
        # self.Ve[0:self.leaderNum+1, :]  = np.hstack((self.v*np.cos(ThetaRandom[0:self.leaderNum+1]),self.v*np.sin(ThetaRandom[0:self.leaderNum+1])))
        # C
        # ThetaRandom = rng.random((self.n,1))*2*np.pi
        # self.Ve[self.leaderNum+1:, :]  = np.hstack((self.v*np.cos(ThetaRandom[self.leaderNum+1:]),self.v*np.sin(ThetaRandom[self.leaderNum+1:])))
        # D
        # default

        leaderNum = self.leaderNum
        # calculate
        #angle
        VeA = self.alignment(WxA=WxA)                                   #alignment
        VeS = self.seperation(WxA=WxA, dx=dx, dy=dy, distance=distance) #seperation
        VeC = self.cohesion(WxA=WxA, dx=dx, dy=dy, di=di)               #cohesion
        # VeCombination = self.Ve + 1.5* VeA + 1.25* VeS + 1.3*VeC
        VeCombination = self.Ve + 1.5* VeA + 1.2* VeS + 1.35*VeC

        # except the leaders
        self.Theta[leaderNum+1:] = np.arctan2(VeCombination[leaderNum+1 :,1].reshape(self.n-leaderNum-1,1),VeCombination[leaderNum+1:,0].reshape(self.n-leaderNum-1,1))                                  
        
        
        # add noises
        self.Theta = self.Theta + Noises
        # leader control
        self.Theta= self.update_Leader_Control(Noises)
        # interval range of angle->[0,2*pi)
        self.Theta = np.mod(self.Theta, 2 * np.pi)
        
        # speed remains unchanged
        # velocity
        self.Ve = np.hstack((self.v*np.cos(self.Theta),self.v*np.sin(self.Theta)))
        # position
        self.Po  = self.Po + self.Ve * 1 # 1 means time
        self.Po = np.mod(self.Po, self.l)
        
        return self.Po, self.Theta, Ax


#=====================================================leader init
    def leader_Init(self,leaderIndex):
        '''
        leader init
        init the position, the velocities, and the angle.

        Parameters:
        ---
        leaderIndex: the largest index of the leader, start from 0.

        '''
        # Rotation
        r = 3
        dTheta = 2*np.pi/(leaderIndex+1)
        for i in range(leaderIndex+1):
            self.Po[i,:]=[self.l/2+r*np.cos(np.pi/2+dTheta*i),self.l/2+r*np.sin(np.pi/2+dTheta*i)]
            self.Ve[i,:]=[-3*np.sin(np.pi/2+dTheta*i),3*np.cos(np.pi/2+dTheta*i)]
            self.Theta[i] = np.arctan2(self.Ve[i,1].reshape(1,1),self.Ve[i,0].reshape(1,1))
        pass

    def update_Leader_Control(self,Noises):        
        '''
        Control the movement of leader.

        Parameters
        --
        Noises: Noises

        '''
        # at the beginning the self.now == 0
        # we are under the assuption that all the leader acting the same movement locally.
        # we can describe it locally with angle and speed. As speed remains unchanged, what we relly need to concern is the angle(Theta).

        Theta = self.Theta
        leaderNum = self.leaderNum 

        Theta[0:leaderNum+1] = Theta[0:leaderNum+1] -Noises[0:leaderNum+1] # eliminate the noises 
        # rotation
        
        r = 3
        Theta[0:leaderNum+1] = Theta[0:self.leaderNum+1] + self.v*1/r  # dtheta = v*dt/r

        #line
        # Theta[0:self.leaderNum+1] = -3*np.pi/4

        # sin motion
        # Theta[0:self.leaderNum+1] = np.arctan(np.cos(0.05*self.now))

        return Theta



        




if __name__ == "__main__":


    # Vicsek(sizeOfArena= 10.0, number= 200, leaderNum=10, wLF=5, speed=.1, senseRadius=1.5, noises=0.2, name="vicsek").start(stepNum=100)


    '''
    the number of leaders

    '''

    numberOfLeaderList = [3,5,8]
    for i in numberOfLeaderList:
        numberList = np.array([60, 100]) # number
        for j in numberList:
            Vicsek(sizeOfArena= 10.0, number= j, leaderNum=i,  wLF=3, speed=.1, senseRadius=1.5, noises=0.3, name="vicsek_i = :"+str(i)+"_j = :"+str(j)).start(stepNum=1000)
            Vicsek(sizeOfArena= 10.0, number= j, leaderNum=i,  wLF=3, speed=.1, senseRadius=0.5, noises=0.3, name="vicsek_i = :"+str(i)+"_j = :"+str(j)).start(stepNum=1000)
    
    
    
    '''
    数量,one leader
    '''
    # numberList = [3,6,10,20,45,60,100] # number
    # wLFList = [1,3,5,10,15] # interaction strength
    # for j in wLFList:
    #     for i in numberList:
    #         # Vicsek(sizeOfArena= 10.0, number= i, leaderNum=1,  wLF=j, speed=.1, senseRadiu=3, noises=0.2, name="vicsek_number:"+str(i)+"_wLf:"+str(j)).start(stepNum=1000)
    #         Vicsek(sizeOfArena= 10.0, number= i, leaderNum=1,  wLF=j, speed=.1, senseRadiu=3, noises=0.2, name="vicsek_number:"+str(i)+"_wLf:"+str(j)).start(stepNum=1000)
    

    '''
    作用半径与尺度的关系
    
    1. 改变尺寸
    2. 改变作用半径
    '''
    #1.
    # sizeList = [1,2,4,6,10] # 倍数

    # for i in sizeList:
    #     numberList = np.array([3,10,30,60,100])*i # number
    #     for j in numberList:
    #         Vicsek(sizeOfArena= 10.0*i, number= j, leaderNum=1,  wLF=3, speed=.1, senseRadius=3, noises=0.2, name="vicsek_number:"+str(i)+"_wLf:"+str(j)).start(stepNum=1000)

    #2.
    # rList = [0.1, 0.5, 1.0, 1.5, 3. ,5.] # 倍数

    # for i in rList:
    #     numberList = np.array([3,10,30,60,100]) # number
    #     for j in numberList:
    #         Vicsek(sizeOfArena= 10.0, number= j, leaderNum=1,  wLF=3, speed=.1, senseRadius=i, noises=0.2, name="vicsek_i = :"+str(i)+"_j = :"+str(j)).start(stepNum=1000)
    
    '''
    wlf:

    '''
    # wLFList = [1,3,5,10,15] # interaction strength

    # for i in wLFList:
    #     Vicsek(sizeOfArena= 10.0, number= 100, leaderNum=1,  wLF=i, speed=.1, senseRadius=1.5, noises=0.2, name="vicsek_i:"+str(i)+" _j:"+str(1.5)).start(stepNum=1000)
    #     Vicsek(sizeOfArena= 10.0, number= 100, leaderNum=1,  wLF=i, speed=.1, senseRadius=3, noises=0.2, name="vicsek_i:"+str(i)+" _j:"+str(3)).start(stepNum=1000)
    
    
    '''
    噪声
    '''
    # noisesList = np.arange(1,21)*0.1*np.pi# 倍数

    # for i in noisesList:
    #     numberList = np.array([3,30,100]) # number
    #     for j in numberList:
    #         Vicsek(sizeOfArena= 10.0, number= j, leaderNum=1,  wLF=3, speed=.1, senseRadius=1.5, noises=i, name="vicsek_i = :"+str(i)+"_j = :"+str(j)).start(stepNum=1000)

    
    
    '''
    噪声和wlf
    '''
    # wlfList = [10, 6.8, 4.6, 3.2, 2.2, 1.5, 1.0]
    # wlfList = [3.2]
    # noise
    # for j in wlfList:
    #     wlf = j
    #     for i in range(11):
    #         yeta = i * 0.2* np.pi
    #         Vicsek(sizeOfArena= 10.0, number= 10, leaderNum=1, wLF=j, speed=.05, senseRadiu=3, noises=yeta, name="vicsek_yeta:"+str(yeta)+"_wLF:"+str(wlf)).start()
    #     pass
    
    '''
    速度
    '''
    #速度太快肯定不行



'''
[1] Vicsek, T., Czirók, A., Ben-Jacob, E., Cohen, I. & Shochet, O. Novel Type of Phase Transition in a System of Self-Driven Particles. Phys. Rev. Lett. 75, 1226-1229 (1995).
[2] Cucker, F. & Smale, S. Emergent Behavior in Flocks. IEEE Trans. Automat. Contr. 52, 852-862 (2007).
[3] Sattari, S. et al. Modes of information flow in collective cohesion. SCIENCE ADVANCES 14 (2022).

'''
