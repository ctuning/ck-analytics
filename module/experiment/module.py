   
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
                                                ("meta")               - coarse grain meta information to distinct entries (species)
                                                ("tags")               - tags (separated by comma)
                                                ("subtags")            - subtags to write to a point

                                                ("dependencies")       - (resolved) dependencies

                                                ("choices")            - choices (for example, optimizations)

                                                ("features")           - species features in points inside entries (mostly unchanged)
                                                                           (may contain state, such as frequency or cache/bus contentions, etc)

                                                "characteristics"      - (dict) species characteristics in points inside entries (measured)
                                                      or
                                                "characteristics_list" - (list) adding multiple experiments at the same time
                                                                         Note: at the end, we only keep characteristics_list
                                                                         and append characteristics to this list...

                                                (choices_desc)         - choices descrpition
                                                (features_desc)        - features description
                                                (characteristics_desc) - characteristic description

                                                (pipeline)             - (dict) if experiment from pipeline, record it to be able to reproduce/replay
                                                (pipeline_uoa)         -   if experiment comes from CK pipeline (from some repo), record UOA
                                                (pipeline_uid)         -   if experiment comes from CK pipeline (from some repo), record UOA
                                                                           (to be able to reproduce experiments, test other choices 
                                                                           and improve pipeline by the community/workgroups)
                                              }

              (experiment_repo_uoa)         - if defined, use it instead of repo_uoa
                                              (useful for remote repositories)
              (remote_repo_uoa)             - if remote access, use this as a remote repo UOA

              (experiment_uoa)              - if entry with aggregated experiments is already known
              (experiment_uid)              - if entry with aggregated experiments is already known

              (force_new_entry)             - if 'yes', do not search for existing entry,
                                              but add a new one!

              (search_point_by_features)    - if 'yes', find subpoint by features
              (search_point_by_choices)     - if 'yes', find subpoint by choices

              (ignore_update)               - if 'yes', do not record update control info (date, user, etc)

              (sort_keys)                   - if 'yes', sort keys in output json

              (skip_flatten)                - if 'yes', skip flattinging and analyzing data ...

              (process_multi_keys)          - list of keys (starts with) to perform stat analysis on flat array,
                                              by default ['characteristics', 'features'],
                                              if empty, no stat analysis

              (record_all_subpoints)        - if 'yes', record all subpoints
              (max_range_percent_threshold) - (float) if set, record all subpoints where max_range_percent exceeds this threshold

              (record_desc_at_each_point)   - if 'yes', record descriptions for each point and not just an entry.
                                                Useful if descriptions change at each point (say checking all compilers 
                                                for 1 benchmark in one entry - then compiler flags will be changing)

              (record_deps_at_each_point)   - if 'yes', record dependencies for each point and not just an entry.
                                                Useful if descriptions change at each point (say different program may require different libs)
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import time
    import copy

    start_time = time.time()

    o=i.get('out','')

    dd=i.get('dict',{})

    meta=dd.get('meta',{})
    ft=dd.get('features', {})
    choices=dd.get('choices', {})
    choices_order=dd.get('choices_order', [])
    ch=dd.get('characteristics',{})
    chl=dd.get('characteristics_list',[])

    ddeps=dd.get('dependencies',{})

    # Check if characteristics lits (to add a number of experimental results at the same time,
    #   otherwise point by point processing can become very slow
    if len(ch)>0: chl.append(ch)
    if 'characteristics' in dd: del(dd['characteristics'])

    ft_desc=dd.get('features_desc', {})
    choices_desc=dd.get('choices_desc', {})
    ch_desc=dd.get('characteristics_desc',{})
    
    pipeline=ck.get_from_dicts(dd, 'pipeline', {}, None) # get pipeline and remove from individual points,
                                                         #  otherwise can be very large duplicates ...
    pipeline_uoa=ck.get_from_dicts(dd, 'pipeline_uoa', '', None)
    pipeline_uid=ck.get_from_dicts(dd, 'pipeline_uid', '', None)

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
    spbc=i.get('search_point_by_choices','')
    dpoint={}
    point=0

    ras=i.get('record_all_subpoints','')
    rdesc=i.get('record_desc_at_each_point','')
    rdeps=i.get('record_deps_at_each_point','')

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
       elif euid=='':
          ii['action']='update'
          x='  Adding new entry ...'

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
        'get_lock':'yes',
        'lock_expire_time':120
       }
    r=ck.access(ii)
    if r['return']>0: return r

    p=r['path']
    dde=r['dict']
    lock_uid=r['lock_uid']
    ipoints=int(dde.get('points','0'))

    # Check old and new pipeline UID if exists
    opipeline_uid=dde.get('pipeline_uid','')
    if opipeline_uid!='' and opipeline_uid!=pipeline_uid:
       return {'return':1, 'error':'existing entry has different pipeline UID ('+opipeline_uid+' vs. '+pipeline_uid+')'}
    if pipeline_uoa!='': dde['pipeline_uoa']=pipeline_uoa
    if pipeline_uid!='': dde['pipeline_uid']=pipeline_uid

    if o=='con': 
       ck.out('  Loaded and locked successfully (lock UID='+lock_uid+') ...')

    # Check if pipeline was recorded or record new
    if len(pipeline)>0:
       ppf=os.path.join(p,'pipeline.json')
       if not os.path.isfile(ppf):
          r=ck.save_json_to_file({'json_file':ppf, 'dict':pipeline})
          if r['return']>0: return r

    # Check key descriptions
    ppfd=os.path.join(p,'desc.json')
    ddesc={'features_desc':ft_desc,
           'choices_desc':choices_desc,
           'characteristics_desc':ch_desc}

    if not os.path.isfile(ppfd):
       r=ck.save_json_to_file({'json_file':ppfd, 'dict':ddesc})
       if r['return']>0: return r

    # If existing experiment found, check if search point by feature
    ddft={'features':ft, 'choices':choices, 'choices_order':choices_order}
    fpoint=''
    if euid!='' and (spbf=='yes' or spbc=='yes'):
#       if spbf=='yes' and len(ft)==0:
#          return {'return':1, 'error':'can\'t search by features when they are not present'}
#       if spbc=='yes' and len(choices)==0:
#          return {'return':1, 'error':'can\'t search by choices when they are not present'}

       if o=='con': ck.out('    Searching points by features ...')

       dwork2={}
       if spbf=='yes': 
          dwork2['features']=ft
       if spbc=='yes': 
          dwork2['choices']=choices 
          dwork2['choices_order']=choices_order

       dirList=os.listdir(p)
       for fn in dirList:
           if fn.endswith('.features.json'):
              pfp=os.path.join(p, fn)

              r=ck.load_json_file({'json_file':pfp})
              if r['return']>0: return r
              ft1=r['dict']

              dwork1={}
              if spbf=='yes': 
                 dwork1['features']=ft1.get('features',{})
              if spbc=='yes': 
                 dwork1['choices']=ft1.get('choices',{}) 
                 dwork1['choices_order']=ft1.get('choices_order',[]) 

              r=ck.compare_dicts({'dict1':dwork1, 'dict2':dwork2})
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
       # Load flattened data
       fpflat=fpoint+'.flat.json'
       fpflat1=os.path.join(p, fpflat)

       ddflat={}
       if os.path.isfile(fpflat1):
          r=ck.load_json_file({'json_file':fpflat1})
          if r['return']>0: return r
          ddflat=r['dict']

       # Avoid changing original input !
       ddx=copy.deepcopy(dd)

       if 'characteristics' in ddx: del(ddx['characteristics'])
       if 'characteristics_list' in ddx: del(ddx['characteristics_list'])

       # Flatten data and perform basic analysis **********************************
       r=ck.flatten_dict({'dict':ddx})
       if r['return']>0: return r
       ddf=r['dict']

       # Process multiple points
       sak=i.get('process_multi_keys','')
       if sak=='': sak=['characteristics', 'features', 'choices']

#       ck.out('')
       ich=0
       for cx in chl:
           ich+=1

           ck.out('        Processing characteristic point '+str(ich)+' out of '+str(len(chl))+' ...')

           cddf=copy.deepcopy(ddf)

           # Flatten data and perform basic analysis **********************************
           r=ck.flatten_dict({'dict':{'characteristics':cx}})
           if r['return']>0: return r
           cddf.update(r['dict'])

           ii={'dict':ddflat, 'dict1':cddf, 'process_multi_keys':sak}

           if ich!=len(chl):
              ii['skip_expected_value']='yes'
              ii['skip_min_max']='yes'

           r=process_multi(ii)
           if r['return']>0: return r

           ddflat=r['dict']
           mdp=r['max_range_percent']
           mmin=r['min']
           mmax=r['max']

    # Check if record all points or only with max_range_percent > max_range_percent_threshold
    sp=ddft.get('sub_points',0)
    if sp==0 or ras=='yes' or ((mdpt!=-1 and mdp>mdpt) or mmin=='yes' or mmax=='yes'):
       sp+=1
#       if sp>9999:
#          return {'return':1, 'error':'max number of subpoints is reached (9999)'}

       if o=='con': ck.out('      Next subpoint: '+str(sp))

       ddft['sub_points']=sp
       ssp='.'+str(sp).zfill(4)

       fssp=fpoint+ssp+'.json'
       fssp1=os.path.join(p, fssp)

       # Prepare what to write
       dds={'features':ft,
            'choices':choices,
            'choices_order':choices_order,
            'characteristics_list':chl}

       # Save subpoint dict to file
       r=ck.save_json_to_file({'json_file':fssp1, 'dict':dds, 'sort_keys':sk})
       if r['return']>0: return r

    # Save features file (that include subpoint)
    pfp=os.path.join(p, fpoint)+'.features.json'
    r=ck.save_json_to_file({'json_file':pfp, 'dict':ddft, 'sort_keys':sk})
    if r['return']>0: return r

    # Save updated flat dict to file
    if i.get('skip_flatten','')!='yes':
       r=ck.save_json_to_file({'json_file':fpflat1, 'dict':ddflat, 'sort_keys':sk})
       if r['return']>0: return r

    pfpd=os.path.join(p, fpoint)+'.desc.json'
    if rdesc=='yes':
       r=ck.save_json_to_file({'json_file':pfpd, 'dict':ddesc})

    pfpds=os.path.join(p, fpoint)+'.deps.json'
    if rdeps=='yes':
       r=ck.save_json_to_file({'json_file':pfpds, 'dict':ddeps})

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
                 (meta)                                - meta in the entry (adds search_dict['meta'])
                 (tags)                                - tags in the entry
                 (features)                            - features in the entry

                       OR 

                 (table)                               - experiment table (if drawing from other functions)
                 (mtable)                              - misc or meta table related to above table
                                                         may be useful, when doing labeling for machine learning


              (flat_keys_list)                      - list of flat keys to extract from points into table
                                                      (order is important: for example, for plot -> X,Y,Z)
              (flat_keys_index)                     - add all flat keys starting from this index 
              (flat_keys_index_end)                 - add all flat keys ending with this index (default #min)
              (flat_keys_index_end_range)           - add range after key (+-)

              (substitute_x_with_loop)              - if 'yes', substitute first vector dimension with a loop
              (add_x_loop)                          - if 'yes', insert first vector dimension with a loop
              (sort_index)                          - if !='', sort by this number within vector (i.e. 0 - X, 1 - Y, etc)

              (ignore_point_if_none)                - if 'yes', ignore points where there is a None
              (ignore_graph_separation)             - if 'yes', ignore separating different entries into graphs 
              (separate_subpoints_to_graphs)        - if 'yes', separate each subpoint of entry into a new graph

              (expand_list)                         - if 'yes', expand list to separate values (useful for histogram)
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              table        - first dimension is for different graphs on one plot
                             Second dimension: list of vectors [X,Y,Z,...]

              mtable       - misc table - misc info related to above table (UOA, point, etc)
                             may be useful, when doing labeling for machine learning

              real_keys    - all added keys (useful when flat_keys_index is used)
            }

    """

    o=i.get('out','')

    table=i.get('table',{})
    mtable=i.get('mtable',{})

    fki=i.get('flat_keys_index','')
    fkie=i.get('flat_keys_index_end','#min')
    fkied=i.get('flat_keys_index_end_range','')
    fkl=i.get('flat_keys_list',[])
    rfkl=[] # real flat keys (if all)
    trfkl=[]

    ipin=i.get('ignore_point_if_none','')
    igs=i.get('ignore_graph_separation','')
    sstg=i.get('separate_subpoints_to_graphs','')

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

       meta=i.get('meta',{})
       if len(meta)>0: sd['meta']=meta

       tags=i.get('tags','')

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
           'ignore_case':ic,
           'tags':tags}
       r=ck.access(ii)
       if r['return']>0: return r

       lst=r['lst']

       table={}
       mtable={}
       igraph=0

       # Iterate over entries
       for e in lst:
           ruoa=e['repo_uoa']
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

           meta=dd.get('meta',{})

           dirList=os.listdir(p)
           features=i.get('features',{})
           added=False
           for fn in sorted(dirList):
               if fn.endswith('.flat.json'):
                  skip=False
                  pp1=fn[:-10]
                  pp2=pp1[4:]
                  drz={}

                  fpf1=os.path.join(p, pp1+'.features.json')
                  rz=ck.load_json_file({'json_file':fpf1})
                  if rz['return']>0: 
                     skip=True
                  else:
                     drz=rz['dict']

                  if not skip and len(features)>0: 
                     rx=ck.compare_dicts({'dict1':drz.get('features',{}), 'dict2':features, 'ignore_case':'yes'})
                     if rx['return']>0: return rx
                     equal=rx['equal']
                     if equal!='yes': skip=True

                     if o=='con' and not skip:
                        ck.out('     Found point with searched features ...')
                  if skip:
                     continue

                  added=True

                  fpflat1=os.path.join(p, fn)

                  r=ck.load_json_file({'json_file':fpflat1})
                  if r['return']>0: return r
                  df=r['dict']

                  # Create final vector (X,Y,Z,...)
                  vect=[]
                  has_none=False
                  if fki!='' or len(fkl)==0:
                     # Add all sorted (otherwise there is no order in python dict)
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
                         vect.append(v)

                  # Add vector
                  sigraph=str(igraph)

                  if sigraph not in table: 
                     table[sigraph]=[]
                     mtable[sigraph]=[]
                  if el=='yes':
                     ei=-1 # find index with list to expand
                     lei=0 # length of vector to expand
                     for ih in range(0, len(vect)):
                         h=vect[ih]
                         if type(h)==list:
                            if ei!=-1:
                               return {'return':1, 'error':'can\'t expand vectors with more than one list dimension'}
                            ei=ih
                            lei=len(h)
                     
                     if ei==-1:
                        table[sigraph].append(vect)
                     else:
                        for q in range(0, lei):
                            vect1=[]
                            for k in range(0, len(vect)):
                                h=vect[k]
                                if k==ei:
                                   v=h[q]
                                else:
                                   v=h
                                vect1.append(v)
                            table[sigraph].append(vect1)
                  else:
                     if ipin!='yes' or not has_none:
                        table[sigraph].append(vect)

                  # Add misc info:
                  mi={'repo_uoa':ruid, 'module_uoa':muid, 'data_uoa':duid,
                      'point_uid':pp2, 'features':drz}

                  mtable[sigraph].append(mi)

                  if sstg=='yes':
                     igraph+=1

           if sstg!='yes' and added and igs!='yes':
              igraph+=1

    if len(rfkl)==0 and len(fkl)!=0: rfkl=fkl

    # If sort/substitute
    si=i.get('sort_index','')
    if si!='':
       rx=sort_table({'table':table, 'sort_index':si})
       if rx['return']>0: return rx
       table=rx['table']

    # Substitute all X with a loop (usually to sort Y and compare with predictions in scatter graphs, etc)
    ii={'table':table}
    if i.get('substitute_x_with_loop','')=='yes' or i.get('add_x_loop','')=='yes':
       if i.get('add_x_loop','')=='yes':
          ii['add_x_loop']='yes'
       rx=substitute_x_with_loop(ii)
       if rx['return']>0: return rx
       table=rx['table']


    return {'return':0, 'table':table, 'mtable':mtable, 'real_keys':rfkl}

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
              (skip_expected_value) - if 'yes', do not calculute expected value
              (skip_min_max)        - if 'yes', do not calculate min, max, mean, etc
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

    sev=i.get('skip_expected_value','')
    smm=i.get('skip_min_max','')

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
           if smm!='yes' and (type(v1)==float or type(v1)==int):
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

              if sev!='yes':
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
              (add_x_loop) - if 'yes', insert first vector dimension with a loop
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
              table        - updated experient table
            }

    """

    table=i['table']

    axl=i.get('add_x_loop','')

    if axl=='yes':
       for q in table:
           tq=table[q]
           for iv in range(0, len(tq)):
               v=tq[iv]
               v.insert(0, 0.0)

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

##############################################################################
# list all points in an entry

def list_points(i):
    """
    Input:  {
               data_uoa          - experiment data UOA
               (repo_uoa)        - experiment repo UOA
               (remote_repo_uoa) - if repo_uoa is remote repo, use this to specify which local repo to use at the remote machine
               (module_uoa)

               (point)           - get subpoints for a given point
               (skip_subpoints)  - if 'yes', do not show number of subpoints
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              points       - list of point UIDs
              (subpoints)  - if 'point' is selected, list of subpoints

              dict         - dict of entry
              path         - local path to the entry
            }

    """

    o=i.get('out','')

    duoa=i.get('data_uoa','')
    muoa=i.get('module_uoa','')
    ruoa=i.get('repo_uoa','')

    puid=i.get('point','')

    ii={'action':'load',
        'module_uoa':muoa,
        'data_uoa':duoa,
        'repo_uoa':ruoa}
    rx=ck.access(ii)
    if rx['return']>0: return rx
    p=rx['path']
    d=rx['dict']

    points=[]
    subpoints=[]

    ssp=i.get('skip_subpoints','')

    # Start listing points
    dirList=os.listdir(p)
    features=i.get('features',{})
    added=False
    for fn in sorted(dirList):
        if fn.startswith('ckp-'):
           if len(fn)>20 and fn[20]=='.':
              uid=fn[4:20]
              if uid not in points:
                 points.append(uid)
              if uid==puid and len(fn)>25 and fn[25]=='.':
                 suid=fn[21:25]
                 if suid!='flat' and suid!='desc' and suid!='deps':
                    subpoints.append(suid)

    if o=='con':
       if ssp!='yes' and puid!='':
          for k in subpoints:
              ck.out(puid+'-'+k)
       else:
          for q in points:
              ck.out(q)

    return {'return':0, 'path':p, 'dict':d, 'points':points, 'subpoints':subpoints}


##############################################################################
# replay experiment == the same as reproduce

def replay(i):
    """
    Input:  { see 'reproduce'
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    return reproduce(i)

##############################################################################
# rerun experiment == the same as reproduce

def rerun(i):
    """
    Input:  { see 'reproduce'
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }
    """

    return reproduce(i)

##############################################################################
# reproduce a given experiment

def reproduce(i):
    """
    Input:  {
               data_uoa          - experiment data UOA (can have wildcards)
               (repo_uoa)        - experiment repo UOA (can have wildcards)
               (module_uoa)
               (tags)            - search by tags

               (point)           - point (or skip, if there is only one), can be of format UID-<subpoint>
               (subpoint)        - subpoint (or skip, if there is only one)
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }
    """

    o=i.get('out','')

    ruoa=i.get('repo_uoa','')
    muoa=i.get('module_uoa','')
    duoa=i.get('data_uoa','')

    i['out']=''
    r=ck.search(i)
    if r['return']>0: return r

    lst=r['lst']
    if len(lst)==0:
       return {'return':1, 'error':'entry not found'}
    elif len(lst)==1:
       ruoa=lst[0]['repo_uoa']

       muoa=lst[0]['module_uoa']
       duoa=lst[0]['data_uoa']
    else:
       if o=='con':
          r=ck.select_uoa({'choices':lst})
          if r['return']>0: return r
          duoa=r['choice']
          ck.out('')
       else:
          return {'return':1, 'error':'multiple entries found - please prune search', 'lst':lst}

    if o=='con':
       ck.out('Found entry '+duoa+'!')
       ck.out('')

    # Check point
    puid=i.get('point','')
    sp=i.get('subpoint','')
    if puid.find('-')>=0:
       puid,sp=puid.split('-')
    puid=puid.strip()
    spid=sp.strip()

    # If point is not specified, get points
    if puid=='':
       rx=list_points({'repo_uoa':ruoa,
                       'module_uoa':muoa,
                       'data_uoa':duoa})
       if rx['return']>0: return rx

       points=rx['points']
       if len(points)==0:
          return {'return':1, 'error':'no points found in a given entry'}
       elif len(points)>1:
          if o=='con':
             ck.out('Multiple points:')
             for q in points:
                 ck.out('  '+q)
             ck.out('')
          return {'return':1, 'error':'select a point in a given entry'}
       else:
          puid=points[0]

    # If subpoint is not specified, get subpoints
    if spid=='':
       rx=list_points({'repo_uoa':ruoa,
                       'module_uoa':muoa,
                       'data_uoa':duoa,
                       'point':puid})
       if rx['return']>0: return rx

       spoints=rx['subpoints']
       if len(spoints)==0:
          return {'return':1, 'error':'no subpoints found in a given entry'}
       elif len(spoints)>1:
          if o=='con':
             ck.out('Multiple subpoints:')
             for q in spoints:
                 ck.out('  '+q)
             ck.out('')
          return {'return':1, 'error':'select a given subpoint for a given point in a given entry'}
       else:
          spid=spoints[0]
      
    # Get all info about this point
    rx=load_point({'repo_uoa':ruoa,
                   'module_uoa':muoa,
                   'data_uoa':duoa,
                   'point':puid,
                   'subpoint':spid,
                   'add_pipeline':'yes'})
    if rx['return']>0: return rx

    dd=rx['dict']

    ch=dd.get('flat',{})
    if len(ch)==0:
       return {'return':1, 'error':'no flat characteristics in the point to compare'}

    cf=dd.get('features',{}) # choices and features
    if 'sub_points' in cf: del(cf['sub_points'])

    deps=dd.get('deps',{})

    pipeline_uoa=rx['pipeline_uoa']
    pipeline_uid=rx['pipeline_uid']
    pipeline=rx['pipeline']

    pipeline.update(cf)
    pipeline.update({'dependencies':deps})

    if len(pipeline)==0:
       return {'return':1, 'error':'pipeline not found in the entry'}

    if o=='con':
       ck.out('Restarting pipeline ...')
       ck.out('')
 
    # Attempt to run pipeline
    ii={'action':'run',
        'module_uoa':cfg['module_deps']['pipeline'],
        'data_uoa':pipeline_uid,
        'pipeline':pipeline}
    r=ck.access(ii)
    if r['return']>0: return r

    # Check that didn't fail (or failed, if reproducing a bug)
    if r.get('fail','')=='yes':
       if o=='con':
          ck.out('')
          ck.out('Pipeline failed ('+r.get('fail_reason','')+')')

    # Flattening characteristics
    chn=r.get('characteristics',{})

    rx=ck.flatten_dict({'dict':chn, 'prefix':'##characteristics'})
    if rx['return']>0: return rx
    fchn=rx['dict']

    # Comparing dicts
    for q in ch:
        if q.startswith('##characteristics'):
#           print q
           if q.endswith('#min'):
              q1=q[:-4]
              if q1 in fchn:
                 print q1
                 print '   '+str(ch[q])
                 print '   '+str(fchn[q1])


    return r

##############################################################################
# load all info about a given point and subpoint

def load_point(i):
    """
    Input:  {
               data_uoa          - experiment data UOA
               (repo_uoa)        - experiment repo UOA
               (module_uoa)

               (point)           - point (or skip, if there is only one), can be of format UID-<subpoint>
               (subpoint)        - subpoint (or skip, if there is only one)

               (add_pipeline)    - if 'yes', load pipeline from entry (if exists)
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              dict         - {point extension = loaded json file}

              pipeline     - if add_pipeline!='yes' and pipeline exists, return dict
              pipeline_uoa - if add_pipeline!='yes' and pipeline_uoa exists, return pipeline UOA
              pipeline_uid - if add_pipeline!='yes' and pipeline_uid exists, return pipeline UID
            }

    """

    o=i.get('out','')

    oo=''
    if o=='con': oo=o

    ruoa=i.get('repo_uoa','')
    muoa=i.get('module_uoa','')
    if muoa=='': muoa=work['self_module_uoa']
    duoa=i.get('data_uoa','')

    sp=i.get('subpoint','')

    ap=i.get('add_pipeline','')

    # Check point
    puid=i.get('point','')

    r=list_points({'module_uoa':muoa,
                   'data_uoa':duoa,
                   'repo_uoa':ruoa,
                   'out':oo})
    if r['return']>0: return r
    p=r['path']
    d=r['dict']

    if puid=='':
       pp=r['points']

       if len(pp)==0:
          return {'return':1, 'error':'points not found in the entry'}
       elif len(pp)>1:
          return {'return':1, 'error':'more than one point found - please prune your choice'}

       puid=pp[0]

    dd={}

    # Check pipeline
    pxuoa=d.get('pipeline_uoa','')
    pxuid=d.get('pipeline_uid','')
    pipeline={}

    if ap=='yes' and (pxuoa!='' or pxuid!=''):
       p1=os.path.join(p, 'pipeline.json')
       if os.path.isfile(p1):
          rx=ck.load_json_file({'json_file':p1})
          if rx['return']>0: return rx
          pipeline=rx['dict']
                 
    # Start listing points
    dirList=os.listdir(p)
    added=False
    for fn in sorted(dirList):
        if fn.startswith('ckp-'):
           if len(fn)>20 and fn[20]=='.':
              uid=fn[4:20]
              if uid==puid:
                 i1=fn.find('.json')
                 if i1>0:
                    key=fn[21:i1]
                    if sp!='' and key!='flat' and key!='deps' and key!='desc' and key!='features' and key!=sp:
                       continue
                    p1=os.path.join(p,fn)
                    rx=ck.load_json_file({'json_file':p1})
                    if rx['return']>0: return rx
                    dd[key]=rx['dict']

    return {'return':0, 'dict':dd, 'pipeline_uoa':pxuoa, 'pipeline_uid':pxuid, 'pipeline':pipeline}
