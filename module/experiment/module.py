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
              dict
              (experiment_repo_uoa) - if defined, use it instead of repo_uoa
                                      (useful for remote repositories)
              (experiment_uoa)      - if entry with aggregated experiments is already known
              (experiment_uid)      - if entry with aggregated experiments is already known
              (add_new)             - if 'yes', do not search for existing entry,
                                      but add a new one!

              (ignore_update)       - if 'yes', do not record update control info (date, user, etc)

              (sort_keys)           - if 'yes', sort keys in output json
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    o=i.get('out','')

    dd=i.get('dict',{})

    if len(dd)==0:
       return {'return':1, 'error':'no data provided'}

    an=i.get('add_new','')
    euoa=i.get('experiment_uoa','')
    euid=i.get('experiment_uid','')

    ruoa=i.get('repo_uoa','')

    sk=i.get('sort_keys','')

    xruoa=i.get('experiment_repo_uoa','')
    if xruoa!='': ruoa=xruoa

    # Search for an entry to aggregate, if needed
    if an!='yes' and (euoa=='' and euid==''):
       if o=='con':
          ck.out('Searching species in the repository with given meta info ...')
       meta=dd.get('meta',{})
       if len(meta)==0:
          return {'return':1, 'error':'meta is not defined - can\'t aggregate'}

       ii={'action':'search',
           'common_func':'yes',
           'repo_uoa': ruoa,
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

    # Adding/updating entry
    ii={'common_func':'yes',
        'repo_uoa': ruoa,
        'module_uoa': work['self_module_uoa'],
        'dict':dd,
        'ignore_update':i.get('ignore_update',''),
        'sort_keys':sk
       }

    if an=='yes' or (euoa=='' and euid==''):
       ii['action']='add'
       if o=='con':
          ck.out('  Species was not found. Adding new entry ...')
    else:
       ii['action']='update'
       ii['data_uoa']=euoa
       ii['data_uid']=euid

#    print (ii)
    r=ck.access(ii)
#    print (r)
     
    return r
