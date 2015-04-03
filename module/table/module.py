#
# Collective Knowledge (dealing with table)
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
# draw table

def draw(i):
    """
    Input:  {
              table   - table to draw [[],[],[]...], [[],[],[]...] ...]

              (out)   - txt (default) or html
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              string       - output
            }

    """

    o=i.get('out','')

    table=i.get('table',[])

    s=''

    if len(table)>0:
       lx=len(table[0])

       lwidth=[]
       for l in range(0, lx):
           lwidth.append(-1)

       # If 'txt', check length of all entries
       if o=='txt':
          for t in table:
              for l in range(0, lx):
                  sx=t[l]
                  lw=lwidth[l]
                  if lw==-1 or len(sx)>lw: 
                     lwidth[l]=len(sx)


          for t in table:
              for l in range(0, lx):
                  sx=t[l]
                  lw=lwidth[l]

                  s+=sx.ljust(lw+2)
              s+='\n'
       else:
          s='<html>\n'
          s+=' <body>\n'
          s+='  <table>\n'
          for t in table:
              s+='  <tr>\n'
              for l in range(0, lx):
                  sx=t[l]
                  s+='    <td>'+sx+'</td>\n'
              s+='   </tr>\n'
          s+='  </table>\n'
          s+=' </body>\n'
          s+='<html>\n'

    return {'return':0, 'string':s}
