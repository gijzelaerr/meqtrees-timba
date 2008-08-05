"""
QuickRef module: QuickRefNodeHelp.py:
"""

# file: ../JEN/QuickRef/QuickRefNodeHelp.py:
#
# Author: J.E.Noordam
#
# Short description:
#   Attaches specific help (string) to the quickref_help field
#   of the state-record of the given node (or subtree)
#
# History:
#   - 257 jul 2008: creation (from QuickRef.py)
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

# NB: Do NOT use this one in here (circular)
## from Timba.Contrib.JEN.QuickRef import EasyNode as EN

# from Timba.Contrib.JEN.QuickRef import QuickRefUtil as QRU
# from Timba.Contrib.JEN.QuickRef import EasyTwig as ET
from Timba.Contrib.JEN.QuickRef import EasyFormat as EF


# import math
# import random
# import numpy


#******************************************************************************** 

def node_help (node, detail=1, rider=None, mode='html', comment=None, trace=False):
   """
   Attach specific help to the quickref_help field of the given node.
   If a rider (CollatedHelpRecord) is specified, attach it too.
   """

   if not is_node(node):
      ss = '\n** QRNH.node_help('+str(type(node))+'): not a node **\n'
      return ss

   # ss = '<dl><dt><font color="blue">'
   ss = '<dl><dt>'
   ss += 'MeqNode: '
   # ss += '<font color="blue">'
   ss += format_nodestring(node)+':'
   # ss += '</font>'
   ss += '<dd>'

   #..........................................
   # Get the generic description of the node, according to its class: 

   rr = node.initrec()
   ss = class_help (node.classname,
                    header=ss, rr=rr,
                    detail=detail,
                    # rider=rider,
                    # comment=comment,
                    mode=mode, trace=False)

   #..........................................
   if False:
      # print dir(node)
      print node.name         # '(constant)'
      print node.basename     # '(constant)'
      print node.quals        # tuple ()
      print node.kwquals      # dict {}
      print node.classname    # 'MeqConstant'
      print node.children     # list []
      print node.num_children() # int 0
      print node.num_parents()  # int 0
      print node.parents      # <WeakValueDictionary at -1258575060>
      print node.family()     # [<Timba.TDL.TDLimpl._NodeStub object at 0xb4e06aec>]
      print str(node.family()[0])  # '(constant)(MeqConstant)'
      print node.initrec()    # { class: MeqConstant, value: 4.5, tags: ['test'] }

   # Add a line of general node info:
   line = ''
   if not line=='':
      ss += line+'<br>'

   #..........................................
   # Show the children:
   nc = node.num_children()
   if nc==0:
      pass
   elif nc==1:
      ss += '- child '+str(0)+': '+format_child(node.children[0][1])+'<br>'
   elif nc<5:
      for i in range(nc):
         ss += '- child '+str(i)+': '+format_child(node.children[i][1])+'<br>'
   else:
      for i in [0,1]:                    # the first two
         ss += '- child '+str(i)+': '+format_child(node.children[i][1])+'<br>'
      ss += '...'+'<br>'
      for i in [nc-1]:                   # the last one
      # for i in [nc-2,nc-1]:              # the last two
         ss += '- child '+str(i)+': '+format_child(node.children[i][1])+'<br>'

   #..........................................
   # Expand the node-specific initrec fields:
   for key in rr.keys():
      v = rr[key]
      if key in ['class','children','quickref_help',
                 'qhelp','qviewer','qbookmark']:
         pass
      elif isinstance(v,(list,tuple)):
         if isinstance(v[0],(int,float,complex)):
            ss += ' - '+str(key)+' = '+str(v)+'<br>'
            # ss += ' - '+str(key)+' = '+str(EF.format_value(v))+'<br>'
         elif isinstance(v[0],str):
            ss += ' - '+str(key)+' = '+str(v)+'<br>'
         elif len(v)<=5:
            ss += ' - '+str(key)+' = '+str(v)+'<br>'
         else:
            ss += ' - '+str(key)+' (n='+str(len(v))+'): '+str(v[:2])+'...'+str(v[-1])+'<br>'
      elif isinstance(v,dict):
         ss += ' - '+str(key)+' (dict/record):<br>'
         for key1 in v.keys():
            v1 = v[key1]
            # ss += ' --- '+str(key1)+': '+str(EF.format_value(v1))+'<br>'
            ss += ' --- '+str(key1)+' = '+str(v1)+'<br>'
      elif isinstance(v,(int,float,complex)):
         ss += ' - '+str(key)+' = '+str(v)+'<br>'
         # ss += ' - '+str(key)+' = '+str(EF.format_value(v))+'<br>'
      elif isinstance(v,str):
         ss += ' - '+str(key)+': '+str(v)+'<br>'
         # ss += ' - '+str(key)+' = '+str(EF.format_value(v))+'<br>'
      else:
         ss += ' - '+str(key)+'(??): '+str(v)+'<br>'

   #..........................................
   # Add a specific comment (if specified):
   if isinstance(comment,str):
      ss += '<i>This node:  '+str(comment)+'</i>'

   #..........................................
   # Closing:
   ss += '</dl><br>\n'

   #..........................................
   # Attach to quickref_help field of the node state record:
   if is_node(node):
      rr = node.initrec()
      key = 'quickref_help'
      if rr.has_key(key):
         rr.quickref_help += ss
      else:
         rr.quickref_help = ss
      # NB: Do not use EasyNode from here (circular)
      # EN.quickref_help (node, append=ss, trace=trace)

   if rider:
      rider.insert_help(rider.path(temp='node'), help=ss, append=True, trace=trace)

   if trace:
      print '\n** QRNH.node_help(',str(node),'):\n  ',ss,'\n'
      
   return ss
      

#===================================================================================

def format_nodestring (node, trace=False):
   """Helper function"""
   ss = str(node)
   if True:
      # Make the classname more distinct:
      nn = ss.split('(')
      ss = '<font color="blue">'+nn[0]+'</font>'
      ss += '<font size=1> ('+nn[1]+'</font>'
   return ss

#-------------------------------------------------------------------------------

def format_child (node, trace=False):
   """Helper function"""
   rr = node.initrec()
   ss = format_nodestring(node)

   # Append some specific initrec fields, if present: 
   ss += '<font size=1>'
   if node.classname=='MeqConstant':
      ss += '  (value='+str(getattr(rr,'value',None))+')'
   if rr.has_key('tags'):
      ss += '  (tags='+str(rr.tags)+')'
   ss += '</font>'
   return ss

#===================================================================================

def class_help (cname, header=None, rr=None,
                detail=1, rider=None, comment=None,
                mode='html', trace=False):
   """
   Attach specific help to the quickref_help field of the given
   node-class name (cname).
   If a rider (CollatedHelpRecord) is specified, attach it too.
   """

   if header==None:
      ss = '<dl><dt><font color="blue">'
      ss += 'MeqNode of class: '+str(cname)
      ss += '</font><dd>'
      rr = record()
   else:
      # Assume that this is called by node_help()
      ss = header

   more = 'specific: '
   more = ''
   if cname=='MeqConstant':
      more += 'May be scalar or tensor (multiple results), real or complex. ' 
      more += 'All the cells of a result domain have the same value.'

   elif cname in ['MeqFreq','MeqTime','MeqGrid']:
      more += 'Assign the value of the specified axis to each domain cell. '

   elif cname in ['MeqNorm','MeqArg','MeqReal','MeqImag','MeqConj']:
      more += 'Operation on complex child. '

   elif cname in ['MeqCeil','MeqFloor']:
      more += 'Rounding function.'

   elif cname=='MeqIdentity':
      more += 'Make a copy node with a different name.'

   elif cname=='MeqStripper':
      more += """Remove all derivatives (if any) from the result.
      This saves space and can be used to control solving."""

   elif cname=='MeqMod':
      more += 'Modulo lhs%rhs (lhs and rhs are its 2 children). '
      more += '<warning>MeqMod() crashes the meqserver.... Needs integer children?? </warning>'


   elif cname=='MeqWSum':
      more += 'Weighted sum of its children: w[0]*c0 + w[1]*c1 + w[2]*c2 + ... '
      more += '<warning>The weights vector must be a vector of DOUBLES (!)</warning>'

   elif cname=='MeqWMean':
      more += """Weighted mean of its children: (w[0]*c0 + w[1]*c1 + w[2]*c2 + ...)/wtot,
      in which wtot = (w[0]+w[1]+w[2]+...)"""

   elif cname in ['MeqAdd','MeqMultiply']:
      more += 'Multi-math function (has one or more children). '

   elif cname in ['MeqSubtract','MeqDivide','MeqPow']:
      more += 'Binary math function (has 2 children, lhs and rhs). '

   elif cname in ['MeqToComplex','MeqPolar']:
      more += 'Converts its two (real) children into a complex result. '
      if cname=='MeqToComplex':
         more += 'The children are real and imaginary, in that order.'
      elif cname=='MeqPolar':
         more += 'The children are ampl and phase (rad), in that order.'


   #---------------------------------------------------------------------------

   elif cname in ['MeqCos','MeqSin','MeqTan']:
      more += '(tri-)goniometric function. Turns an angle (rad) into a fraction.'

   elif cname in ['MeqAcos','MeqAsin','MeqAtan']:
      more += 'Inverse (tri-)goniometric function. Turns a fraction into an angle (rad). '
      if cname in ['MeqAcos','MeqAsin']:
         more += 'The abs input should be smaller than one, of course.'

   elif cname in ['MeqCosh','MeqSinh','MeqTanh']:
      more += 'Hyperbolic function: '
      if cname=='MeqCosh':
         more += 'Cosh(x) = (exp(x)+exp(-x))/2'
      elif cname=='MeqSinh':
         more += 'Sinh(x) = (exp(x)-exp(-x))/2'
      elif cname=='MeqTanh':
         more += 'Tanh(x) = Sinh(x)/Cosh(x) = (exp(x)-exp(-x))/(exp(x)+exp(-x))'

   elif cname in ['MeqPow2','MeqPow3','MeqPow4','MeqPow5',
                  'MeqPow6','MeqPow7','MeqPow8','MeqSqr']:
      more += 'Takes some power of its input.' 

   elif cname in ['MeqAbs','MeqNegate','MeqInvert','MeqExp','MeqSqrt']:
      help = record(Negate='-c', Invert='1/c', Exp='exp(c)', Sqrt='square root',
                    Log='e-log (for 10-log, divide by Log(10))')

   elif cname=='MeqLog':
      more += 'e-log (for 10-log, divide by Log(10))'
      

   elif cname in ['MeqNelements','MeqSum','MeqMean','MeqProduct',
                  'MeqStdDev','MeqRms', 'MeqMin','MeqMax']:
      more += """Operation over all the cells of the domainof its child result.
      Returns a single number, or rather the same number in all cells."""

   #---------------------------------------------------------------------------

   elif cname in ['MeqTranspose','MeqMatrixMultiply','MeqConjTranspose']:
      more += 'matrix operation (on a 2D tensor node). '

   elif cname=='MeqMatrix22':
      more += 'Make a 2x2 matrix from its 4 children. '
      more += '<remark>Meq.Matrix(children=elements) does give an error (!?)</remark>.'
      
   elif cname=='MeqMatrixInvert22':
      more += 'Invert a 2x2 matrix. '

   elif cname=='MeqGaussNoise':
      more += 'Gaussian noise with given stddev (and zero mean). '
      more += '<remark>mean does not work...</remark>.'

   elif cname=='MeqRandomNoise':
      more += 'Random noise between given lower and upper bounds. '
      more += '<warning>The meqserver crashes on this node!</warning>'

   #---------------------------------------------------------------------------


   elif cname=='MeqReqSeq':
      more += """Passes its request to its children one by one. It returns the result
      of the child specified by result_index (default=0)."""
      
   elif cname=='MeqReqMux':
      more += """Like MeqReqSeq...."""
      
   elif cname=='MeqComposer':
      more += """Combine the results of its (scalar) children into a tensor node,
      i.e. a node with multiple results. An optional dims argument may be supplied
      to specify a shape."""
      
   elif cname=='MeqSelector':
      more += """Makes a scalar node (one result) by extracting the specified (index)
      element from its tensor child."""
      
   elif cname=='MeqPaster':
      more += """Past the result of its (scalar) child at the specified (index)
      position of its tensor child.<warning>Does not work</warning>"""
      
      
   #---------------------------------------------------------------------------

   elif cname in ['MeqCompounder']:
      pass
   
   elif cname=='MeqModRes':
      more += """Modifies the resolution (nr of domain cells) of the
      <font color='red'><i>REQUEST</i></font> that is passed on to its child(ren). 
      It does this according to the specified num_cells, which is a list of integers,
      one for each dimensions of the domain. In general, it will be 2D [ntime,nfreq].
      """

   elif cname=='MeqResampler':
      more += 'Resamples the domain of the result according to that of the request.'

   #---------------------------------------------------------------------------

   elif cname=='MeqSolver':
      more += """Non-linear (Levenberg Marquardt) solver node. Uses AIPS++ fitting routines.
      Its children are MeqCondeq nodes that provide condition equations for the (polc coeff)
      of those MeqParm(s) in the MeqCondeq subtrees that have been set to 'solvable'.
      After solution (by SVD matrix inversion), incremental improvements are passed back up
      the tree to the relevant MeqParms.
      """ 
      
   elif cname=='MeqCondeq':
      more += """Uses the difference of its 2 children to generate condition equations
      (one equation per domain cell) for the solver.
      After solving, the condeq result (=residual) should be 'zero' (or rather noise-like).
      """

   elif cname=='MeqParm':
      more += 'This node represents a (M.E.) parameter, which may be solved for. ' 
      
   #---------------------------------------------------------------------------

   elif cname=='MeqZeroFlagger':
      more += """Flags the cells of the result of its child if they are GT,GE,LE,LT zero.
      The child will usually be the rootnode of a subtree."""

   elif cname=='MeqMergeFlags':
      more += """Merges the flags of its children, and returns the result of the
      first child (with the merged flags of course)."""

   #---------------------------------------------------------------------------

   elif cname in ['MeqSpigot','MeqFitsSpigot']:
      pass
   elif cname in ['MeqSink','MeqVisDataMux']:
      pass
   elif cname in ['MeqFITSReader','MeqFITSImage','MeqFITSSpigot','','','']:
      pass

   #---------------------------------------------------------------------------

   elif cname in ['MeqUVBrick','MeqUVInterpol']:
      pass
   elif cname in ['MeqVisPhaseShift']:
      pass

   #---------------------------------------------------------------------------

   elif cname in ['MeqCoordTransform','MeqAzEl','MeqLST','MeqLMN','MeqLMRaDec']:
      pass
   elif cname in ['MeqObjectRADec','MeqParAngle','MeqRaDec','MeqUVW']:
      pass


   #---------------------------------------------------------------------------
   #---------------------------------------------------------------------------

   elif cname=='MeqPyNode':
      more += """User-defined node, written in python. Using standard interface
      routines, the user may interact with state record and child results, and
      produce a result."""

   #---------------------------------------------------------------------------
   #---------------------------------------------------------------------------

   else:
      ss += '<font color="red" size=10>'
      ss += '** class_name not recognized: '+str(cname)+' **'
      ss += '</font>\n'
      trace = True

   #---------------------------------------------------------------------------
   #---------------------------------------------------------------------------

   # Finishing touches:
   if not more=='':
      ss += more+'<br>'

   if isinstance(comment,str):
      ss += '<i>Comment: '+str(comment)+'</i>'

   if header==None:
      ss += '</dl><br>\n'

   if rider:
      rider.insert_help(rider.path(temp='node'), help=ss, append=True, trace=trace)

   if trace:
      print '\n** QRNH.class_help(',cname,'):\n  ',ss,'\n'
      
   return ss
      



#==============================================================================
#==============================================================================

def tree_help (node, detail=1, level=0, recurse=True,
               rider=None, mode='html',
               trace=False):
   """
   Attach specific help to the quickref_help field of the nodes of
   the given subtree (to the specified recursion level).
   """
   prefix = level*'..|..'
   if level==0:
      if isinstance(recurse,bool):
         if not recurse: recurse=0
         if recurse: recurse=1000
      if trace:
         print '\n** QRNH.tree_help('+str(node)+'):'

   ss = node_help(node)
   if trace:
      print prefix,ss.split('<<')[1].split('\n')[0]
   
   if level<=recurse and getattr(node,'children', None):
      for child in node.children:
         tree_help(child[1], detail=detail, level=level+1,
                          rider=rider, recurse=recurse,
                          trace=trace)
   if level==0:
      if trace:
         print '**\n'
   return True
    




















#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

   print '\n** Start of standalone test of: QuickRefNodeHelp.py:\n' 

   ns = NodeScope()

   rider = None
   if 0:
      rider = QRU.create_rider()             # CollatedHelpRecord object

   if 0:
      node = ns << 1.3
      node_help(node, rider=rider, trace=True)

   if 1:
      a = ns << Meq.Constant(range(3))
      b = ns << 78
      node = ns << Meq.Add(a,b)
      class_help(node.classname, rider=rider, trace=True)
      node_help(node, rider=rider, trace=True)
      tree_help(node, rider=rider, trace=True)
            
   print '\n** End of standalone test of: QuickRefNodeHelp.py:\n' 

#=====================================================================================





