#
# Collective Knowledge (various graphs for experiment)
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

    # Check if table already there
    table=i.get('table',[])
    if len(table)==0:
       # Get table from entries
       tmp_a=i.get('action','')
       tmp_mu=i.get('module_uoa','')

       i['action']='get'
       i['module_uoa']=cfg['module_deps']['experiment']

       r=ck.access(i)
       if r['return']>0: return r

       table=r['table']

       i['action']=tmp_a
       i['module_uoa']=tmp_mu
    else:
       # If sort/substitute

       si=i.get('sort_index','')
       if si!='':
          rx=ck.access({'action':'sort_table', 
                        'module_uoa':cfg['module_deps']['experiment'], 
                        'table':table, 
                        'sort_index':si})
          if rx['return']>0: return rx
          table=rx['table']

       # Substitute all X with a loop (usually to sort Y and compare with predictions in scatter graphs, etc)
       if i.get('substitute_x_with_loop','')=='yes':
          rx=ck.access({'action':'substitute_x_with_loop', 
                        'module_uoa':cfg['module_deps']['experiment'], 
                        'table':table})
          if rx['return']>0: return rx
          table=rx['table']

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

                  # Check if no None
                  partial=False
                  for q in u:
                      if q==None:
                         partial=True
                         break

                  if not partial:
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

              if xerr=='yes' and yerr=='yes':
                 sp.errorbar(mx, my, xerr=mxerr, yerr=myerr, ls='none', c=gs[s]['color'])
              elif xerr=='yes' and yerr!='yes':
                 sp.errorbar(mx, my, xerr=mxerr, ls='none', c=gs[s]['color'])
              elif yerr=='yes' and xerr!='yes':
                  sp.errorbar(mx, my, yerr=myerr, ls='none', c=gs[s]['color'])
              else:
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

    else:
       return {'return':1, 'error':'this type of plot ('+pt+') is not supported'}

    return {'return':0}
