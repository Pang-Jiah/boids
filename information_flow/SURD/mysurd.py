import numpy as np


def create_pfm( s, a, dt, bins ):
    '''compute the joint PMF of variables
        
        pfm = create_pfm( s, a, dt )
    Parameters
        s:      [np.ndarray]
            temporal evolution of target variable [size (Nt,)]
        a:      [ tuple ]
            each element must be an np.ndarray of size (Nt,)
            with the temporal evolution of agent variables
        dt:     [int]
            time lag in number of time steps
        bins:     [int]
            number of bins (states) per dimension
    Returns
        pfm     [np.ndarray]
            Mass probability function ( size ( bins, ..., bins ), dim = 1 + len(a) )
    
    '''
    V = np.vstack([ s[:-dt], [ a[i][:-dt] for i in range(len(a)) ] ]).T
    
    # Histogram computes the bins by equally splitting the interval max(var)-min(var)
    h, _ = np.histogramdd( V, bins=bins )
    return h/h.sum()

def create_pfm_specific_bins( s, a, dt, bins):
    '''compute the joint PMF of variables
        
        pfm = create_pfm( s, a, dt )
    Parameters
        s:      [np.ndarray]
            temporal evolution of target variable [size (Nt,)]
        a:      [ tuple ]
            each element must be an np.ndarray of size (Nt,)
            with the temporal evolution of agent variables
        dt:     [int]
            time lag in number of time steps
        bins:     [int] or [List{list{int}}]
            number of bins (states) per dimension or list of boundarys
    Returns
        pfm     [np.ndarray]
            Mass probability function ( size ( bins, ..., bins ), dim = 1 + len(a) )
    
    '''
    V = np.vstack([ s[:-dt], [ a[i][:-dt] for i in range(len(a)) ] ]).T
    
    # Histogram computes the bins by equally splitting the interval max(var)-min(var)
    h, _ = np.histogramdd( V, bins=bins )

    return h/h.sum()



def obtain_DI_twoSources( r_, s_, mi_, leak_ ):
    '''
    obtain the decomposed information (for 3 variable cases, one target, two sources)
    
    '''

    #print( ' Redundant (R):' )
    for k_, v_ in r_.items():
        if k_ == (1, 2):
            redundant = v_

    #print( ' Unique (U):' )
    for k_, v_ in r_.items():
        if k_ == (1, ):
            unique1 = v_
        elif k_ == (2, ):
            unique2 = v_

    #print( ' Synergystic (S):' )
    for k_, v_ in s_.items():
        synergistic = v_
    
    information_leak = leak_ * 100

    return redundant, unique1, unique2, synergistic, information_leak


def obtain_NDI_twoSources( r_, s_, mi_, leak_ ):
    '''
    obtain the normalized decomposed information (for 3 variable cases, one target, two sources)
    
    '''
    
    r_ = {key: value / max(mi_.values()) for key, value in r_.items()}
    s_ = {key: value / max(mi_.values()) for key, value in s_.items()}

    #print( ' Redundant (R):' )
    for k_, v_ in r_.items():
        if k_ == (1, 2):
            redundant = v_

    #print( ' Unique (U):' )
    for k_, v_ in r_.items():
        if k_ == (1, ):
            unique1 = v_
        elif k_ == (2, ):
            unique2 = v_

    #print( ' Synergystic (S):' )
    for k_, v_ in s_.items():
        synergistic = v_
    
    information_leak = leak_ * 100

    return redundant, unique1, unique2, synergistic, information_leak



def obtain_DI_HD( s_, mi_,  ):
    '''
    obtain the synergistic information (for cases with variables more than 3)
    
    '''
    longest_key = max(s_, key=lambda k: len(k))
    print(longest_key)
    synergistic_of_all = s_[longest_key]

    s_ = {key: value / max(mi_.values()) for key, value in s_.items()}
    #print( ' Redundant (R):' )
    
   
    #print( ' Synergystic (S):' )
    
    nsynergistic_of_all = s_[longest_key]
    
    return  synergistic_of_all, nsynergistic_of_all

