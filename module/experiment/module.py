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
    ddfe={}
    if euid!='' and spbf=='yes':
       if len(ft)==0:
          return {'return':1, 'error':'can\'t search by features when they are not present'}

       if o=='con': ck.out('    Searching points by features ...')

       for q in range(1, ipoints+1):
           sp=str(q)
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

       point=ipoints
       sp=str(ipoints)
       spz=sp.zfill(8)
       fp=spz+'.json'
       fp1=os.path.join(p, fp)

       if o=='con': 
          ck.out('  Saving point '+sp+' ...')

       r=ck.save_json_to_file({'json_file':fp1, 'dict':dd, 'sort_keys':sk})
       if r['return']>0: return r

       dd['points']=sp

    # Perform statistical analysis
    if point!=0:

       # Flatten submitted data
       r=ck.flatten_dict({'dict':dd})
       if r['return']>0: return r
       ddf=r['dict']

       # Load flattened and statistically analyzed data
       spz=str(point).zfill(8)
       fpflat=spz+'.flat.json'
       fpflat1=os.path.join(p, fpflat)

       if os.path.isfile(fpflat1):
          r=ck.load_json_file({'json_file':fpflat1})
          if r['return']>0: return r
          ddfe=r['dict']

       r=stat_analysis({'dict':ddfe, 'dict1':ddf})
       if r['return']>0: return r
       ddfe=r['dict']

       # Save updated flat dict to file
       r=ck.save_json_to_file({'json_file':fpflat1, 'dict':ddfe, 'sort_keys':sk})
       if r['return']>0: return r

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

              Graphical parameters:
                plot_type                  - mpl_2d_scatter

            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """


    o=i.get('out','')

    # Get table from entries
    r=get(i)
    if r['return']>0: return r
    table=r['table']

    if len(table)==0:
       return {'return':1, 'error':'no points found'}

    # Prepare libraries
    pt=i.get('plot_type','')
    if pt.startswith('mpl_'):

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

       xerr=i.get('display_x_error_bar','')
       yerr=i.get('display_y_error_bar','')

       # Add points
       s=0
       for g in table:
           gt=table[g]

           if pt=='mpl_2d_scatter':
              mx=[]
              mxerr=[]
              my=[]
              myerr=[]

              for u in gt:
                  iu=0

                  mx.append(u[iu])
                  iu+=1

                  if xerr=='yes':
                     mxerr.append(u[iu])
                     iu+=1 

                  my.append(u[iu])
                  iu+=1

                  if yerr=='yes':
                     myerr.append(u[iu])
                     iu+=1 

              if xerr!='yes' and yerr!='yes':
                 sp.scatter(mx, my, s=int(gs[s]['size']), edgecolor=gs[s]['color'], c=gs[s]['color'], marker=gs[s]['marker'])
              elif xerr!='yes':
                 sp.errorbar(mx, my, myerr, myerr, capsize=0, ls='none', c=gs[s]['color'])
              elif yerr!='yes':
                 sp.errorbar(mx, my, mxerr, capsize=0, ls='none', c=gs[s]['color'])
              else:
                 sp.errorbar(mx, my, mxerr, myerr, capsize=0, ls='none', c=gs[s]['color'])

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

    else:
       return {'return':1, 'error':'this type of plot ('+pt+') is not supported'}

    return {'return':0}

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

              (substitute_x_with_loop)              - if 'yes', substitute first vector dimension with a loop

              (sort_index)                          - if !='', sort by this number within vector (i.e. 0 - X, 1 - Y, etc)
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
    fkl=i.get('flat_keys_list',[])
    rfkl=[] # real flat keys (if all)
    trfkl=[]

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
               if fki!='' or len(fkl)==0:
                  # Add all sorted (otherwise there is no order in python dict
                  for k in sorted(df.keys()):
                      if (fki=='' or k.startswith(fki)) and (fkie=='' or k.endswith(fkie)):
                         if len(rfkl)==0:
                            trfkl.append(k)
                         v=df[k]
                         vect.append(v)
                  if len(trfkl)!=0:
                     rfkl=trfkl
               else:
                  for k in fkl:
                      v=df.get(k,'')
                      try:
                         v=float(v) # TBD
                      except Exception as e:
                         v=0
                         pass
                      vect.append(v)
                     
               # Add vector
               if sigraph not in table: table[sigraph]=[]

               table[sigraph].append(vect)

    if len(rfkl)==0 and len(fkl)!=0: rfkl=fkl

    # If sort
    si=i.get('sort_index','')
    if si!='':
       isi=int(si)
       for sg in table:
           x=table[sg]
           y=sorted(x, key=lambda var: var[isi])
           table[sg]=y

    # Substitute all X with a loop (usually to sort Y and compare with predictions in scatter graphs, etc)
    if i.get('substitute_x_with_loop','')=='yes':
       for sg in table:
           h=0
           x=table[sg]
           for q in range(0, len(x)):
               h+=1
	       x[q][0]=h
           table[sg]=x

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
            try:
              v=str(float(v)).replace(',', dec)
            except Exception as e:
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
# Statistical analysis of experimental results

def stat_analysis(i):
    """

    Input:  {
              dict         - existing flat dict 
              dict1        - new flat dict to add
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              dict         - updated dict
            }

    """

    d=i['dict']
    d1=i['dict1']

    for k in d1:
        v1=d1[k]

        # Put all values (useful to calculate averages, deviations, etc)
        k_all=k+'#all'
        v=d.get(k_all,[])
        if v1 not in v:
           v.append(v1)
           d[k_all]=v

           # Try to convert to float
           vfs=True # successfully converted
           try:
              vf=float(v1)
           except Exception as e:
              vfs=False 
              pass

           if not vfs:
              d[k]=v1
           else:
              # Calculate min
              k_min=k+'#min'

              v=d.get(k_min,'')
              if v=='':
                 vfmin=vf
              else:
                 vfmin=float(v)
                 if vf<vfmin: vfmin=vf
              d[k_min]=str(vfmin)

              # Add min to original (for compatibility with CM)
              d[k]=str(vfmin)

              # Calculate max
              k_max=k+'#max'

              v=d.get(k_max,'')
              if v=='':
                 vfmax=vf
              else:
                 vfmax=float(v)
                 if vf>vfmax: vfmax=vf
              d[k_max]=str(vfmax)

              # Calculate #delta (max-min)
              k_delta=k+'#delta'
              d[k_delta]=str(vfmax-vfmin)

              # Calculate #delta percent (max-min)/min
              if vfmax!=vfmin:
                 k_delta=k+'#delta_percent'
                 d[k_delta]=str((vfmax-vfmin)/vfmin)

              # Calculate average
              k_average=k+'#average'

    return {'return':0, 'dict':d}
