# file: ../Grunt/NodeGroupManager.py

# History:
# - 04jan2007: creation (extracted from Matrix22.py) 

# Description:

# The NodeGroupManager class encapsulates a number of NodeGroups
# e.g. ParmGroups or SimulatedParmGroups.
# It is used in classes like Matrix22. 

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

from ParmGroup import *
from Qualifiers import *

# from Timba.Contrib.JEN.Grunt import ParmGroup
from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect

from copy import deepcopy

#======================================================================================

class NodeGroupManager (object):
    """Class that encapsulates a number of NodeGroups
    e.g. ParmGroups or SimulatedParmGroups."""

    def __init__(self, ns, quals=[], label='ngm', simulate=False):
        self._ns = ns                                # node-scope (required)
        self._label = label                          # label of the matrix 

        # Node-name qualifiers:
        self._quals = Qualifiers(quals, prepend=label)

        self._simulate = simulate                    # if True, use simulation subtrees (i.s.o. MeqParms)
        if self._simulate:
            self._quals.append('simul')

        # NodeGroup objects:
        self._parmgroup = dict()                     # available ParmGroup objects (solvable)
        self._simparmgroup = dict()                  # available SimulatedParmGroup objects 
        self._pgog = dict()                          # used for define_gogs()
        self._sgog = dict()                          # used for define_gogs()
        self._dummyParmGroup = ParmGroup('dummy')    # used for its printing functions...
        return None


    #-------------------------------------------------------------------

    def label(self):
        """Return the NodeGroupManager object label""" 
        return self._label

    def quals(self, append=None, prepend=None, exclude=None):
        """Return the nodename qualifier(s), with temporary modifications"""
        return self._quals.get(append=append, prepend=prepend, exclude=exclude)


    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += '  '+str(self.label())
        ss += '  quals='+str(self.quals())
        if self._simulate: ss += ' (simulate)'
        return ss

    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        # NB: This function is called in .display().
        #     It should be re-implemented in a derived class.
        return True

    def display(self, txt=None, full=False):
        """Print a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print ' * (txt='+str(txt)+')'
        self.display_specific(full=full)
        print '** Generic (class NodeGroupManager):'
        #...............................................................
        ntot = len(self._parmgroup) + len(self._simparmgroup)
        print ' * Available NodeGroup objects ('+str(ntot)+'): '
        for key in self.parmgroups():
            print '  - '+str(self._parmgroup[key].oneliner())
        for key in self._simparmgroup.keys():
            print '  - (sim) '+str(self._simparmgroup[key].oneliner())
        #...............................................................
        print '**\n'
        return True


    #=====================================================================

    def define_parmgroup(self, name, descr=None,
                         default=0.0, tags=[], 
                         Tsec=1000.0, Tstddev=0.1,
                         scale=1.0, stddev=0.1,
                         matrel='*',
                         rider=None):
        """Helper function to define a named (Simulated)ParmGroup object."""

        # ....
        node_groups = ['Parm']
        # node_groups.extend(self.quals())               # <---------- !!!

        # Make sure that the group name is in the list of node tags:
        ptags = deepcopy(tags)
        if not isinstance(ptags,(list,tuple)): ptags = [ptags]
        if not name in ptags: ptags.append(name)

        # Specific information is attached to the ParmGroup via its rider.
        if not isinstance(rider, dict): rider = dict()

        # OK, define the relevant ParmGroup:
        if self._simulate:
            spg = SimulatedParmGroup (self._ns, label=name,
                                      quals=self.quals(),
                                      descr=descr, default=default,
                                      tags=ptags, 
                                      Tsec=Tsec, Tstddev=Tstddev,
                                      scale=scale, stddev=stddev,
                                      rider=rider) 
            self._simparmgroup[name] = spg

        else:
            # - matrel specifies the matrix elements that are affected by the
            #   MeqParms in this ParmGroup, and that are to be used in solving.
            rider['matrel'] = deepcopy(matrel)
            pg = ParmGroup (self._ns, label=name, 
                            quals=self.quals(),
                            descr=descr, default=default,
                            tags=ptags, node_groups=node_groups,
                            rider=rider)
            self._parmgroup[name] = pg

        # Collect information for define_gogs():
        for tag in ptags:
            if not tag in [name]:
                if self._simulate:
                    self._sgog.setdefault(tag, [])
                    self._sgog[tag].append(self._simparmgroup[name])
                else:
                    self._pgog.setdefault(tag, [])
                    self._pgog[tag].append(self._parmgroup[name])

        # Finished:
        return True

    #.....................................................................................

    def create_parmgroup_entry(self, key=None, qual=None):
        """Create an entry with the specified qual in the specified (key)
        (Simulated)ParmGroup (object)"""
        if self._simulate:
            return self._simparmgroup[key].create_entry(qual)
        return self._parmgroup[key].create_entry(qual)

    #.....................................................................................

    def define_gogs(self, name='NodeGroupManager'):
        """Helper function to define NodeGogs, i.e. groups of ParmGroups.
        It uses the information gleaned from the tags in define_parmgroup()"""
        print '\n** define_gogs(',name,'):'

        # First collect the primary ParmGroups in pg and spg:
        pg = []
        for key in self._parmgroup.keys():
            pg.append(self._parmgroup[key])
        spg = []
        for key in self._simparmgroup.keys():
            spg.append(self._simparmgroup[key])
            
        # Then make separate gogs, as defined by the common tags:
        for key in self._pgog.keys():
            rider = self._make_pgog_rider(self._pgog[key])
            self._parmgroup[key] = NodeGog (self._ns, label=key, descr='<descr>', 
                                            group=self._pgog[key],rider=rider)
        for key in self._sgog.keys():
            self._simparmgroup[key] = NodeGog (self._ns, label=key, descr='<descr>', 
                                               group=self._sgog[key])

        # Make the overall parmgroup(s) last, using the pg collected first:
        # (Otherwise it gets in the way of the automatic group finding process).
        for label in [name,'*']:
            if len(pg)>0:
                rider = self._make_pgog_rider(pg)
                self._parmgroup[label] = NodeGog (self._ns, label=label, group=pg, rider=rider,
                                                  descr='all '+name+' parameters')
            if len(spg)>0:
                self._simparmgroup[label] = NodeGog (self._ns, label=label, group=spg,
                                                     descr='all simulated '+name+' parameters')
        return None

    #.....................................................................

    def _make_pgog_rider(self, group=[]):
        """Helper function to make a NodeGog rider from the riders of
        the given group (list) of ParmGroups"""
        # If any of the groups has matrel=='*' (all), return that.
        for pg in group:
            if pg.rider('matrel')=='*': return dict(matrel='*')
        # Otherwise, collect a list:
        mm = []
        for pg in group:
            mg = pg.rider('matrel')
            if not isinstance(mg,(list,tuple)): mg = [mg]
            for m in mg:
                if not m in mm:
                    mm.append(m)
        return dict(matrel=mm)


    #--------------------------------------------------------------

    def parmgroups(self):
        """Return the available ParmGroup names."""
        return self._parmgroup.keys()

    def parmgroup(self, key=None):
        """Return the specified ParmGroup (object)"""
        return self._parmgroup[key]
    
    def display_parmgroups(self, full=False):
        """Display its ParmGroup objects"""
        print '\n******** .display_parmgroups(full=',full,'):'
        print '           ',self.oneliner()
        for key in self.parmgroups():
            self._parmgroup[key].display(full=full)
        print '********\n'
        return True

    def merge_parmgroups(self, other):
        """Helper function to merge its parmgroups with those of another NodeGroupManager object"""
        self._parmgroup.update(other._parmgroup)
        self._simparmgroup.update(other._simparmgroup)
        return True



    

    #=====================================================================
    # Test module:
    #=====================================================================

    def test (self):
        """Helper function to make some test-matrices"""
        quals = self.quals()
        name = 'matrix22'
        keys = self._matrel.keys()
        index = 0
        indices = []
        for key in keys:
            index += 1
            indices.append(index)
            self.define_parmgroup(key, descr='matrix element: '+key,
                                  default=index/10.0, stddev=0.01,
                                  tags=['test'])
            mm = dict(m11=0.0, m12=0.0, m21=0.0, m22=0.0)
            mm[key] = self.create_parmgroup_entry(key, index)
            mm[key] = self._ns << Meq.Polar(1.0,mm[key])
            mat = self._ns[name](*quals)(index) << Meq.Matrix22(mm['m11'],mm['m12'],
                                                                mm['m21'],mm['m22'])
        # Store the matrices and the list if indices:
        self.indices(new=indices)
        self.matrix(new=self._ns[name](*quals))

        # Make some secondary (composite) ParmGroups:
        self.define_gogs()
        return True







     
#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []
    simulate = True

    mat1 = NodeGroupManager(ns, quals=[], simulate=True)
    mat1.test()
    cc.append(mat1.visualize())
    mat1.display(full=True)

    mat2 = NodeGroupManager(ns, quals=[], simulate=False)
    mat2.test()
    cc.append(mat2.visualize())
    mat2.display(full=True)

    reqseq = mat1.make_solver('*', mat2)
    cc.append(reqseq)

    ns.result << Meq.ReqSeq(children=cc)
    return True

#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       


#===============================================================
# Test routine:
#===============================================================

if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        m1 = NodeGroupManager(ns, quals=['3c84','xxx'], label='HH', simulate=True)
        m1.test()
        # m1.display_parmgroups(full=False)
        m1.display(full=True)

    if 0:
        m1.unop('Cos')
        m1.display('after unop', full=True)
        


#===============================================================
    