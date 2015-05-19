#
# Collective Knowledge (detect frontier for multi-objective optimizations (such as execution time vs energy vs code size vs faults vs price ...))
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
# Filter frontier (leave only best points) - my own greedy and probably not very optimal algorithm
#
# TBD: should leave only a few points otherwise can be quickly too many 
#  particularly if more than 2 dimensions (performance, energy, size, faults)
#
# Note, that we minimize all dimensions. Otherwise, provide reversed dimension.
#
# HELP IS APPRECIATED!

def filter(i):
    """
    Input:  {
              points    - dict with points, each has dict with optimization dimensions (should have the same names)
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              points       - filtered points!
            }

    """

    oo=i.get('out','')

    points=i['points']
    lp=len(points)

    uids=list(points.keys())

    if oo=='con':
       ck.out('Original number of points: '+str(lp))

    if lp>1:
       for l0 in range(0,lp,1):
           ul0=uids[l0]
           if ul0!='':
              p0=points[ul0]
              # Check if at least one dimension is better than all other points!
              keep=False
              for d0 in p0:
                  v0=p0[d0]
                  better=True
                  if v0!=None and v0!='':
                     v0=float(v0)
                     for l1 in range(0,lp,1):
                         ul1=uids[l1]
                         if ul1!='':
                            p1=points[ul1]
                            v1=p1.get(d0,None)
                            if v1!=None and v1!='':
                               v1=float(v1)
                               if v0>v1:
                                  better=False
                                  break
                  if better:
                     keep=True
                     break

              if not keep:
                 del(points[ul0])
                 uids[l0]=''

    lp=len(points)
    if oo=='con':
       ck.out('Final number of points: '+str(lp))

    return {'return':0, 'points':points}
