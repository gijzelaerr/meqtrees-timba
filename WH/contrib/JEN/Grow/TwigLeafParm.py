# file: ../JEN/Grow/TwigLeafParm.py

# History:
# - 14sep2007: creation (from Growth.py)

# Description:

"""The TwigLeafParm class makes makes a subtree that represents a
single MeqParm node.
"""


#======================================================================================

#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL import *
from Timba.Meq import meq

import Meow

from Timba.Contrib.JEN.Grow import TwigLeaf
from Timba.Contrib.JEN.control import OptionManager
from Timba.Contrib.JEN.control import Executor

import math
import random



#=============================================================================
#=============================================================================

class TwigLeafParm(TwigLeaf.TwigLeaf):
    """Class derived from TwigLeaf"""

    def __init__(self, quals=None,
                 submenu='compile',
                 OM=None, namespace=None,
                 **kwargs):

        TwigLeaf.TwigLeaf.__init__(self,
                                   quals=quals,
                                   name='TwigLeafParm',
                                   submenu=submenu,
                                   OM=OM, namespace=namespace,
                                   **kwargs)
        return None

    
    #====================================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = TwigLeaf.TwigLeaf.oneliner(self)
        return ss
    

    def display (self, txt=None, full=False, recurse=3, OM=True, level=0):
        """Print a summary of this object"""
        prefix = self.display_preamble(self.name, level=level, txt=txt)
        #...............................................................
        print prefix,'  * xxx'
        #...............................................................
        TwigLeaf.TwigLeaf.display(self, full=full,
                          recurse=recurse,
                          OM=OM, level=level+1)
        #...............................................................
        return self.display_postamble(prefix, level=level)


    #====================================================================

    def define_compile_options(self, trace=True):
        """Specific: Define the compile options in the OptionManager.
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................
        self.defopt('default', 0.0,
                    prompt='default value',
                    opt=[0.0,1.0,-1.0], more=float,
                    doc="""the default value of the MeqParm
                    """)
        self.defopt('freq_deg', 2,
                    prompt='freq polc',
                    opt=[0,1,2,3,4,5], more=int,
                    doc="""Degree (order) of the freq polynonial that is
                    to be solved for (constant in freq: freq_deg=0).
                    """)
        self.defopt('time_deg', 2,
                    prompt='time polc',
                    opt=[0,1,2,3,4,5], more=int,
                    doc="""Degree (order) of the time polynonial that is
                    to be solved for (constant in time: time_deg=0).
                    """)
        opt = [None,1,2,3,4,5,10]
        # opt.append(dmi.record(time=0,freq=0, l=.., m=..))
        self.defopt('tiling', None,
                    prompt='subtile size',
                    opt=opt,                    # more=str,
                    doc="""The domain (tile) may be split up into subtiles,
                    (for the moment, in the time-direction only)
                    If specified, different solutions are made for each
                    subtile, rather than a single one for the entire domain.
                    """)
        self.defopt('tags', [],
                    prompt='MeqParm tag(s)',
                    opt=[[],['solvable']],      # more=str,
                    doc="""Node tags can be used to search for (groups of)
                    nodes in the nodescope.
                    """)
        #..............................................
        return self.on_exit(trace=trace)


    #--------------------------------------------------------------------
    #--------------------------------------------------------------------

    def grow (self, ns, test=None, trace=True):
        """The TwigLeafParm class is derived from the TwigLeaf class.
        It is just a (scalar) MeqParm node.
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        # Read the specified options:
        value = self.optval('default', test=test)
        tiling = self.optval('tiling', test=test)
        time_deg = self.optval('time_deg', test=test)
        freq_deg = self.optval('freq_deg', test=test)
        tags = self.optval('tags', test=test)

        # Make the MeqParm node:
        mparm = Meow.Parm(value=value,
                          tiling=tiling,
                          time_deg=time_deg,
                          freq_deg=freq_deg,
                          tags=tags)
        nodename = 'Meow.Parm(t'+str(time_deg)+',f'+str(freq_deg)+')'
        node = self.ns[nodename] << mparm.make()

        #..............................................
        # Finishing touches:
        return self.on_output (node, trace=trace)


    



#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================


plf = None
if 0:
    xtor = Executor.Executor()
    # xtor.add_dimension('l', unit='rad')
    # xtor.add_dimension('m', unit='rad')
    plf = TwigLeafParm(insist=dict(tags=['aa','bb']))
    plf.make_TDLCompileOptionMenu()
    plf.display('outside')


def _define_forest(ns):

    global plf,xtor
    if not plf:
        xtor = Executor.Executor()
        plf = TwigLeafParm()
        plf.make_TDLCompileOptionMenu()

    cc = []

    rootnode = plf.grow(ns)
    cc.append(rootnode)

    if len(cc)==0: cc.append(ns.dummy<<1.1)
    ns.result << Meq.Composer(children=cc)
    xtor.make_TDLRuntimeOptionMenu(node=ns.result)
    return True



#---------------------------------------------------------------

Settings.forest_state.cache_policy = 100

def _tdl_job_execute (mqs, parent):
    """Execute the forest with the specified options (domain etc),
    starting at the named node"""
    return xtor.execute(mqs, parent)
    
def _tdl_job_display (mqs, parent):
    """Just display the current contents of the TwigLeaf object"""
    plf.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the TwigLeaf object"""
    plf.display('_tdl_job', full=True)
       


       



#===============================================================
# Test routine (without meqbrowser):
#===============================================================


if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        plf = TwigLeafParm(insist=dict(tags=[]))
        plf.display('initial')

    if 1:
        plf.make_TDLCompileOptionMenu()

    if 1:
        test = dict(default=78)
        plf.grow(ns, test=test, trace=True)

    if 1:
        plf.display('final', OM=True, full=True)



#===============================================================
