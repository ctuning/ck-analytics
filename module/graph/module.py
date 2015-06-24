
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
var_post_subgraph='subgraph'
var_post_cur_subgraph='cur_subgraph'
var_post_tmp_graph_file='graph_tmp_file'
var_post_refresh_graph='refresh_graph'
var_post_reset_graph='reset_graph'
var_post_autorefresh='graph_autorefresh'
var_post_autorefresh_time='graph_autorefresh_time'

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
              (load_table_from_file)                     - load table directly from file
                         or
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

              (flat_keys_list_separate_graphs)      - [ [keys], [keys], ...] - several graphs ...

              (sort_index)                          - (int) dimension to sort 

              (labels_for_separate_graphs)          - list of labels for separate graphs

              (flat_keys_index)                     - add all flat keys starting from this index 
              (flat_keys_index_end)                 - add all flat keys ending with this index (default #min)

              (out_to_file)                         - save picture or html to file, if supported 
                                                        (will be preserved and not replotted - useful to have a copy of an original image
                                                         when replotting graphs in interactive papers)

              (out_repo_uoa)                        - repo uoa where to save file (when reproducing graphs for interactive articles)
              (out_module_uoa)                      - module uoa where to save file (when reproducing graphs for interactive articles)
              (out_data_uoa)                        - data uoa where to save file (when reproducing graphs for interactive articles)

              (save_table_to_json_file)             - save table to json file
              (save_info_table_to_json_file)        - save info table (mtable) to json file
              (save_table_to_csv_file)              - save table to csv file (need keys)

              (save_to_html)                        - if interactive or html-based graph, save to html
              (save_to_style)                       - if interactive or html-based graph, save to style (if needed)

              Graphical parameters:
                plot_type                  - mpl_2d_scatter
                point_style                - dict, setting point style for each separate graph {"0", "1", etc}

                x_ticks_period             - (int) for bar graphs, put periodicity when to show number 


            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              (html)       - html, if HTML generator such as d3
              (style)      - style for html, if HTML generator such as d3
            }

    """

    import os

    o=i.get('out','')

    pst=i.get('point_style',{})

    otf=i.get('out_to_file','')
    otf_ruoa=i.get('out_repo_uoa','')
    otf_muoa=i.get('out_module_uoa','')
    otf_duoa=i.get('out_data_uoa','')

    xtp=i.get('x_ticks_period','')
    if xtp=='' or xtp==0: xtp=1
    if xtp!='': xtp=int(xtp)

    lsg=i.get('labels_for_separate_graphs',[])

    stjf=i.get('save_table_to_json_file','')
    sitjf=i.get('save_info_table_to_json_file','')
    stcf=i.get('save_table_to_csv_file','')

    table=i.get('table',[])

    rk=i.get('real_keys',[])

    ltfj=i.get('load_table_from_file','')
    if ltfj!='':
       rx=ck.load_json_file({'json_file':ltfj})
       if rx['return']>0: return rx
       table=rx['dict']

    # Check if table already there
    if len(table)==0:
       # Get table from entries
       tmp_a=i.get('action','')
       tmp_mu=i.get('module_uoa','')

       i['action']='get'
       i['module_uoa']=cfg['module_deps']['experiment']

       if i.get('remote_repo_uoa','')!='':
          i['repo_uoa']=i['remote_repo_uoa']
          del(i['remote_repo_uoa'])
          if 'out' in i: del(i['out'])

       r=ck.access(i)
       if r['return']>0: return r

       table=r['table']
       mtable=r.get('mtable',{})

       rk=r['real_keys']

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

    print (table)

    # Check if out to module
    pp=''
    if otf_duoa!='':
       if otf_muoa=='': otf_muoa=work['self_module_uid']
       # Try to update this entry to be sure that we can record there, and get path
       ii={'action':'update',
           'module_uoa':otf_muoa,
           'repo_uoa':otf_ruoa,
           'data_uoa':otf_duoa,
           'ignore_update':'yes'}
       rx=ck.access(ii)
       if rx['return']>0: return rx
       pp=rx['path']

    # Save table to JSON file, if needed
    if stjf!='':
       if pp!='':
          ppx=os.path.join(pp, stjf)
       else:
          ppx=stjf

       rx=ck.save_json_to_file({'json_file':ppx, 'dict':table})
       if rx['return']>0: return rx

    # Save info table to JSON file, if needed
    if sitjf!='':
       if pp!='':
          ppx=os.path.join(pp, sitjf)
       else:
          ppx=sitjf

       rx=ck.save_json_to_file({'json_file':ppx, 'dict':mtable})
       if rx['return']>0: return rx

    # Save table to CSV file, if needed
    if stcf!='':
       if pp!='':
          ppx=os.path.join(pp, stcf)
       else:
          ppx=stcf

       ii={'action':'convert_table_to_csv',
           'module_uoa':cfg['module_deps']['experiment'],
           'table':table,
           'keys':rk,
           'merge_multi_tables':'yes',
           'file_name':ppx}
       rx=ck.access(ii)
       if rx['return']>0: return rx

    # Prepare libraries
    pt=i.get('plot_type','')

    html=''
    style=''

    ####################################################################### MPL ###
    if pt.startswith('mpl_'):

   #    import numpy as np
       import matplotlib as mpl


       if ck.cfg.get('use_internal_engine_for_plotting','')=='yes':
          mpl.use('agg') # if XWindows is not installed, use internal engine
       elif os.environ.get('CK_MPL_BACKEND','')!='':
          mpl.use(os.environ['CK_MPL_BACKEND'])

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

       bl=i.get('bound_lines','')

       if pt=='mpl_3d_scatter' or pt=='mpl_3d_trisurf':
          from mpl_toolkits.mplot3d import Axes3D
          sp=fig.add_subplot(111, projection='3d')
       else:
          sp=fig.add_subplot(111)

       if i.get('xscale_log','')=='yes': sp.set_xscale('log')
       if i.get('yscale_log','')=='yes': sp.set_yscale('log')
       if i.get('zscale_log','')=='yes': sp.set_zscale('log')

       # Find min/max in all data and all dimensions
       tmin=[]
       tmax=[]

       for g in table:
           gt=table[g]
           for k in gt:
               for d in range(0, len(k)):
                   v=k[d]
                   if len(tmin)<=d:
                      tmin.append(v)
                      tmax.append(v)
                   else:
                      if v<tmin[d]: tmin[d]=v
                      if v>tmax[d]: tmax[d]=v 

       # If density or heatmap, find min and max for both graphs:
       if pt=='mpl_1d_density' or pt=='mpl_1d_histogram' or pt=='mpl_2d_heatmap' or pt=='mpl_3d_scatter' or pt=='mpl_3d_trisurf':
          index=0
          if pt=='mpl_2d_heatmap': index=2

          dmean=0.0
          start=True
          dmin=0.0
          dmax=0.0
          it=0
          dt=0
          for g in table:
              gt=table[g]

              for k in gt:
                  v=k[index]

                  if v!=None and v!='':
                     if start: 
                        dmin=v
                        start=False
                     else: 
                        dmin=min(dmin, v)

                     if start: 
                        dmax=v
                        start=False
                     else: 
                        dmax=max(dmax, v)

                     it+=1
                     dt+=v

          if it!=0: dmean=dt/it

       # If heatmap, prepare colorbar
       if pt=='mpl_2d_heatmap' or pt=='mpl_3d_trisurf':
          from matplotlib import cm
          xcmap = plt.cm.get_cmap('coolwarm')


       xmin=i.get('xmin','')
       xmax=i.get('xmax','')
       ymin=i.get('ymin','')
       ymax=i.get('ymax','')

       if xmin!='':
          sp.set_xlim(left=float(xmin))
       if xmax!='':
          sp.set_xlim(right=float(xmax))
       if ymin!='':
          sp.set_ylim(bottom=float(ymin))
       if ymax!='':
          sp.set_ylim(top=float(ymax))

       xerr=i.get('display_x_error_bar','')
       yerr=i.get('display_y_error_bar','')
       zerr=i.get('display_z_error_bar','')

       if pt=='mpl_2d_bars' or pt=='mpl_2d_lines':
          ind=[]
          gt=table['0']
          xt=0
          for q in gt:
              xt+=1

              if xt==xtp: 
                 v=q[0]
                 xt=0
              else: 
                 v=0

              ind.append(v)

          sp.set_xticks(ind)
          sp.set_xticklabels(ind, rotation=-20)

          width=0.9/len(table)

       # Iterate over separate graphs and add points
       s=0

       for g in sorted(table, key=int):
           gt=table[g]

           lbl=''
           if s<len(lsg): lbl=lsg[s]

           xpst=pst.get(g,{})

           elw=int(xpst.get('elinewidth',0))

           cl=xpst.get('color','')
           if cl=='': cl=gs[s]['color']

           sz=xpst.get('size','')
           if sz=='': sz=gs[s]['size']

           mrk=xpst.get('marker','')
           if mrk=='': mrk=gs[s]['marker']

           lst=xpst.get('line_style','')
           if lst=='': lst=gs[s].get('line_style', '-')

           heatmap=None

           if pt=='mpl_2d_scatter' or pt=='mpl_2d_bars' or pt=='mpl_2d_lines':
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

              if pt=='mpl_2d_bars':
                 mx1=[]
#                 mx2=[]
#                 names={}
#                 iq=0
                 for q in mx:
#                     if type(q)!=int and type(q)!=float:
#                        if q in names: q=names[q]
#                        else:
#                           names[q]=iq
#                           q=iq
#                           iq+=1
#                        mx2.append(str(q))
                     mx1.append(q+width*s)

                 if yerr=='yes':
                    sp.bar(mx1, my, width=width, edgecolor=cl, facecolor=cl, align='center', yerr=myerr, label=lbl) # , error_kw=dict(lw=2))
                 else:
                    sp.bar(mx1, my, width=width, edgecolor=cl, facecolor=cl, align='center', label=lbl)

              elif pt=='mpl_2d_lines':

                 if yerr=='yes':
                     sp.errorbar(mx, my, yerr=myerr, ls='none', c=cl, elinewidth=elw)
                 sp.plot(mx, my, c=cl, label=lbl)


              else:
                 if xerr=='yes' and yerr=='yes':
                    sp.errorbar(mx, my, xerr=mxerr, yerr=myerr, ls='none', c=cl, elinewidth=elw, label=lbl)
                 elif xerr=='yes' and yerr!='yes':
                    sp.errorbar(mx, my, xerr=mxerr, ls='none',  c=cl, elinewidth=elw, label=lbl)
                 elif yerr=='yes' and xerr!='yes':
                     sp.errorbar(mx, my, yerr=myerr, ls='none', c=cl, elinewidth=elw, label=lbl)
                 else:
                    sp.scatter(mx, my, s=int(sz), edgecolor=cl, c=cl, marker=mrk, label=lbl)

                 if xpst.get('frontier','')=='yes':
                    # not optimal solution, but should work (need to sort to draw proper frontier)
                    a=[]
                    for q in range(0, len(mx)):
                        a.append([mx[q],my[q]])

                    b=sorted(a, key=lambda k: k[0])

                    mx=[tmin[0]]
                    my=[tmax[1]]

                    for j in b:
                        mx.append(j[0])
                        my.append(j[1])

                    mx.append(tmax[0])
                    my.append(tmin[1])

                    sp.plot(mx, my, c=cl, linestyle=lst, label=lbl)

           elif pt=='mpl_1d_density' or pt=='mpl_1d_histogram':
              if not start: # I.e. we got non empty points
                 xbins=i.get('bins', 100)

                 mx=[]
                 for u in gt:
                     mx.append(u[0])

                 ii={'action':'analyze',
                     'min':dmin,
                     'max':dmax,
                     'module_uoa':cfg['module_deps']['math.variation'],
                     'bins':xbins,
                     'characteristics_table':mx}

                 r=ck.access(ii)
                 if r['return']>0: return r

                 xs=r['xlist']
                 dxs=r['ylist']

                 pxs=r['xlist2s']
                 dpxs=r['ylist2s']

                 if pt=='mpl_1d_density':
                    sp.plot(xs,dxs, label=lbl)
                    sp.plot(pxs, dpxs, 'x', mec='r', mew=2, ms=8) #, mfc=None, mec='r', mew=2, ms=8)
                    sp.plot([dmean,dmean],[0,dpxs[0]],'g--',lw=2)
                 else:
                    plt.hist(mx, bins=xbins, normed=True, label=lbl)

           elif pt=='mpl_2d_heatmap' or pt=='mpl_3d_scatter' or pt=='mpl_3d_trisurf':
                mx=[]
                mxerr=[]
                my=[]
                myerr=[]
                mz=[]
                mzerr=[]

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

                       mz.append(u[iu])
                       iu+=1
                       if zerr=='yes':
                          mzerr.append(u[iu])
                          iu+=1 

                if pt=='mpl_2d_heatmap':
                   heatmap=sp.scatter(mx, my, c=mz, s=int(sz), marker=mrk, lw=elw, vmin=dmin, vmax=dmax, cmap=xcmap)
                elif pt=='mpl_3d_scatter':
                   heatmap=sp.scatter(mx,my,mz, c=cl, s=int(sz), marker=mrk, lw=elw)
                elif pt=='mpl_3d_trisurf':
                   heatmap=sp.plot_trisurf(mx,my,mz,cmap=cm.coolwarm, lw=elw)
           s+=1
           if s>=len(gs):s=0

       # If heatmap, finish colors
       if pt=='mpl_2d_heatmap' or pt=='mpl_3d_trisurf':
          plt.colorbar(heatmap, orientation=xpst.get('colorbar_orietation','horizontal'), label=xpst.get('colorbar_label',''))

       # If bounds
       if bl=='yes':
          xbs=i.get('bound_style',':')
          xbc=i.get('bound_color','r')
          sp.plot([tmin[0],tmax[0]],[tmin[1],tmin[1]], linestyle=xbs, c=xbc)
          sp.plot([tmin[0],tmin[0]],[tmin[1],tmax[1]], linestyle=xbs, c=xbc)

       # Set axes names
       axd=i.get('axis_x_desc','')
       if axd!='': plt.xlabel(axd)

       ayd=i.get('axis_y_desc','')
       if ayd!='': plt.ylabel(ayd)

       atitle=i.get('title','')
       if atitle!='': plt.title(atitle)

#       handles, labels = plt.get_legend_handles_labels()
       plt.legend() #handles, labels)

       if otf=='':
          plt.show()
       else:
          if pp!='':
             ppx=os.path.join(pp, otf)
          else:
             ppx=otf

          plt.savefig(ppx)

    ####################################################################### D3 ###
    elif pt.startswith('d3_'):
       # Try to load template
       ppx=os.path.join(work['path'],'templates',pt+'.html')
       if not os.path.isfile(ppx):
          return {'return':1, 'error':'template for this graph is not found'}

       rx=ck.load_text_file({'text_file':ppx})
       if rx['return']>0: return rx
       html=rx['string']

       # Check if style is there (optional)
       ppx=os.path.join(work['path'],'templates',pt+'.style')
       if os.path.isfile(ppx):
          rx=ck.load_text_file({'text_file':ppx})
          if rx['return']>0: return rx
          style=rx['string']

       # Convert data table into JSON
       rx=ck.dumps_json({'dict':table})
       if rx['return']>0: return rx
       stable=rx['string']

       # Convert info table into JSON
       rx=ck.dumps_json({'dict':mtable})
       if rx['return']>0: return rx
       smtable=rx['string']

       # Convert point styles into JSON
       rx=ck.dumps_json({'dict':pst})
       if rx['return']>0: return rx
       spst=rx['string']

       html=html.replace('$#cm_data_json#$',stable)
       html=html.replace('$#cm_info_json#$',smtable)
       html=html.replace('$#cm_point_style_json#$',spst)

       # Set axes names
       axd=i.get('axis_x_desc','')
       html=html.replace('$#axis_x_desc#$', axd)

       ayd=i.get('axis_y_desc','')
       html=html.replace('$#axis_y_desc#$', ayd)

       size_x=i.get('image_width','')
       if size_x=='': size_x=600
       html=html.replace('$#ck_image_width#$', str(size_x))

       size_y=i.get('image_height','')
       if size_y=='': size_y=400
       html=html.replace('$#ck_image_height#$', str(size_y))

       xmin=i.get('xmin','')
       html=html.replace('$#ck_xmin#$', str(xmin))

       xmax=i.get('xmax','')
       html=html.replace('$#ck_xmax#$', str(xmax))

       ymin=i.get('ymin','')
       html=html.replace('$#ck_ymin#$', str(ymin))

       ymax=i.get('ymax','')
       html=html.replace('$#ck_ymax#$', str(ymax))

       # Save html to file (do not hardwire URLs)
       x=i.get('out_to_file','')
       if x!='':
          if pp!='':
             ppx=os.path.join(pp, x)
          else:
             ppx=x

          rx=ck.save_text_file({'text_file':ppx, 'string':html})
          if rx['return']>0: return rx

       # Save style to file, if needed
       x=i.get('save_to_style','')
       if x!='':
          if pp!='':
             ppx=os.path.join(pp, x)
          else:
             ppx=x

          rx=ck.save_text_file({'text_file':ppx, 'string':style})
          if rx['return']>0: return rx

       # Update URLs if needed (for example, to load .js files from CK repo)
       html=html.replace('$#ck_root_url#$', ck.cfg.get('wfe_url_prefix',''))

       # Save working html locally to visualize without CK
       if i.get('save_to_html','')!='':
          x='<html>\n\n<style>\n'+style+'</style>\n\n'+'<body>\n\n'+html+'\n\n</body>\n</html>\n'
          x=x.replace('$#ck_where#$','body')

          rx=ck.save_text_file({'text_file':i['save_to_html'], 'string':x})
          if rx['return']>0: return rx

    else:
       return {'return':1, 'error':'this type of plot ('+pt+') is not supported'}

    return {'return':0, 'html':html, 'style':style}

##############################################################################
# Continuously updated plot

def continuous_plot(i):
    """
    Input:  {

            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    for q in range(0, 1000):
        r=plot(i)
        if r['return']>0: return r

        x=ck.inp({'text':'Press any key'})

    return {'return':0}

##############################################################################
# view entry as html

##############################################################################
# view entry as html

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
    import os

    h=''
    st=''
    raw='no'
    top='no'

    duoa=i['data_uoa']
    burl=i['url_base']
    purl=i['url_pull']
    wurl=i.get('url_wiki','')

    url_cid=i.get('url_cid','')

    tpurl=i['url_pull_tmp']
    tpuoa=i['tmp_data_uoa']

    ap=i.get('all_params',{})

    ruoa=ap.get('ck_top_repo','')
    muoa=ap.get('ck_top_module','')

    cparams=ap.get('graph_params','') # current graph params

    hshare=i.get('html_share','')

    itype='png'

    # Check autorefresh
    ar=ap.get(var_post_autorefresh,'')
    if ar=='on':
       ap[var_post_refresh_graph]='yes'

    form_name=i['form_name']
    form_submit='document.'+form_name+'.submit();'

    art=ap.get(var_post_autorefresh_time,'')
    iart=5
    if art!='':
       try:
          iart=int(art)
       except ValueError:
          iart=5

    if ar=='on':
       h+='\n'
       h+='<script language="javascript">\n'
       h+=' <!--\n'
       h+='  setTimeout(\''+form_submit+'\','+str(iart*1000)+');\n'
       h+=' //-->\n'
       h+='</script>\n'
       h+='\n'

       # Set replotting
       jj={'action':'create_input',
           'module_uoa':cfg['module_deps']['wfe'],
           'type':'hidden', 
           'name': var_post_refresh_graph, 
           'value':'yes'}
       rx=ck.access(jj)
       if rx['return']>0: return rx
       h+=rx['html']+'\n'

    if duoa!='':
       # Load entry
       rx=ck.access({'action':'load',
                     'module_uoa':work['self_module_uid'],
                     'data_uoa':duoa})
       if rx['return']>0: return rx

       pp=rx['path']

       dd=rx['dict']
       duid=rx['data_uid']

       name=dd.get('name','')

       gsr=dd.get('get_shared_repo','')

       sruoa=dd.get('scripts_repo_uoa','')
       smuoa=dd.get('scripts_module_uoa','')
       sduoa=dd.get('scripts_data_uoa','')

       h+=' <span id="ck_entries1a">'+name+'</span><br>\n'
       h+=' <div id="ck_entries_space4"></div>\n'

       graphs=dd.get('graphs',[])

       # If more than one subgraph, prepare selector
       hsb=''

       igraph=0
       cgraph=0
       x=ap.get(var_post_cur_subgraph,'')
       try:
          cgraph=int(x)
       except ValueError:
          cgraph=0

#       sgraph=i.get(var_post_subgraph,'')
#       if sgraph=='':
       sgraph=ap.get(var_post_subgraph,'')

       if len(graphs)>1:
          dx=[]
          jgraph=0
          for q in graphs:
              vid=q.get('id','')
              if vid==sgraph: 
                 igraph=jgraph
              dx.append({'name':q.get('name',''), 'value':vid})
              jgraph+=1

          jj={'action':'create_selector',
              'module_uoa':cfg['module_deps']['wfe'],
              'name': var_post_subgraph, 
              'onchange':form_submit,
              'data':dx,
              'selected_value':sgraph}

          rx=ck.access(jj)
          if rx['return']>0: return rx
          hsb=rx['html']+'\n'

          if igraph!=cgraph:
             ap[var_post_reset_graph]='yes'
             cgraph=igraph

          # Save current subgraph to detect change and reset ...
          jj={'action':'create_input',
              'module_uoa':cfg['module_deps']['wfe'],
              'type':'hidden', 
              'name': var_post_cur_subgraph, 
              'value':str(cgraph)}
          rx=ck.access(jj)
          if rx['return']>0: return rx
          h+=rx['html']+'\n'

       # Visualize
       gid=''
       if igraph<len(graphs):
          g=graphs[igraph]

          output=g.get('output','')

          gid=g.get('id','')
          if gid!='':
             # Get graph params
             if g.get('notes','')!='':
                h+='<i>'+g['notes']+'</i>'

             pjson=os.path.join(pp, gid+'.json')
             if not os.path.isfile(pjson): pjson=''

             pcsv=os.path.join(pp, gid+'.csv')
             if not os.path.isfile(pcsv): pcsv=''

             h+='<div id="ck_entries_space4"></div>\n'

             if hshare!='':
                h+='<div id="ck_entries_space4"></div>\n'
                h+=hshare
                h+=' <div id="ck_entries_space4"></div>\n'

             h+='<div style="text-align: right;">'

             if wurl!='':
                h+='[&nbsp;<a href="'+wurl+'">Discussion wiki (comments, reproducibility, etc.)</a>&nbsp;]'

             h+='</div>\n'

#             h+=' <hr class="ck_hr">\n'

             if hsb!='':
                h+=' <div id="ck_entries_space4"></div>\n'
                h+='<center>Select subgraph:&nbsp;'+hsb+'</center>\n'
#                h+=' <hr class="ck_hr">\n'

             if output=='html':
                image=gid+'.html'
             else:
                image=gid+'.'+itype

             params=g.get('params',{})

             problem_converting_json=''

             if var_post_reset_graph not in ap and cparams!='':
                rx=ck.convert_json_str_to_dict({'str':cparams, 'skip_quote_replacement':'yes'})
                if rx['return']>0:
                   problem_converting_json=rx['error']
                else:
                   params=rx['dict']

             rx=ck.dumps_json({'dict':params, 'sort_keys':'yes'})
             if rx['return']>0: return rx
             jparams=rx['string']

             # Check if need to regenerate
             problem=''
             image_orig=image
             himage=''
             if var_post_refresh_graph in ap:
                image_orig=''
                import copy

                ii=copy.deepcopy(params)
                ii['action']='plot'
                ii['module_uoa']=work['self_module_uoa']

                image=ap.get(var_post_tmp_graph_file,'')
                if image=='':
                   rx=ck.gen_tmp_file({'prefix':'tmp-', 'suffix':'.'+itype, 'remove_dir':'yes'})
                   if rx['return']>0: return rx
                   image=rx['file_name']

                ii['out_to_file']=image

                # Preset current entry params
                jj={'action':'create_input',
                    'module_uoa':cfg['module_deps']['wfe'],
                    'type':'hidden', 
                    'name': var_post_tmp_graph_file, 
                    'value':image}
                rx=ck.access(jj)
                if rx['return']>0: return rx
                h+=rx['html']+'\n'

                if ck.cfg.get('graph_tmp_repo_uoa','')!='':
                   ii['out_repo_uoa']=ck.cfg['graph_tmp_repo_uoa']

                ii['out_module_uoa']='tmp'
                ii['out_data_uoa']=tpuoa

#               (save_table_to_json_file)             - save table to json file

                rx=ck.access(ii)
                if rx['return']>0: 
                   problem=rx['error']

                purl=tpurl

             # Prepare html
             size_x=params.get('size_x','')
             size_y=params.get('size_y','')

             h+=' <table border="0" cellpadding="3" width="100%">\n'
             h+=' <tr>\n'

             extra=''
             if size_x!='': extra+='width="'+str(size_x)+'" '

             h+='  <td valign="top" '+extra+'>\n'

             h+='   <div id="ck_entries">\n'

             h+='    <b><small>Graph:</small></b>\n'
             if problem!='':
                h+='<br><br><span style="color:red;"><i>Problem: '+problem+'!</i></span><br>\n'
             else:
                if output=='html' and image!='':
                   # Check if style exists
                   pstyle=os.path.join(pp, gid+'.style')
                   if os.path.isfile(pstyle): 
                      rx=ck.load_text_file({'text_file':pstyle})
                      if rx['return']>0: return rx
                      st=rx['string']

                   # Generate UID
                   rx=ck.gen_uid({})
                   if rx['return']>0: return rx
                   uid=rx['data_uid']
                   div_with_uid='ck_interactive_'+uid

                   h+='<div id="'+div_with_uid+'">\n'

                   z=muoa+':'+duoa
                   if var_post_refresh_graph in ap:
                      z=url_cid

                   h+='$#ck_include_start#${"cid":"'+z+'", "where":"div#'+div_with_uid+'", "html":"'+image+'", "style":"2d_points_time_vs_size_with_pareto_interactive.style"}$#ck_include_stop#$\n'
                   h+='</div>\n'

                else:
                   if image!='':
                      if size_y!='': extra+='height="'+str(size_y)+'" '
                      himage='<img src="'+purl+image+'" '+extra+'>'
                      h+='   '+himage

             h+='   </div>\n'
             h+='  </td>\n'

             h+='  <td valign="top">\n'

             x='width:99%;'
             if size_y!='': x+='height:'+str(size_y)+'px;'

             h+='   <div id="ck_entries">\n'

             h+='    <b><small>Graph params (to customize/reproduce):</small></b>\n'

             if problem_converting_json!='':
                h+='<br><br><span style="color:red;"><i>'+problem_converting_json+'</i></span><br>\n'

             h+='   <textarea name="graph_params" style="'+x+'">\n'
             h+=jparams+'\n'
             h+='   </textarea><br>\n'

             h+='   </div>\n'

             h+='  </td>\n'

             h+=' </tr>\n'
             h+='</table>\n'

#             h+=' <hr class="ck_hr">\n'

             h+='<center>\n'
             h+='<button type="submit" name="'+var_post_refresh_graph+'">Replot graph</button>\n'
             h+='<button type="submit" name="'+var_post_reset_graph+'">Reset graph</button>\n'

             checked=''
             if ar=='on': checked=' checked '
             h+='&nbsp;&nbsp;&nbsp;Auto-replot graph:&nbsp;<input type="checkbox" name="'+var_post_autorefresh+'" id="'+var_post_autorefresh+'" onchange="submit()"'+checked+'>,'
             h+='&nbsp;seconds: <input type="text" name="'+var_post_autorefresh_time+'" value="'+str(iart)+'">\n'
             h+='</center>\n'

#             h+='<hr class="ck_hr">\n'

             h+='<center>\n'
             h+='<div id="ck_entries" style="background-color: #dfffbf;">\n'

             h+='<b>Reproducing graph:</b>\n'

             h+='<table width="99%">\n'
             h+=' <tr>\n'
             h+='  <td valign="top" align="left" width="44%">\n'

             h+='   <table border="0" cellpadding="5">\n'

             h+='    <tr>\n'
             h+='     <td valign="top" width="140"><b>Experiment entries:</b></td>\n'
             h+='     <td valign="top"><i>\n'

             duoal=params.get('data_uoa_list','')
             if len(duoal)>0:
                h+='\n'
                for q in duoal:
                    h+='<a href="'+burl+'wcid=experiment:'+q+'">'+q+'</a><br>\n'
                h+='\n'

             h+='     </i></td>\n'
             h+='    </tr>\n'

             if smuoa!='' and sduoa!='':
                cid=smuoa+':'+sduoa
                if sruoa!='': cid=sruoa+':'+cid

                h+='    <tr>\n'
                h+='     <td valign="top"><b>Scripts to rebuild:</b></td>\n'
                h+='     <td valign="top"><i>\n'
                h+='      ck find '+cid+'<br>\n'
                h+='      <a href="'+burl+'wcid='+cid+'">View in CK viewer</a>\n'
                h+='     </i></td>\n'
                h+='    </tr>\n'


             h+='    <tr>\n'
             h+='     <td valign="top"><b>Replay graph from CMD:</b></td>\n'
             h+='     <td valign="top"><i>\n'
             h+='      ck replay graph:'+duoa+' id='+gid+'\n'
             h+='     </i></td>\n'
             h+='    </tr>\n'


             h+='   </table>\n'

             h+='  </td>\n'
             h+='  <td valign="top" align="left" width="56%">\n'

             h+='   <table border="0" cellpadding="5">\n'

             if gsr!='':
                h+='    <tr>\n'
                h+='     <td valign="top" width="250"><b>Obtain shared CK repo with all artifacts:</b></td>\n'
                h+='     <td valign="top">\n'
                h+='      <i>'+gsr+'</i>\n'
                h+='     </td>\n'
                h+='    </tr>\n'

             if (pjson!='' or pcsv!='') and image_orig!='' and himage!='':
                x1=purl+gid+'.json'
                x2=purl+gid+'.csv'

                h+='    <tr>\n'
                h+='     <td valign="top"><b>Experiment table:</b></td>\n'
                h+='     <td valign="top"><i>\n'
                if pjson!='':
                   h+='      <a href="'+x1+'">Download in JSON</a>;&nbsp;&nbsp'
                if pcsv!='':
                   h+='      <a href="'+x2+'">Download in CSV</a>\n'
                h+='     </i></td>\n'
                h+='    </tr>\n'

             if image_orig!='' and himage!='':
                h+='    <tr>\n'
                h+='     <td valign="top"><b>Embedd original image into interactive report/paper:</b></td>\n'
                h+='     <td valign="top"><i>\n'
                h+='      '+himage.replace('<','&lt;').replace('>','&gt;')+'\n'
                h+='     </i></td>\n'
                h+='    </tr>\n'

             h+='   </table>\n'

             h+='  </td>\n'
             h+=' </tr>\n'
             h+='</table>\n'

             h+='</div>\n'

             h+='</center>\n'

    return {'return':0, 'raw':raw, 'show_top':top, 'html':h, 'style':st}

##############################################################################
# replaying saved graph from CMD

def replay(i):
    """
    Input:  {
              (repo_uoa)   - repo UOA of s saved graph
              data_uoa     - data UOA of a saved graph
              (id)         - subgraph id
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    o=i.get('out','')

    duoa=i['data_uoa']
    ruoa=i.get('repo_uoa','')

    ii={'action':'load',
        'module_uoa':work['self_module_uid'],
        'data_uoa':duoa,
        'repo_uoa':ruoa}
    rx=ck.access(ii)
    if rx['return']>0: return rx

    dd=rx['dict']

    graphs=dd.get('graphs',[])

    if len(graphs)==0:
       return {'return':1, 'error':'no saved graphs found'}

    igraph=-1

    if len(graphs)==1:
       igraph=0
    elif len(graphs)>1:
       gid=i.get('id','')
       if gid=='':
          if o=='con':
             ck.out('Available subgraphs ID:')
             for q in graphs:
                 ck.out('  '+q.get('id',''))
             ck.out('')

          return {'return':1, 'error':'more than one subgraph found - please, specify id'}

       jgraph=0
       for q in graphs:
           if q.get('id','')==gid:
              igraph=jgraph
              break
           jgraph+=1

    if igraph==-1:
       return {'return':1, 'error':'can\'t find subgraph'}

    params=graphs[igraph].get('params',{})

    # Replaying
    params['action']='plot'
    params['module_uoa']=work['self_module_uid']

    return ck.access(params)
