#
# Collective Knowledge (analysis of variation of experimental results)
#
# See CK LICENSE.txt for licensing details
# See CK Copyright.txt for copyright details
#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://cTuning.org/lab/people/gfursin
#

cfg={}  # Will be updated by CK (meta description of this module)
work={} # Will be updated by CK (temporal data)
ck=None # Will be updated by CK (initialized CK kernel) 

# Local settings

##############################################################################
# Initialize module

def init(i):
    """

    Input:  {}

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """
    return {'return':0}

##############################################################################
# analyze variation of experimental results

def analyze(i):
    """
    Input:  {
              characteristics_table - characteristics table (list)

              (bins)                - number of bins (int, default = 100)

              (min)                 - min float value (if multiple ctables are processed)
              (max)                 - max float value (if multiple ctables are processed)

              (cov_factor)          - float covariance factor
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              (xlist)      - list of x values
              (ylist)      - list of y values (density)

            }

    """

    from scipy.stats import gaussian_kde
    from scipy.signal import argrelextrema
    import numpy as np

    ctable=i['characteristics_table']

    bins=i.get('bins',-1)
    if bins==-1: bins=100

    dmin=i.get('min',-1)
    dmax=i.get('max',-1)

    if dmin==-1: dmin=min(ctable)
    if dmax==-1: dmax=max(ctable)

    cf=i.get('cov_factor',-1)

    density = gaussian_kde(ctable)
    xlist = np.linspace(dmin,dmax,bins)

    if cf!=-1:
       density.covariance_factor = lambda:cf
       density._compute_covariance()

    ylist=density(xlist)

    # Get picks (expectations + features)
    xlistx=argrelextrema(ylist, np.greater)[0] # np.less for local minima

    xlist2=[]
    ylist2=[]
    for q in xlistx:
        xlist2.append(xlist[q])
        ylist2.append(ylist[q])

    return {'return':0, 'xlist':xlist, 'ylist':ylist, 'xlist2':xlist2, 'ylist2':ylist2}
