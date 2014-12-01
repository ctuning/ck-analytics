#
# Collective Knowledge (Universal Experiment)
#
# See CK LICENSE.txt for licensing details
# See CK Copyright.txt for copyright details
#
# Developer: Grigori Fursin
#

cfg={}  # Will be updated by CK (meta description of this module)
work={} # Will be updated by CK (temporal data)
ck=None # Will be updated by CK (initialized CK kernel) 

# Local settings
import os

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
# adding and processing experiment

def add(i):
    """

    Input:  {
              dict                       - format prepared for predictive analytics
                                           {
                                             "meta"            - coarse grain meta information to distinct entries (species)
                                             ("choices")       - choices (for example, optimizations)
                                             "features"        - species features (mostly unchanged)
                                             "characteristics" - species characteristics (measured)
                                           }

              (experiment_repo_uoa)      - if defined, use it instead of repo_uoa
                                           (useful for remote repositories)
              (remote_repo_uoa)          - if remote access, use this as a remote repo UOA
              (experiment_uoa)           - if entry with aggregated experiments is already known
              (experiment_uid)           - if entry with aggregated experiments is already known
              (add_new)                  - if 'yes', do not search for existing entry,
                                           but add a new one!

              (search_point_by_features) - if 'yes', add point

              (ignore_update)            - if 'yes', do not record update control info (date, user, etc)

              (sort_keys)                - if 'yes', sort keys in output json
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import time
    start_time = time.time()

    o=i.get('out','')

    dd=i.get('dict',{})

    ft=dd.get('features',{})

    if len(dd)==0:
       return {'return':1, 'error':'no data provided'}

    an=i.get('add_new','')
    euoa=i.get('experiment_uoa','')
    euid=i.get('experiment_uid','')

    sk=i.get('sort_keys','')

    ruoa=i.get('repo_uoa','')
    xruoa=i.get('experiment_repo_uoa','')
    if xruoa!='': ruoa=xruoa

    rruoa=i.get('remote_repo_uoa','')

    spbf=i.get('search_point_by_features','')
    dpoint={}
    point=0

    # Search for an entry to aggregate, if needed
    lock_uid=''
    if an!='yes' and (euoa=='' and euid==''):
       if o=='con':
          ck.out('Searching species in the repository with given meta info ...')
          ck.out('')

       meta=dd.get('meta',{})
       if len(meta)==0:
          return {'return':1, 'error':'meta is not defined - can\'t aggregate'}

       ii={'action':'search',
           'common_func':'yes',
           'repo_uoa': ruoa,
           'remote_repo_uoa': rruoa,
           'module_uoa': work['self_module_uoa'],
           'search_dict':{'meta':meta}}
       r=ck.access(ii)
       if r['return']>0: return r

       lst=r['lst']
       if len(lst)>1:
          return {'return':1, 'error':'more than one meta was returned - ambiguity'}

       if len(lst)==1:
          euoa=lst[0]['data_uoa']
          euid=lst[0]['data_uid']

          if o=='con': 
             ck.out('  Species was found: '+euoa+' ('+euid+') ...')

    # If not found, add entry
    if an=='yes' or (euoa=='' and euid==''):
       if o=='con':
          ck.out('  Species was not found. Adding new entry ...')

       ii={'action':'add',
           'common_func':'yes',
           'repo_uoa': ruoa,
           'remote_repo_uoa': rruoa,
           'module_uoa': work['self_module_uoa'],
           'dict':dd}
       r=ck.access(ii)
       if r['return']>0: return r
       euoa=r['data_uoa']
       euid=r['data_uid']

    # Load and lock
    if o=='con': 
       ck.out('  Loading and locking entry ('+euoa+') ...')

    # Loading species
    ii={'action':'load',
        'common_func':'yes',
        'repo_uoa': ruoa,
        'remote_repo_uoa': rruoa,
        'module_uoa': work['self_module_uoa'],
        'data_uoa':euid,
        'get_lock':'yes'
        }
    r=ck.access(ii)
    if r['return']>0: return r

    p=r['path']
    dde=r['dict']
    lock_uid=r['lock_uid']
    ipoints=int(dde.get('points','0'))

    if o=='con': 
       ck.out('  Loaded and locked successfully (lock UID='+lock_uid+') ...')

    # If species found, check if search point by feature
    if euid!='' and spbf=='yes':
       if len(ft)==0:
          return {'return':1, 'error':'can\'t search by features when they are not present'}

       if o=='con': ck.out('    Searching points by features ...')

       for q in range(1, ipoints+1):
           sp=str(q)
#              ck.out('   Checking q='+sp+' ...')
           fp=sp.zfill(8)+'.json'
           pfp=os.path.join(p,fp)

           r=ck.load_json_file({'json_file':pfp})
           if r['return']>0: return r

           dpoint=r['dict']
           ft1=dpoint.get('features',{})

           r=ck.compare_dicts({'dict1':ft1, 'dict2':ft})
           if r['return']>0: return r

           if r['equal']=='yes': 
              point=q
              if o=='con':
                 ck.out('      Found point by features: '+str(q))
              break

    # Adding new point (if not found by features)
    if point==0:
       ipoints+=1
       sp=str(ipoints)
       spz=sp.zfill(8)
       fp=spz+'.json'
       fp1=os.path.join(p, fp)

       fpflat=spz+'.flat.json'
       fpflat1=os.path.join(p, fpflat)

       if o=='con': 
          ck.out('  Saving point '+sp+' ...')

       r=ck.save_json_to_file({'json_file':fp1, 'dict':dd, 'sort_keys':sk})
       if r['return']>0: return r

       # Flatten dictionary
       r=ck.flatten_dict({'dict':dd})
       if r['return']>0: return r

       ddf=r['dict']
       r=ck.save_json_to_file({'json_file':fpflat1, 'dict':ddf, 'sort_keys':sk})
       if r['return']>0: return r

       dd['points']=sp

    # Adding/updating entry
    if o=='con': 
       ck.out('  Updating entry and unlocking ...')

    ii={'action':'update',
        'common_func':'yes',
        'repo_uoa': ruoa,
        'remote_repo_uoa': rruoa,
        'module_uoa': work['self_module_uoa'],
        'data_uoa':euid,
        'dict':dd,
        'ignore_update':i.get('ignore_update',''),
        'sort_keys':sk,
        'unlock_uid':lock_uid
       }
    r=ck.access(ii)

    et=time.time() - start_time
    r['elapsed_time'] = str(et)

    return r

##############################################################################
# plot universal graph by flat dimensions

def plot(i):
    """

    Input:  {
              (repo_uoa) or (experiment_repo_uoa)   - can be wild cards
              (module_uoa)                          - can be wild cards
              (data_uoa)                            - can be wild cards

              (repo_uoa_list)      - list of repos to search
              (module_uoa_list)    - list of module to search
              (data_uoa_list)      - list of data to search

              (search_dict)        - search dict
              (ignore_case)        - if 'yes', ignore case when searching

              (font)               - dict with font params ({family, weight, size})

              (flat_keys_list)                      - list of flat keys to extract from points into table
                                                      (order is important: for example, for plot -> X,Y,Z)
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """


    o=i.get('out','')

    rruoa=i.get('remote_repo_uoa','')

    # Get table
    r=get(i)
    if r['return']>0: return r
    table=r['table']

    if len(table)==0:
       return {'return':1, 'error':'no points found'}

    # Prepare libraries
#    import numpy as np
    import matplotlib as mpl

    if ck.cfg.get('use_internal_engine_for_plotting','')=='yes':
       mpl.use('Agg') # if XWindows is not installed, use internal engine

    import matplotlib.pyplot as plt

    # Set font
    font=i.get('font',{})
    if len(font)==0:
       font = {'family':'arial', 
               'weight':'normal', 
               'size': 10}

    plt.rc('font', **font)

    # Configure graph
    gs=cfg['mpl_point_styles']

    sizex=i.get('mpl_image_size_x','')
    if sizex=='': sizex='9'

    sizey=i.get('mpl_image_size_y','')
    if sizey=='': sizey='5'

    dpi=i.get('mpl_image_dpi','')
    if dpi=='': dpi='100'

    if sizex!='' and sizey!='' and dpi!='':
       fig=plt.figure(figsize=(int(sizex),int(sizey)))
    else:
       fig=plt.figure()

    if i.get('plot_grid','')=='yes':
       plt.grid(True)

    sp=fig.add_subplot(111)
#    sp.set_yscale('log')

    xmin=i.get('xmin','')
    xmax=i.get('xmax','')
    ymin=i.get('ymin','')
    ymax=i.get('ymax','')

    if xmin!='' and xmax!='':
       sp.set_xlim(float(xmin), float(xmax))
    if ymin!='' and ymax!='':
       sp.set_ylim(float(ymin), float(ymax))

    # Add points
    s=0
    for g in table:
        gt=table[g]

        mx=[]
        my=[]

        for u in gt:
            mx.append(u[0])
            my.append(u[1])

        sp.scatter(mx, my, s=int(gs[s]['size']), edgecolor=gs[s]['color'], c=gs[s]['color'], marker=gs[s]['marker'])
        s+=1
        if s>=len(gs):s=0

    # Set axes names
    axd=i.get('axis_x_desc','')
    if axd!='': plt.xlabel(axd)

    ayd=i.get('axis_y_desc','')
    if ayd!='': plt.ylabel(ayd)

    atitle=i.get('title','')
    if atitle!='': plt.title(atitle)

    plt.show()

    return {'return':0}

##############################################################################
# get points from multiple entries

def get(i):
    """

    Input:  {
              (repo_uoa) or (experiment_repo_uoa)   - can be wild cards
              (remote_repo_uoa)                     - if remote access, use this as a remote repo UOA
              (module_uoa)                          - can be wild cards
              (data_uoa)                            - can be wild cards

              (repo_uoa_list)                       - list of repos to search
              (module_uoa_list)                     - list of module to search
              (data_uoa_list)                       - list of data to search

              (search_dict)                         - search dict
              (ignore_case)                         - if 'yes', ignore case when searching

              (flat_keys_list)                      - list of flat keys to extract from points into table
                                                      (order is important: for example, for plot -> X,Y,Z)
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              table        - First dimension is for different graphs on one plot
                             Second dimension: list of values for 
            }

    """

    o=i.get('out','')

    ruoa=i.get('repo_uoa','')
    xruoa=i.get('experiment_repo_uoa','')
    if xruoa!='': ruoa=xruoa

    rruoa=i.get('remote_repo_uoa','')

    muoa=i.get('module_uoa','')
    duoa=i.get('data_uoa','')

    ruoal=i.get('repo_uoa_list',[])
    muoal=i.get('module_uoa_list',[])
    duoal=i.get('data_uoa_list',[])

    sd=i.get('search_dict',{})
    ic=i.get('ignore_case','')

    fkl=i.get('flat_keys_list',[])

    # Search entries
    ii={'action':'search',
        'common_func':'yes',
        'repo_uoa':ruoa,
        'remote_repo_uoa': rruoa,
        'module_uoa':muoa,
        'data_uoa':duoa,
        'repo_uoa_list':ruoal,
        'module_uoa_list':muoal,
        'data_uoa_list':duoal,
        'search_dict':sd,
        'ignore_case':ic}
    r=ck.access(ii)
    if r['return']>0: return r

    lst=r['lst']

    table={}
    igraph=0
    sigraph=str(igraph)

    # Iterate over entries
    for e in lst:
        ruid=e['repo_uid']
        muoa=e['module_uoa']
        muid=e['module_uid']
        duoa=e['data_uoa']
        duid=e['data_uid']

        # Load entry
        if o=='con':
           ck.out('Loading entry '+muoa+':'+duoa+' ...')

        ii={'action':'load',
            'repo_uoa':ruid,
            'module_uoa':muid,
            'data_uoa':duid}
        r=ck.access(ii)
        if r['return']>0: return r

        p=r['path']
        dd=r['dict']
        ipoints=int(dd.get('points','0'))

        for ip in range(1, ipoints+1):
            sp=str(ip)
            spz=sp.zfill(8)
            fpflat=spz+'.flat.json'
            fpflat1=os.path.join(p, fpflat)

            r=ck.load_json_file({'json_file':fpflat1})
            if r['return']>0: return r
            df=r['dict']

            # Create final vector (X,Y,Z,...)
            vect=[]
            if len(fkl)==0:
               # Add all sorted (otherwise there is no order in python dict
               for k in sorted(df.keys()):
                   v=df[k]
                   vect.append(v)
            else:
               for k in fkl:
                   v=float(df.get(k,'')) # TBD
                   vect.append(v)

            # Add vector
            if sigraph not in table: table[sigraph]=[]

            table[sigraph].append(vect)

    # If sort
#    for sg in table:
#        x=table[sg]
#        y=sorted(x, key=which_key)
#        table[sg]=y

    return {'return':0, 'table':table}

#def which_key(d):
#    return d[0]
