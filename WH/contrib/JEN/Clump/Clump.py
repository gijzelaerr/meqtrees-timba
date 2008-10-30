"""
Clump.py: Base-class for an entire zoo of derived classes that
represent 'clumps' of trees, i.e. sets of similar nodes.
Examples are ParmClump, JonesClump and VisClump.
"""

# file: ../JEN/Clump/Clump.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 25 oct 2008: creation
#
# Description:
#
# Remarks:
#
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

from Timba.Contrib.JEN.control import TDLOptionManager as TOM

from Timba.Contrib.JEN.Easy import EasyNode as EN
from Timba.Contrib.JEN.Easy import EasyFormat as EF

import Meow.Bookmarks
from Timba.Contrib.JEN.util import JEN_bookmarks


import math                 # support math.cos() etc
# from math import *          # support cos() etc
# import numpy                # support numpy.cos() etc

clump_counter = -1          # used in Clump.__init__()

#******************************************************************************** 

class Clump (object):
   """
   Base-class for an entire zoo of derived classes that
   represent 'clumps' of trees, i.e. sets of similar nodes.
   Examples are ParmClump, JonesClump and VisClump.
   """

   def __init__(self, name=None,
                qual=None, kwqual=None,
                treequals=None,
                ns=None, TCM=None,
                use=None, init=True,
                **kwargs):
      """
      Initialize the Clump object, according to its type (see .init()).
      If another Clump of the same class is specified (use), use its
      defining characteristics (self._treequals etc)
      """
      # Make a short version of the type name (e.g. Clump)
      self._typename = str(type(self)).split('.')[1].split("'")[0]

      # If another Clump object is given (use), use its contents
      if not isinstance(use,type(self)):
         use = None
      
      # The Clump node names are derived from name and qualifier:
      self._name = name       
      self._qual = qual  
      self._kwqual = kwqual
      self._kwargs = kwargs
      self._used = None
      if use:
         self._used = use.oneliner() 
         if not isinstance(name,str):          # name not specified
            self._name = '('+use._name+')'
         if qual==None:                        # qual not specified
            self._qual = use._qual
         if kwqual==None:                      # kwqual not specified
            self._kwqual = use._kwqual
      if not isinstance(self._name,str):
         self._name = self._typename           # e.g. 'Clump'    
         global clump_counter
         clump_counter += 1
         self._name += str(clump_counter)

      # The 'size' of the Clump (i.e. the number of its trees)
      # is defined by the list of tree qualifiers:
      # NB: This is NOT necessarily the number of nodes.
      if use:
         self._treequals = use._treequals
      elif treequals==None:
         self._treequals = range(3)            # for testing
      elif isinstance(treequals,tuple):
         self._treequals = list(treequals)
      elif not isinstance(treequals,list):     # assume Clump of one
         self._treequals = [treequals]         #
      else:
         self._treequals = treequals           # just copy

      # Make sure that it has a nodescope (ns):
      self._ns = ns
      if use:
         self._ns = use._ns
      elif not ns:
         # If not supplied, make a local one.
         self._ns = NodeScope()

      # Make sure that it has an TDLOptionManager (TCM):
      self._TCM = TCM
      if use:
         self._TCM = use._TCM
      elif not self._TCM:
         # If not supplied, make a local one.
         self._TCM = TOM.TDLOptionManager(self._name)

      # Each Clump object has a special submenu, which is
      # started in .start_of_object_submenu(), which may be called
      # from .init() if that function defines any options,
      # or from another function (which one?)
      # In any case, any function that calls .start_of_submenu()
      # must end with: self.end_of_object_submenu()
      self._object_submenu = None   
      self._slavemaster = None
      if isinstance(kwargs,dict):
         if kwargs.has_key('master'):
            self._slavemaster = kwargs['master']

      # The nodes may be composed into a single tensor node.
      # In that case, the following qualifier will be used.
      # The list self._nodequals always has the same length as self._nodes.
      self._tensor_qual = 'tensor'+str(len(self._treequals))
      self._composed = False            # see .compose() and .decompose()
      self._nodequals = self._treequals     # self._nodequals is used for node generation


      # A Clump object maintains a history of itself:
      self._history = None                  # see self.history()

      # Nodes without parents (e.g. visualisation) are collected on the way:
      self._orphans = []                    # see self.rootnode()

      # A Clump objects operates in 'stages'. See self.unique_nodestub().
      self._stagename = None                # name of the current stage 
      self._stagecounter = -1               # number of the current stage

      # See self..unique_nodestub()
      self._stubtree = None

      # Finally: Initialize with suitable nodes (if required):
      # The function .init() is re-implemented in derived classes.
      # NB: See .copy() for an example where init=False.
      if init:
         self.init()

      return None

   #--------------------------------------------------------------------------

   def init (self, trace=False):
      """Initialize the object with suitable nodes.
      Called from __init__() only
      Place-holder: To be re-implemented for derived classes.
      """
      submenu = self.start_of_object_submenu()
      self._TCM.add_option('initype', ['real','complex','parm',
                                       'freq','time','freq+time'],
                           prompt='init node type')

      initype = self._TCM.getopt('initype', submenu)
      self._nodes = []
      stub = self.unique_nodestub()
      for i,qual in enumerate(self._nodequals):
         if initype=='parm':
            node = stub(qual) << Meq.Parm(i)
         elif initype=='freq':
            node = stub(qual) << Meq.Freq()
         elif initype=='time':
            node = stub(qual) << Meq.Time()
         elif initype=='freq+time':
            node = stub(qual) << Meq.Add(self._ns << Meq.Freq(),
                                         self._ns << Meq.Time())
         else:
            node = stub(qual) << Meq.Constant(i)
         self._nodes.append(node)
      self.history('.init()', trace=trace)

      # The LAST statement:
      self.end_of_object_submenu()
      return True

   #-------------------------------------------------------------------------

   def commensurate(self, other, severe=False, trace=False):
      """Return True if the given (other) Clump is commensurate,
      i.e. it has the same self._nodequals (NOT self._treequals!)
      """
      cms = True
      if not self.size()==other.size():
         cms = False
      else:
         snq = self._nodequals
         onq = other._nodequals
         for i,qual in enumerate(snq):
            if not qual==onq[i]:
               cms = False
               break
      if not cms:
         s = '\n** '+self.oneliner()+'   ** NOT COMMENSURATE ** with:'
         s += '\n   '+other.oneliner()+'\n'
         if severe:
            raise ValueError,s
         if trace:
            print s
      return cms
         

   #=========================================================================
   # Clump connection operations (very important for building complex structures)
   # Obviously, all this requires some thought....
   # def insert/append/chain(self, other)
   #=========================================================================

   def link (self, name=None, qual=None, unops=None, trace=False):
      """
      Return a new instance of this class, with the same size, treequals, ns and TCM.
      If no name is specified, derive a new name by enclosing self._name in brackets.
      The nodes are copied, possibly after applying one or more unary operations
      (unops) on them.
      NB: It does NOT matter whether the clump is 'composed' (i.e. a single tensor node)
      """
      if not isinstance(name, str):
         name = 'link('+self._name+')'

      # Create a new Clump of the same (possibly derived) type:
      new = self.newinstance(name=name, qual=qual, init=False)

      # Copy the nodes:
      new._nodes = []
      stub = new.unique_nodestub()
      for i,qual in enumerate(self._nodequals):
         node = self._nodes[i]
         new._nodes.append(node)

      new.history('link(unop='+str(unops)+')', trace=trace)
      new.history('| copied from: '+self.oneliner(), trace=trace)
      if unops:
         # Optionally, apply one or more unary operations
         new.apply_unops(unops, trace=trace)
      return new

   #-------------------------------------------------------------------------

   def newinstance(self, name=None, qual=None, init=False):
      """Make a new instance of this class. Called by .link().
      This function should be re-implemented in derived classes.
      """
      return Clump(name=name, qual=qual, use=self, init=init)

   #-------------------------------------------------------------------------

   def deepcopy (self, name=None, qual=None, trace=False):
      """Version of .link(), in which an Identity operation is applied
      to the nodes of the new object. This may not be very useful....?
      """
      return self.link (name=name, qual=qual, unops='Identity', trace=trace)


   #==========================================================================
   # Various text display functions:
   #==========================================================================

   def oneliner (self):
      ss = self._typename+': '
      ss += ' '+str(self._name)
      if not self._qual==None:
         ss += ' qual='+str(self._qual)
      ss += '  size='+str(self.size())
      ss += '  treequals=['+str(self._treequals[0])+'..'+str(self._treequals[-1])+']'
      if self._slavemaster:
         ss += '  slaved'
      if self._composed:
         ss += '  (composed: '+self._tensor_qual+')'
      ss += ' stage'+str(self._stagecounter)+':'+str(self._stagename)
      return ss

   #--------------------------------------------------------------------------

   def show (self, txt=None, full=True, doprint=True):
      """
      Format a summary of the contents of the object.
      If doprint=True, print it also.  
      """
      ss = '\n'
      ss += '\n** '+self.oneliner()
      if txt:
         ss += '   ('+str(txt)+')'
      ss += '\n * Generic (baseclass Clump):'
      ss += '\n * self._used: '+str(self._used)
      ss += '\n * self._kwqual: '+str(self._kwqual)
      ss += '\n * self._kwargs: '+str(self._kwargs)
      #.....................................................

      ss += '\n * self._nodes (.len()='+str(self.len())+', .size()='+str(self.size())+'):'
      n = len(self._nodes)
      if full:
         nmax = 2
         for i in range(min(nmax,n)):
            ss += '\n   - '+str(self._nodes[i])
         if n>nmax:
            if n>nmax+1:
               ss += '\n       ...'
            ss += '\n   - '+str(self._nodes[-1])
      else:
         ss += '\n   - node[0] = '+str(self._nodes[0])
         ss += '\n   - node[-1]= '+str(self._nodes[-1])
                                       
      #.....................................................
      ss += '\n * self._orphans (n='+str(len(self._orphans))+'):'
      for i,node in enumerate(self._orphans):
         ss += '\n   - '+str(node)
      #.....................................................

      nmax = 20
      qq = self._treequals
      ss += '\n * self._treequals(n='+str(len(qq))+'): '
      if len(qq)<=nmax:
         ss += str(qq)
      else:
         ss += str(qq[:nmax])+'...'+str(qq[-1])
      #.....................................................

      ss += '\n * self._ns: '+str(self._ns)
      if self._TCM:
         ss += '\n * self._TCM: '+str(self._TCM.oneliner())
      else:
         ss += '\n * self._TCM = '+str(self._TCM)
      ss += '\n * self._object_submenu = '+str(self._object_submenu)
      ss += '\n * self._slavemaster = '+str(self._slavemaster)
      #.....................................................

      ss += self.history(format=True, prefix='   | ')
      ss += self.show_specific()
      ss += '\n**\n'
      if doprint:
         print ss
      return ss

   #-------------------------------------------------------------------------

   def show_specific(self):
      """
      Format the specific (non-generic) contents of the class.
      Placeholder for re-implementation in derived class.
      """
      ss = '\n + Specific (derived class '+str(self._typename)+'):'
      ss += '\n + aa'
      ss += '\n + bb'
      return ss

   #-------------------------------------------------------------------------

   def show_tree (self, index=-1, full=True):
      """Show the specified (index) subtree.
      """
      node = self._nodes[index]
      print EN.format_tree(node, full=full)
      return True

   #-------------------------------------------------------------------------

   def history (self, append=None, prefix='',
                clear=False, format=False, 
                show=False, trace=False):
      """Interact with the object history (a list of strings).
      """
      clear |= (self._history==None)             # the first time
      if clear:
         self._history = []
         self._history.append('')
         s = '** Object history of: '+self.oneliner()
         self._history.append(s)
         if trace:
            print '** .history(clear)'

      if isinstance(append,str):
         if append[0]=='|':
            s = '    '+str(append)
         else:
            s = ' -- '+str(append)
            ilast = self.len()-1
            s += '   -> node['+str(ilast)+']: '+str(self._nodes[ilast])
         self._history.append(s)
         if trace:
            print '** .history(append): ',self._history[-1]

      if show or format:
         ss = ''
         for line in self._history:
            ss += '\n'+prefix+line
         ss += '\n'+prefix+'** Current oneliner(): '+str(self.oneliner())
         ss += '\n   |'
         if show:
            print ss
         if format:
            return ss

      # Always return the currently accumulated history (except when format=True)
      return self._history


   #=========================================================================
   # Some general helper functions
   #=========================================================================

   def len(self):
      """Return the number of nodes in the Clump (=1 if a tensor)
      """
      return len(self._nodes)

   #--------------------------------------------------------------------------

   def size(self):
      """Return the number of trees in the Clump (even if in a tensor)
      """
      return len(self._treequals)

   #--------------------------------------------------------------------------

   def __getitem__(self, index):
      """Get the specified (index) node.
      """
      return self._nodes[index]


   #=========================================================================
   # Convenience functions for use in Clump methods 
   #=========================================================================

   def start_of_body(self, func=None, *args, **kwargs):
      """To be called at the start of the 'body' of a Clump stage-method,
      i.e. AFTER any self._TCM menu and option definitions,
      and AFTER any 'if self._TCM.submenu_selected:' statement.
      Syntax: self._start_of_body(func, arg1, arg2, **kwargs)
      """
      func = self.start_of_body         # temporary
      name = func.func_name
      print '\n ** start_of_body(',name, args, kwargs,'):'
      return True

   #--------------------------------------------------------------------------

   def end_of_body(self, func, result=None, **kwargs):
      """To be called at the end of the body of a Clump stage-method,
      (but inside any 'if self._TCM.submenu_selected:' block).
      Syntax: self._end_of_body(func, [result,] **kwargs)
      """
      return True

   #--------------------------------------------------------------------------

   def start_of_object_submenu(self, trace=False):
      """Convenience function to be called from .init() etc.
      It generates the submenu that controls the object,
      in an organised way (this avoids errors when re-implementing
      .init() in derived classes.
      """
      self._object_submenu = self._TCM.start_of_submenu(self._name,
                                                 master=self._slavemaster,
                                                 qual=self._qual)
      return self._object_submenu

   #--------------------------------------------------------------------------

   def end_of_object_submenu(self, trace=False):
      """Counterpart of .start_of_object_submenu().
      """
      return self._TCM.end_of_submenu()

   #--------------------------------------------------------------------------

   def unique_nodestub (self, stagename=None, qual=None, help=None, trace=False):
      """Convenience function to generate a (unique) nodestub.
      The stub is then initialized (which helps the uniqueness determination!)
      and attached to the internal subtree of stub-nodes, which would otherwise
      be orphaned. They are used to carry quickref-help information, which
      can be used in the various bookmark pages.
      """
      self._stagecounter += 1
      self._stagename = str(stagename)
      stub = EN.unique_stub(self._ns, self._name, self._qual, qual)
      if False:
         ## parent.initrec().quickref_help = rider.format_html(path=rider.path())
         if self._stubtree:
            self._stubtree = stub << Meq.Identity(self._stubtree,
                                                  quickref_help=help)
         else:                                # The first one
            self._stubtree = stub << Meq.Constant(-0.123456789,
                                                  quickref_help=help)
      if trace:
         print '\n** .unique_nodestub(',qual,') ->',str(stub)
      return stub



   #=========================================================================
   # To and from tensor nodes:
   #=========================================================================

   def rootnode (self, name='rootnode', trace=False):
      """Return a single node with the specified name [=rootnode] which has all
      the internal nodes (self._nodes and self._orphans) as its children.
      The internal state of the object is not changed.
      """
      node = self.bundle('autoname')            # <----- !!
      self.show('inside rootnode()')
      if len(self._orphans)>0:
         nodes = [node]
         nodes.extend(self._orphans)
         print '+++++',nodes
         # use MeqComposer? or MeqReqSeq? or stepchildren?
         node = self._ns[name] << Meq.ReqSeq(children=nodes)
         print 'rootnode',str(node)
      self.history('.rootnode('+str(name)+')', trace=trace)
      return node

   #-------------------------------------------------------------------------

   def bundle (self, name=None, qual=None, combine='Composer', trace=False):
      """Return a single node that bundles the Clump nodes, using the
      specified combining node (default: combine='Composer').
      The internal state of the object is not changed.
      """
      if not isinstance(name,str):
         name = 'bundle_'+str(self._name)
      hist = '.bundle('+str(name)+','+str(qual)+','+str(combine)+'): '

      stub = EN.unique_stub(self._ns, name, self._qual, qual)
      if not self._composed:                              
         node = stub << getattr(Meq,combine)(*self._nodes)
      elif combine=='Composer':
         node = stub << Meq.Identity(self._nodes[0]) 
      else:
         pass        # decompose first....?

      self.history(hist, trace=trace)
      return node

   #-------------------------------------------------------------------------

   def compose (self, replace=True, trace=False):
      """Return a single tensor node, which has all the tree nodes as its children.
      If replace=True (default), make sure that the Clump object is in
      the 'composed' state, i.e. self._nodes contains a single tensor node.
      See also .decompose() and .bundle()
      """
      node = self._nodes[0]
      if not self._composed:               # Only if in 'decomposed' state
         stub = self.unique_nodestub('composed')(self._tensor_qual)
         node = stub << Meq.Composer(*self._nodes)
         if replace:
            self._nodes = [node]              # a list of a single node
            self._composed = True             # set the switch
            self._nodequals = [self._tensor_qual]
            self.history('.compose()', trace=trace)
      return node

   #-------------------------------------------------------------------------

   def decompose (self, replace=True, trace=False):
      """
      The reverse of .compose(). Return a list of separate tree nodes.
      If replace=True (default), make sure that the Clump object is in
      the 'decomposed' state, i.e. self._nodes contains separate tree nodes.
      """
      nodes = self._nodes[0]
      if self._composed:                   # ONLY if in 'composed' state
         tensor = self._nodes[0]
         nodes = []
         stub = self.unique_nodestub('decomposed')
         for index,qual in enumerate(self._nodequals):
            node = stub(qual) << Meq.Selector(tensor, index=index)
            nodes.append(node)
         if replace:
            self._nodes = nodes
            self._composed = False            # set the switch
            self._nodequals = self._treequals
            self.history('.decompose()', trace=trace)
      return nodes

   #-------------------------------------------------------------------------

   #-------------------------------------------------------------------------

   #-------------------------------------------------------------------------


   #=========================================================================
   # Unops and binops:
   #=========================================================================

   def apply_unops (self, unops, trace=False):
      """
      Apply one or more unary operation(s) (e.g. MeqCos) on its nodes.
      """
      if isinstance(unops,tuple):
         unops = list(unops)
      elif isinstance(unops,str):
         unops = [unops]

      # Apply in order of specification:
      for unop in unops:
         stub = self.unique_nodestub(unop)
         for i,qual in enumerate(self._nodequals):
            self._nodes[i] = stub(qual) << getattr(Meq,unop)(self._nodes[i])
         self.history('.apply_unops('+unop+')', trace=trace)

      return True

   #-------------------------------------------------------------------------

   def apply_binop (self, binop=None, rhs=None, trace=False):
      """Apply a binary operation (e.g. MeqAdd) between its nodes
      and the given right-hand-side (rhs). The latter may be various
      things: a Clump, a node, a number etc.
      """
      hist = '.binop('+str(binop)+') '
      if isinstance(rhs,(int,float,complex)):    # rhs is a number
         hist += str(rhs)+' '
         rhs = self._ns << Meq.Constant(rhs)     # convert to MeqConstant
         
      if is_node(rhs):                           # rhs is a node
         hist += 'node '+str(rhs.name)
         stub = self.unique_nodestub(binop)(rhs.name)
         for i,qual in enumerate(self._nodequals):
            self._nodes[i] = stub(qual) << getattr(Meq,binop)(self._nodes[i],rhs)

      elif isinstance(rhs,type(self)):           # rhs is a Clump object
         hist += rhs.oneliner()
         if self.commensurate(rhs, severe=True):
            stub = self.unique_nodestub(binop)(rhs._name)
            for i,qual in enumerate(self._nodequals):
               self._nodes[i] = stub(qual) << getattr(Meq,binop)(self._nodes[i],rhs._nodes[i])
         
      self.history(hist, trace=trace)
      return True


   #=========================================================================
   # Visualization:
   #=========================================================================

   def inspector (self, bookpage=None, folder=None, trace=False):
      """Make an inspector node for its nodes, and make a bookmark.
      """
      nodename = 'inspector'                       # <--------!!
      if self._composed:
         bundle = self._ns[nodename] << Meq.Identity(self._nodes[0])
      else:
         bundle = self._ns[nodename] << Meq.Composer(children=self._nodes)
      bundle.initrec().plot_label = self._treequals
      self._orphans.append(bundle)
      
      if not isinstance(bookpage,str):
         bookpage = self._name
      JEN_bookmarks.create(bundle,
                           name=bookpage, folder=folder,
                           viewer='Collections Plotter')
      self.history('.inspector('+str(bookpage)+','+str(folder)+')', trace=trace)
      return bundle




      
   #=========================================================================
   # Some test-function that define options (TCM):
   #=========================================================================

   def testopt1 (self, trace=False):
      """
      Test-function
      """
      submenu = self._TCM.start_of_submenu(self.testopt1,
                                           qual=self._qual)
      self._TCM.add_option('clone', range(3))
      self._TCM.add_option('aa', range(3))
      self._TCM.add_option('bb', range(3))

      if self._TCM.submenu_is_selected(trace=True):
         clone = self._TCM.getopt('clone', submenu)
         self._TCM.getopt('aa', submenu)
         self._TCM.getopt('bb', submenu)
         for i in range(clone):
            cp = Clump('clone', qual=i,
                       master=submenu,
                       ns=self._ns,
                       TCM=self._TCM)
            # cp.show('testopt1()', full=True)
         self.history('.testopt1()', trace=trace)

      # The LAST statement:
      self._TCM.end_of_submenu()
      return True

   #-------------------------------------------------------------------------
      
   def testopt2 (self, trace=False):
      """
      Test-function
      """
      submenu = self._TCM.start_of_submenu(self.testopt2,
                                           qual=self._qual)
      self._TCM.add_option('aa', range(3))
      self._TCM.add_option('bb', range(3))

      if self._TCM.submenu_is_selected(trace=True):
         self._TCM.getopt('aa', submenu)
         self._TCM.getopt('bb', submenu)
         self.history('.testopt2()', trace=trace)

      # The LAST statement:
      self._TCM.end_of_submenu()
      return True




#********************************************************************************
#********************************************************************************
# Standalone forest (i.e. not part of QuickRef.py) of this QR_module.
# Just load it into the browser, and compile/execute it.
#********************************************************************************
#********************************************************************************


def _define_forest (ns, **kwargs):
   """The expected function just calls do_define_forest().
   The latter is used outside _define_forest() also (see below)
   """
   if not enable_testing:
      print '\n**************************************************************'
      print '** TDLOptionManager _define_forest(): testing not enabled yet!!'
      print '**************************************************************\n'
      return False

   # Execute the function that does the actual work. It is the same
   # function that was called outside _define_forest(), where the
   # TDLOptions/Menus were configured (in TCM) and generated.
   # This second run uses the existing option values, which are
   # transferred by means of diskfiles (.TCM and .TRM)
   # It also re-defines the options/menus in a dummy TDLOptionManager,
   # but these are NOT converted into TDLOption/Menu objects. 

   do_define_forest (ns, TCM=TOM.TDLOptionManager(TCM))       

   # Generate at least one node:
   node = ns.dummy << 1.0

   return True


#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the node 'rootnode'
    """
    # domain = meq.domain(1.0e8,1.1e8,1,10)                            # (f1,f2,t1,t2)
    domain = meq.domain(1,10,-10,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=11, num_time=21)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='rootnode', request=request))
    return result
       
#------------------------------------------------------------------------------


def do_define_forest (ns, TCM):
   """The function that does the actual work for _define_forest()
   It is used twice, outside and inside _define_forest() 
   """

   submenu = TCM.start_of_submenu(do_define_forest)
   TCM.add_option('testopt',[1,2,3])
   TCM.add_option('clump',[1,2,3])
   TCM.add_option('derived',[1,2,3])

   if TCM.submenu_is_selected():
      testopt = TCM.getopt('testopt', submenu)
      cp = Clump(ns=ns, TCM=TCM)

      if testopt==1:
         cp.testopt1()
      elif testopt==2:
         cp.testopt2()
      elif testopt==3:
         cp.testopt1()
         cp.testopt2()
      cp.inspector()
      cp.rootnode()
      cp.show('do_define_forest()', full=True)

   # The LAST statement:
   TCM.end_of_submenu()
   return True

#------------------------------------------------------------------------------

# This bit is executed whenever the module is imported (blue button etc)

itsTDLCompileMenu = None
TCM = TOM.TDLOptionManager(__file__)
enable_testing = False


enable_testing = True        # normally, this statement will be commented out
if enable_testing:
   ns = NodeScope()
   cp = do_define_forest (ns, TCM=TCM)
   itsTDLCompileMenu = TCM.TDLMenu(trace=False)

   



#********************************************************************************
#********************************************************************************
# Standalone test (without the browser):
#********************************************************************************
#********************************************************************************

if __name__ == '__main__':

   print '\n****************************************************'
   print '** Start of standalone test of: Clump.py:'
   print '****************************************************\n' 

   ns = NodeScope()
   # rider = QRU.create_rider()             # CollatedHelpRecord object

   if 1:
      cp = Clump(master='xxx')
      cp.show('creation', full=True)

   if 0:
      for node in cp:
         print str(node)
   if 0:
      for index in [0,1,-1,5]:
         print '-- cp[',index,'] -> ',str(cp[index])
   if 0:
      cp.show_tree(-1, full=True)

   if 0:
      cp.compose()
      cp.show('.compose()')
      if 0:
         cp.decompose()
         cp.show('.decompose()')

   if 0:
      unops = 'Cos'
      unops = ['Cos','Sin']
      cp.apply_unops(unops)

   if 0:
      rhs = math.pi
      # rhs = ns.rhs << Meq.Constant(2.3)
      # rhs = Clump('RHS', use=cp)
      cp.apply_binop('Add', rhs=rhs)

   if 0:
      unops = None
      unops = 'Identity'
      cp2 = cp.link(unops=unops)
      cp2.show('.link('+str(unops)+')', full=True)

   if 0:
      treequals = range(5)
      treequals = ['a','b','c']
      cp3 = Clump(treequals=treequals)
      cp.commensurate(cp3, severe=False, trace=True)
      cp3.show('.commensurate()')

   if 0:
      node = cp.inspector()
      cp.show('.inspector()')
      print '->',str(node)

   if 0:
      node = cp.rootnode() 
      cp.show('.rootnode()')
      print '->',str(node)

   if 1:
      cp.show('final', full=True)

   #-------------------------------------------------------------------

   if 0:
      cp.start_of_body('func', 1,5,8, a=6, b=7)
   
      
   print '\n** End of standalone test of: Clump.py:\n' 

#=====================================================================================





