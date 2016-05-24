#
# Collective Knowledge (analysis of variation of experimental results)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://fursin.net
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

              (cov_factor)          - float covariance factor (0.5 by default)

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

    import copy

    has_deps=True
    try:
       from scipy.stats import gaussian_kde
       from scipy.signal import argrelextrema
       import numpy as np
    except Exception as e: 
       has_deps=False
       if i.get('skip_fail','')!='yes':
          return {'return':1, 'error':'Seems that some scientific python modules are not installed ('+format(e)+')'}

    ctable1=i['characteristics_table']
    ctable=copy.deepcopy(ctable1) # since slightly changing it ...

    dmin=i.get('min',-1)
    dmax=i.get('max',-1)

    xlist=[]
    ylist=[]

    xlist2=[]
    ylist2=[]

    xlist2s=[]
    ylist2s=[]


    dmin=i.get('min',-1.0)
    dmax=i.get('max',-1.0)

    if has_deps:
       if len(ctable)>0:
          xlistx=[]
          if len(ctable)>1:
             bins=i.get('bins','')
             if bins=='': bins=100
             bins=int(bins)

             if dmin==dmax:
                dmin=min(ctable)
                dmax=max(ctable)

             cf=i.get('cov_factor','')
             if cf=='': cf=0.5
             cf=float(cf)

             ctable.insert(0,0.0)
             ctable.append(0.0)

             try:
                density = gaussian_kde(ctable)
                xlist = np.linspace(dmin,dmax,bins)

                if cf!=-1 and cf!='':
                   density.covariance_factor = lambda:cf
                   density._compute_covariance()

                ylist=density(xlist)

                ylist5=[0.0]
                for q in ylist:
                    ylist5.append(q)
                ylist5.append(0.0)

                ylist6=np.array(ylist5)

                xlistx=argrelextrema(ylist6, np.greater)[0] # np.less for local minima

                xlistxx=[]
                for q in xlistx:
                    xlistxx.append(q-1)

                xlistx=xlistxx

             except Exception as e:
                x=format(e)
                if x.find('singular matrix')<0:
                   ck.out('CK warning: '+x+' in analyze math.variation ...')
                pass

          else:
             xlist=[ctable[0]]
             ylist=[100.0]
             xlistx=[0]

          # Convert from numpy to float
          for q in range(0, len(xlist)):
              xlist[q]=float(xlist[q])
              ylist[q]=float(ylist[q])

          if len(xlistx)>0:
             for q in xlistx:
                 xlist2.append(float(xlist[q]))
                 ylist2.append(float(ylist[q]))

             ylist2s, xlist2s = (list(t) for t in zip(*sorted(zip(ylist2, xlist2),reverse=True)))

    return {'return':0, 'xlist':xlist, 'ylist':ylist, 
                        'xlist2':xlist2, 'ylist2':ylist2,
                        'xlist2s':xlist2s, 'ylist2s':ylist2s}

##############################################################################
# analyze speedup (prepared by Anton Lokhmotov)

def speedup(i):
    """
    Input:  {
              samples1 - list of original empirical results
              samples2 - list of new empirical results (lower than original is better)
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    s1=i['samples1']
    s2=i['samples2']

    s1min=min(s1)
    s1max=max(s1)

    s2min=min(s2)
    s2max=max(s2)

    s1mean=float(sum(s1))/len(s1)
    s2mean=float(sum(s2))/len(s2)

    # naive speedups
    ns1=s1mean/s2mean
    ns2=s1min/s2min

    # perform statistical analysis, if available
#    import pandas as pd




    rr={'return':0, 's1min':s1min, 's1max':s1max,
                    's2min':s2min, 's2max':s2max,
                    's1mean':s1mean, 's2mean': s2mean,
                    'naive_speedup':ns1, 
                    'naive_speedup_min':ns2}

    return rr
