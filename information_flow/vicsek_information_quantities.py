#data processing 
# Under developing
# authority: Pang Jiahuan
# start time: 2022/10/30
# last time: 2022/11/19
# end time: ~
#information flow: mutual information; 
#                  time-delayed mutual information; 
#                  transfer entropy; 
#                  shared, intrinsic, syn.. entropy.
# python: 3.6

'''
version description:
    完成某些类型图的绘制与数据的读取，格式的一些修改
'''
#考虑：
#   ·. 取和不为1
#   ·.intrinsic information flow
#   *.数据读取顺序和图中顺序的确认(first thing to do)
#   *.数据读取和数据存储的安排有些笨重

import h5py
import numpy as np
import os

import itertools as it # sorting
import dit # information theory
import matplotlib.pyplot as plt 
import progressbar

'''
#Attention !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

文件排序方式为:名称+增序

'''

class H5PY_Processor():
    '''
    A Class for basic HDF5 file operation

    Init Parameters
    --
    filename: str
        name of the file

    authority: str
        the authority of operation:
        - r  只读，文件必须已存在 read-only;
        - r+ 读写，文件必须已存在 read and write;
        - w  新建文件，若存在覆盖;
        - w- 或x, 新建文件, 若存在报错;
        - a  如存在则读写，不存在则创建(默认).
    '''
    
    def __init__(self, fileName: str, authority: str) -> None:
        self.f = h5py.File(fileName, authority)
        pass
    def close(self):
        # print("文件被释放")
        self.f.close()
        pass
    def search_Deep(self,path: str,name:str = '/') -> None:
        '''
        Use depth-first algorithm to draw the file structure of HDF5 groups. 

        Parameters
        -------
        path: str,
            the absolute path of a group or a database
        name: str, default: '/'
            the name of a group or a database, and the default value poits to root directory.
        
        Warning
        ----------
        this function now is under development and is not able to vertify the correctness of the input parameters.

        Examples:
        ---
        >>> self.search_Deep(path = '/')
        
        '''
        dog = self.f[path] # a group or dataset
        if dog.name == "/":
            print('+-',end='')
            count = 0
        else:
            count = dog.name.count("/")
        for i in range(count):
            print("+----",end='')
        #Group有.keys()方法 而dataset没有
        #dataset有.len()方法

        try:# if is a group
            length = len(dog.keys())
            print(name,"[G]")
            if length != 0:
                for key in dog.keys():
                    self.search_Deep(dog.name +"/"+key,key)
        except:# a dataset
            # print(name,"[D]", np.shape(dog),end = '')#没有长度的dataset可能会被看作是group，因此len()失效
            # print(dog)
            print(name,"[D]", np.shape(dog))#没有长度的dataset可能会被看作是group，因此len()失效

class Information_Processor():
    def __init__(self, Theta, stepNum,x,y) -> None:
        self.Theta = Theta
        self.stepNum = stepNum
        self.discretize()
        #init alphabet
        self.alphabet={}
        for e in it.product('012345', repeat=3):
            a = ''.join(e)
            self.alphabet[a] = 0.0   
        # print(self.alphabet)  
        self.count_Distribution(x=x,y=y)
        self.calculate_Information()
        pass

    def discretize(self):
        '''
        discretize the angle set (self.Theta (0~2*pi )) into 6 parts
        0 1 2 3 4 5  

        for example: [0°,60°) -> 0; [60°,120°) -> 1 ...

        '''
        Theta = self.Theta
        Theta = np.mod(Theta,2*np.pi)#将2*pi变为0
        Theta = np.floor_divide(Theta, np.pi/3)
        self.bins = Theta 
        pass


    def count_Distribution(self, x:int, y:int):
        '''
        count the occurrences of  (x(t), y(t), y(t+τ)) 
            x affect y. For convenience, let X, Y, and Z denote x(t), y(t), y(t+τ)seperately.

        Parameters
        --
        x,y: int
            the index of vairable

        
        '''
        # count
        for i in range(self.stepNum-1):
            index = str(int(self.bins[x][i])) + str(int(self.bins[y][i])) + str(int(self.bins[y][i+1]))
            # print(index)
            self.alphabet[index] += 1/(self.stepNum-1)

        alphabetKeys  = list(self.alphabet.keys()) # seperate the keys form dict
        alphabetValue = list(self.alphabet.values()) # seperate the value from dict

        self.XYZ = dit.Distribution(alphabetKeys, alphabetValue) # get the joint distribution
        self.XYZ.set_rv_names('XYZ')
        # print(self.XYZ)
        pass

    def mutual_Information(self):
        '''
        calculate the mutual information of x(t) and y(t)

        Return
        ---
            mI: mutual information of x(t) and y(t)
        '''
        
        mI = dit.shannon.mutual_information(self.XYZ,'X','Y')
        # print(mutual_Information)
        return mI
        
    def time_Delayed_Mutual_Information(self):
        '''
        calculate time delayed mutual information (TDMI)
        
        Return
        ---
            tMDI: TMDI
        '''
        tMDI = dit.shannon.mutual_information(self.XYZ,'X','Z')
        return tMDI

    def transfer_Entropy(self):
        '''
        calculate  transfer_Entropy (TE)
        
        Return
        ---
            tE: TE
        '''
        # tE = dit.multivariate.coinformation(self.XYZ, rvs = 'XZ', crvs = 'Y')
        tE = dit.multivariate.coinformation(self.XYZ, 'XZ','Y')
        return tE

    def intrinsic_Information_Flow(self):
        '''
        calculate time intrinsic_Information_Flow (IIF)
        
        Return
        ---
            iIF: IIF
        '''
        iIF = dit.multivariate.secret_key_agreement.intrinsic_mutual_information(self.XYZ, 'XZ','Y')
        return iIF

    def shared_Information_Flow(self, tE, iIF):
        '''
        calculate time shared_Information_Flow (SHIF)
        
        Parameters
        ---
        tE: TE
        iIF: IIF

        Return
        ---
            sHIF: SHIF
        '''
        sHIF = tE - iIF
        return sHIF

    def synergistic_Information_Flow(self, tDMI, iIF):
        '''
        calculate time synergistic_Information_Flow (SYIF)
        
        Parameters
        ---
        tDMI: TDMI
        iIF: IIF

        Return
        ---
            sYIF: SYIF
        '''
        sYIF = tDMI - iIF
        return sYIF

    def calculate_Information(self):
        '''
        calculate all the information we need
        '''
        self.mI = self.mutual_Information()
        self.tDMI = self.time_Delayed_Mutual_Information()
        self.tE = self.transfer_Entropy()
        self.iIF = self.intrinsic_Information_Flow()
        self.sHIF = self.shared_Information_Flow(tE= self.tE, iIF= self.iIF)
        self.sYIF = self.synergistic_Information_Flow(tDMI=self.tDMI, iIF=self.iIF)
        pass

    def get_Information(self):
        '''
        Collect all the quantities we need in a `dict`.
        '''
        informationDict = {
            "mutual_information": self.mI,
            "time_delayed_mutual_information": self.tDMI,
            "transfer_entropy":self.tE,
            "intrinsic_Information_Flow":self.iIF,
            "shared_information_flow":self.sHIF,
            "synergistic_information_flow":self.sYIF,
        }

        return informationDict

def draw_Heat_Map(infAll:list, infName:str, figSize:tuple, flag: int):
    '''
    Draw the heat map    
    
    Parameters
    ---
    infAll: List [{}]
        all the information quantities
    infName: str
        the information quantity you want to draw
    figSize: tuple
        the size of the heat map
    flag: int
        0: Leader-> Follower; 1: Follower->Leader
    
    Attention
    ---
    the figSize and axis need to be carefully check mannually 
    '''
    size = np.shape(infAll)[0]
    data = np.zeros(size)
    i = 0
    for i in range(size):
        data[i] = infAll[i][infName]
    
    data = data.reshape(figSize)
    # print(data)
    #显示图像
    #这里的cmap='bone'等价于plt.cm.bone
    plt.imshow(data,interpolation = 'nearest',cmap = 'Reds' ,origin = 'lower')
    #显示右边的栏
    plt.colorbar(shrink = .5)
    # plt.colorbar(shrink = .92)
    plt.xticks(np.arange(0,11,1),np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]))
    plt.yticks(np.arange(0,7,1), np.array([10, 6.8, 4.6, 3.2, 2.2, 1.5, 1.0]))
    if flag == 0:
        figName = "./" + infName + "_leader_to_follower" + "_yeta_Wlf"+ ".jpg"
    else:
        figName = "./" + infName + "_follower_to_leader" +"_yeta_Wlf"+ ".jpg"
    plt.savefig(figName)
    plt.close()

def draw_Linear(infAll:list, infName:str, figSize:tuple):
    '''
    Draw the Linear 
    
    Parameters
    ---
    >>> infAll: List [{}]
        all the information quantities
    >>> infName: str
        the information quantity you want to draw
    >>> figSize: (the data for drawing a line, others)
        
    
    Attention!!!!!!!!!!!!!!!!!
    ---
    the figSize and axis need to be carefully check mannually 
    label should be changed
    '''
    size = np.shape(infAll)[0]
    data = np.zeros(size)

    for i in range(size):
        data[i] = infAll[i][infName]
    data = data.reshape(figSize)
    # print(data)

    #显示图像
    #这里的cmap='bone'等价于plt.cm.bone
    plt.plot(np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]), data[0,:],label='N_f ='+str(3))
    plt.plot(np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]), data[1,:],label='N_f ='+str(9))

    # plt.xticks(np.arange(0,5,1),np.array([0, 0.2, 0.4, 0.6, 0.8]))
    # plt.yticks(np.arange(0,2,1),np.array([1.0, 1.5]))
    figName = "./" + "different W_lf _" + infName + "_varing with Follower"+ ".jpg"
    plt.legend()
    plt.savefig(figName)
    plt.close()

if __name__ == "__main__":
    # enter the absolute path of this python file
    mypath = os.path.split(__file__)[0]
    os.chdir(mypath)



    # prograssbar part
    os.chdir("D")# 存放数据的文件夹，注意要在python 文件的同级目录下
    fileNumber = np.shape(os.listdir("."))[0]
    # print(fileNumber)
    widgets = ['Progress: ',progressbar.Percentage(), ' ', progressbar.Bar('#'),' ', progressbar.Timer(),
           ' ', progressbar.ETA(), ' ', progressbar.FileTransferSpeed()]
    pbar = progressbar.ProgressBar(widgets=widgets, max_value=fileNumber).start()
    fileNow = 0


    '''
    Accessing data part
    # 先为了实现功能，每组数据的排序通过文件名称中的时间来实现，时间从过去到未来-》先 noises 从小到大，再 wFT从小到大
    # 这样虽然方便但是太过于脆弱了
    '''
    infAllLF = []
    infAllFL = []
    
    for fileName in os.listdir("."):
        try:
            pbar.update(fileNow+1)
            fileNow += 1
            
            # print(fileName)
            os.chdir(fileName)  # 当前目录路径

            # get the file
            f = H5PY_Processor("vicsekData.hdf5","r")
            # f.search_Deep("/")
            
            # in the condition one leader
            #leader->follower
            infLF = Information_Processor(Theta= f.f["angleSaved"][:,:],stepNum=f.f['stepNum'][0],x=0,y=1).get_Information()
            infAllLF.append(infLF)# collect the information of all the situation in a list
            #follower->leader
            # infFL = Information_Processor(Theta= f.f["angleSaved"][:,:],stepNum=f.f['stepNum'][0],x=1,y=0).get_Information()
            # infAllFL.append(infFL)# collect the information of all the situation in a list
            f.close()
            os.chdir('..')
        except:
            print(fileName)

    os.chdir('..')
    print(" :) Data read and processed successfully")
    


    '''
        figure part

        informationDict = {
        "mutual_information": self.mI,
        "time_delayed_mutual_information": self.tDMI,
        "transfer_entropy":self.tE,
        "intrinsic_Information_Flow":self.iIF,
        "shared_information_flow":self.sHIF,
        "synergistic_information_flow":self.sYIF,
        }
    '''

    dataSavedPath = "result"
    if not os.path.isdir(dataSavedPath):
        os.mkdir(dataSavedPath)
    os.chdir(dataSavedPath)


    # draw_Heat_Map(infAll=infAllLF,infName="time_delayed_mutual_information",figSize=(2,11),flag=0)

    #leader to follower
    draw_Heat_Map(infAll=infAllLF,infName="mutual_information",figSize=(7,11),flag=0)
    draw_Heat_Map(infAll=infAllLF,infName="time_delayed_mutual_information",figSize=(7,11),flag=0)
    draw_Heat_Map(infAll=infAllLF,infName="transfer_entropy",figSize=(7,11),flag=0)
    draw_Heat_Map(infAll=infAllLF,infName="intrinsic_Information_Flow",figSize=(7,11),flag=0)
    draw_Heat_Map(infAll=infAllLF,infName="shared_information_flow",figSize=(7,11),flag=0)
    draw_Heat_Map(infAll=infAllLF,infName="synergistic_information_flow",figSize=(7,11),flag=0)
    # #follower to leader
    # draw_Heat_Map(infAll=infAllFL,infName="mutual_information",figSize=(7,11),flag=1)
    # draw_Heat_Map(infAll=infAllFL,infName="time_delayed_mutual_information",figSize=(7,11),flag=1)
    # draw_Heat_Map(infAll=infAllFL,infName="transfer_entropy",figSize=(7,11),flag=1)
    # draw_Heat_Map(infAll=infAllFL,infName="intrinsic_Information_Flow",figSize=(7,11),flag=1)
    # draw_Heat_Map(infAll=infAllFL,infName="shared_information_flow",figSize=(7,11),flag=1)
    # draw_Heat_Map(infAll=infAllFL,infName="synergistic_information_flow",figSize=(7,11),flag=1)


    # draw_Linear(infAll=infAllLF,infName="mutual_information",figSize=(2,11))
    # draw_Linear(infAll=infAllLF,infName="time_delayed_mutual_information",figSize=(2,11))
    # draw_Linear(infAll=infAllLF,infName="transfer_entropy",figSize=(2,11))
    # draw_Linear(infAll=infAllLF,infName="intrinsic_Information_Flow",figSize=(2,11))
    # draw_Linear(infAll=infAllLF,infName="shared_information_flow",figSize=(2,11))
    # draw_Linear(infAll=infAllLF,infName="synergistic_information_flow",figSize=(2,11))

    
    print(":) An artist has finished his\her\its job")
    
    os.chdir('..')

    # print("multual_Information:",processor.mI)
    # print("time_Delayed_Mutual_Information:",processor.tDMI)
    # print("transfer_Entropy:",processor.tE)
    # print("intrinsic_Information_Flow:",processor.iIF)
    # print("shared_Information_Flow:",processor.sHIF)
    # print("synergistic_Information_Flow:",processor.sYIF)

# ABCD->读取所有的数据和信息 如何存储这些信息呢？

'''
reference:
1. G. James, R., J. Ellison, C. & P. Crutchfield, J. dit: a Python package for discrete information theory. JOSS 3, 738 (2018).
'''