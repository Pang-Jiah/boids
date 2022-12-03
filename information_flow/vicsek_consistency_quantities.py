#data processing 
# Under developing
# authority: Pang Jiahuan
# start time: 2022/11/28
# last time: 2022/12/03
# end time: ~
#consistency quantities: v_{a} \omega_{a} f_{a}
# python: 3.6

'''
version description:
    quantities to transition
    the latest quantities are $v_{a1}^{\star} and v_{a2}^{\star}$
'''

#考虑：
#   *.数据读取和数据存储的安排有些笨重


import h5py
import numpy as np
import os

import matplotlib.pyplot as plt 

from scipy.fftpack import fft # fast fourier transform
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



# ======================== ordering judge 
def my_Plot(x,y,xlable='',ylable='',leaderNum=1): 
    '''
    plot

    Parameter
    ---
        x: x;
        y: y;
        xlable: x axis lable
        ylable: y axis lable
        leaderNum: The number of leaders
    '''
    # add xlable and ylable

    plt.figure()
    plt.xlabel(xlabel=xlable,size = 15)#x轴上的名字
    plt.ylabel(ylabel=ylable,size = 15)#y轴上的名字
    # plt.legend(loc = 'upper right')
    n = np.shape(y)[0]
    for i in range(n):
        if i <leaderNum:
            plt.plot(x,y[i],linewidth=1,color = 'red',zorder=n+1)
        else:
            plt.plot(x,y[i],linewidth=2,color = 'blue')
    plt.show()
    pass


def v_a(Ve,s):
    '''
    va  (1 x stepNum)

    Function
    ---
        $$V_a = \frac{|\sum_{i}^{N} \vec{v}_i|}{Nv}$$
    
    parameter
    ---
        Ve: velocity
        s: speed
    '''
    sumVe = Ve.sum(axis = 0)
    n = np.shape(Ve)[0]
    a = np.hypot(sumVe[0,:],sumVe[1,:])
    va = a/(n*s)
    va = va.reshape(1,np.shape(va)[0])
    return 
    
def v_a_star(Ve):
    n = np.shape(Ve)[0]
    '''
    $v_{a1}^{\star} = |\frac{1}{N} \sum_{i=1}^{N}\vec{v_i}-\vec{v_L}|$
    '''
    sumVe = Ve.sum(axis = 0)
    a = sumVe/n - Ve[0,:,:]

    vaStar1 = np.hypot(a[0,:],a[1,:])
    # vaStar1 = vaStar1.reshape(1,np.shape(vaStar1)[0])
    '''
    $v_{a2}^{\star} = \frac{1}{N}\sum_{i=1}^{N}|\vec{v_i}-\vec{v_L}|$
    '''
    a2 = Ve-Ve[0,:,:]
    sumVa = np.hypot(a2[:,0,:],a2[:,1,:]).sum(axis=0)
    vaStar2 = sumVa/n
    return vaStar1, vaStar2

def w_a(We,w):
    '''
    wa  (1 x (stepNum-1))

    Function
    ---
        $$\omega_a = \frac{|\sum_{i}^{N} \omega_i|}{N\omega}$$
    
    parameter
    ---
        We: angular velocity
        w: referent angular velocity 

    the dimention of We must >1
    '''
    a = We.sum(axis=0)
    n = np.shape(We)[0]
    # print("a",np.shape(a),a)
    wa = a/(n*w)
    wa = wa.reshape(1,np.shape(wa)[0])
    return wa


def fft_Get(y, Ns, timeResolution ):
    '''
    fast fourier transform

    parameter
    ---
        y: value
        Ns: the number of sampling
            here Ns==stepNum 
        timeResolution: time gap between two dicrete point

    return
    ---
        halfY: half
        halfX: half frequency
    '''
    fftResult = fft(y)
    absY = np.abs(fftResult)
    normalizationY = absY/Ns # 归一化 normalization 
    halfY = normalizationY[:,range(int(Ns/2))] # half

    t = timeResolution*Ns
    x = np.arange(Ns)/t # frequency resolution
    halfX = x[range(int(Ns/2))]  #取一半区间
    return halfY, halfX


def f_a(frequencyList):
    '''
    wa  1 x ( total sampling / each smallsampling)

    Function
    ---
        $$f_a = \frac{\sum_{i}^{N} f_i}{N*f_L}$$
    
    parameter
    ---
        frequencyList: frequency list

    the dimention of We must >1
    '''
    n = np.shape(frequencyList)[0]
    t = np.shape(frequencyList)[1]
    fLeader = frequencyList[0,:]
    a = frequencyList.sum(axis = 0)

    fa = a/(n*fLeader)
    fa = fa.reshape(1,t)# this is for the plot. a x b: a is for the number of line, b is for the x sequence
    return fa

def f_a_star(frequencyList):
    n = np.shape(frequencyList)[0]
    t = np.shape(frequencyList)[1]
    fLeader = frequencyList[0,:]
    
    
    a = frequencyList.sum(axis = 0)-fLeader*n
    a = ((a/n)**2)**0.5

    fa_star = a.sum()

    return fa_star

if __name__ == "__main__":
    # enter the absolute path of this python file
    mypath = os.path.split(__file__)[0]
    os.chdir(mypath)

#%%有序度相关处理过程
    os.chdir("tes")# 存放数据的文件夹，注意要在python 文件的同级目录下
    # os.chdir("sin_NoiseToOrder")
    # os.chdir("sin1")
    os.chdir("rotation_cohesion")
    # os.chdir("rotation_fft_coh")
    # os.chdir("rotation_back")
    f = H5PY_Processor("vicsekData.hdf5","r")
    # f.search_Deep('/')


    Ve             = f.f["velocitySaved"][:,:,:]
    Theta          = f.f["angleSaved"][:,:]
    timeResolution = f.f["timeResolution"][:][0]
    stepNum        = f.f["stepNum"][:][0]
    
    n     = np.shape(Theta)[0]  # the number of nodes 
    # get the angular velocity
    # Omiga = (Theta[:,1:stepNum] -Theta[:,0:stepNum-1]) + 2*np.pi
    # Omiga = Omiga% 2*np.pi
    # kmask = Omiga>np.pi
    # ksign = np.ones(np.shape(Omiga))
    # k = kmask*ksign
    # Omiga = Omiga - 2*np.pi*k
    # # Omiga = np.subtract(Omiga, 2*np.pi, where = Omiga>np.pi)
    # Omiga = Omiga/timeResolution

    t     = timeResolution*stepNum # the total times (second)

    '''
        为了获得一个过程,我们1000个采样点(fps=20)共50s(20Hz),可检测频率最高约为10Hz(根据 采样定理).所要检测的频率为1Hz.每秒进行一次检测20个采样点。
        每次得到最可能的频率并
    '''
    # sP = int(1/timeResolution) # the number of sampling points at each time
    # sP              = 200 # the number of sampling points at each time cover the 
    # sPList          = np.arange(0,stepNum,sP)
    # maxFrequeceList = np.zeros((n,int(stepNum/sP)))
    # faStarList = np.zeros((1,int(stepNum/sP)))


    y_fft1,x_fft1= fft_Get(y=Ve[:,0,:],Ns=stepNum,timeResolution=timeResolution)

    my_Plot(x = x_fft1,y = y_fft1[0,:].reshape(1,np.shape(x_fft1)[0]),xlable="$f$",ylable="y")
    my_Plot(x = x_fft1,y = y_fft1, xlable="$f$", ylable="y",leaderNum = 8)


    # plt.figure()
    # for i in range(np.shape(maxFrequeceList)[1]):
    #     y_fft,x_fft= fft_Get(y=Ve[:,1,i*sP:(i+1)*sP],Ns=sP,timeResolution=timeResolution)

    
    #     plt.subplot(5,5,i+1)
    #     plt.plot( x_fft,y_fft[87,:])
    #     plt.xlim((-.1,0.5))

    #     # my_Plot(x = x_fft,y = y_fft[87,:].reshape(1,np.shape(x_fft)[0]),xlable="$f$",ylable="y")

    #     maxFrequeceList[:,i] = np.argmax(y_fft,axis = 1)/(sP*timeResolution)
    #     # maxFrequeceList[:,i] = np.argmax(y_fft,axis = 1)
    # plt.show()

    # x1 = np.arange(1, np.shape(maxFrequeceList)[1]+1)#a k
    # fa = f_a(maxFrequeceList)
    # # print(np.shape(fa),fa,maxFrequeceList[0,:])
    # my_Plot(x = x1, y = maxFrequeceList[87,:].reshape(1,np.shape(maxFrequeceList)[1]),xlable="$n$",ylable="$f_{max}$")
    # my_Plot(x=x1, y= fa, xlable="$n$", ylable="$f_a$")




    # fa_star

    # for i in range(np.shape(faStarList)[1]):
    
    #     y_ffty,x_ffty= fft_Get(y=Ve[:,1,i*sP:(i+1)*sP],Ns=sP,timeResolution=timeResolution)
    #     y_fftx,x_fftx= fft_Get(y=Ve[:,0,i*sP:(i+1)*sP],Ns=sP,timeResolution=timeResolution)
    #     faStary = f_a_star(y_ffty)
    #     faStarx = f_a_star(y_fftx) # k
    #     faStarList[0,i] = faStary + faStarx #k


    # x1 = np.arange(1, np.shape(faStarList)[1]+1)#a k
    # my_Plot(x=x1, y= faStarList.reshape(1,np.shape(faStarList)[1]), xlable="$n$", ylable="$f_a^{\star}$") # k

    #==================== 相似度处理
    # y_fft1,x_fft1= fft_Get(y=Ve[:,1,:],Ns=stepNum,timeResolution=timeResolution)
    


    #==========v_a
    '''
    %v_a% and % v_a^*%
    '''
    # x = np.arange(stepNum)

    # # # y_lin = v_a(Ve=Ve,s=2)
    # y_lin1, y_lin2 = v_a_star(Ve=Ve)
    # # my_Plot(x,y_lin,xlable="$t$",ylable="$v_a^{\star}$")
    # plt.figure()
    # plt.xlabel(xlabel='$n$',size = 15)#x轴上的名字
    # plt.ylabel(ylabel='$v_a$',size = 15)#y轴上的名字
    # # plt.legend(loc = 'upper right')
    # plt.plot(x,y_lin1,label='$v_{a1}^{\star}$')
    # plt.plot(x,y_lin2,label='$v_{a2}^{\star}$')
    # plt.legend()
    # plt.show()
    
    ## batch processing
    # os.chdir("tes1")# 存放数据的文件夹，注意要在python 文件的同级目录下

    # for fileName in os.listdir("."):
    #     print("go",end=' ')
    #     os.chdir(fileName)  # 当前目录路径
    #     f = H5PY_Processor("vicsekData.hdf5","r")


    #     Ve             = f.f["velocitySaved"][:,:,:]
    #     Theta          = f.f["angleSaved"][:,:]
    #     timeResolution = f.f["timeResolution"][:][0]
    #     stepNum        = f.f["stepNum"][:][0]
        
    #     n     = np.shape(Theta)[0]  # the number of nodes 
    #     x = np.arange(stepNum)

    #     y_lin1, y_lin2 = v_a_star(Ve=Ve)
    #     plt.figure()
    #     plt.xlabel(xlabel='$n$',size = 15)#x轴上的名字
    #     plt.ylabel(ylabel='$v_a$',size = 15)#y轴上的名字
    #     plt.plot(x,y_lin1,label='$v_{a1}^{\star}$')
    #     plt.plot(x,y_lin2,label='$v_{a2}^{\star}$')
    #     plt.legend()
    #     plt.savefig("./v_a.png")
    #     plt.close()
    #     f.close()
    #     os.chdir('..')


    # os.chdir("..")
    #==========w_a
    '''
    $/omega_a$
    '''

    # x1 = np.arange(stepNum-1)
    # # print(Omiga[8,:])
    # y_ang = w_a(Omiga,Omiga[0,0])
    # # print(y_ang)
    # my_Plot(x1,y_ang,xlable="$n$",ylable="$\omega_a$")

#D:\HIT\大四\information_flowing\代码\testingandbuilding\boids_test\main\tes1

    os.chdir("..")# sin3
    os.chdir("..")# tes


