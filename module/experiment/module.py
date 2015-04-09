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
              dict                          - format prepared for predictive analytics
                                              {
                                                "meta"            - coarse grain meta information to distinct entries (species)
                                                ("choices")       - choices (for example, optimizations)
                                                ("features")      - species features (mostly unchanged)
                                                "characteristics" - species characteristics (measured)
                                              }

              (experiment_repo_uoa)         - if defined, use it instead of repo_uoa
                                              (useful for remote repositories)
              (remote_repo_uoa)             - if remote access, use this as a remote repo UOA

              (experiment_uoa)              - if entry with aggregated experiments is already known
              (experiment_uid)              - if entry with aggregated experiments is already known

              (force_new_entry)             - if 'yes', do not search for existing entry,
                                              but add a new one!

              (search_point_by_features)    - if 'yes', add point

              (ignore_update)               - if 'yes', do not record update control info (date, user, etc)

              (sort_keys)                   - if 'yes', sort keys in output json

              (skip_flatten)                - if 'yes', skip flattinging and analyzing data ...

              (process_multi_keys)          - list of keys (starts with) to perform stat analysis on flat array,
                                              by default ['characteristics', 'features'],
                                              if empty, no stat analysis

              (record_all_subpoints)        - if 'yes', record all subpoints
              (max_range_percent_threshold) - (float) if set, record all subpoints where max_range_percent exceeds this threshold
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

    meta=dd.get('meta',{})
    ft=dd.get('features',{})

    if len(dd)==0:
       return {'return':1, 'error':'no data provided ("dict" key is empty)'}

    an=i.get('force_new_entry','')

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

    ras=i.get('record_all_subpoints','')

    # Search for an entry to aggregate, if needed
    lock_uid=''
    lst=[]
    if an!='yes' and (euoa=='' and euid==''):
       if o=='con':
          ck.out('Searching existing experiments in the repository with given meta info ...')
          ck.out('')

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
          x=''
          for q in lst:
              if x!='': x+=', '
              x+=q['data_uoa']
          return {'return':1, 'error':'more than one meta was returned ('+x+') - ambiguity'}

       if len(lst)==1:
          euoa=lst[0]['data_uoa']
          euid=lst[0]['data_uid']

          if o=='con': 
             ck.out('  Existing experiment was found: '+euoa+' ('+euid+') ...')

    # If not found, add dummy entry
    if an=='yes' or len(lst)==0:
       ii={'common_func':'yes',
           'repo_uoa': ruoa,
           'remote_repo_uoa': rruoa,
           'data_uoa':euoa,
           'data_uid':euid,
           'module_uoa': work['self_module_uoa'],
           'dict':{}}

       if euoa=='' and euid=='':
          ii['action']='add'
          x='  Existing experiments were not found. Adding new entry ...'
       else:
          ii['action']='update'
          x='  Updating entry ...'

       if o=='con': ck.out(x)

       r=ck.access(ii)
       if r['return']>0: return r
       euoa=r['data_uoa']
       euid=r['data_uid']

    # Load and lock
    if o=='con': 
       ck.out('  Loading and locking entry ('+euoa+') ...')

    # Loading existing experiment
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

    # If existing experiment found, check if search point by feature
    ddft={'features':ft}
    fpoint=''
    if euid!='' and spbf=='yes':
       if len(ft)==0:
          return {'return':1, 'error':'can\'t search by features when they are not present'}

       if o=='con': ck.out('    Searching points by features ...')

       dirList=os.listdir(p)
       for fn in dirList:
           if fn.endswith('.features.json'):
              pfp=os.path.join(p, fn)

              r=ck.load_json_file({'json_file':pfp})
              if r['return']>0: return r
              ft1=r['dict']

              r=ck.compare_dicts({'dict1':ft1.get('features',{}), 'dict2':ft})
              if r['return']>0: return r

              if r['equal']=='yes': 
                 fpoint=fn[:-14]
                 ddft=ft1

                 if o=='con': ck.out('      Found point by features: '+str(fpoint))

                 break

    # Add information about user
    ri=ck.prepare_special_info_about_entry({})
    if ri['return']>0: return ri
    dsi=ri['dict']

    if len(dde.get('added',{}))==0:
       dde['added']=dsi
    if len(dde.get('meta',{}))==0:
       dde['meta']=meta
    if len(dd.get('tags',[]))!=0:
       dde['tags']=dd['tags']

    # Prepare new point (if not found by features)
    if fpoint=='':
       ipoints+=1

       rx=ck.gen_uid({})
       if rx['return']>0: return rx
       uid=rx['data_uid']
 
       fpoint='ckp-'+uid

       dde['points']=str(ipoints)

       if o=='con': ck.out('  Prepared new point '+uid+' ...')

    # Check if need to flat and basic perform analysis
    mdpt=i.get('max_range_percent_threshold',-1)
    mmin=''
    mmax=''

    if i.get('skip_flatten','')!='yes':
       # Flatten data and perform basic analysis **********************************
       r=ck.flatten_dict({'dict':dd})
       if r['return']>0: return r
       ddf=r['dict']

       # Load flattened data
       fpflat=fpoint+'.flat.json'
       fpflat1=os.path.join(p, fpflat)

       ddflat={}
       if os.path.isfile(fpflat1):
          r=ck.load_json_file({'json_file':fpflat1})
          if r['return']>0: return r
          ddflat=r['dict']

       # Process multiple points
       sak=i.get('process_multi_keys',['characteristics', 'features'])

       r=process_multi({'dict':ddflat, 'dict1':ddf, 'process_multi_keys':sak})
       if r['return']>0: return r
       ddflat=r['dict']
       mdp=r['max_range_percent']
       mmin=r['min']
       mmax=r['max']

    # Check if record all points or only with max_range_percent > max_range_percent_threshold
    sp=ddft.get('sub_points',0)
    if sp==0 or ras=='yes' or ((mdpt!=-1 and mdp>mdpt) or mmin=='yes' or mmax=='yes'):
       sp+=1
       if sp>9999:
          return {'return':1, 'error':'max number of subpoints is reached (9999)'}

       if o=='con': ck.out('      Next subpoint: '+str(sp))

       ddft['sub_points']=sp
       ssp='.'+str(sp).zfill(4)

       fssp=fpoint+ssp+'.json'
       fssp1=os.path.join(p, fssp)

       # Save subpoint dict to file
       r=ck.save_json_to_file({'json_file':fssp1, 'dict':dd, 'sort_keys':sk})
       if r['return']>0: return r

    # Save features file (that include subpoint)
    pfp=os.path.join(p, fpoint)+'.features.json'
    r=ck.save_json_to_file({'json_file':pfp, 'dict':ddft, 'sort_keys':sk})
    if r['return']>0: return r

    # Save updated flat dict to file
    if i.get('skip_flatten','')!='yes':
       r=ck.save_json_to_file({'json_file':fpflat1, 'dict':ddflat, 'sort_keys':sk})
       if r['return']>0: return r

    # Adding/updating entry *****************************************************
    if o=='con': 
       ck.out('  Updating entry and unlocking ...')

    ii={'action':'update',
        'common_func':'yes',
        'repo_uoa': ruoa,
        'remote_repo_uoa': rruoa,
        'module_uoa': work['self_module_uoa'],
        'data_uoa':euid,
        'dict':dde,
        'ignore_update':i.get('ignore_update',''),
        'sort_keys':sk,
        'unlock_uid':lock_uid
       }
    r=ck.access(ii)

    et=time.time() - start_time
    r['elapsed_time'] = str(et)

    return r

##############################################################################
# get points from multiple entries

def get(i):
    """

    Input:  {
              Select entries or table:
                 (repo_uoa) or (experiment_repo_uoa)     - can be wild cards
                 (remote_repo_uoa)                       - if remote access, use this as a remote repo UOA
                 (module_uoa) or (experiment_module_uoa) - can be wild cards
                 (data_uoa) or (experiment_data_uoa)     - can be wild cards

                 (repo_uoa_list)                       - list of repos to search
                 (module_uoa_list)                     - list of module to search
                 (data_uoa_list)                       - list of data to search

                 (search_dict)                         - search dict
                 (ignore_case)                         - if 'yes', ignore case when searching

                       OR 

                 table                                 - experiment table (if drawing from other functions)


              (flat_keys_list)                      - list of flat keys to extract from points into table
                                                      (order is important: for example, for plot -> X,Y,Z)
              (flat_keys_index)                     - add all flat keys starting from this index 
              (flat_keys_index_end)                 - add all flat keys ending with this index (default #min)
              (flat_keys_index_end_range)           - add range after key (+-)

              (substitute_x_with_loop)              - if 'yes', substitute first vector dimension with a loop
              (sort_index)                          - if !='', sort by this number within vector (i.e. 0 - X, 1 - Y, etc)

              (ignore_point_if_none)                - if 'yes', ignore points where there is a None
              (ignore_graph_separation)             - if 'yes', ignore separating different entries into graphs 

              (expand_list)                         - if 'yes', expand list to separate values (useful histogram)
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              table        - first dimension is for different graphs on one plot
                             Second dimension: list of vectors [X,Y,Z,...]

              real_keys    - all added keys (useful when flat_keys_index is used)
            }

    """

    o=i.get('out','')

    table=i.get('table',{})

    fki=i.get('flat_keys_index','')
    fkie=i.get('flat_keys_index_end','#min')
    fkied=i.get('flat_keys_index_end_range','')
    fkl=i.get('flat_keys_list',[])
    rfkl=[] # real flat keys (if all)
    trfkl=[]

    ipin=i.get('ignore_point_if_none','')
    igs=i.get('ignore_graph_separation','')

    el=i.get('expand_list','') # useful for histograms

    if len(table)==0:
       ruoa=i.get('repo_uoa','')
       xruoa=i.get('experiment_repo_uoa','')
       if xruoa!='': ruoa=xruoa

       rruoa=i.get('remote_repo_uoa','')

       muoa=i.get('experiment_module_uoa','')
       if muoa=='':
          muoa=i.get('module_uoa','')

       duoa=i.get('experiment_data_uoa','')
       if duoa=='':
          duoa=i.get('data_uoa','')

       ruoal=i.get('repo_uoa_list',[])
       muoal=i.get('module_uoa_list',[])
       duoal=i.get('data_uoa_list',[])

       sd=i.get('search_dict',{})
       ic=i.get('ignore_case','')

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

       # Iterate over entries
       for e in lst:
           sigraph=str(igraph)

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

           dirList=os.listdir(p)
           for fn in dirList:
               if fn.endswith('.flat.json'):
                  fpflat1=os.path.join(p, fn)

                  r=ck.load_json_file({'json_file':fpflat1})
                  if r['return']>0: return r
                  df=r['dict']

                  # Create final vector (X,Y,Z,...)
                  vect=[]
                  has_none=False
                  if fki!='' or len(fkl)==0:
                     # Add all sorted (otherwise there is no order in python dict
                     for k in sorted(df.keys()):
                         if (fki=='' or k.startswith(fki)) and (fkie=='' or k.endswith(fkie)):
                            if len(rfkl)==0:
                               trfkl.append(k)
                            v=df[k]
                            if v==None: has_none=True
                            if v!=None and type(v)==list:
                               if len(v)==0: v=None
                               else: 
                                  if el!='yes':
                                     v=v[0]
                            if type(v)==list and el=='yes':
                               for h in v:
                                   vect.append(h)
                            else:
                               vect.append(v)

                            # Check if range
                            if fkie!='' and fkied!='':
                               kb=k[:len(k)-len(fkie)]
                               kbd=kb+fkied
                               if len(rfkl)==0:
                                  trfkl.append(kbd)
                               vd=df.get(kbd, None)
                               if vd==None: has_none=True
                               if vd!=None and type(vd)==list:
                                  if len(vd)==0: vd=None
                                  else: 
                                     if el!='yes':
                                        vd=vd[0]

                               if type(vd)==list and el=='yes':
                                  for h in vd:
                                      vect.append(h)
                               else:
                                  vect.append(vd)

                     if len(trfkl)!=0:
                        rfkl=trfkl
                  else:
                     for k in fkl:
                         v=df.get(k,None)
                         if v==None: has_none=True
                         if v!=None and type(v)==list:
                            if len(v)==0: v=None
                            else: 
                               if el!='yes':
                                  v=v[0]
                         if type(v)==list and el=='yes':
                            for h in v:
                                vect.append(h)
                         else:
                            vect.append(v)
                        
                  # Add vector
                  if sigraph not in table: table[sigraph]=[]
                  if ipin!='yes' or not has_none:
                     if el=='yes' and type(v)==list:
                        for h in v:
                            table[sigraph].append(h)

                     else:
                        table[sigraph].append(vect)

           if igs!='yes':
              igraph+=1

    if len(rfkl)==0 and len(fkl)!=0: rfkl=fkl

    # If sort/substitute
    si=i.get('sort_index','')
    if si!='':
       rx=sort_table({'table':table, 'sort_index':si})
       if rx['return']>0: return rx
       table=rx['table']

    # Substitute all X with a loop (usually to sort Y and compare with predictions in scatter graphs, etc)
    if i.get('substitute_x_with_loop','')=='yes':
       rx=substitute_x_with_loop({'table':table})
       if rx['return']>0: return rx
       table=rx['table']

    return {'return':0, 'table':table, 'real_keys':rfkl}

##############################################################################
# Convert experiment table to CSV

def convert_table_to_csv(i):
    """

    Input:  {
              table              - experiment table
              keys               - keys
              file_name          - output file for CSV
              csv_no_header      - if 'yes', do not add header
              (csv_separator)    - CSV entry separator (default ;)
              (csv_decimal_mark) - CSV decimal mark    (default .)

            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    tbl=i['table']
    keys=i['keys']
    keys_desc=i.get('keys_desc',{})

    fout=i['file_name']

    sep=i.get('csv_separator',';')
    if sep=='': sep=';'

    dec=i.get('csv_decimal_mark',',')
    if dec=='': dec=','

    c=''

    # Prepare description line
    line=''
    if i.get('csv_no_header','')!='yes':
       for k in keys:
           if line!='': line+=sep
           line+='"'+k+'"'
       c+=line+'\n'

    # Iterate over data
    for t in tbl:
        line=''
        for k in range(0, len(keys)):
            if line!='': line+=sep
            v=t[k]

            if type(v)==float:
               v=str(v).replace(',', dec)
            elif type(v)==int:
               v=str(v)
            else:
               v='"'+str(v)+'"'
            line+=v
        c+=line+'\n'

    try:
       f=open(fout,'wt')
       f.write(c+'\n');
       f.close()
    except Exception as e:
       return {'return':1, 'error':'problem writing csv file ('+format(e)+')'}

    return {'return':0}

##############################################################################
# Process multiple experiments (flatten array + apply statistics)

def process_multi(i):
    """

    Input:  {
              dict                  - existing flat dict 
              dict1                 - new flat dict to add
              (process_multi_keys)  - list of keys (starts with) to perform stat analysis on flat array,
                                      by default ['characteristics', 'features'],
                                      if empty, no stat analysis
            }

    Output: {
              return            - return code =  0, if successful
                                              >  0, if error
              (error)           - error text if return > 0

              dict              - updated dict
              max_range_percent - max % range in float/int data (useful to record points with unusual behavior)
              min               - 'yes', if one of monitored values reached min
              max               - 'yes', if one of monitored values reached max
            }

    """

    d=i['dict']
    d1=i['dict1']

    sak=i.get('process_multi_keys',['characteristics', 'features'])

    max_range_percent=0
    mmin=''
    mmax=''

    for k in d1:
        process=False
        for kk in sak:
            if k.startswith('##'+kk+'#'):
               process=True
               break

        if process:
           v1=d1[k]

           # Number of repetitions
           k_repeats=k+'#repeats'
           vr=d.get(k_repeats,0)
           vr+=1
           d[k_repeats]=vr

           # Put all values (useful to calculate means, deviations, etc)
           k_all=k+'#all'
           v=d.get(k_all,[])
           v.append(v1)
           d[k_all]=v

           # Put only unique values 
           k_all_u=k+'#all_unique'
           v=d.get(k_all_u,[])
           if v1 not in v: v.append(v1)
           d[k_all_u]=v

           # If float or int, perform basic analysis
           if type(v1)==float or type(v1)==int:
              # Calculate min
              k_min=k+'#min'
              vmin=d.get(k_min,v1)
              if v1<vmin: 
                 vmin=v1
                 mmin='yes'
              d[k_min]=vmin

              # Calculate max
              k_max=k+'#max'
              vmax=d.get(k_max,v1)
              if v1>vmax: 
                 vmax=v1
                 mmax='yes'
              d[k_max]=vmax

              # Calculate #range (max-min)
              k_range=k+'#range'
              vrange=vmax-vmin
              d[k_range]=vrange

              # Calculate #halfrange (max-min)/2
              k_halfrange=k+'#halfrange'
              vhrange=vrange/2
              d[k_halfrange]=vhrange

              # Calculate #halfrange (max-min)/2
              k_center=k+'#center'
              d[k_center]=vmin+vhrange

              # Calculate #range percent (max-min)/min
              if vmin!=0:
                 vp=(vmax-vmin)/vmin
                 k_range_p=k+'#range_percent'
                 d[k_range_p]=vp
                 if vp>max_range_percent: max_range_percent=vp

              # Calculate mean
              k_mean=k+'#mean'
              va=sum(d[k_all])/float(vr)
              d[k_mean]=va

              # Check density, expected value and peaks
              rx=ck.access({'action':'analyze',
                            'module_uoa':cfg['module_deps']['math.variation'],
                            'characteristics_table':d[k_all],
                            'skip_fail':'yes'})
              if rx['return']>0: return rx

              valx=rx['xlist2s']
              valy=rx['ylist2s']

              if len(valx)>0:
                 k_exp=k+'#exp'
                 d[k_exp]=valx[0]

                 k_exp_allx=k+'#exp_allx'
                 d[k_exp_allx]=valx

                 k_exp_ally=k+'#exp_ally'
                 d[k_exp_ally]=valy

                 warning='no'
                 if len(valx)>1: warning='yes'
                 k_exp_war=k+'#exp_warning'
                 d[k_exp_war]=warning
           else:
              # Add first value to min 
              k_min=k+'#min'
              vmin=d.get(k_min,'')
              if vmin=='':
                 mmin='yes'
                 d[k_min]=v1

    return {'return':0, 'dict':d, 'max_range_percent':max_range_percent, 'min':mmin, 'max':mmax}

##############################################################################
# sort table

def sort_table(i):
    """
    Input:  {
              table        - experiment table
              sort_index   - if !='', sort by this number within vector (i.e. 0 - X, 1 - Y, etc)
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              table        - updated experient table
            }

    """

    table=i['table']
    si=i['sort_index']

    isi=int(si)
    for sg in table:
        x=table[sg]
        y=sorted(x, key=lambda var: 0 if var[isi] is None else var[isi])
        table[sg]=y

    return {'return':0, 'table':table}

##############################################################################
# substitute x axis in table with loop

def substitute_x_with_loop(i):
    """
    Input:  {
              table        - experiment table
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
              table        - updated experient table
            }

    """

    table=i['table']

    for sg in table:
        h=0
        x=table[sg]
        for q in range(0, len(x)):
            h+=1
            x[q][0]=h
        table[sg]=x

    return {'return':0, 'table':table}

##############################################################################
# filter function

def get_all_meta_filter(i):

    dd=i.get('dict',{})
    d=i.get('dict_orig',{})
    aggr=i.get('aggregation',{})

    ks=aggr.get('keys_start','')
    ke=aggr.get('keys_end','')

    ameta=aggr.get('meta',{})
    atags=aggr.get('tags',{})
    akeys=aggr.get('keys',[])

    # Process meta
    meta=d.get('meta',{})
    for k in meta:
        v=meta[k]

        if k not in ameta:
           ameta[k]=[v]
        else:
           if v not in ameta[k]:
              ameta[k].append(v)

    # Process keys
    for k in dd:
        add=True

        if ks!='' and not k.startswith(ks): add=False
        if add and ke!='' and not k.endswith(ke): add=False

        if add and k not in akeys:
           akeys.append(k)

    # Process meta
    tags=d.get('tags',[])
    for v in tags:
        if v not in atags:
           atags[v]=1
        else:
           atags[v]+=1

    aggr['meta']=ameta
    aggr['tags']=atags
    aggr['keys']=akeys
            
    return {'return':0}

##############################################################################
# Get all meta information from entries

def get_all_meta(i):
    """
    Input:  {
               Input for 'filter' function

               (aggregation) - dict with some params
                               (keys_start) - prune keys
                               (keys_end)   - prune keys
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              all_meta     - each key is a list with all values
              all_tags     - each key is a tag with a number of occurances
            }

    """

    o=i.get('out','')

    import copy
    ii=copy.deepcopy(i)

    ii['filter_func']='get_all_meta_filter'

    r=filter(ii)
    if r['return']>0: return r

    aggr=r.get('aggregation',{})

    ameta=aggr.get('meta',{})
    atags=aggr.get('tags',{})
    akeys=aggr.get('keys',{})

    if o=='con':
       import json

       ck.out('Keys:')
       ck.out('')
       for q in sorted(akeys):
           ck.out('   "'+q+'",')

       ck.out('')
       ck.out('Meta:')
       ck.out('')
       ck.out(json.dumps(ameta, indent=2, sort_keys=True))

       ck.out('')
       ck.out('Tags:')
       ck.out('')

       satags=[(k, atags[k]) for k in sorted(atags, key=atags.get, reverse=True)]

       for k,v in satags:
           ck.out(k+' = '+str(v))

    return {'return':0, 'all_meta':ameta, 'all_tags':atags}

##############################################################################
# filter / pre-process data

def filter(i):
    """
    Input:  {
              Select entries or table:
                 (repo_uoa) or (experiment_repo_uoa)     - can be wild cards
                 (remote_repo_uoa)                       - if remote access, use this as a remote repo UOA
                 (module_uoa) or (experiment_module_uoa) - can be wild cards
                 (data_uoa) or (experiment_data_uoa)     - can be wild cards

                 (repo_uoa_list)                       - list of repos to search
                 (module_uoa_list)                     - list of module to search
                 (data_uoa_list)                       - list of data to search

                 (search_dict)                         - search dict
                 (ignore_case)                         - if 'yes', ignore case when searching

                 (filter_func)        - name of filter function
                 (filter_func_addr)   - address of filter function

              (aggregation)           - dictionary to aggregate information across entries

            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              (aggregation)           - dictionary to aggregate information across entries
            }

    """

    o=i.get('out','')

    ruoa=i.get('repo_uoa','')
    xruoa=i.get('experiment_repo_uoa','')
    if xruoa!='': ruoa=xruoa

    rruoa=i.get('remote_repo_uoa','')

    muoa=i.get('experiment_module_uoa','')
    if muoa=='': muoa=i.get('module_uoa','')

    duoa=i.get('experiment_data_uoa','')
    if duoa=='': duoa=i.get('data_uoa','')

    ruoal=i.get('repo_uoa_list',[])
    muoal=i.get('module_uoa_list',[])
    duoal=i.get('data_uoa_list',[])

    sd=i.get('search_dict',{})
    ic=i.get('ignore_case','')

    sff=i.get('filter_func','')
    ff=i.get('filter_func_addr',None)
    if sff!='': 
       import sys
       ff=getattr(sys.modules[__name__], sff)

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

    aggr=i.get('aggregation',{})

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

        dirList=os.listdir(p)
        for fn in dirList:
            if fn.endswith('.flat.json'):
               fpflat1=os.path.join(p, fn)

               r=ck.load_json_file({'json_file':fpflat1})
               if r['return']>0: return r
               df=r['dict']

               rx=ff({'dict':df, 'dict_orig':dd, 'aggregation':aggr})
               if rx['return']>0: return rx

               changed=rx.get('changed','')
               df=rx.get('dict',{})

               if changed=='yes':
                  r=ck.save_json_to_file({'json_file':fpflat1, 'dict':df})
                  if r['return']>0: return r

    return {'return':0, 'aggregation':aggr}
