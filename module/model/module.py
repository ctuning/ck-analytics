#
# Collective Knowledge (Universal predictive model)
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
# use model

def use(i):
    """

    Input:  {}

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    print ('use model')

    return {'return':0}

##############################################################################
# build model (universal)

def build(i):
    """

    Input:  {
              Select entries:

                (repo_uoa) or (experiment_repo_uoa)     - can be wild cards
                (remote_repo_uoa)                       - if remote access, use this as a remote repo UOA
                (module_uoa) or (experiment_module_uoa) - can be wild cards
                (data_uoa) or (experiment_data_uoa)     - can be wild cards

                (repo_uoa_list)                         - list of repos to search
                (module_uoa_list)                       - list of module to search
                (data_uoa_list)                         - list of data to search

                (search_dict)                           - search dict
                (ignore_case)                           - if 'yes', ignore case when searching

                (features_flat_keys_list)               - list of flat keys to extract from points into table
                                                          (order is important: for example, for plot -> X,Y,Z)
                (features_flat_keys_index)              - add all flat keys starting from this index 
                                                          (for example, ##features#)

                (characteristics_flat_keys_list)        - list of flat keys to extract from points into table
                                                          (order is important: for example, for plot -> X,Y,Z)
                (characteristics_flat_keys_index)       - add all flat keys starting from this index 
                                                          (for example, ##features#)

              Model:
                model_module_uoa                        - model module
                model_name                              - model name
                (model_out_file)                        - model output file, otherwise generated as tmp file
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import copy

    o=i.get('out','')
    i['out']=''

    mmuoa=i['model_module_uoa']
    mn=i['model_name']

    # Get table through experiment module for features
    iif=copy.deepcopy(i)
    iif['action']='get'
    iif['module_uoa']=cfg['module_deps']['experiment']
    iif['flat_keys_list']=i.get('features_flat_keys_list',[])
    iif['flat_keys_index']=i.get('features_flat_keys_index','')
    r=ck.access(iif)
    if r['return']>0: return r
    ftable=r['table'].get('0',[])
    fkeys=r['real_keys']

    if len(ftable)==0:
       return {'return':1, 'error':'no points found'}

    # Get table through experiment module for characteristics
    iic=copy.deepcopy(i)
    iic['action']='get'
    iic['module_uoa']=cfg['module_deps']['experiment']
    iic['flat_keys_list']=i.get('characteristics_flat_keys_list',[])
    iic['flat_keys_index']=i.get('characteristics_flat_keys_index','')
    r=ck.access(iic)
    if r['return']>0: return r
    ctable=r['table'].get('0',[])
    ckeys=r['real_keys']

    if len(ctable)==0:
       return {'return':1, 'error':'no points found'}

    # Calling model
    ii={'action':'build',
        'module_uoa':mmuoa,
        'model_name':mn,
        'model_out_file':i.get('model_out_file',''),
        'features_table': ftable,
        'features_keys': fkeys,
        'characteristics_table': ctable,
        'characteristics_keys': ckeys
       }
    r=ck.access(ii)
    if r['return']>0: return r

    mf=r['model_file']

    if o=='con':
       ck.out('Generated model was saved into file '+mf)

    i['out']=o

    return r

##############################################################################
# validate model (universal)

def validate(i):
    """

    Input:  {
              Select entries:

                (repo_uoa) or (experiment_repo_uoa)     - can be wild cards
                (remote_repo_uoa)                       - if remote access, use this as a remote repo UOA
                (module_uoa) or (experiment_module_uoa) - can be wild cards
                (data_uoa) or (experiment_data_uoa)     - can be wild cards

                (repo_uoa_list)                         - list of repos to search
                (module_uoa_list)                       - list of module to search
                (data_uoa_list)                         - list of data to search

                (search_dict)                           - search dict
                (ignore_case)                           - if 'yes', ignore case when searching

                (features_flat_keys_list)               - list of flat keys to extract from points into table
                                                          (order is important: for example, for plot -> X,Y,Z)
                (features_flat_keys_index)              - add all flat keys starting from this index 
                                                          (for example, ##features#)

                (characteristics_flat_keys_list)        - list of flat keys to extract from points into table
                                                          (order is important: for example, for plot -> X,Y,Z)
                (characteristics_flat_keys_index)       - add all flat keys starting from this index 
                                                          (for example, ##features#)

              Model:
                model_module_uoa                        - model module
                model_name                              - model name
                model_file                              - model file
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import copy
    import math

    o=i.get('out','')
    i['out']=''

    mmuoa=i['model_module_uoa']
    mn=i['model_name']
    mf=i['model_file']

    # Get table through experiment module for features
    iif=copy.deepcopy(i)
    iif['action']='get'
    iif['module_uoa']=cfg['module_deps']['experiment']
    iif['flat_keys_list']=i.get('features_flat_keys_list',[])
    iif['flat_keys_index']=i.get('features_flat_keys_index','')
    r=ck.access(iif)
    if r['return']>0: return r
    ftable=r['table'].get('0',[])
    fkeys=r['real_keys']

    if len(ftable)==0:
       return {'return':1, 'error':'no points found'}

    # Get table through experiment module for characteristics
    iic=copy.deepcopy(i)
    iic['action']='get'
    iic['module_uoa']=cfg['module_deps']['experiment']
    iic['flat_keys_list']=i.get('characteristics_flat_keys_list',[])
    iic['flat_keys_index']=i.get('characteristics_flat_keys_index','')
    r=ck.access(iic)
    if r['return']>0: return r
    ctable=r['table'].get('0',[])
    ckeys=r['real_keys']

    lctable=len(ctable)
    if lctable==0:
       return {'return':1, 'error':'no points found'}

    # Calling model
    ii={'action':'validate',
        'module_uoa':mmuoa,
        'model_name':mn,
        'model_file':mf,
        'features_table': ftable,
        'features_keys': fkeys
       }
    r=ck.access(ii)
    if r['return']>0: return r

    pt=r['prediction_table']
    lpt=len(pt)

    if lctable!=lpt:
       return {'return':1, 'error':'length of characteristic table ('+str(lctable)+') is not the same as table with predictions ('+str(lpt)+')'}

    # Checking model
    s=0.0

    for k in range(0, lctable):
        v=ctable[k][0]
        pv=pt[k][0]

        s+=(v-pv)*(v-pv)
        diff=abs(pv-v)/v
        x1=''
        if diff>0.1: #10%
           x1=' ***'

        line="%11.3f" % v + "%11.3f" % pv + "%7.3f" % diff + x1
        ck.out(line)

    rmse=math.sqrt(s/lctable)

#    rr['rmse']=str(rmse)
#    rr['max_var']=var

    ck.out('')
    ck.out('Model RMSE='+str(rmse))

    # Visualize?
    if i.get('visualize','')=='yes':
       table={"0":[], "1":[]}
       for k in range(0, lctable):
           table["0"].append([0, ctable[k][0]])
           table["1"].append([0, pt[k][0]])

       ii={'action':'plot',
           'module_uoa':cfg['module_deps']['experiment'],
           'table':table,
           'sort_index':'1',
           'substitute_x_with_loop':'yes'}
       iig=i.get('graph_params',{})
       ii.update(iig)
       r=ck.access(ii)
       if r['return']>0: return r

    i['out']=o
    return {'return':0}
