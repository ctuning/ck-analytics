#
# Collective Knowledge (universal advice about experiments, bugs, models, 
#                       features, optimizations, adaptation, 
#                       community remarks ...)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://fursin.net
#

cfg={}  # Will be updated by CK (meta description of this module)
work={} # Will be updated by CK (temporal data)
ck=None # Will be updated by CK (initialized CK kernel) 

# Local settings

hextra='<i><center>\n'
hextra+=' [ <a href="http://cKnowledge.org/ai">Community-driven AI R&D powered by CK</a> ], '
hextra+=' [ <a href="https://github.com/dividiti/ck-caffe">CK-Caffe</a> ], '
hextra+=' [ <a href="https://github.com/ctuning/ck-tensorflow">CK-TensorFlow</a> ], '
hextra+=' [ <a href="https://en.wikipedia.org/wiki/Collective_Knowledge_(software)">Wikipedia</a>, \n'
hextra+='<a href="https://www.researchgate.net/publication/304010295_Collective_Knowledge_Towards_RD_Sustainability">paper 1</a>, \n'
hextra+='<a href="https://arxiv.org/abs/1506.06256">Paper 2</a>, \n'
hextra+='<a href="https://www.youtube.com/watch?v=Q94yWxXUMP0">YouTube CK intro</a> ] \n'
hextra+='</center></i>\n'
hextra+='<br>\n'

form_name='ck_ai_web_form'
onchange='document.'+form_name+'.submit();'

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
# access available CK-AI self-optimizing functions

def show(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import copy

    h=''
    st=''

    h+='<center>\n'
    h+='\n\n<script language="JavaScript">function copyToClipboard (text) {window.prompt ("Copy to clipboard: Ctrl+C, Enter", text);}</script>\n\n' 

#    h+='<h2>Aggregated results from Caffe crowd-benchmarking (time, accuracy, energy, cost, ...)</h2>\n'

    h+=hextra

    # Check host URL prefix and default module/action
    rx=ck.access({'action':'form_url_prefix',
                  'module_uoa':'wfe',
                  'host':i.get('host',''), 
                  'port':i.get('port',''), 
                  'template':i.get('template','')})
    if rx['return']>0: return rx
    url0=rx['url']
    template=rx['template']

    url=url0
    action=i.get('action','')
    muoa=i.get('module_uoa','')

    url+='action=index&module_uoa=wfe&native_action='+action+'&'+'native_module_uoa='+muoa
    url1=url

    # Start form
    r=ck.access({'action':'start_form',
                 'module_uoa':cfg['module_deps']['wfe'],
                 'url':url1,
                 'name':form_name})
    if r['return']>0: return r
    h+=r['html']

    # Check available API is modules
    r=ck.access({'action':'search',
                 'module_uoa':cfg['module_deps']['module'],
                 'tags':'ck-ai-json-web-api'})
    if r['return']>0: return r
    l=r['lst']

    if len(l)==0:
       h='<b>WARNING:</b> No CK modules found with CK AI JSON web API\n'
    else:
       dt=[{'name':'', 'value':''}]

       for x in l:
           v=x['data_uid']

           # Load module info
           r=ck.access({'action':'load',
                        'module_uoa':cfg['module_deps']['module'],
                        'data_uoa':v})
           if r['return']>0: return r

           d=r['dict']

           name=d.get('actions',{}).get('ask_ai_web',{}).get('desc','')

           if name!='':
              dt.append({'name':name, 'value':v})

       # Create selector
       ai=i.get('ai_scenario','')

       ii={'action':'create_selector',
           'module_uoa':cfg['module_deps']['wfe'],
           'data':dt,
           'name':'ai_scenario',
           'onchange':onchange, 
           'skip_sort':'yes',
           'selected_value':ai}
       r=ck.access(ii)
       if r['return']>0: return r
       x=r['html']

       h+='Select AI scenario (which has unified <a href="http://github.com/ctuning/ck">CK JSON API</a>): '+x

       # Render scenario
       if ai!='':
          ii=copy.deepcopy(i)

          ii['action']='ask_ai_web'
          ii['module_uoa']=ai

          ii['widget']='yes'
          ii['prepared_url0']=url0
          ii['prepared_url1']=url1
          ii['prepared_form_name']=form_name

          r=ck.access(ii)
          if r['return']>0: return r

          h+='\n<hr>\n'+r.get('html','')
          st+='\n'+r.get('style','')+'\n'

    return {'return':0, 'html':h, 'style':st}

##############################################################################
# CK-AI dashboard

def browse(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    i['action']='browser'
    i['cid']=''
    i['module_uoa']=''
    i['template']='ck-ai-basic'

    return ck.access(i)
