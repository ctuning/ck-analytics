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

              (skip_fail)           - if 'yes', do not fail, if SciPy and NumPy
                                      are not available
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              min        - min X values from input or calculated
              max        - max X values from input or calculated  

              xlist      - list of x values
              ylist      - list of y density values 

              xlist2     - list of x values with peaks
              ylist2     - list of y density values with peaks

              xlist2s    - list of sorted x values with peaks (max y -> hence 1st expected value)
              ylist2s    - list of sorted y density values with peaks
            }

    """

    has_deps=True
    try:
       from scipy.stats import gaussian_kde
       from scipy.signal import argrelextrema
       import numpy as np
    except Exception as e: 
       has_deps=False
       if i.get('skip_fail','')!='yes':
          return {'return':1, 'error':'Seems like some python math modules are not installed ('+format(e)+')'}

    ctable=i['characteristics_table']

    dmin=i.get('min',-1)
    dmax=i.get('max',-1)

    xlist=[]
    ylist=[]

    xlist2=[]
    ylist2=[]

    xlist2s=[]
    ylist2s=[]

    if has_deps:
       if len(ctable)>0:
          xlistx=[]
          if len(ctable)>1:
             bins=i.get('bins',100)

             if dmin==-1: dmin=min(ctable)
             if dmax==-1: dmax=max(ctable)

             cf=i.get('cov_factor',-1)

             try:
                density = gaussian_kde(ctable)
                xlist = np.linspace(dmin,dmax,bins)

                if cf!=-1:
                   density.covariance_factor = lambda:cf
                   density._compute_covariance()

                ylist=density(xlist)

                xlistx=argrelextrema(ylist, np.greater)[0] # np.less for local minima
             except Exception as e:
                pass

          else:
             xlist=[ctable[0]]
             ylist=[100.0]
             xlistx=[0]

          if len(xlistx)>0:
             for q in xlistx:
                 xlist2.append(xlist[q])
                 ylist2.append(ylist[q])

             ylist2s, xlist2s = (list(t) for t in zip(*sorted(zip(ylist2, xlist2),reverse=True)))

    return {'return':0, 'xlist':xlist, 'ylist':ylist, 
                        'xlist2':xlist2, 'ylist2':ylist2,
                        'xlist2s':xlist2s, 'ylist2s':ylist2s}
