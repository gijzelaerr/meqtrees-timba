# JEN_nodenames.py:

# Demonstrates the following MeqTree features:
# - The various ways that node names can be defined
# - Including qualifiers



 
#********************************************************************************
# Initialisation:
#********************************************************************************

from Timba.TDL import *
from Timba.Meq import meq

Settings.forest_state.cache_policy = 100
Settings.forest_state.bookmarks = []



#********************************************************************************
# The function under the 'blue button':
#********************************************************************************

def _define_forest (ns, **kwargs):
   """Definition of a 'forest' of one or more trees"""

   # Organise in groups (cc) of related nodes.
   # These are bundled by supplying the cc as children to a MeqComposer node.
   # Bundle the groups in the same way into a child-list (gg):

   gg = []

   # 
   group = 'user_specified_name'
   cc = [
      ns.xxx << 1.0,
      ns['yyy'] << 1.0,
      ]
   gg.append(ns[group] << Meq.Composer(children=cc))

   # Automatic generation of node-names:
   group = 'automatic_name'
   x = ns.x << 1.0
   y = ns.y << -1.0
   cc = [
      ns << 1.0,
      ns << -1.0,
      ns << x+y,
      ns << x-2/y,
      ]
   gg.append(ns[group] << Meq.Composer(children=cc))

   # Qualifiers:
   group = 'name_qualifiers'
   sp1 = ns.station_phase(s=3) << 2.2
   sp2 = ns.station_phase(s=4) << -5.1
   cc = [sp1,sp2,
         ns.ifr_phase(s1=3, s2=4) << Meq.Subtract(sp1,sp2),
         ns.qmerge.qmerge(sp1,sp2) << Meq.Subtract(sp1,sp2),
         ns.qadd(q=8).qadd(sp1,sp2) << Meq.Subtract(sp1,sp2),
         ns.list('a','b',7) << 1.0,
         ns.kwargs(a='a',b='b',c=7) << 1.0,
         ns['list+kwargs']('a','b',a='a',b='b',c=7) << 1.0,
         ns.dict(**dict(a='a',b='b',c=7)) << 1.0,
         ns.dict2(dict(a='a',b='b',c=7)) << 1.0,
         ]
   gg.append(ns[group] << Meq.Composer(children=cc))

   # Subscope:
   group = 'Subscope'
   nsub1 = ns.Subscope('ssc')
   nsub2 = ns.Subscope('ssc',['a','b'])
   cc = [
      nsub1.zzz << 1.0,
      nsub1.list('a','b',7) << 1.0,
      nsub2.qual_list << 1.0,
      ]
   gg.append(ns[group] << Meq.Composer(children=cc))

   # Node-name conflict:
   group = 'name_conflict'
   cc = [
      nsub1.conflict << 1.0,
      ns.conflict << 1.0,
      # ns.conflict << 1.0
      ]
   gg.append(ns[group] << Meq.Composer(children=cc))

   # The root node of the tree can have any name, but in this example it
   # should be named 'result', because this name is used in the default
   # execute command (see below), and the bookmark.
   result = ns.result << Meq.Composer(children=gg)

   # Finished:
   return True



#********************************************************************************
# The function under the TDL Exec button:
#********************************************************************************

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1,10,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       

#********************************************************************************
# Comments:
#********************************************************************************

# - All the information is in the Trees panel:
#   - Expand the various (groups of) nodes
#   - Check in _define_forest() how their names were generated

#********************************************************************************
#********************************************************************************


