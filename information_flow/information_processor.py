import numpy as np
import itertools as it # sorting
import dit # information theory
from dit.pid import *
import math


def mutual_Information(distribution:dit.Distribution, var1:str='X', var2:str='Y'):
    '''
    calculate the mutual information of x(t) and y(t)

    Return
    ---
        distribution: distribution
        mI: mutual information of x(t) and y(t)
    '''
    
    mI = dit.shannon.mutual_information(distribution,var1,var2)
    # print(mutual_Information)
    return mI

    
def multivariate_Mutual_Information(distribution:dit.Distribution, var1:str='XY', var2:str='Z'):
    '''
    calculate the mutual information with multivirables

    Return
    ---
        mI: mutual information 
    '''
    
    mI = dit.multivariate.coinformation(distribution, [var1, var2])
    # print(mutual_Information)
    return mI

def time_Delayed_Mutual_Information(distribution:dit.Distribution,var1:str='X', var2:str='Z'):
    '''
    calculate time delayed mutual information (TDMI)
    
    Return
    ---
        tMDI: TMDI
    '''
    tMDI = dit.shannon.mutual_information(distribution,var1,var2)
    return tMDI

def transfer_Entropy(distribution:dit.Distribution, var1:str='X', var2:str='Z', cvar = 'Y'):
    '''
    calculate  transfer_Entropy (TE)
    
    Return
    ---
        tE: TE
    '''
    # tE = dit.multivariate.coinformation(self.XYZ, rvs = 'XZ', crvs = 'Y')
    tE = dit.multivariate.coinformation(distribution, var1+var2,cvar)
    return tE




# secret agreement rata
# Upper Intrinsic Mutual Information (Upper Bound)
#   #intrinsic mutaul information
def intrinsic_Mutual_Information(distribution:dit.Distribution, var1:str='X', var2:str='Z', cvar = 'Y'):
    '''
    information decomposition of intrinsic mutual information (IMI) (three variables)
    
    Return
    ---
        imi: intrinsic mutal information -> I(var1;var2|bar{cvar})
        share: shared information -> TDMI-imi
        syner: synergistic information -> TE-imi
    '''
    try:
        imi = dit.multivariate.secret_key_agreement.intrinsic_mutual_information(distribution, var1+var2, cvar)
    except:
        imi=0
    share = time_Delayed_Mutual_Information(distribution=distribution, var1=var1, var2=var2) - imi
    syner = transfer_Entropy(distribution=distribution, var1=var1, var2=var2, cvar=cvar) - imi

    return imi, share, syner


#   #reduced_intrinsic_mutual_information
def reduced_Intrinsic_Mutual_Information(distribution:dit.Distribution, var1:str='X', var2:str='Z', cvar = 'Y'):
    '''
    information decomposition of reduced intrinsic mutual information (IMI) (three variables)
    
    Return
    ---
        rimi: reduced intrinsic mutal information -> I(var1;var2|bar{cvar})
        share: shared information -> TDMI-imi
        syner: synergistic information -> TE-imi
    '''
    try:
        rimi = dit.multivariate.secret_key_agreement.reduced_intrinsic_mutual_information(distribution, var1+var2, cvar)
    except:
        rimi=0
    share = time_Delayed_Mutual_Information(distribution=distribution, var1=var1, var2=var2) - rimi
    syner = transfer_Entropy(distribution=distribution, var1=var1, var2=var2, cvar=cvar) - rimi

    return rimi, share, syner    



#   #minimal_intrinsic_mutual_information
def minimal_Intrinsic_Mutual_Information(distribution:dit.Distribution, var1:str='X', var2:str='Z', cvar = 'Y'):
    '''
    information decomposition of minimal intrinsic mutual information (IMI) (three variables)
    
    Return
    ---
        mimi: minimal intrinsic mutal information -> I(var1;var2|bar{cvar})
        share: shared information -> TDMI-imi
        syner: synergistic information -> TE-imi
    '''
    try:
        mimi = dit.multivariate.secret_key_agreement.minimal_intrinsic_total_correlation(distribution, var1+var2, cvar)
    except:
        mimi=0
    share = time_Delayed_Mutual_Information(distribution=distribution, var1=var1, var2=var2) - mimi
    syner = transfer_Entropy(distribution=distribution, var1=var1, var2=var2, cvar=cvar) - mimi

    return mimi, share, syner   


# Lower Intrinsic Mutual Information (lower bound)
#   # lower bound of secret key agreement
def lower_Intrinsic_Mutual_Information(distribution:dit.Distribution, var1:str='X', var2:str='Z', cvar = 'Y'):
    '''
    information decomposition of lower intrinsic mutual information (lIMI) (three variables)
    
    Return
    ---
        limi: lower intrinsic mutal information -> I(var1;var2|bar{cvar})
        share: shared information -> TDMI-imi
        syner: synergistic information -> TE-imi
    '''
    try:
        limi = dit.multivariate.secret_key_agreement.lower_intrinsic_mutual_information(distribution, var1+var2, cvar)
    except:
        limi=0
    share = time_Delayed_Mutual_Information(distribution=distribution, var1=var1, var2=var2) - limi
    syner = transfer_Entropy(distribution=distribution, var1=var1, var2=var2, cvar=cvar) - limi

    return limi, share, syner



#   # necessary_intrinsic_mutual_information (lower bound)
def necessary_Intrinsic_Mutual_Information(distribution:dit.Distribution, var1:str='X', var2:str='Z', cvar = 'Y'):
    '''
    information decomposition of necessary intrinsic mutual information (IMI) (three variables)
    
    Return
    ---
        nimi: necessary intrinsic mutal information -> I(var1;var2|bar{cvar})
        share: shared information -> TDMI-imi
        syner: synergistic information -> TE-imi
    '''
    try:
        nimi = dit.multivariate.secret_key_agreement.necessary_intrinsic_mutual_information(distribution, var1+var2, cvar)
    except:
        nimi=0
    share = time_Delayed_Mutual_Information(distribution=distribution, var1=var1, var2=var2) - nimi
    syner = transfer_Entropy(distribution=distribution, var1=var1, var2=var2, cvar=cvar) - nimi

    return nimi, share, syner



# partial information decomposition
def I_Min(distribution:dit.Distribution):
    '''
    information decomposition of I_min (three variables) [Nonnegative Decomposition of Multivariate Information]
    
    only can calculate the information pass from the first two variables to the third one 


    Parameters:
    ---
    distribution: the distribution

    Return
    ---
    unique0: unique information 0->2
    unique1: unique information 1->2
    redundance: redundant information 0,1->2
    synergy: synergistic information 0,1->2
    '''
    I_min = PID_WB(distribution)
    tuple_dic = {"unique0":((0,),),"unique1":((1,),),"reduandence":((0,), (1,)),"synergistic":((0, 1),)}
    unique0 = I_min.get_partial(node=tuple_dic["unique0"])
    unique1 = I_min.get_partial(node=tuple_dic["unique1"])
    redundance = I_min.get_partial(node=tuple_dic["reduandence"])
    synergy = I_min.get_partial(node=tuple_dic["synergistic"])
    
    return unique0, unique1, redundance, synergy

def I_Mmi(distribution:dit.Distribution):
    '''
    information decomposition of I_mmi (three variables) [Shared information—new insights and problems in decomposing information in complex systems]
    
    only can calculate the information pass from the first two variables to the third one 


    Parameters:
    ---
    distribution: the distribution

    Return
    ---
    unique0: unique information 0->2
    unique1: unique information 1->2
    redundance: redundant information 0,1->2
    synergy: synergistic information 0,1->2
    '''
    I_mmi = PID_MMI(distribution)
    tuple_dic = {"unique0":((0,),),"unique1":((1,),),"reduandence":((0,), (1,)),"synergistic":((0, 1),)}
    unique0 = I_mmi.get_partial(node=tuple_dic["unique0"])
    unique1 = I_mmi.get_partial(node=tuple_dic["unique1"])
    redundance = I_mmi.get_partial(node=tuple_dic["reduandence"])
    synergy = I_mmi.get_partial(node=tuple_dic["synergistic"])
    
    return unique0, unique1, redundance, synergy

def I_Wedge(distribution:dit.Distribution):
    '''
    information decomposition of I_wedge (three variables) [Intersection information based on common randomness]
    
    only can calculate the information pass from the first two variables to the third one 


    Parameters:
    ---
    distribution: the distribution

    Return
    ---
    unique0: unique information 0->2
    unique1: unique information 1->2
    redundance: redundant information 0,1->2
    synergy: synergistic information 0,1->2
    '''
    I_wedge = PID_GK(distribution)
    tuple_dic = {"unique0":((0,),),"unique1":((1,),),"reduandence":((0,), (1,)),"synergistic":((0, 1),)}
    unique0 = I_wedge.get_partial(node=tuple_dic["unique0"])
    unique1 = I_wedge.get_partial(node=tuple_dic["unique1"])
    redundance = I_wedge.get_partial(node=tuple_dic["reduandence"])
    synergy = I_wedge.get_partial(node=tuple_dic["synergistic"])
    
    return unique0, unique1, redundance, synergy

def I_Proj(distribution:dit.Distribution):
    '''
    information decomposition of I_proj (three variables) [Bivariate measure of redundant information]
    
    only can calculate the information pass from the first two variables to the third one 


    Parameters:
    ---
    distribution: the distribution

    Return
    ---
    unique0: unique information 0->2
    unique1: unique information 1->2
    redundance: redundant information 0,1->2
    synergy: synergistic information 0,1->2
    '''
    tuple_dic = {"unique0":((0,),),"unique1":((1,),),"reduandence":((0,), (1,)),"synergistic":((0, 1),)}
    try:
        I_proj = PID_Proj(distribution)
        unique0 = I_proj.get_partial(node=tuple_dic["unique0"])
        unique1 = I_proj.get_partial(node=tuple_dic["unique1"])
        redundance = I_proj.get_partial(node=tuple_dic["reduandence"])
        synergy = I_proj.get_partial(node=tuple_dic["synergistic"])
    except:
        distribution.set_rv_names("XYZ")
        unique0 = 0
        unique1 = 0

        redundance =  time_Delayed_Mutual_Information(distribution=distribution, var1='X', var2='Z')
        synergy = transfer_Entropy(distribution=distribution, var1='X', var2='Z', cvar='Y')
        distribution.set_rv_names((0,1,2))
    return unique0, unique1, redundance, synergy

def I_Broja(distribution:dit.Distribution):
    '''
    information decomposition of I_Broja (three variables) [Quantifying unique information]
    
    only can calculate the information pass from the first two variables to the third one 


    Parameters:
    ---
    distribution: the distribution

    Return
    ---
    unique0: unique information 0->2
    unique1: unique information 1->2
    redundance: redundant information 0,1->2
    synergy: synergistic information 0,1->2
    '''
    I_broja = PID_BROJA(distribution)
    tuple_dic = {"unique0":((0,),),"unique1":((1,),),"reduandence":((0,), (1,)),"synergistic":((0, 1),)}
    unique0 = I_broja.get_partial(node=tuple_dic["unique0"])
    unique1 = I_broja.get_partial(node=tuple_dic["unique1"])
    redundance = I_broja.get_partial(node=tuple_dic["reduandence"])
    synergy = I_broja.get_partial(node=tuple_dic["synergistic"])
    
    return unique0, unique1, redundance, synergy


def I_CCS(distribution:dit.Distribution):
    '''
    information decomposition of I_CCS (three variables) [Measuring multivariate redundant information with pointwise common change in surprisal]
    
    only can calculate the information pass from the first two variables to the third one 


    Parameters:
    ---
    distribution: the distribution

    Return
    ---
    unique0: unique information 0->2
    unique1: unique information 1->2
    redundance: redundant information 0,1->2
    synergy: synergistic information 0,1->2
    '''
    I_ccs = PID_CCS(distribution)
    tuple_dic = {"unique0":((0,),),"unique1":((1,),),"reduandence":((0,), (1,)),"synergistic":((0, 1),)}
    unique0 = I_ccs.get_partial(node=tuple_dic["unique0"])
    unique1 = I_ccs.get_partial(node=tuple_dic["unique1"])
    redundance = I_ccs.get_partial(node=tuple_dic["reduandence"])
    synergy = I_ccs.get_partial(node=tuple_dic["synergistic"])

    return unique0, unique1, redundance, synergy

def I_Dep(distribution:dit.Distribution):
    '''
    information decomposition of I_Dep (three variables) [Unique information via dependency constraints]
    
    only can calculate the information pass from the first two variables to the third one 


    Parameters:
    ---
    distribution: the distribution

    Return
    ---
    unique0: unique information 0->2
    unique1: unique information 1->2
    redundance: redundant information 0,1->2
    synergy: synergistic information 0,1->2
    '''
    I_dep = PID_dep(distribution)
    tuple_dic = {"unique0":((0,),),"unique1":((1,),),"reduandence":((0,), (1,)),"synergistic":((0, 1),)}
    unique0 = I_dep.get_partial(node=tuple_dic["unique0"])
    unique1 = I_dep.get_partial(node=tuple_dic["unique1"])
    redundance = I_dep.get_partial(node=tuple_dic["reduandence"])
    synergy = I_dep.get_partial(node=tuple_dic["synergistic"])

    return unique0, unique1, redundance, synergy


def I_PM(distribution:dit.Distribution):
    '''
    information decomposition of I_Dep (three variables) [Pointwise partial information decomposition using the specificity and ambiguity lattices]
    
    only can calculate the information pass from the first two variables to the third one 


    Parameters:
    ---
    distribution: the distribution

    Return
    ---
    unique0: unique information 0->2
    unique1: unique information 1->2
    redundance: redundant information 0,1->2
    synergy: synergistic information 0,1->2
    '''
    I_pm = PID_PM(distribution)
    tuple_dic = {"unique0":((0,),),"unique1":((1,),),"reduandence":((0,), (1,)),"synergistic":((0, 1),)}
    unique0 = I_pm.get_partial(node=tuple_dic["unique0"])
    unique1 = I_pm.get_partial(node=tuple_dic["unique1"])
    redundance = I_pm.get_partial(node=tuple_dic["reduandence"])
    synergy = I_pm.get_partial(node=tuple_dic["synergistic"])

    return unique0, unique1, redundance, synergy

def I_Rav(distribution:dit.Distribution):
    '''
    information decomposition of I_rav (three variables) 
    
    only can calculate the information pass from the first two variables to the third one 


    Parameters:
    ---
    distribution: the distribution

    Return
    ---
    unique0: unique information 0->2
    unique1: unique information 1->2
    redundance: redundant information 0,1->2
    synergy: synergistic information 0,1->2
    '''
    I_rav = PID_RAV(distribution)
    tuple_dic = {"unique0":((0,),),"unique1":((1,),),"reduandence":((0,), (1,)),"synergistic":((0, 1),)}
    unique0 = I_rav.get_partial(node=tuple_dic["unique0"])
    unique1 = I_rav.get_partial(node=tuple_dic["unique1"])
    redundance = I_rav.get_partial(node=tuple_dic["reduandence"])
    synergy = I_rav.get_partial(node=tuple_dic["synergistic"])

    return unique0, unique1, redundance, synergy



def I_RR(distribution:dit.Distribution):
    '''
    information decomposition of I_RR (three variables) [Temporal information partitioning: Characterizing synergy, uniqueness, and redundancy in interacting environmental variables]
    
    only can calculate the information pass from the first two variables to the third one 


    Parameters:
    ---
    distribution: the distribution

    Return
    ---
    unique0: unique information 0->2
    unique1: unique information 1->2
    redundance: redundant information 0,1->2
    synergy: synergistic information 0,1->2
    '''
    I_rr = PID_RR(distribution)
    tuple_dic = {"unique0":((0,),),"unique1":((1,),),"reduandence":((0,), (1,)),"synergistic":((0, 1),)}
    unique0 = I_rr.get_partial(node=tuple_dic["unique0"])
    unique1 = I_rr.get_partial(node=tuple_dic["unique1"])
    redundance = I_rr.get_partial(node=tuple_dic["reduandence"])
    synergy = I_rr.get_partial(node=tuple_dic["synergistic"])

    return unique0, unique1, redundance, synergy


def I_RA(distribution:dit.Distribution):
    '''
    information decomposition of I_RA (three variables) [An overview of reconstructability analysis]
    
    only can calculate the information pass from the first two variables to the third one 


    Parameters:
    ---
    distribution: the distribution

    Return
    ---
    unique0: unique information 0->2
    unique1: unique information 1->2
    redundance: redundant information 0,1->2
    synergy: synergistic information 0,1->2
    '''
    I_ra = PID_RA(distribution)
    tuple_dic = {"unique0":((0,),),"unique1":((1,),),"reduandence":((0,), (1,)),"synergistic":((0, 1),)}
    unique0 = I_ra.get_partial(node=tuple_dic["unique0"])
    unique1 = I_ra.get_partial(node=tuple_dic["unique1"])
    redundance = I_ra.get_partial(node=tuple_dic["reduandence"])
    synergy = I_ra.get_partial(node=tuple_dic["synergistic"])

    return unique0, unique1, redundance, synergy





def defined_influence_at(influence:np.ndarray, x:int, z:int, adjacent_matrix, start_point, stop_point):
    '''
    calculate the average influence x gives to z (for pairwise interaction)

    stationary threshold which should be consist with the count_distribution_adjacent() function
    '''
    if np.sum(adjacent_matrix[z,x,start_point:stop_point]) == 0:
        influence_xz = 0
    else:
        influence_xz = np.sum(np.abs(influence[z,x,start_point:stop_point],dtype=np.float64)/np.sum(adjacent_matrix[z,x,start_point:stop_point],dtype=np.float64), dtype=np.float64)

    
    return influence_xz

def defined_influence_ta(influence:np.ndarray, x:int, z:int, adjacent_matrix, start_point, stop_point):
    '''
    calculate the average influence x gives to z (for pairwise interaction)

    stationary threshold which should be consist with the count_distribution_adjacent() function
    '''

    if np.sum(adjacent_matrix[z,x,start_point:stop_point]) == 0:
        influence_xz = 0
    else:
        influence_xz=np.abs(np.sum(influence[z,x,start_point:stop_point]/np.sum(adjacent_matrix[z,x,start_point:stop_point], dtype=np.float64),dtype=np.float64))
    
    return influence_xz