   
# Collective Knowledge (Universal Experiment)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Developer: Grigori Fursin
#

cfg={}  # Will be updated by CK (meta description of this module)
work={} # Will be updated by CK (temporal data)
ck=None # Will be updated by CK (initialized CK kernel) 

# Local settings
import os

var_post_subview='subview'

line='****************************************************************'

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
                                                ("dict")               - add to meta of the entry (useful for subview_uoa, for example)

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

                                                                         Note, that if a string starts with @@, it should be 
                                                                         of format "@@float_value1,float_value2,...
                                                                         and will be converted into list of values which
                                                                         will be statistically processed as one dimension in time
                                                                         (needed to deal properly with bencmarks like slambench
                                                                         which report kernel times for all frames)

                                                (pipeline_state)       - final state of the pipeline
                                                                          {
                                                                           'repetitions':
                                                                           'fail_reason'
                                                                           'fail'
                                                                           'fail_bool'
                                                                          }
                                        

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
              (features_keys_to_process)    - list of keys for features (and choices) to process/search (can be wildcards)
                                                   by default ['##features#*', '##choices#*', '##choices_order#*']

              (ignore_update)               - if 'yes', do not record update control info (date, user, etc)

              (sort_keys)                   - if 'yes', sort keys in output json

              (skip_flatten)                - if 'yes', skip flattinging and analyzing data (including stat analysis) ...

              (skip_stat_analysis)          - if 'yes', just flatten array and add #min

              (process_multi_keys)          - list of keys (starts with) to perform stat analysis on flat array,
                                              by default ['##characteristics#*', '##features#*' '##choices#*'],
                                              if empty, no stat analysis

              (record_all_subpoints)        - if 'yes', record all subpoints (i.e. do not search and reuse existing points by features)

              (max_range_percent_threshold) - (float) if set, record all subpoints where max_range_percent exceeds this threshold
                                                      useful, to avoid recording too many similar points, but only *unusual* ...

              (record_desc_at_each_point)   - if 'yes', record descriptions for each point and not just an entry.
                                                Useful if descriptions change at each point (say checking all compilers 
                                                for 1 benchmark in one entry - then compiler flags will be changing)

              (record_deps_at_each_point)   - if 'yes', record dependencies for each point and not just an entry.
                                                Useful if descriptions change at each point (say different program may require different libs)
            }

    Output: {
              return        - return code =  0, if successful
                                          >  0, if error
              (error)       - error text if return > 0

              update_dict   - dict after updating entry
              dict_flat     - flat dict with stat analysis (if performed)
              stat_analysis - whole output of stat analysis (with warnings)

              flat_features - flat dict of real features of the recorded point (can be later used to search the same points)

              recorded_uid  - UID of a recorded experiment
              point         - recorded point
              sub_point     - recorded subpoint

              elapsed_time  - elapsed time (useful for debugging - to speed up processing of "big data" ;) )
            }

    """

    import time
    import copy

    start_time = time.time()

    o=i.get('out','')

    oo=''
    if o=='con': oo=o

    ssa=i.get('skip_stat_analysis','')

    dd=i.get('dict',{})
    ddx=copy.deepcopy(dd) # To avoid changing original input !!! 

    ddd=ddx.get('dict','')
    if ddd=='': ddd={}

    meta=ddx.get('meta','')
    if meta=='': meta={}

    tags=ddx.get('tags','')
    if tags=='': tags=[]

    ft=ddx.get('features', {})
    choices=ddx.get('choices', {})
    choices_order=ddx.get('choices_order', [])

    ddeps=ddx.get('dependencies',{})

    ch=ddx.get('characteristics', {})

    # Check if characteristics lits (to add a number of experimental results at the same time,
    #   otherwise point by point processing can become very slow
    chl=ddx.get('characteristics_list', [])
    if len(ch)>0: chl.append(ch)

    ft_desc=ddx.get('features_desc', {})
    choices_desc=ddx.get('choices_desc', {})
    ch_desc=ddx.get('characteristics_desc',{})
    
    pipeline=ck.get_from_dicts(ddx, 'pipeline', {}, None) # get pipeline and remove from individual points,
                                                         #  otherwise can be very large duplicates ...
    pipeline_uoa=ck.get_from_dicts(ddx, 'pipeline_uoa', '', None)
    pipeline_uid=ck.get_from_dicts(ddx, 'pipeline_uid', '', None)

    if len(ddx)==0:
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

    cmpr=i.get('features_keys_to_process','') # keys to search similar and already existing points 
    if cmpr=='': cmpr=['##features#*', '##choices#*', '##choices_order#*']

    sf=i.get('skip_flatten','')

    sak=i.get('process_multi_keys','') # Keys to perform stat analysis
    if sak=='': sak=['##characteristics#*', '##features#*', '##choices#*', '##pipeline_state#*']

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
           'dict':ddd}

       if euoa=='' and euid=='':
          ii['action']='add'
          x='  Existing experiments were not found. Adding new entry ...'
       elif euid=='':
          ii['action']='update'
          x='  Adding/updating entry ...'

       else:
          ii['action']='update'
          x='  Updating entry ...'

       if o=='con': ck.out(x)

       # If entry exists, we just touch it. Hence if it is locked, we can wait here ...
       success=False
       start_time1 = time.time()
       while not success:
             r=ck.access(ii)

             if r['return']==0:
                success=True
             elif r['return']==32:
                tm = time.time()-start_time1
                if tm>120:
                   return r
                if o=='con':
                   ck.out('    Entry exists ('+r['data_uoa']+') and locked - waiting 5 sec ...')
                   time.sleep(5)   
             else:
                return r

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
    if len(ddd)>0: dde.update(ddd)
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

    # Flatten and prune features and choices (to be able to faster detect related points for a given experiment later)
    r=ck.flatten_dict({'dict':ddft, 'prune_keys':cmpr})
    if r['return']>0: return r
    fddft=r['dict']

    # Find related point by features and/or choices
    fpoint=''
    fpoint_uid=''
    if euid!='' and spbf=='yes':
       if o=='con': ck.out('    Searching points by features (and choices if needed) ...')

       rx=list_points({'path':p, 
                       'prune_by_features':fddft})
       if rx['return']>0: return rx

       points=rx['points']

       if len(points)>1:
          return {'return':1, 'error':'ambiguity - more than one point found with the same features'}

       if len(points)==1:
          fpoint_uid=fpoints[0]
          fpoint='ckp-'+fpoint_uid

       if fpoint!='':
          if o=='con': 
             ck.out('      Found point by features: '+str(fpoint))

          # Reload feature file from this point to get number of subpoints
          px=os.path.join(p, fpoint+'.features.json')
          rx=ck.load_json_file({'json_file':px})
          if rx['return']>0: return rx
          ddft=rx['dict']

    # Add information about user
    ri=ck.prepare_special_info_about_entry({})
    if ri['return']>0: return ri
    dsi=ri['dict']

    if len(dde.get('added',{}))==0:
       dde['added']=dsi
    if len(dde.get('meta',{}))==0:
       dde['meta']=meta
    if len(tags)!=0:
       dde['tags']=tags

    # Prepare new point (if not found by features)
    if fpoint=='':
       ipoints+=1

       rx=ck.gen_uid({})
       if rx['return']>0: return rx
       uid=rx['data_uid']
 
       fpoint_uid=uid
       fpoint='ckp-'+uid

       dde['points']=str(ipoints)

       if o=='con': ck.out('  Prepared new point '+uid+' ...')

    # Check if need to flat and basic perform analysis
    mdpt=i.get('max_range_percent_threshold',-1)
    mmin=''
    mmax=''

    ddflat={}
    rsa={}
    if sf!='yes':
       # Pre-load flattened data, if already exists
       fpflat1=os.path.join(p, fpoint+'.flat.json')

       if os.path.isfile(fpflat1):
          r=ck.load_json_file({'json_file':fpflat1})
          if r['return']>0: return r
          ddflat=r['dict']

       # Perform statistical analysis of (multiple statistical) characteristics
       rsa=multi_stat_analysis({'flat_dict':ddflat,
                                'dict_to_add':ddx,
                                'process_multi_keys':sak,
                                'skip_stat_analysis':ssa,
                                'out':oo})
       if rsa['return']>0: return rsa

       ddflat=rsa['dict_flat']
       mdp=rsa['max_range_percent']
       mmin=rsa['min']
       mmax=rsa['max']

       # Save updated flat file
       r=ck.save_json_to_file({'json_file':fpflat1, 'dict':ddflat, 'sort_keys':sk})
       if r['return']>0: return r

    # Check if record all points or only with max_range_percent > max_range_percent_threshold
    sp=ddft.get('sub_points',0)
    if sp==0 or ras=='yes' or ((mdpt!=-1 and mdp>mdpt) or mmin=='yes' or mmax=='yes'):
       sp+=1
#       if sp>9999:
#          return {'return':1, 'error':'max number of subpoints is reached (9999)'}

       if o=='con': ck.out('      Subpoint: '+str(sp))

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

    # Save flattened features file
    pfpf=os.path.join(p, fpoint)+'.features_flat.json'
    r=ck.save_json_to_file({'json_file':pfpf, 'dict':fddft, 'sort_keys':sk})
    if r['return']>0: return r

    # Save universal descriptions of (all) dimensions
    pfpd=os.path.join(p, fpoint)+'.desc.json'
    if rdesc=='yes':
       r=ck.save_json_to_file({'json_file':pfpd, 'dict':ddesc})

    # Save dependencies for experiment
    pfpds=os.path.join(p, fpoint)+'.deps.json'
    if rdeps=='yes':
       r=ck.save_json_to_file({'json_file':pfpds, 'dict':ddeps})

    # Updating and unlocking entry *****************************************************
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
    if r['return']>0: return r

    et=time.time() - start_time

    return {'return':0, 'elapsed_time':str(et), 
                        'update_dict':r, 
                        'dict_flat':ddflat, 
                        'stat_analysis':rsa, 
                        'flat_features':fddft,
                        'recorded_uid':euid,
                        'point':fpoint_uid,
                        'sub_point':sp}

##############################################################################
# get points from multiple entries

def get(i):
    """

    Input:  {
              Select entries or table:
                 (repo_uoa) or (experiment_repo_uoa)     - can be wild cards
                 (remote_repo_uoa)                       - if remote access, use this as a remote repo UOA
                 (module_uoa) or (experiment_module_uoa) - can be wild cards
                 (data_uoa) or (experiment_uoa) or (experiment_data_uoa)     - can be wild cards

                 (repo_uoa_list)                       - list of repos to search
                 (module_uoa_list)                     - list of module to search
                 (data_uoa_list)                       - list of data to search

                 (search_dict)                         - search dict
                 (ignore_case)                         - if 'yes', ignore case when searching

                       OR
                 (meta)                                - search by meta in the entry (adds search_dict['meta'])
                 (tags)                                - search by tags in the entry

                 (features)                            - search by features in the entry
                       OR
                 (flat_features)                       - search by flat features in the entry (faster) ...

                 (features_keys_to_ignore)             - list of keys to remove from features (can be wildcards) - useful for frontier detection

                       OR 

                 (table)                               - experiment table (if drawing from other functions)
                 (mtable)                              - misc or meta table related to above table
                                                         may be useful, when doing labeling for machine learning

              (skip_processing)                        - if 'yes', do not load data (useful to return points for frontier detection)
              (get_all_points)                         - if 'yes', add all points
              (load_json_files)                        - list of json files to load for a given point 
                                                         (features, features_flat, flat, 0001, 0002, etc ...)
              (get_keys_from_json_files)               - which keys to get from json files (useful for frontier) ...

              (flat_keys_list)                      - list of flat keys to extract from points into table
              (flat_keys_list_ext)                  - add this extension to all above keys (useful to add #min)

              (flat_keys_list_separate_graphs)      - [ [keys], [keys], ...] - several graphs ...

                                                      (order is important: for example, for plot -> X,Y,Z)
              (flat_keys_index)                     - add all flat keys starting from this index 
              (flat_keys_index_end)                 - add all flat keys ending with this index (default #min)
              (flat_keys_index_end_range)           - add range after key (+-)

              (substitute_x_with_loop)              - if 'yes', substitute first vector dimension with a loop
              (add_x_loop)                          - if 'yes', insert first vector dimension with a loop
              (sort_index)                          - if !='', sort by this number within vector (i.e. 0 - X, 1 - Y, etc)

              (ignore_point_if_none)                - if 'yes', ignore points where there is a None
              (ignore_point_if_empty_string)        - if 'yes', ignore points where there is a None
              (ignore_graph_separation)             - if 'yes', ignore separating different entries into graphs 
              (separate_subpoints_to_graphs)        - if 'yes', separate each subpoint of entry into a new graph

              (vector_thresholds)                   - List of values: if a given value in this vector is !=None and more than
                                                        a value in a processed vector - skip it
              (vector_thresholds_conditions)        - specify threshold conditions for above vector values ("<" - default or ">")

              (expand_list)                         - if 'yes', expand list to separate values (useful for histogram)
                                                         (all checks for valid vectors or thresholds are currently turned off)
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              table        - first dimension is for different graphs on one plot
                             Second dimension: list of vectors [X,Y,Z,...]

              mtable       - misc table - misc info related to above table (UOA, point, etc)
                             may be useful, when doing labeling for machine learning

              points       - list of points {'repo_uoa','repo_uid','module_uoa','module_uid','data_uoa','data_uid','point_uid', '<file_extension_name>'=dict ...}}

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
    xfkl=i.get('flat_keys_list_ext','')

    fkti=i.get('features_keys_to_ignore',[])

    fkls=i.get('flat_keys_list_separate_graphs','')
    if fkls=='': fkls=[]
    if len(fkls)==0 or len(fkl)>0: fkls.append(fkl) # at least one combination of keys, even empty!

    rfkl=[] # real flat keys (if all)
    trfkl=[]

    ipin=i.get('ignore_point_if_none','')
    ipies=i.get('ignore_point_if_empty_string','')
    igs=i.get('ignore_graph_separation','')
    sstg=i.get('separate_subpoints_to_graphs','')

    sl=i.get('skip_processing','')
    gop=i.get('get_all_points','')
    ljf=i.get('load_json_files',[])
    gkjf=i.get('get_keys_from_json_files',[])

    el=i.get('expand_list','') # useful for histograms

    vt=i.get('vector_thresholds',[])
    vtc=i.get('vector_thresholds_conditions',[])

    points=[]

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
       if duoa=='':
          duoa=i.get('experiment_uoa','')

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

       features=i.get('features',{})
       ffeatures=i.get('flat_features',{})

       if len(features)>0 and len(ffeatures)==0:
          r=ck.flatten_dict({'dict':features})
          if r['return']>0: return r
          ffeatures=r['dict']

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

           added=False
           for fn in sorted(dirList):
               if fn.endswith('.flat.json'):
                  pp1=fn[:-10]
                  pp2=pp1[4:]
                  drz={}

                  skip=False

                  fpf1=os.path.join(p, pp1+'.features_flat.json')
                  rz=ck.load_json_file({'json_file':fpf1})
                  if rz['return']==0: 
                     drz=rz['dict']

                  if gop=='yes' or (len(drz)>0 and len(ffeatures)>0):
                     if gop!='yes':
                        rx=ck.compare_flat_dicts({'dict1':drz, 'dict2':ffeatures, 'ignore_case':'yes', 'space_as_none':'yes', 'keys_to_ignore':fkti})
                        if rx['return']>0: return rx
                        equal=rx['equal']
                        if equal!='yes': skip=True

                     if o=='con' and not skip:
                        ck.out('     Found point with related features ('+ruoa+':'+muoa+':'+duoa+'/'+pp2+') ...')

                  if skip:
                     continue

                  ppx={'repo_uoa':ruoa, 'repo_uid':ruid, 'module_uoa':muoa, 'module_uid':muid, 'data_uoa':duoa, 'data_uid':duid, 'point_uid':pp2}
                  
                  # If load json files ...
                  if len(ljf)>0:
                     for jf in ljf:
                         pj=os.path.join(p,pp1+'.'+jf+'.json')

                         rx=ck.load_json_file({'json_file':pj})
                         if rx['return']>0: return rx
                         
                         dpj=rx['dict']

                         if len(gkjf)>0:
                            x={}
                            for k in gkjf:
                                x[k]=dpj.get(k, None)
                            dpj=x

                         ppx[jf]=dpj

                  points.append(ppx)

                  added=True

                  if sl!='yes':
                     fpflat1=os.path.join(p, fn)

                     r=ck.load_json_file({'json_file':fpflat1})
                     if r['return']>0: return r
                     df=r['dict']

                     # Iterate over combinations of keys
                     for fkl in fkls:
                         # Create final vector (X,Y,Z,...)
                         vect=[]
                         has_none=False
                         has_empty_string=False
                         if fki!='' or len(fkl)==0:
                            # Add all sorted (otherwise there is no order in python dict)
                            for k in sorted(df.keys()):
                                if (fki=='' or k.startswith(fki)) and (fkie=='' or k.endswith(fkie)):
                                   if len(rfkl)==0:
                                      trfkl.append(k)
                                   v=df[k]
                                   if v==None: has_none=True
                                   if v=='': has_empty_string=True
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
                                      if vd=='': has_empty_string=True
                                      if vd!=None and type(vd)==list:
                                         if len(vd)==0: vd=None
                                         else: 
                                            if el!='yes':
                                               vd=vd[0]

                                      vect.append(vd)

                            if len(trfkl)!=0:
                               rfkl=trfkl
                         else:
                            for kx in fkl:
                                k=kx+xfkl
                                v=df.get(k,None)
                                if v==None: has_none=True
                                if v=='': has_empty_string=True
                                if v!=None and type(v)==list:
                                   if len(v)==0: v=None
                                   else: 
                                      if el!='yes':
                                         v=v[0]
                                vect.append(v)

                         # Add vector (if valid)
                         sigraph=str(igraph)

                         if sigraph not in table: 
                            table[sigraph]=[]
                            mtable[sigraph]=[]

                         if el=='yes':
                            max_length=0
                            for ih in range(0, len(vect)):
                                vih=vect[ih]
                                if vih!=None:
                                   max_length=max(max_length, len(vih))
                            
                            for q in range(0, max_length):
                                vect1=[]
                                for ih in range(0, len(vect)):
                                    h=vect[ih]
                                    if q<len(h): v1=h[q]
                                    else: v1=h[len(h)-1]
                                    vect1.append(v1)
                                table[sigraph].append(vect1)
                         else:
                            if (ipin!='yes' or not has_none) and (ipies!='yes' or not has_empty_string):
                               skip=False

                               if len(vt)>0:
                                  for o in range(0, len(vt)):
                                      vx=vt[o]
                                      vxo=vect[o]
                                      if vx!=None:
                                         xvtc='<'
                                         if len(vtc)>0 and o<len(vtc) and vtc[o]!=None:
                                            xvtc=vtc[o]

                                         if (xvtc=='<' and vxo>vx) or (xvtc=='>' and vxo<vx): 
                                            skip=True
                                            break

                               if not skip:
                                  table[sigraph].append(vect)

                         # Add misc info:
                         mi={'repo_uoa':ruid, 'module_uoa':muid, 'data_uoa':duid,
                             'point_uid':pp2, 'features':drz}

                         mtable[sigraph].append(mi)

                         if sstg=='yes' or len(fkls)>1:
                            igraph+=1

           if sstg!='yes' and added and igs!='yes':
              igraph+=1

    if len(rfkl)==0 and len(fkls)!=0 and len(fkls[0])>0: 
       rfkl=fkls[0]

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

    return {'return':0, 'table':table, 'mtable':mtable, 'real_keys':rfkl, 'points':points}

##############################################################################
# Convert experiment table to CSV

def convert_table_to_csv(i):
    """

    Input:  {
              table                - experiment table
              (merge_multi_tables) - if 'yes', merge multiple tables to one
              keys                 - list of keys
              (keys_desc)          - dict with desc of keys
              file_name            - output file for CSV
              csv_no_header        - if 'yes', do not add header
              (csv_separator)      - CSV entry separator (default ;)
              (csv_decimal_mark)   - CSV decimal mark    (default .)

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

    mmt=i.get('merge_multi_tables','')
    if mmt=='yes':
       tbl1=[]
       for g in sorted(tbl, key=int):
           for j in tbl[g]:
               tbl1.append(j)
       tbl=tbl1

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

def stat_analysis(i):
    """

    Input:  {
              dict                  - existing flat dict 
              dict1                 - new flat dict to add
                                      if empty, no stat analysis

              (skip_expected_value) - if 'yes', do not calculute expected value
              (skip_min_max)        - if 'yes', do not calculate min, max, mean, etc

                 For expected value (via gaussian_kde):

              (bins)                - number of bins (int, default = 100)
              (cov_factor)          - float covariance factor

              (skip_stat_analysis)  - if 'yes', just flatten array and add #min
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

    issa=False
    ssa=i.get('skip_stat_analysis','')
    if ssa=='yes': issa=True

    d=i['dict']
    d1=i['dict1']

    max_range_percent=0
    mmin=''
    mmax=''

    sev=i.get('skip_expected_value','')
    smm=i.get('skip_min_max','')

    bins=i.get('bins','')
    cov_factor=i.get('cov_factor','')

    for k in d1:
        vv1=d1[k]

        # If float or int, perform basic analysis
        if type(vv1)!=list: vv1=[vv1]
        for v1 in vv1:
            if not issa:
               # Number of repetitions
               k_repeats=k+'#repeats'
               vr=d.get(k_repeats,0)
               vr+=1
               d[k_repeats]=vr

               # Put all values (useful to calculate means, deviations, etc)
               k_all=k+'#all'
               v_all=d.get(k_all,[])
               v_all.append(v1)
               d[k_all]=v_all

               # Put only unique values 
               k_all_u=k+'#all_unique'
               v=d.get(k_all_u,[])
               if v1 not in v: v.append(v1)
               d[k_all_u]=v

            if not issa and smm!='yes' and (type(v1)==float or type(v1)==int):
               # Calculate min
               k_min=k+'#min'
               vmin=d.get(k_min,v1)

               for b in v_all:
                   if b<vmin: vmin=b

               if v1<vmin: 
                  vmin=v1
                  mmin='yes'
               d[k_min]=vmin

               # Calculate max
               k_max=k+'#max'
               vmax=d.get(k_max,v1)

               for b in v_all:
                   if b>vmax: vmax=b

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
                                'bins':bins,
                                'cov_factor':cov_factor,
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
               data_uoa            - experiment data UOA
               (repo_uoa)          - experiment repo UOA
               (remote_repo_uoa)   - if repo_uoa is remote repo, use this to specify which local repo to use at the remote machine
               (module_uoa)
                    or
               (path)              - if called from internal modules, can specify path of the experiment entry directly ...

               (prune_by_features) - flat dict with features to check (no wild cards here)

               (point)             - get subpoints for a given point
               (skip_subpoints)    - if 'yes', do not show number of subpoints
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              points       - list of point UIDs
              (subpoints)  - if 'point' is selected, list of subpoints

              dict         - dict of entry (if not loaded by path)
              path         - local path to the entry
            }

    """

    o=i.get('out','')

    p=i.get('path','')
    d={}

    puid=i.get('point','')

    if p=='':
       # Attempt to load entry
       duoa=i.get('data_uoa','')
       muoa=i.get('module_uoa','')
       ruoa=i.get('repo_uoa','')
       rruoa=i.get('remote_repo_uoa','')

       ii={'action':'load',
           'module_uoa':muoa,
           'data_uoa':duoa,
           'repo_uoa':ruoa}
       if rruoa!='': ii['remote_repo_uoa']=rruoa
       rx=ck.access(ii)
       if rx['return']>0: return rx
       p=rx['path']
       d=rx['dict']

    points=[]
    skiped_points=[]
    subpoints=[]

    ssp=i.get('skip_subpoints','')

    pp=i.get('prune_by_features',{})

    # Start listing points
    dirList=os.listdir(p)
    added=False
    for fn in sorted(dirList):
        if fn.startswith('ckp-'):
           if len(fn)>20 and fn[20]=='.':
              uid=fn[4:20]

              if uid not in skiped_points:
                 if len(pp)>0:
                    skip=True

                    px=os.path.join(p, 'ckp-'+uid+'.features_flat.json')
                    if os.path.isfile(px):
                       rx=ck.load_json_file({'json_file':px})
                       if rx['return']>0: return rx
                       ft=rx['dict']

                       ry=ck.compare_flat_dicts({'dict1':ft, 'dict2':pp, 'space_as_none':'yes'})
                       if ry['return']>0: return ry

                       if ry['equal']=='yes': 
                          skip=False

                    if skip:
                       skiped_points.append(uid)
                       continue

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
    Input:  {
               data_uoa                      - experiment data UOA (can have wildcards)
               (repo_uoa)                    - experiment repo UOA (can have wildcards)
               (experiment_repo_uoa)         - use it, if repository is remote
               (remote_repo_uoa)             - if repo above is remote, use this repo on remote machine

               (module_uoa)
               (tags)                        - search by tags

               (point)                       - point (or skip, if there is only one), can be of format UID-<subpoint>
               (subpoint)                    - subpoint (or skip, if there is only one)

               (repetitions)                 - statistical repetitions (default=4)
               (pipeline_update)             - customize pipeline with this dict (useful to update already prepared pipeline from file)

               (dims_to_check) or (dims)     - list of dimensions to check, can have wildcards (if empty, check all); 
                                               alternatively can use a string (useful for CMD)
               (end_of_dims_to_check)        - list of endings of dimensions to compare ...

               (threshold_to_compare)        - % threshold to decide whether dim is different or not

               (record_original_flat_json)   - file to record flat dict with original results
               (record_reproduced_flat_json) - file to record flag dict with reproduced results

               (skip)                        - if 'yes', do not perform comparison

               ==============================
                 If one would like to compare results with another point (for example, to check speedups 
                 rather than just reproducing a given point)

               (compare_data_uoa)
               (compare_repo_uoa)
               (compare_point)
               (compare_subpoint)

               ==============================
                 Some productivity keys specifically for autotuning pipeline (ck-autotuning repo):

               (local_platform) or (local)   - if 'yes', use parameters of a local platform (to retarget experiment)
               (deps)                        - if 'yes', use recorded deps (to run on the same platform)
               (skip_clean_after)            - if 'yes', do not clean program pipeline after execution 
                                               (keeping low level scripts in tmp directory for low-level debugging)
               (all)                         - print all comparisons of keys (not only when there is a difference)
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              output of a given pipeline

              different_dims - list of different dimensions
            }
    """

    import os

    o=i.get('out','')

    ruoa=i.get('repo_uoa','')
    if i.get('experiment_repo_uoa','')!='': ruoa=i['experiment_repo_uoa']
    cruoa=ruoa
    rruoa=i.get('remote_repo_uoa','')

    # Check if repo remote (to save in json rather than to out)
    remote='no'
    if ruoa!='':
       rx=ck.load_repo_info_from_cache({'repo_uoa':ruoa})
       if rx['return']>0: return rx
       remote=rx.get('dict',{}).get('remote','')

    muoa=i.get('module_uoa','')
    duoa=i.get('data_uoa','')

    pipeline_update=i.get('pipeline_update',{})
    repetitions=i.get('repetitions','')

    if i.get('local_platform','')!='': pipeline_update['local_platform']=i['local_platform']
    if i.get('local','')!='':          pipeline_update['local_platform']=i['local']
    if i.get('skip_clean_after','')!='': pipeline_update['skip_clean_after']=i['skip_clean_after']

    pp=os.getcwd()+os.path.sep

    ii={'out':'',
        'repo_uoa':ruoa,
        'module_uoa':muoa,
        'data_uoa':duoa,
        'action':'search'}
    if rruoa!='': ii['remote_repo_uoa']=rruoa
    r=ck.access(ii)
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

    if remote=='yes':
       rruoa=ruoa
       ruoa=cruoa

    # Check point
    puid=i.get('point','')
    sp=i.get('subpoint','')
    if puid.find('-')>=0:
       puid,sp=puid.split('-')
    puid=puid.strip()
    spid=sp.strip()

    # If point is not specified, get points
    if puid=='':
       ii={'repo_uoa':ruoa,
           'module_uoa':muoa,
           'data_uoa':duoa,
           'action':'list_points'}
       if rruoa!='': ii['remote_repo_uoa']=rruoa
       rx=ck.access(ii)
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
          return {'return':1, 'error':'select a point in a given entry (via --point=[above point UID])'}
       else:
          puid=points[0]

    # If subpoint is not specified, get subpoints
    if spid=='':
       ii={'repo_uoa':ruoa,
           'module_uoa':muoa,
           'data_uoa':duoa,
           'point':puid,
           'action':'list_points'}
       rx=ck.access(ii)
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
    ii={'repo_uoa':ruoa,
        'module_uoa':muoa,
        'data_uoa':duoa,
        'point':puid,
        'subpoint':spid,
        'add_pipeline':'yes',
        'action':'load_point'}
    rx=ck.access(ii)
    if rx['return']>0: return rx

    dd=rx['dict']

    ch=dd.get('flat',{})

    ft=dd.get('features',{})
    choices=ft.get('choices',{})

    cf=dd.get('features',{}) # choices and features
    if 'sub_points' in cf: del(cf['sub_points'])

    deps=dd.get('deps',{})

    # Check if compare with results from another point *******************************
    cduoa=i.get('compare_data_uoa','')
    cruoa=i.get('compare_repo_uoa','')
    cpuid=i.get('compare_point','')
    csp=i.get('compare_subpoint','')
    if cpuid.find('-')>=0:
       cpuid,csp=cpuid.split('-')
    cpuid=cpuid.strip()
    cspid=csp.strip()

    if cduoa!='' or cpuid!='' or cspid!='':
       if o=='con':
          ck.out('Loading dimensions to compare from different entry '+cduoa+' ...')
          ck.out('')

       ii={'repo_uoa':cruoa,
           'module_uoa':muoa,
           'data_uoa':cduoa,
           'point':cpuid,
           'subpoint':cspid,
           'action':'load_point'}
       rx=ck.access(ii)
       if rx['return']>0: return rx

       cdd=rx['dict']

       ch=cdd.get('flat',{})

    #******************************************************************
    if len(ch)==0:
       return {'return':1, 'error':'no flat characteristics in the point to compare'}

    # Trying to get number of statistical repetitions from the entry
    if repetitions=='':
       rpt=ch.get('##pipeline_state#repetitions#min','')
       if rpt=='': rpt=choices.get('repeat','')
       if rpt!='': 
          rpt=int(rpt)
          repetitions=rpt
    
    #******************************************************************
    pipeline_uoa=rx['pipeline_uoa']
    pipeline_uid=rx['pipeline_uid']
    pipeline=rx['pipeline']

    pipeline.update(cf)
    if i.get('deps','')=='yes':
       pdeps=pipeline.get('dependencies',{})
       rz=ck.merge_dicts({'dict1':pdeps, 'dict2':deps})
       if rz['return']>0: return rz
       pdeps=rz['dict1']
    else:
       pdeps={}
    pipeline['dependencies']=pdeps

    if len(pipeline)==0:
       return {'return':1, 'error':'pipeline not found in the entry'}

    #******************************************************************
    if o=='con':
       ck.out('Restarting pipeline ...')
       ck.out('')

    # Attempt to run pipeline
    ii={'action':'run',
        'out':o,
        'module_uoa':cfg['module_deps']['pipeline'],
        'data_uoa':pipeline_uid,
        'pipeline':pipeline,
        'repetitions':repetitions,
        'pipeline_update':pipeline_update,
        'force_pipeline_update':'yes',
        'skip_done':'yes'}
    r=ck.access(ii)
    if r['return']>0: return r

    rlio=r.get('last_iteration_output',{})
    fail=rlio.get('fail','')

    # Check that didn't fail (or failed, if reproducing a bug)
    if fail=='yes':
       if o=='con':
          ck.out('')
          ck.out('Pipeline failed during replay ('+rlio.get('fail_reason','')+')')

    # Flattening characteristics
    chn=r.get('last_stat_analysis',{}).get('dict_flat',{})

    # Record orig and reproduced results, if needed
    rofj=i.get('record_original_flat_json','').replace('$#ck_cur_path#$',pp)
    rrfj=i.get('record_reproduced_flat_json','').replace('$#ck_cur_path#$',pp)

    if rofj!='':
       rx=ck.save_json_to_file({'json_file':rofj, 'dict':ch})
       if rx['return']>0: return rx

    if rrfj!='':
       rx=ck.save_json_to_file({'json_file':rrfj, 'dict':chn})
       if rx['return']>0: return rx

    # Check if skip comparison
    if fail!='yes' and i.get('skip','')!='yes':
       al=i.get('all','')

       # Comparing dicts
       if o=='con':
          ck.out('')
          ck.out('Performing comparison on output dimensions (original vs new results) ...')
          ck.out('')

       ends=i.get('end_of_dims_to_check',[])
       ttc=i.get('threshold_to_compare','')
       if ttc=='': ttc=8.0
       ttc=float(ttc)/100

       import fnmatch

       dc=i.get('dims_to_check',[])

       if len(dc)==0: dc=i.get('dims',[])

       if type(dc)!=list: dc=[dc]

       # On Linux from CMD substitute ^ with #
       for q in range(0, len(dc)):
           dc[q]=dc[q].replace('^','#')

       dd=[]

       # Create a list of all keys in original and new output
       lk=list(ch.keys())
       for q in chn:
           if q not in lk:
              lk.append(q)

       # Compare
       ichecked=0
       for q in sorted(lk):
           v=ch.get(q,None)
           v1=chn.get(q, None)

           if type(v)!=list and type(v)!=dict:
              check=False

              if len(dc)==0: 
                 check=True
              else:
                 for k in dc:
                     if fnmatch.fnmatch(q,k):
                        check=True
                        break

              if check:
                 check=False

                 if len(ends)==0: 
                    check=True
                 else:
                    for k in ends:
                        if q.endswith(k):
                           check=True
                           break

              if check:
                 ichecked+=1

                 ss=q+':  '+str(v)+'  vs  '+str(v1)
                 if v!=v1:
                    if (type(v)==int or type(v)==float) and (type(v1)==int or type(v1)==float) and v!=0:
                       vx=abs(v1-v)/v
                       if vx>ttc:
                          ss+='    diff='+( '%3.1f'% (vx*100))+'%'
                          dd.append(q)
                    else:
                       dd.append(q)

                 if o=='con' and (v!=v1 or al=='yes'):
                    ck.out(ss)
                                                                             
       if o=='con':
          ck.out('')
          if ichecked==0:
             ck.out('Warning: no matched keys found in the output dictionary of the replicated experiment (possibly failed experiment)!')
          elif len(dd)==0:
             ck.out('All existing dimensions are the same (within statistical margin '+str(ttc*100)+'%)!')

       r['different_dims']=dd

    return r

##############################################################################
# rerun experiment == the same as reproduce

def rerun(i):
    """
    Input:  { see 'replay'
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }
    """

    return replay(i)

##############################################################################
# reproduce a given experiment

def reproduce(i):
    """
    Input:  { see 'replay'
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }
    """

    return replay(i)

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

##############################################################################
# stat analysis with multiple points at the same time

def multi_stat_analysis(i):
    """
    Input:  {
              (dict)                        - pre-loaded dict with characteristics that will be flattened
                  or
              (flat_dict)                   - pre-loaded flat dict with characteristics

                                                  USE 'characteristic_list' in dict!

              dict_to_add                   - data to analyze and add to dict

              (process_multi_keys)          - list of keys (starts with) to perform stat analysis on flat array,
                                              by default ['##characteristics#*', '##features#*' '##choices#*'],
                                              if empty, no stat analysis

              (skip_stat_analysis)          - if 'yes', just flatten array and add #min
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              dict_flat         - updated and flattened original dictionary
              max_range_percent - max % range in float/int data (useful to record points with unusual behavior)
              min               - 'yes', if one of monitored values reached min
              max               - 'yes', if one of monitored values reached max
            }

    """

    import copy

    o=i.get('out','')

    ddflat=i.get('flat_dict',{})
    dd=i.get('dict',{})

    # Select keys to prune and flat
    sak=i.get('process_multi_keys','')
    if sak=='': 
       sak=['##characteristics#*', '##features#*', '##choices#*']

    if len(dd)>0 and len(ddflat)==0:
       r=ck.flatten_dict({'dict':dd, 'prune_keys':sak})
       if r['return']>0: return r
       ddflat=r['dict']

    ddx=i.get('dict_to_add',{})

    cddx=copy.deepcopy(ddx)

    # Remove characteristics from original
    ch=ck.get_from_dicts(cddx, 'characteristics', {}, None)

    # Check if characteristics lits (to add a number of experimental results at the same time,
    #   otherwise point by point processing can become very slow
    chl=ck.get_from_dicts(cddx, 'characteristics_list', [], None)
    if len(ch)>0: chl.append(ch)

    # Flatten input dict
    r=ck.flatten_dict({'dict':cddx, 'prune_keys':sak})
    if r['return']>0: return r
    ddf=r['dict']

    mmin=''
    mmax=''
    mdp=''

    ich=0
    for cx in chl:
        ich+=1

        if o=='con':
           ck.out('        Processing characteristic point '+str(ich)+' out of '+str(len(chl))+' ...')

        cddf=copy.deepcopy(ddf) # Prepare clean input (and append iteration of statistical characteristics)

        # Flatten/prune next iteration of statistical characteristic dict and perform basic analysis **********************************
        r=ck.flatten_dict({'dict':{'characteristics':cx}, 'prune_keys':sak})
        if r['return']>0: return r
        ddfi=r['dict']

        # Process multiple values in time packed as @@value1,value2
        for q in ddfi:
            v=ddfi[q]
            x=False
            try: x=v.startswith('@@')
            except AttributeError: pass
            if x:
               v1=ddfi[q][2:].split(',')
               v2=[]
               for k in v1:
                   try: k=float(k)
                   except ValueError: pass
                   v2.append(k)
               ddfi[q]=v2

        # Update original input with iteration from statistical repetition
        cddf.update(ddfi)

        # Prepare input for statistical analysis
        ii={'dict':ddflat, 'dict1':cddf}

        if ich!=len(chl):
           ii['skip_expected_value']='yes'
           ii['skip_min_max']='yes'

        if i.get('skip_stat_analysis','')!='':
           ii['skip_stat_analysis']=i['skip_stat_analysis']

        r=stat_analysis(ii)
        if r['return']>0: return r

        ddflat=r['dict']
        mdp=r['max_range_percent']
        mmin=r['min']
        mmax=r['max']

    return {'return':0, 'dict_flat':ddflat, 'min':mmin, 'max':mmax, 'max_range_percent':mdp}

##############################################################################
# delete multiple points from multiple entries (for example, during Pareto frontier filtering)

def delete_points(i):
    """
    Input:  {
              points       - list of points {'repo_uoa','repo_uid','module_uoa','module_uid','data_uoa','data_uid','point_uid'}
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    o=i.get('out','')

    points=i['points']

    apoints={}

    # Get unique repo/module/data and aggregate points
    for q in points:
        ruoa=q.get('repo_uoa','')
        ruid=q.get('repo_uid','')
        muoa=q.get('module_uoa','')
        muid=q.get('module_uid','')
        duoa=q.get('data_uoa','')
        duid=q.get('data_uid','')
        puid=q.get('point_uid','')

        k=ruoa+';'+ruid+';'+muoa+';'+muid+';'+duoa+';'+duid

        if k not in apoints:
           apoints[k]=q
           apoints[k]['point_uids']=[]

        apoints[k]['point_uids'].append(puid)

    # Go through entries and delete points ...
    for q in apoints:
        qq=apoints[q]
        ruoa=qq.get('repo_uoa','')
        ruid=qq.get('repo_uid','')
        muoa=qq.get('module_uoa','')
        muid=qq.get('module_uid','')
        duoa=qq.get('data_uoa','')
        duid=qq.get('data_uid','')
        puids=qq.get('point_uids',[])

        # Load and lock entry
        ii={'action':'load',
            'repo_uoa':ruid,
            'module_uoa':muid,
            'data_uoa':duid,
            'get_lock':'yes'}

        rx=ck.access(ii)
        if rx['return']>0: return rx

        lock_uid=rx['lock_uid']
        p=rx['path']
        d=rx['dict']

        dp=d.get('points', '')
        if dp=='': dp=0
        dp=int(dp)
        dp-=len(puids)
        if dp<0: dp=0 # should not be, but just in case

        d['points']=str(dp)

        # Remove files for each point
        for k in puids:
            px='ckp-'+k+'.'

            dirList=os.listdir(p)

            for fn in dirList:
                if fn.startswith(px):
                   os.remove(os.path.join(p,fn))

        # Update and unlock entry
        ii['action']='update'
        del(ii['get_lock'])
        ii['unlock_uid']=lock_uid
        ii['dict']=d
        rx=ck.access(ii)
        if rx['return']>0: return rx

    return {'return':0}

##############################################################################
# view entries as html

def html_viewer(i):
    """
    Input:  {
              data_uoa

              url_base
              url_pull

              url_cid

              (subgraph)

              url_pull_tmp
              tmp_data_uoa

              url_wiki

              html_share

              form_name     - current form name

              (all_params)
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    h=''
    st=''
    raw='yes'
    top='yes'

    duoa=i['data_uoa']
    burl=i['url_base']
    purl=i['url_pull']
    wurl=i.get('url_wiki','')

    url_cid=i.get('url_cid','')

    tpurl=i['url_pull_tmp']
    tpuoa=i['tmp_data_uoa']

    ap=i.get('all_params',{})

    sp=ap.get('subpoint','')

    ts=ap.get('table_sort','')
    its=-1
    if ts!='': its=int(ts)

    rts=ap.get('reverse_table_sort','')
    irts=-1
    if rts!='': irts=int(rts)

    ruoa=ap.get('ck_top_repo','')
    muoa=ap.get('ck_top_module','')

    cparams=ap.get('graph_params','') # current graph params

    hshare=i.get('html_share','')

    # Check if data is available
    if duoa!='':
       # Load entry
       rx=ck.access({'action':'load',
                     'module_uoa':work['self_module_uid'],
                     'data_uoa':duoa})
       if rx['return']>0: return rx

       pp=rx['path']

       dd=rx['dict']
       duid=rx['data_uid']
       muid=rx['module_uid']

       name=dd.get('name','')

       sv=ap.get(var_post_subview,'')

       if sv=='' and dd.get('subview_uoa','')!='':
          sv=dd['subview_uoa']

       if sv!='':
          burl+=var_post_subview+'='+sv+'&'

       # Get list of experiment views
       r=ck.access({'action':'list',
                    'module_uoa':cfg['module_deps']['experiment.view'],
                    'add_info':'yes',
                    'add_meta':'yes'})
       if r['return']>0: return r
       lm=r['lst']

       r=ck.access({'action':'convert_ck_list_to_select_data',
                    'module_uoa':cfg['module_deps']['wfe'],
                    'lst':lm, 
                    'add_empty':'no', 
                    'sort':'yes', 
                    'value_uoa':sv, 
                    'ignore_remote':'yes'})
       if r['return']>0: return r
       dlm=r['data']
       if r.get('value_uid','')!='': sv=r['value_uid']

       onchange='submit()'

       ii={'action':'create_selector', 
           'module_uoa':cfg['module_deps']['wfe'],
           'data':dlm, 
           'name':var_post_subview, 
           'onchange':onchange, 
           'style':'width:300px;'}
       if sv!='': ii['selected_value']=sv
       r=ck.access(ii)
       if r['return']>0: return r

       h+='Select experiment view:&nbsp;&nbsp;'+r['html']

       # Get keys from experiment view (meta - dict of selected experiment.view entry)
       rk=[]
       rkd=[]

       if sv=='': isv=0
       else:
          for isv in range(0, len(lm)):
              if sv==lm[isv]['data_uid'] or sv==lm[isv]['data_uoa']:
                 break

       if isv<len(lm):
          meta=lm[isv].get('meta',{})
       else:
          meta={}
       rk=meta.get('flat_keys',[])
       rkd=meta.get('flat_keys_desc',[])
       no_replay=meta.get('no_replay','')

       # Array with data from points
       arr=[]

       # Check points
       dirList=os.listdir(pp)
       for fn in sorted(dirList):
           if fn.endswith('.flat.json'):
              pp1=fn[:-10]
              pp2=pp1[4:]
              drz={}

              fpf1=os.path.join(pp, fn)
              rz=ck.load_json_file({'json_file':fpf1})
              if rz['return']==0:
                 drz=rz['dict']
                 kdrz=sorted(list(drz.keys()))

                 # Create vector
                 vv=[]
                 vvv=[]
                 vvn=[]

                 for iv in range(0, len(rk)):
                     k=rk[iv]
                     v=None
                     v2=None
                     v3=None

                     dd={}
                     if iv<len(rkd): 
                        dd=rkd[iv]

                     vak=dd.get('view_add_key','')

                     if '*' not in k and '?' not in k:
                        k1=k+'#min'
                        if k1 in drz:
                           v=drz[k1]

                        # Check variation
                        k2x=k+'#all_unique'
                        k2=k+'#range_percent'
                        if len(drz.get(k2x,[]))>1 and k2 in drz:
                           vx=drz[k2]

                           fvx=-1.0
                           try:
                              fvx=float(vx)*100
                           except ValueError:
                              pass

                           if fvx!=-1.0:
                              v2=fvx

                              # Check number of experiments
                              if k+'#all' in drz:
                                 v3=len(drz[k+'#all'])

                     else:
                        import fnmatch
                        v=''
                        k1=k+'#min'
                        for kk in kdrz:
                            if fnmatch.fnmatch(kk,k1):
                               vx=drz[kk]
                               if vx!=None:
                                  if v!='': v+=' '
                                  if vak=='yes':
                                     tx=kk.rfind('#')
                                     if tx>0:
                                        tx1=kk.rfind('#',0,tx-1)
                                        if tx1>0:
                                           v+=kk[tx1+1:tx]
                                  if vx!='':
                                     if vak=='yes': v+='='
                                     v+=str(vx)

                     vv.append(v)
                     vvv.append(v2)
                     vvn.append(v3)

                 arr.append({'main':vv, 'var':vvv, 'uid':pp2})

       # Sort, if needed
       if its!=-1:
          arr1=sorted(arr, key=lambda k: k['main'][its])
          arr=arr1
       elif irts!=-1:
          arr1=sorted(arr, key=lambda k: k['main'][irts], reverse=True)
          arr=arr1

       # Prepare view
#       h+='<div id="ck_entries">\n'

       if len(arr)==0:
          h+='<br>No points found!<br>\n'
       else:
          # add script to copy to Clipboard
          h+='\n\n<script language="JavaScript">function copyToClipboard (text) {window.prompt ("Copy to clipboard: Ctrl+C, Enter", text);}</script>\n\n' 

          h+=' <table class="ck_table" border="0">\n'
          ss=''
          ss1=''
          ss2=''

          px=0
          for ip in range(-2, len(arr)):
              if ip==-2:
                 ############################ Prepare header
                 h+='  <tr style="background-color:#cfcfff;">\n'
                 h+='    <td valign="top" class="light_right_in_table"></td>\n'
                 h+='    <td valign="top" colspan="'+str(len(rkd))+'" class="light_right_in_table" align="center"><i><b>Dimensions</b></i></td>\n'
                 h+='    <td valign="top" colspan="3" class="light_right_in_table" align="center"><i><b>Raw JSON files</b></i></td>\n'
                 h+='    <td valign="top" class="light_right_in_table"></td>\n'
                 if no_replay!='yes':
                    h+='    <td valign="top" class="" align="center"><i><b></b></i></td>\n'
                 h+'   </tr>\n'

                 h+='  <tr style="background-color:#cfcfff;">\n'
                 h+='    <td valign="top" class="light_bottom_in_table light_right_in_table"><b>#</b></td>\n'
                 for iv in range(0, len(rk)):
                     v=''
                     if iv<len(rkd): v=rkd[iv].get('desc','')
                     xs=''
                     if iv==len(rk)-1: xs='light_right_in_table'
                     xurl=burl+'wcid='+muid+':'+duid
                     if sp!='': xurl+='&subpoint='+sp
                     rv=''
                     if iv==its: rv='reverse_'
                     xurl+='&'+rv+'table_sort='+str(iv)
                     h+='    <td valign="top" align="right" class="light_bottom_in_table '+xs+'"><b><a href="'+xurl+'">'+v+'</a></b></td>\n'

                 h+='    <td valign="top" align="center" class="light_bottom_in_table"><b>Aggregated flat data</b></td>\n'
                 h+='    <td valign="top" align="center" class="light_bottom_in_table"><b>Features</b></td>\n'
                 h+='    <td valign="top" align="center" class="light_right_in_table light_bottom_in_table"><b>Flat features</b></td>\n'
                 h+='    <td valign="top" align="right" class="light_right_in_table light_bottom_in_table"><b>Point UID</b></td>\n'
                 if no_replay!='yes':
                    h+='    <td valign="top" align="center" class="light_bottom_in_table"><b>Replay (reproduce)</b></td>\n'

              else:
                 e1=''
                 e2=''
                 if ip==-1:
                    ##################### Put as first pre-selected point (useful when clicked from interactive graphs)
                    if sp=='': continue

                    px+=1
                    
                    found=False
                    for isp in range(0, len(arr)):
                        if arr[isp]['uid']==sp: 
                           found=True
                           break
 
                    if found:
                       zz=arr[isp]
                       vv=zz['main']
                       vvv=zz['var']
                       vp=zz['uid']

                       e1='<i>'
                       e2='</i>'
                       ss1='color: #7f0000;'
                 else:
                    px+=1

                    zz=arr[ip]
                    vv=zz['main']
                    vvv=zz['var']
                    vp=zz['uid']

                    if sp!='' and vp==sp: continue

                    ss1=''

                 h+='  <tr style="'+ss+ss1+'">\n'
                 h+='    <td valign="top" class="light_right_in_table">'+e1+str(px)+e2+'</td>\n'
                 for iv in range(0, len(vv)):
                     v=vv[iv]
                     v2=vvv[iv]

                     dd={}
                     if iv<len(rkd): 
                        dd=rkd[iv]

                     tp=dd.get('type','')

                     xs=''
                     if iv==len(vv)-1: xs='light_right_in_table'

                     xv=''
                     if v2!=None and v2!=0.0:
                        xv=''
                        if v2>5: xv+='<b>'

                        xv+='&nbsp;&plusmn;&nbsp;'+('%3.1f' % v2)+'%'

                        v3=vvn[iv]
                        if v3!='None':
                           xv+='&nbsp;<i>('+str(v3)+')</i>'

                        if v2>5: xv+='</b>'

                     if dd.get('format','')=='':
                        ssv=str(v)
                     else:
                        try:
                           ssv=(dd['format'] % float(str(v)))
                        except ValueError:
                           ssv=''

                     sv=ssv+xv
                     
                     if tp=='uoa':
                        xmuoa=dd.get('module_uoa','')
                        if xmuoa!='':
                           sv='<a href="'+burl+'wcid='+xmuoa+':'+str(v)+'">'+sv+'</a>'
                     else:
                        if len(sv)>100:
                           sv='<input type="button" class="ck_small_button" onClick="copyToClipboard(\''+sv+'\');" value="View">'

                     h+='    <td valign="top" align="right" class="'+xs+'">'+e1+sv+e2+'</td>\n'

                 xurl=purl+'ckp-'+str(vp)

                 ss2=''
#                 if ss!='': ss2='light_green_in_table1'
                 h+='    <td valign="top" align="center" class="'+ss2+'"><a href="'+xurl+'.flat.json'+'">View</a></td>\n'
                 h+='    <td valign="top" align="center" class="'+ss2+'"><a href="'+xurl+'.features.json'+'">View</a></td>\n'
                 h+='    <td valign="top" align="center" class="light_right_in_table '+ss2+'"><a href="'+xurl+'.features_flat.json'+'">View</a></td>\n'
                 h+='    <td valign="top" align="right" class="light_right_in_table">'+e1+str(vp)+e2+'</td>\n'
                 if no_replay!='yes':
                    h+='    <td valign="top" align="center"><input type="button" class="ck_small_button" onClick="copyToClipboard(\''+'ck replay experiment:'+duoa+' --point='+str(vp)+'\');" value="Copy to clipboard"></td>\n'

                 if ss=='': ss='background-color: #efefff'
                 else: ss=''
           
              h+='  </tr>\n'
          h+=' </table>\n'
#       h+='</div>\n'

    return {'return':0, 'raw':raw, 'show_top':top, 'html':h, 'style':st}

##############################################################################
# crowdsource experiments

def crowdsource(i):
    """
    Input:  {
              (scenario)         - UOA of a module with crowdsourcing scenario
              (tags)             - extra tags to prunce experimental scenarios

              (quiet)            - do not ask questions, but select random ...
              (skip_welcome)     - if 'yes', do not print welcome header
              
              (skip_exchange)    - if 'yes', do not exchange platform info
                                   (development mode)

              (change_user)      - if yes', change user

              (local)            - if 'yes', use local repo for exchange (local autotuning/benchmarking)
              (exchange_repo)    - which repo to record/update info (remote-ck by default)
              (exchange_subrepo) - if remote, remote repo UOA

              (once)             - if 'yes', run scenario ones (useful for autotuning a given program)
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    # Setting output
    o=i.get('out','')
    oo=''
    if o=='con': oo='con'

    scenario=i.get('scenario','')

    et=i.get('tags','')
    if et!='': et+=','
    et+='crowdsource,experiments'

    quiet=i.get('quiet','')

    finish=False
    sit=0
    sdeps={}

    once=i.get('once','')

    pi={}
    sw=i.get('skip_welcome','')

    while not finish:
       sit+=1

       # Selecting scenario
       if o=='con':
          ck.out(line)
          ck.out('Scenario iteration: '+str(sit))

          if scenario=='':
             ck.out('')
             ck.out('Detecting available crowdsourcing scenarios ...')

             ii={'action':'search',
                 'module_uoa':cfg['module_deps']['module'],
                 'add_meta':'yes',
                 'add_info':'yes',
                 'scenario':scenario,
                 'tags':et}
             r=ck.access(ii)
             if r['return']>0: return r

             lst=r['lst']

             if len(lst)==0:
                if o=='con':ck.out('')
                return {'return':1, 'error':'no local scenarios to crowdsource experiments found!\n\nYou can install "ck-crowdtuning" shared repository via\n  $ ck pull repo:ck-crowdtuning\n\nThis will let you participate in collaborative program optimization and benchmarking'}  
             elif len(lst)==1:
                scenario=lst[0].get('data_uid','')
             else:
                zss=sorted(lst, key=lambda v: (int(v.get('meta',{}).get('priority',0)), v['data_uoa']))

                if quiet=='yes':
                   scenario=zss[0]['data_uid']
                else:
                   ck.out('')
                   ck.out('More than one experimental scenario found:')
                   ck.out('')
                   zz={}
                   iz=0
                   for z1 in zss:
                       z=z1['data_uid']
                       zu=z1['data_uoa']

                       zux=z1.get('info',{}).get('data_name','')
                       if zux!='': zu=zux

                       zs=str(iz)
                       zz[zs]=z

                       ck.out(zs+') '+zu+' ('+z+')')

                       iz+=1

                   ck.out('')
                   rx=ck.inp({'text':'Select scenario number you want to participate in (or Enter to select 0): '})
                   x=rx['string'].strip()
                   if x=='': x='0'

                   if x not in zz:
                      return {'return':1, 'error':'scenario number is not recognized'}

                   scenario=zz[x]
             
          # Print selected scenario
          ii={'action':'load',
              'module_uoa':cfg['module_deps']['module'],
              'data_uoa':scenario}
          rs=ck.access(ii)
          if rs['return']>0: return rs

          d=rs['dict']

          sn=d.get('desc','')
          if sn=='': sn=scenario
          else:      sn+=' ('+scenario+')'

          if o=='con':
             ck.out('')
             ck.out('Executing scenario "'+sn+'" ...')
             ck.out('')

          # Executing scenario
          i['module_uoa']=scenario
          i['platform_info']=pi
          i['skip_welcome']=sw

          r=ck.access(i)
          if r['return']>0: 
             if o=='con':
                ck.out(line)
                ck.out('Scenario FAILED: '+r['error'])
                ck.out('')

                if quiet!='yes':
                   ck.inp({'text':'Press Enter to continue: '})

             if o!='con' or quiet=='yes':
                import time
                time.sleep(4)
          else:
             pi=r.get('platform_info',{})
             sw='yes'

       if once=='yes':
          finish=True

    ck.out(line)
    ck.out('Experiments completed!')

    return {'return':0}
