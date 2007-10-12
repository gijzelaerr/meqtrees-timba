# file: ../control/ParmGroupManager.py

# History:
# - 17jul2007: creation (from ParameterizationPlus.py)
# - 24jul2007: adapted to OptionManager
# - 17sep2007: get OptionManager from /control/
# - 24sep2007: move to ../JEN/control/

# Description:

# This class encapsulates a collection of ParmGroup objects.


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

from Timba.Contrib.JEN.control import OptionManager
from Timba.Contrib.JEN.Grunt import ParmGroup
from Timba.Contrib.JEN.NodeList import NodeList
from Timba.Contrib.JEN.Grunt import display

from copy import deepcopy

#======================================================================================

class ParmGroupManager (Meow.Parameterization):
    """The Grunt ParmGroupManager class is derived from the
    Meow Parameterization class. It adds some extra functionality
    for groups of similar parms, which may find their way into the
    more official Meow system eventually."""

    def __init__(self, ns=None, name='<parent>', namespace=None,
                 tobesolved=None):

        # Scopify ns, if necessary:
        if is_node(ns):
            ns = ns.QualScope()        

        # Make sure that there is a nodescope (Required by Meow.Parameterization)
        if ns==None:
            ns = NodeScope()

        Meow.Parameterization.__init__(self, ns, name)

        self._frameclass = 'Grunt.ParmGroupManager'       # for reporting

        # Initialize local data:
        self._parmgroups = dict()
        self._parmgogs = dict()
        self._pmerged = []
        self._accumulist = dict()

        # Options management:
        self._OM = OptionManager.OptionManager(name=self.name,
                                               namespace=namespace)
        self.define_options(tobesolved=tobesolved)

        return None


    #---------------------------------------------------------------

    def __getitem__ (self, key):
        """Get (a reference to) the specified parmgroup"""
        if not isinstance(key, str):
            s = 'invalid key: '+str(key)
            raise ValueError,s
        elif not key in self._parmgroups:
            s = 'key not recognized: '+str(key)
            raise ValueError,s
        return self._parmgroups[key]


    def active_groups (self, new=None):
        """Get/set the list of (names of) 'active' parmgroups.
        Reimplementation of the quare-brackets call: pg = PGM[key]"""
        active = []
        for key in self._parmgroups.keys():
            pg = self._parmgroups[key]
            if isinstance(new, (list,tuple)):
                pg.active(key in new)
            if pg.active():
                active.append(key)
        if new:
            self.TDLShowActive()

        # Make a new set of parmgogs (of active groups):
        gogs = self.gogs()

        # Finished:
        return active

    #---------------------------------------------------------------

    def nodescope (self, ns=None):
        """Get/set the internal nodescope (can also be a node)"""
        if ns:
            if is_node(ns):
                self.ns = ns.QualScope()        
            else:
                self.ns = ns
            # Pass the new nodescope on to its parmgroup(s):
            for key in self._parmgroups.keys():
                self._parmgroups[key].nodescope(self.ns)         
        # Always return the current nodescope:
        return self.ns



    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = 'Grunt.ParmGroupManager:'
        ss += '  (name='+str(self.name)+')'
        ss += '  ('+str(self.ns['<>'].name)+')'
        return ss


    def display(self, txt=None, full=False, recurse=3, OM=True, pg=False, level=0):
        """Print a summary of this object"""
        prefix = '  '+(level*'  ')+'PGM'
        if level==0: print
        print prefix,' '
        print prefix,'** '+self.oneliner()
        if txt: print prefix,'  * (txt='+str(txt)+')'
        #...............................................................
        print prefix,'  * Grunt _parmgroups ('+str(len(self._parmgroups))+'):'
        for key in self._parmgroups:
            pg = self._parmgroups[key]
            if pg.active():
                print prefix,'    - ('+key+'): '+str(pg.oneliner())
            else:
                print prefix,'    - ('+key+'):   ... not active ...'
        #...............................................................
        print prefix,'  * Simuldev expressions (mode==simulate only):'
        for key in self._parmgroups:
            pg = self._parmgroups[key]
            if pg.mode()=='simulate':
                print prefix,'    - ('+key+'): '+pg._OM['simuldev']
        #...............................................................
        print prefix,'  * Grunt _parmgogs (groups of parmgroups, derived from their node tags):'
        for key in self.gogs():
            print prefix,'    - ('+str(key)+'): '+str(self._parmgogs[key])
        #...............................................................
        print prefix,'  * Accumulist entries: '
        for key in self._accumulist.keys():
            vv = self._accumulist[key]
            print prefix,'    - '+str(key)+' ('+str(len(vv))+'):'
            if full:
                for v in vv: print prefix,'    - '+str(type(v))+' '+str(v)
        #...............................................................
        if self._parmdefs:
            print prefix,'  * Meow _parmdefs ('+str(len(self._parmdefs))+') (value,tags,solvable):'
            if full:
                for key in self._parmdefs:
                    rr = list(deepcopy(self._parmdefs[key]))
                    rr[0] = str(rr[0])
                    print prefix,'    - ('+key+'): '+str(rr)
            print prefix,'  * Meow.Parm options (in _parmdefs):'
            if full:
                for key in self._parmdefs:
                    value = self._parmdefs[key][0]
                    if isinstance(value, Meow.Parm):
                        print prefix,'    - ('+key+'): (='+str(value.value)+') '+str(value.options)
            print prefix,'  * Meow _parmnodes ('+str(len(self._parmnodes))+'):'
            if full:
                for key in self._parmnodes:
                    rr = self._parmnodes[key]
                    print prefix,'    - ('+key+'): '+str(rr)
        #...............................................................
        print prefix,'  * '+self._OM.oneliner()
        if OM: self._OM.display(full=False, level=level+1)
        #...............................................................
        if pg: self.pg_display(OM=OM, level=level+1)
        #...............................................................
        print prefix,'**'
        if level==0: print
        return True

    #---------------------------------------------------------------

    def pg_display(self, full=False, OM=False, level=0):
        """Display summaries of its parmgroups"""
        for key in self._parmgroups.keys():
            self._parmgroups[key].display(full=full, OM=OM, level=level)
        return True


    #===============================================================
    # - Parmgroups are designed for the common case of
    # groups of similar parameters, like the station phases of a set
    # of Jones matrices. The latter are encapsulated in a Joneset22
    # object, which is derived (via the class Matrixett22) from
    # ParmGroupManager.
    # - A parmgroup (e.g. Gphase) must first be defined, together with
    # the various attributes (tags, default value, etc) that its members
    # have in common. Individual members (MeqParm nodes or subtrees that
    # simulate their behaviour) of such a group are created with extra
    # nodename qualifier(s).
    # - The members (nodes/subtrees) of a parmgroup may be obtained
    # (e.g. for solving) and/or manipulated (e.g. visualized) as a group.
    #===============================================================



    def parmgroups (self):
        """Return a list of names of the available parmgroups"""
        return self._parmgroups.keys()

    def has_parmgroup (self, key, severe=False):
        """Test whether it has a parmgroup of this name (key).
        If severe==True, raise a ValueError if it does not"""
        if self._parmgroups.has_key(key): return True
        if severe:
            s = '** parmgroup not recognized: '+str(key)
            raise ValueError, s
        return False

    #...............................................................

    def groups (self):
        """Older call, not recommended (use .parmgroups())"""
        return self.parmgroups()

    def has_group (self, key, severe=False):
        """Older call, not recommended (use .has_parmgroup())"""
        return self.has_parmgroup(key=key, severe=severe)


    #---------------------------------------------------------------

    def define_parmgroup (self, key, tags=None,
                          descr='<descr>', unit=None,
                          default=0.0,
                          constraint=dict(min=None, max=None),
                          simuldev=None,
                          tiling=None, time_deg=0, freq_deg=0,
                          mode='nosolve'):
        """Define a named (key) group of similar parameters"""

        # Check whether the group exists already:
        if self._parmgroups.has_key(key):
            s = '** duplicate parmgroup definition: '+str(key)
            raise ValueError,s

        # Some added value:
        tags = self.tags2list(tags)
        if True:
            if self.name:
                if not self.name in tags:
                    tags.append(self.name)    

        # Create the ParmGroup:
        pg = ParmGroup.ParmGroup (self.ns, key, tags=tags,
                                  namespace=self.name,
                                  descr=descr, unit=unit,
                                  default=default,
                                  constraint=constraint,
                                  simuldev=simuldev,
                                  tiling=tiling,
                                  time_deg=time_deg,
                                  freq_deg=freq_deg,
                                  mode=mode)
        
        self._parmgroups[key] = pg

        # Change the option list of the 'tobesolved' option:
        opt = []
        self._make_gogs()
        opt.extend(self._parmgogs.keys())
        # opt.extend(self.active_groups())
        if not None in opt: opt.append(None)
        self._OM.modify ('tobesolved', opt=opt)

        return key



    #-------------------------------------------------------------------

    def simuldev_expr (self, ampl='{0.01~10%}', Psec='{500~10%}', PHz=None):
        """Helper function to make a standard simuldev expression.
        All arguments must be strings of the form {<value>~<stddev>}.
        The <stddev> is used to generate different values around <value>
        for each member of the group (see .group_create_member())."""
        s = ampl
        if isinstance(Psec,str):
            s += ' * sin(2*pi*([t]/'+Psec+'+{0~1}))'
        if isinstance(PHz,str):
            s += ' * sin(2*pi*([f]/'+PHz+'+{0~1}))'
        return s



    #===================================================================
    # TDLOptions:
    #===================================================================

    def make_TDLCompileOptionMenu (self, **kwargs):
        """Make the TDLMenu of compile-time options"""
        oolist = []
        for key in self._parmgroups.keys():
            pg = self._parmgroups[key]
            oolist.append(pg.make_TDLCompileOptionMenu(include_reset_option=False))        
        return self._OM.make_TDLCompileOptionMenu(insert=oolist, **kwargs)
    
    def make_TDLRuntimeOptionMenu (self, **kwargs):
        """Make the TDLMenu of runtime-time options"""
        oolist = []
        for key in self._parmgroups.keys():
            pg = self._parmgroups[key]
            oolist.append(pg.make_TDLRuntimeOptionMenu(include_reset_option=False))        
        return self._OM.make_TDLRuntimeOptionMenu(insert=oolist, **kwargs)
    
    #.........................................................................

    def define_options(self, tobesolved=None):
        """Define the various options in its OptionManager object"""
        key = 'tobesolved'
        doc = 'the selected groups will be solved simultaneously'
        self._OM.define(key, tobesolved,
                        prompt='PGM: solve for parmgroup(s)/parmgog(s)',
                        callback=self._callback_tobesolved,
                        opt=[None], more=str, doc=doc)
        # NB: The option-list of 'tobesolved' is updated after each
        #     ParmGroup definition. See .define_parmgroup()
        return True
    
    #.........................................................................

    def _callback_tobesolved (self, tobs):
        """Called whenever option 'tobesolved' is changed"""
        keys = self.find_parmgroups(tobs, severe=True)
        # Set the mode of selected groups (is this the desired behaviour...?)
        for key in self._parmgroups.keys():
            pg = self._parmgroups[key]
            if pg.active():
                if key in keys:
                    pg._OM.set_value('mode', 'solve')
                else:
                    pg._OM.set_value('mode', 'nosolve')
        return True

    #.........................................................................

    def TDLShowActive (self):
        """Show the TDL options for the 'active' parmgroup(s), and hide the rest.
        Also redefine the parmgogs, and update the relevant TDL options."""

        # First show/hide the parmgroups:
        for key in self._parmgroups.keys():
            pg = self._parmgroups[key]
            pg._OM.show(pg.active())
                
        # Then update the option list of option 'tobesolved':
        self._make_gogs()
        key = 'tobesolved'
        if self._OM.TDLOption(key):
            oo = self._OM.TDLOption(key)
            value = oo.value
            newopt = [None]
            newopt.extend(self._parmgogs.keys())
            if False:
                for key in self._parmgogs.keys():
                    if len(self._parmgogs[key])>1:
                        newopt.append(key)
                newopt.extend(self.active_groups())
            if value in newopt:
                oo.set_option_list(newopt, conserve_selection=True)
            else:
                index = 0         # index of first value (None)
                oo.set_option_list(newopt, select=index)

        # Finished:
        return True

    #.....................................................................

    def reset_options(self, trace=False):
        """Helper function to reset the TDLCompileOptions and their local
        counterparts to the original default values (in self.tdloption_reset).
        Recursive: It calls the same function for its parmgroups.
        """
        self._OM.reset_options(trace=trace)
        # Recursive:
        for key in self._parmgroups:
            self._parmgroups[key]._OM.reset_options(trace=trace)
        return True
        


    #===============================================================
    # Merge the parametrization of another object in its own.
    #===============================================================

    # NB: One should be careful with this since it has merit to keep 
    #     parameter sets with the same names but different qualifiers apart.
    #     But it is useful for merging parametrizations in the same subtree.
    #     For instance, a JJones object, which is the multiplication of 
    #     multiple Jones matrices, with DIFFERENT parmgroup names.

    def merge (self, other, trace=False):
        """Merge the parm contents with those of another object.
        The latter must be derived of Meow.Parametrization, but
        it may or may not be derived from Grunt.ParmGroupManager.
        If not, it will copy the parmdefs, but not any parmgroups."""
        
        if trace:
            self.display('before PGM.merge()', full=True)
            ff = getattr(other, 'display', None)
            if ff: other.display('other', full=True)

        if other in self._pmerged:
            # print '\n** merge(): skipped (merged before): ',str(other),'\n'
            return True


        # Check whether the other object has a Grunt.ParmGroupManager
        PGM = getattr(other, '_PGM', None)
        print '\n** PGM =',type(PGM), isinstance(PGM, ParmGroupManager),'\n'
        if isinstance(PGM, ParmGroupManager):
            # The other object DOES have a Grunt.ParmGroupManager
            self._pmerged.append(other)               # Avoid duplicate merging....
            
            # Copy its ParmGroup(s) (objects):
            # NB: Avoid duplicate parmgroups (solvable and simulated versions
            # of the same Joneset should be compared, rather than merged!).
            pgs = PGM._parmgroups
            for key in pgs:
                if not pgs[key].active():
                    print '** skipping inactive parmgroup:',key
                else:
                    if self._parmgroups.has_key(key):
                        if self._parmgroups[key].active():
                            s = '** cannot merge duplicate parmgroups: '+key 
                            raise ValueError, s
                        print '** overwriting inactive parmgroup:',key
                    self._parmgroups[key] = pgs[key]


        # Check whether the other object is derived from Meow.Parameterization
        elif isinstance(rr, getattr(other, '_parmdefs', None)):
            rr = getattr(other, '_parmdefs', None)
            # The other object IS derived from Meow.Parameterization
            self._pmerged.append(other)               # avoid duplicate merging....

            # Make a single parmgroup from its parmnodes
            # Copy the parmdefs with slightly different names
            descr = 'copied from Meow.Parameterization of: '
            if getattr(other,'oneliner',None):
                descr += str(other.oneliner())
            else:
                descr += str(other.name)
            self.define_parmgroup (other.name, tags=None, descr=descr)
            pg = self._parmgroups[other.name]
            for key in other._parmdefs:
                pd = other._parmdefs[key]               # assume: (value, tags, solvable)
                newkey = other.name+'_'+key
                # self._parmdefs[newkey] = pd
                pg._parmdefs[newkey] = pd
                # pg._nodes.append(self._parm(newkey))      # generate a node in self, not other!
                pg._nodes.append(pg._parm(newkey))      # generate a node in pg, not other!
                pg._solvable.append(pd[2])              # 3rd element: solvable (boolean)
                pg._plot_labels.append(newkey)          # ....?


        else:
            # Error?
            pass

        if trace:
            self.display('after PGM.merge()', full=True)
        return True



    #===============================================================
    # Convenient access to a list of nodes/subtrees, e.g. for solving
    #===============================================================


    def tobesolved (self, return_nodes=True, return_NodeList=False, trace=False):
        """Get a list of the parmgroups (or tags?) that have been selected for solving.
        If return_nodes or return_NodeList (object), do that."""
        pgs = self._tobesolved
        if return_nodes or return_NodeList:
            return self.solvable(groups=pgs, trace=trace,
                                    return_NodeList=return_NodeList)
        elif trace:
            print '\n** tobesolved: ',pgs,'\n'
        return pgs


    #----------------------------------------------------------------

    def solvable (self, tags=None, groups='*', return_NodeList=False, trace=False):
        """Return a list with the specified selection of solvable MeqParm nodes.
        The nodes may be specified by their tags (n.search) or by parmgroups."""
        return self.find_nodes (tags=tags, groups=groups,
                                  return_NodeList=return_NodeList,
                                  solvable=True, trace=trace)


    #----------------------------------------------------------------

    def find_nodes (self, tags=None, groups='*', solvable=None,
                    return_NodeList=False, trace=False):
        """Return a list with the specified selection of the nodes (names)
        that are known to this Parameterization object. The nodes may be
        specified by their tags (n.search) or by parmgroups. The defaults are
        tags=None and groups='*', but tags are checked first."""

        if trace:
            print '\n** find_nodes(tags=',tags,', groups=',groups,', solvable=',solvable,'):'
        nodes = []
        labels = []
        name = 'parms'

        if tags:
            # A tags specification has precedence:
            # NB: Should we search the nodescopes of its parmgroups?
            #     (assuming that those have been derived from self.ns...?)
            tags = self.tags2list(tags)
            class_name = None
            if solvable:
                tags.append('solvable')
                class_name = 'MeqParm'
            if trace:
                print ' -- self.ns.Search(',class_name,' tags=',tags,')'
            nodes = self.ns.Search(tags=tags, class_name=class_name)
            for node in nodes:
                labels.append(node.name)

        elif groups:
            # Use the groups specification:
            pgs = self.find_parmgroups (groups, severe=True)
            for key in pgs:
                pg = self._parmgroups[key]              # convenience
                if not isinstance(solvable, bool):      # solvable not specified
                    nodes.extend(pg._nodes)             # include all nodes
                    labels.extend(pg._plot_labels)      # include all 
                else:
                    for k,node in enumerate(pg._nodes):
                        if pg._solvable[k]==solvable:   # the specified kind
                            nodes.append(node)          # selected nodes only
                            labels.append(pg._plot_labels[k])

        # Report the found nodes (if any):
        if trace:
            for k,node in enumerate(nodes):
                print '  - (',labels[k],'):',str(node)
            print ' ->',len(nodes),'nodes, ',len(labels),'labels'

        # Optionally, return a NodeList object of the selected nodes and their labels
        if return_NodeList:
            if tags:
                name = 'tags'
                for k,tag in enumerate(tags):
                    name += str(tag)
                if trace:
                    print ' -- tags =',tags,' (name=',name,')'
            else:
                name = 'gogs'
                if isinstance(groups,str):
                    name += groups
                elif isinstance(groups,(list,tuple)):
                    for k,group in enumerate(groups):
                        name += str(group)
                if trace:
                    print ' -- groups =',groups,'(name=',name,') -> pgs =',pgs
            nn = NodeList.NodeList(self.ns, name, nodes=nodes, labels=labels)
            if trace: print ' ->',nn.oneliner(),'\n'
            return nn

        else:
            # Otherwise, just return a list of nodes:
            return nodes


    #------------------------------------------------------------------------

    def find_parmgroups (self, groups, severe=True, trace=False):
        """Helper function to covert the specified groups (parmgroups or gogs)
        into a list of existing parmgroup names. If severe==True, stop if error.
        """
        # First make sure that the selection is a list (of names):
        if groups==None:
            return []
        if isinstance(groups, str):
            groups = groups.split(' ')                 # make a list from string
        groups = list(groups)                          # make sure of list
        if groups[0]=='*':
            groups = self._parmgroups.keys()           # all parmgroups

        # Make a (unique) list pg of valid parmgroups from the gogs: 
        self._make_gogs()
        pg = []
        for key in groups:
            if self._parmgogs.has_key(key):
                for g in self._parmgogs[key]:
                    if not g in pg: pg.append(g)
            elif severe:
                raise ValueError,'** parmgroup not recognised: '+key
        return pg


    #===============================================================
    # Parmgogs: Groups of parmgroups
    #===============================================================

    def gogs (self):
        """Return the list of available groups of parmgroups (gogs).
        These are used in finding groups, e.g. for solving."""
        return self._make_gogs().keys()


    def _make_gogs (self):
        """Derive a dict of named groups of (active) parmgroups from the tags
        of the various (active) parmgroups. These may be used to select groups,
        e.g. in .solvable()."""
        gg = dict()
        gg.setdefault('*',[])
        keys = self._parmgroups.keys()
        for key in keys:
            pg = self._parmgroups[key]
            if pg.active():                # active groups only!
                tags = pg._tags
                for tag in tags:
                    gg.setdefault(tag,[])
                    if not key in gg[tag]:
                        gg[tag].append(key)
                if not key in gg['*']:     # all active groups (*)
                    gg['*'].append(key)
        self._parmgogs = gg
        return self._parmgogs



    #===============================================================
    # Methods using NodeList(s):
    #===============================================================

    def compare (self, parmgroup, other, show=False):
        """Compare the nodes of a parmgroup with the corresponding ones
        of the given (and assumedly commensurate) parmgroup (other).
        The results are visualized in various helpful ways.
        The rootnode of the comparison subtree is returned.
        """
        self.has_group (parmgroup, severe=True)
        self.has_group (other, severe=True)
        pg1 = self._parmgroups[parmgroup]
        pg2 = self._parmgroups[other]
        return pg1.compare(pg2, show=show)


    #---------------------------------------------------------------

    def bundle (self, parmgroup='*', combine='Composer',
                  bookpage=True, folder=None, show=False):
        """Bundle the nodes in the specified parmgroup(s) by applying the
        specified combine-operation (default='Add') to them. Return the
        root node of the resulting subtree. Make bookpages for each parmgroup.
        """
        pgs = self.find_parmgroups (parmgroup, severe=True)
        if folder==None:
            if len(pgs)>1: folder = 'bundle_'+self.name
        bb = []
        for key in pgs:
            pg = self._parmgroups[key]
            bb.append(pg.bundle(bookpage=bookpage, folder=folder))
        return self._bundle_of_bundles (bb, name='bundle',
                                          qual=parmgroup,
                                          accu=True, show=show)

    #---------------------------------------------------------------

    def plot_rvsi (self, parmgroup='*',
                     bookpage=True, folder=None, show=False):
        """Make separate rvsi plots of the specified parmgroup(s). Return the
        root node of the resulting subtree. Make bookpages for each parmgroup.
        """
        pgs = self.find_parmgroups (parmgroup, severe=True)
        if bookpage:
            if not isinstance(bookpage, str):
                bookpage = 'plot_rvsi_'+self.name
        bb = []
        for key in pgs:
            pg = self._parmgroups[key]
            bb.append(pg.plot_rvsi(bookpage=bookpage, folder=folder))
        return self._bundle_of_bundles (bb, name='plot_rvsi',
                                          qual=parmgroup,
                                          accu=True, show=show)
    
    #---------------------------------------------------------------

    def plot_timetracks (self, parmgroup='*', 
                           bookpage=True, folder=None, show=False):
        """Visualize the nodes in the specified parmgroup(s) in a separate
        'inspector' (time-tracks) per parmgroup. Return the root node of
        the resulting subtree. Make bookpages for each parmgroup.
        """
        pgs = self.find_parmgroups (parmgroup, severe=True)
        if bookpage:
            if not isinstance(bookpage, str):
                bookpage = 'plot_timetracks_'+self.name
        bb = []
        for key in pgs:
            pg = self._parmgroups[key]
            bb.append(pg.plot_timetracks (bookpage=bookpage, folder=folder))
        return self._bundle_of_bundles (bb, name='plot_timetracks',
                                          qual=parmgroup,
                                          accu=True, show=show)


    #---------------------------------------------------------------

    def plot_spectra (self, parmgroup='*', 
                           bookpage=True, folder=None, show=False):
        """Visualize the nodes in the specified parmgroup(s) in a separate
        'inspector' (time-tracks) per parmgroup. Return the root node of
        the resulting subtree. Make bookpages for each parmgroup.
        """
        pgs = self.find_parmgroups (parmgroup, severe=True)
        if bookpage:
            if not isinstance(bookpage, str):
                bookpage = 'plot_spectra_'+self.name
        bb = []
        for key in pgs:
            pg = self._parmgroups[key]
            bb.append(pg.plot_spectra (bookpage=bookpage, folder=folder))
        return self._bundle_of_bundles (bb, name='plot_spectra',
                                          qual=parmgroup,
                                          accu=True, show=show)


    
    #---------------------------------------------------------------
    # Helper function:
    #---------------------------------------------------------------

    def _bundle_of_bundles (self, bb, name=None, qual=None,
                              accu=False, show=False):
        """Helper function to bundle a list of parmgroup bundles"""

        if len(bb)==0:
            return None
        elif len(bb)==1:
            qnode = bb[0]
        else:
            qnode = self.ns[name](qual)
            if not qnode.initialized():                        #......!!?
                qnode << Meq.Composer(children=bb)

        # Finished: Return the root-node of the bundle subtree:
        if accu: self.accumulist(qnode)
        if show: display.subtree(qnode, show_initrec=False)
        return qnode


    #===============================================================
    # Some useful helper functions (available to all derived classes)
    #===============================================================

    def tags2list (self, tags):
        """Helper function to make sure that the given tags are a list"""
        if tags==None: return []
        if isinstance(tags, (list, tuple)): return list(tags)
        if isinstance(tags, str): return tags.split(' ')
        s = '** cannot convert tag(s) to list: '+str(type(tags))+' '+str(tags)
        raise TypeError, s

    def quals2list (self, quals):
        """Helper function to make sure that the given quals are a list"""
        if quals==None: return []
        if isinstance(quals, (list,tuple)): return list(quals)
        if isinstance(quals, str): return quals.split(' ')
        return [str(quals)]

    #----------------------------------------------------------------

    def get_quals (self, merge=None, remove=None):
        """Helper function to get a list of the current nodescope qualifiers"""
        quals = (self.ns.dummy).name.split(':')
        quals.remove(quals[0])
        if isinstance(merge,list):
            for q in merge:
                if not q in quals:
                    quals.append(q)
        if isinstance(remove,list):
            for q in remove:
                if q in quals:
                    quals.remove(q)
        return quals


    #===============================================================
    # Some extra functionality for Meow.Parameterization 
    #===============================================================

    def modify_default (self, key):
        """Modify the default value of the specified (key) parm"""
        # Not yet implemented..... See Expression.py
        return False





    #=====================================================================================
    #=====================================================================================
    # Accumulist service:
    # NB: This service does not really belong here, but is convenient.
    #=====================================================================================

    def accumulist (self, item=None, key=None, flat=False, clear=False):
        """Interact with the internal service for accumulating named (key) lists of
        items (nodes, usually), for later retrieval downstream.
        If flat=True, flatten make a flat list by extending the list with a new item
        rather than appending it.
        An extra list with key=* contains all items of all lists"""

        print '\n** accumulist(',str(item),')\n'
        
        if key==None: key = '_default_'
        if not isinstance(key, str):
            print '\n** .accumulist(): key is wrong type:',type(key),'\n'
            return False      
        self._accumulist.setdefault(key, [])           # Make sure that the list exists
        self._accumulist.setdefault('*', [])           # The list of ALL entries
        if item:
            if not flat:                                                                  
                self._accumulist[key].append(item)
                self._accumulist['*'].append(item)
            elif isinstance(item, (list,tuple)):
                self._accumulist[key].extend(item)
                self._accumulist['*'].extend(item)
            else:
                self._accumulist[key].append(item)
                self._accumulist['*'].append(item)
        # Always return the current value of the specified (key) list:
        keylist = self._accumulist[key]           
        if clear:
            # Optional: clear the entry (NB: What happens to '*' list??)
            self._accumulist[key] = []
            # self._accumulist['*'] = []
        # Enhancement: If flat=True, flatten the keylist....?
        return keylist

    #---------------------------------------------------------------------

    def bundle_accumulist(self, quals=None):
        """Bundle the nodes in self._accumulist with a reqseq"""
        cc = self.accumulist(clear=False)
        n = len(cc)
        if n==0: return None
        if n==1: return cc[0]
        # self.history('.bundle_accumulist()')
        qnode = self.ns['bundle_accumulist']
        if quals: qnode = qnode(quals)
        if not qnode.initialized():
            qnode << Meq.ReqSeq(children=cc, result_index=n-1)
        return qnode

    #---------------------------------------------------------------------------

    def merge_accumulist (self, other):
        """Merge the accumulist of another Matrix22 object with its own."""
        # self.history('.merge_accumulist()')
        olist = other._accumulist
        for key in olist.keys():
            if not key=='*':
                self.accumulist(olist[key], key=key, flat=True)
        return True





#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================


if 1:
    PGM = ParmGroupManager(name='GJones',
                           namespace='ParmGroupManagerNamespace')
    PGM.define_parmgroup('Gphase', tiling=3, mode='nosolve')
    PGM.define_parmgroup('Ggain', default=1.0, freq_deg=2)
    PGM.make_TDLCompileOptionMenu()
    PGM.display('initial')



def _define_forest(ns):

    cc = []
    PGM.nodescope(ns)

    if 1:
        PGM['Gphase'].create_member(1)
        PGM['Gphase'].create_member(2.1, value=(ns << -89))
        PGM['Gphase'].create_member(2, value=34)
        PGM['Gphase'].create_member(3, tiling=5, mode='simulate')
        PGM['Gphase'].create_member(7, freq_deg=2)

    if 1:
        PGM['Ggain'].create_member(7, freq_deg=6)
        PGM['Ggain'].create_member(4, time_deg=3)

    if 0:
        cc.append(PGM.bundle(show=True))
        cc.append(PGM.plot_timetracks())
        cc.append(PGM.plot_spectra())

    if 0:
        nn = PGM.solvable(groups='GJones', return_NodeList=True)
        nn.display('solvable')
        nn.bookpage(select=4)
        

    PGM.display('final', full=True)
    if 1:
        PGM.pg_display(full=True)

    if len(cc)==0: cc.append(ns.dummy<<1.1)
    ns.result << Meq.Composer(children=cc)
    PGM.make_TDLRuntimeOptionMenu()
    return True



#---------------------------------------------------------------

def _tdl_job_2D_tf (mqs, parent):
    """Execute the forest with a 2D request (freq,time), starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,0,2000)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=100)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       










#===============================================================
# Test routine:
#===============================================================


if __name__ == '__main__':
    from Timba.Contrib.JEN.Expression import Expression
    ns = NodeScope()

    if 1:
        PGM = ParmGroupManager(ns, 'GJones')
        PGM.define_parmgroup('Gphase', tiling=3, mode='nosolve')
        PGM.define_parmgroup('Ggain', default=1.0, freq_deg=2)
        if 1:
            PGM.make_TDLCompileOptionMenu()
        PGM.display('initial')


    if 0:
        print PGM['Gphase'].oneliner()
        print PGM['Ggain'].oneliner()

    if 0:
        PGM['Gphase'].create_member(1)
        PGM['Gphase'].create_member(2.1, value=(ns << -89))
        PGM['Gphase'].create_member(2, value=34)
        PGM['Gphase'].create_member(3, tiling=5, mode='solve')
        PGM['Gphase'].create_member(7, freq_deg=2)

    if 0:
        PGM['Ggain'].create_member(7, freq_deg=6)
        PGM['Ggain'].create_member(4, time_deg=3)


    if 0:
        PGM.bundle(show=True)
    if 0:
        PGM.plot_rvsi(show=True)
    if 0:
        PGM.plot_spectra(show=True)
    if 0:
        PGM.plot_timetracks(show=True)

    if 0:
        PGM.display('final', full=True, om=True)


    #------------------------------------------------------------------

    if 0:
        print dir(PGM)
        print getattr(PGM,'_parmgroup',None)

    if 0:
        print 'ns.Search(tags=Gphase):',ns.Search(tags='Gphase')
        print 'PGM.ns.Search(tags=Gphase):',PGM.ns.Search(tags='Gphase')

    if 0:
        PGM.solvable()
        PGM.solvable(groups='Gphase', trace=True)
        PGM.solvable(groups=['Ggain'], trace=True)
        PGM.solvable(groups=['GJones'], trace=True)
        PGM.solvable(groups=['Gphase','Ggain'], trace=True)
        PGM.solvable(groups=PGM.groups(), trace=True)
        PGM.solvable(groups=PGM.gogs(), trace=True)
        # PGM.solvable(groups=['Gphase','xxx'], trace=True)

    if 0:
        PGM.solvable(tags='Gphase', trace=True)
        PGM.solvable(tags=['Gphase','Ggain'], trace=True)
        PGM.solvable(tags=['Gphase','GJones'], trace=True)
        PGM.solvable(tags=['Gphase','Dgain'], trace=True)

    if 0:
        solvable = True
        PGM.find_nodes(groups='GJones', solvable=solvable, trace=True)
        PGM.find_nodes(groups=PGM.gogs(), solvable=solvable, trace=True)

    if 0:
        pp2 = ParmGroupManager(ns, 'DJones')
        pp2.define_parmgroup('Ddell')
        pp2.define_parmgroup('Ddang')
        pp2.group_create_member('Ddang', 1)
        pp2.group_create_member('Ddell', 7)
        pp2.display(full=True)
        if 1:
            PGM.merge(pp2, trace=True)
            PGM.find_nodes(groups=['GJones','DJones'], solvable=True, trace=True)
            PGM.find_nodes(groups=['GJones','DJones'], solvable=False, trace=True)
        PGM.display('after merge', full=True)

    if 0:
        e0 = Expression.Expression(ns, 'e0', '{a}+{b}*[t]-{e}**{f}+{100~10}', simul=False)
        e0.display()
        if 0:
            pp3 = ParmGroupManager(ns, 'e0', merge=e0)
            pp3.display('after merge', full=True)
        if 1:
            PGM.merge(e0, trace=True)
            PGM.display('after merge', full=True)
            PGM.pg_display(full=True)

    if 0:
        PGM.accumulist('aa')
        PGM.accumulist('2')
        PGM.accumulist(range(3), flat=True)
        PGM.accumulist('bb', key='extra')
        PGM.display(full=True)
        print '1st time:',PGM.accumulist()
        print '1st time*:',PGM.accumulist(key='*')
        print '2nd time:',PGM.accumulist(clear=True)
        print '3rd time:',PGM.accumulist()


#===============================================================
