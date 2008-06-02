# file: ../JEN/demo/QR_MeqNodes.py:
#
# Author: J.E.Noordam
#
# Short description:
#   Functions that make subtrees that demonstrate MeqNodes
#   Called from QuickRef.py
#
# History:
#   - 25 may 2008: creation (from QuickRef.py)
#   - 30 may 2008: local testing tree/routine
#
# Description:
#
# Remarks:
#
# Problem nodes:
#
#   MeqNElements()           multiple children give error
#   (Reduction nodes do not work on multiple children...?)
#   MeqMod()                 crashes the browser/server
#   MeqRandomNoise()         crashes the browser/server
#
#   MeqPaster()              does not paste
#   MeqSelector()            index=[1,2] not supported          
#
# Workaround exists:
#
#   MeqMatrix22()            use of children=[...] gives error
#   MeqConjugateTranspose()  use of children=[...] gives error
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

import QuickRef as QR

# import math
# import random



#********************************************************************************
# Top function, called from QuickRef.py:
#********************************************************************************

def MeqNodes (ns, path, rider=None):
   """
   Available standard nodes: ns[name] << Meq.XYZ(*children,**kwargs).
   """
   bundle_help = MeqNodes.__doc__
   path = QR.add2path(path,'MeqNodes')
   cc = []
   cc.append(unops (ns, path, rider=rider))
   cc.append(binops (ns, path, rider=rider))
   cc.append(leaves (ns, path, rider=rider))
   cc.append(tensor (ns, path, rider=rider))
   cc.append(reduction (ns, path, rider=rider))
   cc.append(regridding (ns, path, rider=rider))
   cc.append(flagging (ns, path, rider=rider))
   cc.append(solving (ns, path, rider=rider))
   # cc.append(visualization (ns, path, rider=rider))
   # cc.append(transforms (ns, path, rider=rider))
   # cc.append(flowcontrol (ns, path, rider=rider))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)



#********************************************************************************
# 2nd tier: Functions called from the top function above:
#********************************************************************************

def unops (ns, path, rider=None):
   """
   Unary math operations on one child, which may be a "tensor node" (multiple
   vellsets in its Result). An illegal operation (e.g. sqrt(-1)) produces a NaN
   (Not A Number) for that cell, which is then carried all the way downstream
   (i.e. from child to parent, towards the root of the tree). It does NOT produce
   a FAIL. See also ....
   """
   bundle_help = unops.__doc__
   path = QR.add2path(path,'unops')
   cc = [] 
   cc.append(unops_elementary (ns, path, rider=rider))
   cc.append(unops_goniometric (ns, path, rider=rider))
   cc.append(unops_hyperbolic (ns, path, rider=rider))
   cc.append(unops_power (ns, path, rider=rider))
   cc.append(unops_misc (ns, path, rider=rider))
   cc.append(unops_complex (ns, path, rider=rider))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)

#--------------------------------------------------------------------------------

def binops (ns, path, rider=None):
   """
   Binary nodes perform math operations on two or more children....
   """
   bundle_help = binops.__doc__
   path = QR.add2path(path,'binops')
   cc = []
   cc.append(binops_two_children (ns, path, rider=rider))
   cc.append(binops_one_or_more (ns, path, rider=rider))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)

#--------------------------------------------------------------------------------

def leaves (ns, path, rider=None):
   """
   Leaf nodes have no children. They often (but not always) have access to
   some external source of information (like a file) to satisfy a request. 
   """
   bundle_help = leaves.__doc__
   path = QR.add2path(path,'leaves')
   cc = []
   cc.append(leaves_constant (ns, path, rider=rider))
   cc.append(leaves_parm (ns, path, rider=rider))
   cc.append(leaves_grids (ns, path, rider=rider))
   cc.append(leaves_noise (ns, path, rider=rider))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)


#--------------------------------------------------------------------------------

def tensor (ns, path, rider=None):
   """
   Many node classes can handle Results with multiple vellsets.
   They are somewhat clumsily (and wrongly) called 'tensor nodes'.
   The advantages of multiple vellsets are:
   - the trees are more compact, so easier to define and read
   - efficiency: execution can be optimized internally
   - they allow special nodes that do matrix/tensor operations
   - etc, etc
   """
   bundle_help = tensor.__doc__
   path = QR.add2path(path,'tensor')
   cc = []
   cc.append(tensor_manipulation (ns, path, rider=rider))
   cc.append(tensor_matrix (ns, path, rider=rider))
   cc.append(tensor_matrix22 (ns, path, rider=rider))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)


#--------------------------------------------------------------------------------

def reduction (ns, path, rider=None):
   """
   Reduction nodes reduce the values of all domain cells to a smaller
   number of values (e.g. their mean). They operate on all the vellsets
   in the Result(s) of their child(ren?).
   NB: It is not clear (to me, in this stage) what happens if some cells
   are flagged....!?
   If one or more reduction_axes are specified, the reduction is only
   along the specified axes (e.g. reduction_axes=['time'] reduces only
   the time-axis to length 1. The default is all available axes, of course. 
   The Result of a reduction node will be expanded when needed to fit a
   domain of the original size, in which multiple cells have the same value.
   """
   bundle_help = reduction.__doc__
   path = QR.add2path(path,'reduction')
   cc = []
   cc.append(reduction_single (ns, path, rider=rider))
   cc.append(reduction_multiple (ns, path, rider=rider))
   cc.append(reduction_axes (ns, path, rider=rider))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)


#--------------------------------------------------------------------------------

def regridding (ns, path, rider=None):
   """
   MeqModRes
   MeqResampler
   MeqCompounder
   """
   bundle_help = regridding.__doc__
   path = QR.add2path(path,'regridding')
   cc = []
   cc.append(regridding_modres (ns, path, rider=rider))
   # cc.append(regridding_compounder (ns, path, rider=rider))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)

#--------------------------------------------------------------------------------

def flowcontrol (ns, path, rider=None):
   """
   MeqReqSeq
   MeqReqMux
   MeqSink
   MeqVisDataMux
   """
   bundle_help = flowcontrol.__doc__
   path = QR.add2path(path,'flowcontrol')
   cc = []
   # cc.append(flowcontrol_reqseq (ns, path, rider=rider))
   # cc.append(flowcontrol_reqmux (ns, path, rider=rider))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)

#--------------------------------------------------------------------------------

def flagging (ns, path, rider=None):
   """
   MeqZeroFlagger
   MeqMergeFlags
   """
   bundle_help = flagging.__doc__
   path = QR.add2path(path,'flagging')
   cc = []
   cc.append(flagging_simple (ns, path, rider=rider))
   # cc.append(flagging_merge (ns, path, rider=rider))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)


#--------------------------------------------------------------------------------

def solving (ns, path, rider=None):
   """
   MeqSolver
   MeqCondeq
   MeqStripper (?)
   """
   bundle_help = solving.__doc__
   path = QR.add2path(path,'solving')
   cc = []
   cc.append(solving_ab (ns, path, rider=rider))
   # cc.append(solving_single (ns, path, rider=rider))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)

#--------------------------------------------------------------------------------

def visualization (ns, path, rider=None):
   """
   MeqComposer (inpector)
   MeqParmFiddler
   MeqDataCollect (?)
   MeqDataConcat (?)
   MeqHistoryCollect (?)
   point to pyNodes...
   """
   bundle_help = visualization.__doc__
   path = QR.add2path(path,'visualization')
   cc = []
   # cc.append(visualization_simple (ns, path, rider=rider))
   # cc.append(visualization_merge (ns, path, rider=rider))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)

#--------------------------------------------------------------------------------

def transforms (ns, path, rider=None):
   """
   MeqUVBrick
   MeqUVInterpol
   MeqVisPhaseShift
   MeqCoordTransform
   MeqAzEl
   MeqLST
   MeqLMN
   MeqLMRaDec
   MeqObjectRADec (A?)
   MeqParAngle
   MeqRaDec
   MeqUVW
   
   """
   bundle_help = transforms.__doc__
   path = QR.add2path(path,'transforms')
   cc = []
   # cc.append(transforms_coord (ns, path, rider=rider))
   # cc.append(transforms_FFT (ns, path, rider=rider))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)





#********************************************************************************
#********************************************************************************
#********************************************************************************
#********************************************************************************
# 3rd tier: Functions called from functions at the 2nd tier above
#********************************************************************************
#********************************************************************************



#================================================================================
# visualization_... 
#================================================================================

#================================================================================
# transforms_... 
#================================================================================

#================================================================================
# flowcontrol_... 
#================================================================================

#================================================================================
# solving_... 
#================================================================================

def solving_ab (ns, path, rider=None):
   """
   Demonstration of solving for two unknown parameters (a,b),
   using two linear equations (one condeq child each):
   - condeq 0:  a + b = p (=10)
   - condeq 1:  a - b = q (=2)
   The result should be: a = (p+q)/2 (=6), and b = (p-q)/2 (=4)
   Condeq Results are the solution residuals, which should be small.
   """
   bundle_help = solving_ab.__doc__
   path = QR.add2path(path,'ab')

   a = QR.uniquestub(ns, 'a') << Meq.Parm(0)
   b = QR.uniquestub(ns, 'b') << Meq.Parm(0)
   p = QR.uniquestub(ns, 'p') << Meq.Constant(10)
   q = QR.uniquestub(ns, 'q') << Meq.Constant(2)
   sum_ab = ns << Meq.Add(a,b) 
   diff_ab = ns << Meq.Subtract(a,b)
   condeqs = []
   condeqs.append(QR.MeqNode (ns, path, meqclass='Condeq',name='Condeq(a+b,p)',
                              help='Represents equation: a + b = p (=10)',
                              rider=rider, children=[sum_ab, p]))
   condeqs.append(QR.MeqNode (ns, path, meqclass='Condeq',name='Condeq(a-b,q)',
                              help='Represents equation: a - b = q (=2)',
                              rider=rider, children=[diff_ab, q]))
   solver = QR.MeqNode (ns, path, meqclass='Solver',
                        name='Solver(*condeqs, solvable=[a,b])',
                        help='Solver', rider=rider, children=condeqs,
                        solvable=[a,b])  
   residuals = QR.MeqNode (ns, path, meqclass='Add', name='residuals',
                           help='The sum of the (abs) condeq residuals',
                           rider=rider, children=condeqs, unop='Abs')
   cc = [solver,residuals,a,b,p,q]
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider,
                     parentclass='ReqSeq', result_index=0)

#--------------------------------------------------------------------------------


def solving_ft (ns, path, rider=None):
   """
   Demonstration of solving for two unknown parameters (a,b),
   using two linear equations (one condeq child each):
   - condeq 0:  a + b = p (=10)
   - condeq 1:  a - b = q (=2)
   The result should be: a = (p+q)/2 (=6), and b = (p-q)/2 (=4)
   Condeq Results are the solution residuals, which should be small.
   """
   bundle_help = solving_ab.__doc__
   path = QR.add2path(path,'ab')

   a = QR.uniquestub(ns, 'a') << Meq.Parm(0)
   b = QR.uniquestub(ns, 'b') << Meq.Parm(0)
   sum_ab = ns << Meq.Add(a,b) 
   diff_ab = ns << Meq.Subtract(a,b)
   condeqs = []
   condeqs.append(ns << Meq.Condeq(sum_ab, 10))
   condeqs.append(ns << Meq.Condeq(diff_ab, 2))
   solver = QR.MeqNode (ns, path, meqclass='Solver',
                        name='Solver(*condeqs, solvable=[a,b])',
                        help='Solver', rider=rider, children=condeqs,
                        solvable=[a,b])  
   cc = [solver,condeqs[0],condeqs[1],a,b]
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider,
                     reqseq=0)


#--------------------------------------------------------------------------------


#================================================================================
# flagging_... 
#================================================================================

  
def flagging_simple (ns, path, rider=None):
   """
   Demonstration of simple flagging. A zero-criterion (zcrit) is calculated
   by a little subtree. This calculates the abs(diff) from the mean of the
   input, and then subtracts 5 times its stddev.
   The ZeroFlagger(oper=GE) flags all domain cells whose zcrit value is >= 0.
   Other behaviour can be specified with oper=LE or GT or LT.
   The MergeFlags node merges the new flags with the original flags of the input.
   """
   bundle_help = flagging_simple.__doc__
   path = QR.add2path(path,'simple')
   input = QR.uniquestub(ns,'input') << Meq.Exp(ns.noise3)
   mean =  ns << Meq.Mean(input)
   stddev =  ns << Meq.Stddev(input)
   diff = ns << Meq.Subtract(input,mean)
   absdiff = ns << Meq.Abs(diff)
   zcrit = QR.uniquestub(ns,'zcrit') << Meq.Subtract(absdiff,5*stddev)
   zflag = QR.MeqNode (ns, path, meqclass='ZeroFlagger',
                       name='ZeroFlagger(zcrit, oper=GE)',
                       help='oper=GE: Flag all cells for which zcrit>=0.0.',
                       rider=rider, children=[zcrit], oper='GE')
   mflag = QR.MeqNode (ns, path, meqclass='MergeFlags',
                       name='MergeFlags(input,zflag)',
                       help='Merge new flags with existing flags',
                       rider=rider, children=[input, zflag])
   cc = [input, mean, stddev, zcrit, zflag, mflag]
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)


#--------------------------------------------------------------------------------

#================================================================================
# regridding_... 
#================================================================================


def regridding_modres (ns, path, rider=None):
   """
   Demonstration of changing the number of cells in the domain.
   ...
   - The MeqModRes(child, num_cells=[2,3]) node changes the number
   of cells in the domain of the REQUEST that it issues to its child.
   Thus, the entire subtree below the child is evaluated with this
   resolution. 
   - The MeqResample(child, mode=1) resamples the domain of the Result
   it gets from its child, to match the resolution of the Request that
   it received itself. (So it does nothing if the domains already match,
   i.e. if there is no MeqModRes upstream).
   - The MeqResample(child, mode=2) resamples in a different way
   .....
   The various examples show the difference between the input, and after
   a sequence of ModRes and Resample. Obviously, the differences are
   smaller when the input is smoother and/or when num_cells is larger.
   ...
   This feature has been developed (by Sarod) for 'peeling': If the
   phase-centre is shifted to the position of the peeling source, its
   visibility function will be smooth over the domain, so it is not
   necessary to predict it at the full time/freq resolution of the data.
   Since the number of cells may be 100 less, this can save a lot of
   processing.
   There may also be other applications of these nodes....
   """
   bundle_help = regridding_modres.__doc__
   path = QR.add2path(path,'modres')
   cc = []
   cc.append(regridding_modres_noise (ns, path, rider=rider))
   cc.append(regridding_modres_linear (ns, path, rider=rider))
   cc.append(regridding_modres_curved (ns, path, rider=rider))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)

#--------------------------------------------------------------------------------

def regridding_modres_noise (ns, path, rider=None):
   """
   The input is gaussian noise. The ModRes and Resampling have a smoothing effect.
   """
   bundle_help = regridding_modres_noise.__doc__
   path = QR.add2path(path,'noise')
   return regridding_modres_generic (ns, path, rider, bundle_help,
                                     input=ns.noise2, num_cells=[4,5])

#--------------------------------------------------------------------------------

def regridding_modres_linear (ns, path, rider=None):
   """
   The input is linear over the domain. The fact that the residuals are very small
   despite the small number of cells, proves that the basic algorithm is sound.
   """
   bundle_help = regridding_modres_linear.__doc__
   path = QR.add2path(path,'linear')
   return regridding_modres_generic (ns, path, rider, bundle_help, input=ns.xy)

#--------------------------------------------------------------------------------

def regridding_modres_curved (ns, path, rider=None):
   """
   The input is curved over the domain. The residuals reflect the fact that the
   function is not quite linear over a cell. The residuals will be smaller if the
   cells are smaller, i.e. for larger values of num_cells.
   """
   bundle_help = regridding_modres_curved.__doc__
   path = QR.add2path(path,'curved')
   return regridding_modres_generic (ns, path, rider, bundle_help,
                                     input=ns.gaussian2D, num_cells=[4,5])

#--------------------------------------------------------------------------------

def regridding_modres_generic (ns, path, rider, bundle_help, input,
                                num_cells=[2,3], mode=1):
   """
   Generic subtree to demonstrate MeqModRes regridding.
   """
   original = QR.uniquestub(ns, 'original') << Meq.Identity(input)
   modres = QR.MeqNode (ns, path, meqclass='ModRes',
                        name='ModRes(input, num_cells='+str(num_cells)+')',
                        help='changes the resolution of the REQUEST',
                        rider=rider, children=[input], num_cells=num_cells)
   resampled = QR.MeqNode (ns, path, meqclass='Resampler',
                           name='Resampler(modres, mode='+str(mode)+')',
                           help='resamples the domain according to the input request',
                           rider=rider, children=[modres], mode=mode)
   diff = QR.uniquestub(ns, 'diff(resampled,original)') << Meq.Subtract(resampled,original)
   return QR.bundle (ns, path, nodes=[diff], help=bundle_help, rider=rider,
                     bookmark=[original, modres, resampled, diff])




#================================================================================
# reduction_... 
#================================================================================

def reduction_single (ns, path, rider=None):
   """
   Demonstration of basic reduction, on one child, with a single vellset.
   The reduction is done along all available axes (the default), producing a
   single-number Result.
   """
   bundle_help = reduction_single.__doc__
   path = QR.add2path(path,'single')
   cc = [ns.x]
   help = record(NElements='nr of cells',
                 Sum='sum of cell values', Mean='mean of cell values',
                 Product='product of cell values',
                 Min='min cell value', Max='max  cell value',
                 StdDev='stddev of cell values',
                 Rms='same as StdDev (obsolete?)')
   for q in ['Nelements','Sum','Mean','Product','StdDev','Rms', 'Min','Max']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x)',
                            help=help[q], rider=rider, children=[ns.x]))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)

#--------------------------------------------------------------------------------

def reduction_multiple (ns, path, rider=None):
   """
   Demonstration of more advanced reduction,
   involving multiple children (....?) 
   with Results that may contain multiple vellsets.
   The reduction is done along all available axes (the default), producing a
   single-number Result.
   This demonstration uses only one of the relevant MeqNodes (MeqSum).
   """
   bundle_help = reduction_multiple.__doc__
   path = QR.add2path(path,'multiple')
   democlass = 'Sum'
   help = democlass+' over the cells of '
   cc = [ns.y,ns.range5,ns.ny]
   cc.append(QR.MeqNode (ns, path, meqclass=democlass, name=democlass+'(y)',
                         help=help+'a single vellset, of a single child',
                         rider=rider, children=[ns.y]))
   cc.append(QR.MeqNode (ns, path, meqclass=democlass, name=democlass+'(range5)',
                         help=help+'multiple vellsets, from a single tensor child',
                         rider=rider, children=[ns.range5]))
   if False:
      # Reduction nodes do not work on multiple children...?
      cc.append(QR.MeqNode (ns, path, meqclass=democlass, name=democlass+'(x,y)',
                            help=help+'multiple vellsets, from two children',
                            rider=rider, children=[ns.x,ns.y]))
      cc.append(QR.MeqNode (ns, path, meqclass=democlass, name=democlass+'(range5,x)',
                            help=help+'multiple vellsets, from inhomogeneos children',
                            rider=rider, children=[ns.range5,ns.x]))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)


#--------------------------------------------------------------------------------

def reduction_axes (ns, path, rider=None):
   """
   Demonstration of more advanced reduction, along a subset of the available axes.
   If one or more reduction_axes are specified, the reduction is only
   along the specified axes (e.g. reduction_axes=['time'] reduces only
   the time-axis to length 1. The default is all available axes, of course. 
   The Result of a reduction node will be expanded when needed to fit a
   domain of the original size, in which multiple cells have the same value.
   This demonstration uses only one of the relevant MeqNodes (MeqSum).
   """
   bundle_help = reduction_axes.__doc__
   path = QR.add2path(path,'axes')
   democlass = 'Sum'
   help = democlass+' over the cells of '
   c0 = ns.xy
   nc0 = ns << Meq.NElements(c0)
   cc = [c0,nc0]
   cc.append(QR.MeqNode (ns, path, meqclass=democlass,
                         name=democlass+'(xy)',
                         help=help+'no reduction_axes specified, assume all',
                         rider=rider, children=[c0]))
   cc.append(QR.MeqNode (ns, path, meqclass=democlass,
                         name=democlass+'(xy, reduction_axes=[time])',
                         help=help+'the time-axis is reduced to length 1.',
                         rider=rider, children=[c0], reduction_axes=['time']))
   cc.append(QR.MeqNode (ns, path, meqclass=democlass,
                         name=democlass+'(xy, reduction_axes=[freq])',
                         help=help+'the freq-axis is reduced to length 1.',
                         rider=rider, children=[c0], reduction_axes=['freq']))
   cc.append(QR.MeqNode (ns, path, meqclass=democlass,
                         name=democlass+'(xy, reduction_axes=[freq,time])',
                         help=help+'both the freq and time axes are reduced.',
                         rider=rider, children=[c0], reduction_axes=['freq','time']))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)




#================================================================================
# tensor_... 
#================================================================================


def tensor_manipulation (ns, path, rider=None):
   """
   Manipulation of 'tensor' nodes, i.e. nodes with multiple vellsets.
   """
   bundle_help = tensor_manipulation.__doc__
   path = QR.add2path(path,'manipulation')
   cc = []
   cc.append(QR.MeqNode (ns, path, meqclass='Composer', name='Composer(x,y,ft)',
                         help="""Combine the vellsets in the Results of its children
                         into a Result with multiple vellsets in the new node.""",
                         rider=rider, children=[ns.x,ns.y,ns.ft]))
   cc.append(QR.MeqNode (ns, path, meqclass='Selector', name='Selector(child, index=1)',
                         help="""Select the specified (index) vellset in its child
                         for a new node with a single vellset in its Result""",
                         rider=rider, children=[cc[0]], index=1))
   if True:
      # Problem: Gives an error (list indix not supported?)
      cc.append(QR.MeqNode (ns, path, meqclass='Selector', name='Selector(child, index=[0,2])',
                            help="""Select the specified (index) vellsets in its child
                            for a new node with this subset of vellsets in its Result""",
                            rider=rider, children=[cc[0]], index=[0,2]))
   if True:
      # Problem: Does not work... (nr of vells stays the same). But index is the correct keyword...
      cc.append(QR.MeqNode (ns, path, meqclass='Paster', name='Paster(c0, c1, index=1)',
                            help="""Make a new node, in which the vellset from the
                            second child (c1) is pasted at the specified (index) position
                            among the vellsets of its first child (c0)""",
                            rider=rider, children=[cc[0],ns.ft], index=1))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)

#--------------------------------------------------------------------------------

def tensor_matrix (ns, path, rider=None):
   """
   Nodes with multiple vellsets can be treated as matrices.
   There are some specialised nodes that do matrix operations.
   NB: For the moment, only 2x2 matrices can be inverted, since
   this was easiest to program by hand (see MatrixInvert22).
   A more general inversion node will be implemted later.
   """
   bundle_help = tensor_matrix.__doc__
   path = QR.add2path(path,'matrix')
   cc = []
   cc.append(QR.MeqNode (ns, path, meqclass='Composer',
                         name='Composer(1,2,3,4,5,6, dims=[2,3])',
                         help="""Make a tensor node with a 2x3 array of vellsets.
                         This can be treated as a 2x3 matrix. Note the use of
                         constants as children, for easier inspection and verification.""",
                         rider=rider, children=range(6),dims=[2,3]))
   cc.append(QR.MeqNode (ns, path, meqclass='Transpose', name='Transpose(m0)',
                         help="""Make the 3x2 transpose of the given 2x3 matrix.""",
                         rider=rider, children=[cc[0]]))
   cc.append(QR.MeqNode (ns, path, meqclass='MatrixMultiply', name='MatrixMultiply(m0,m1)',
                         help="""Multply the original 2x3 matrix with its 3x2 transpose.
                         This produces a 2x2 matrix.""",
                         rider=rider, children=[cc[0],cc[1]]))
   cc.append(QR.MeqNode (ns, path, meqclass='MatrixMultiply', name='MatrixMultiply(m1,m0)',
                         help="""Multply the 3x2 transpose with the original 2x3 matrix.
                         This produces a 3x3 matrix.""",
                         rider=rider, children=[cc[1],cc[0]]))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)

#--------------------------------------------------------------------------------

def tensor_matrix22 (ns, path, rider=None):
   """
   Because the 2x2 cohaerency matrix and the 2x2 Jones matrix play an important
   role in the radio-astronomical Measurement Equation (M.E.), there are a few
   specialized nodes that deal with 2x2 matrices.
   """
   bundle_help = tensor_matrix22.__doc__
   path = QR.add2path(path,'matrix22')
   cc = []
   cc.append(QR.MeqNode (ns, path, meqclass='Matrix22', name='Matrix22(cxx,0,0,cxy)',
                         help="""Make a complex 2x2 diagonal matrix.""",
                         rider=rider, children=[ns.cxx,0,0,ns.cxy]))
   cc.append(QR.MeqNode (ns, path, meqclass='MatrixInvert22', name='MatrixInvert22(m0)',
                         help="""Invert the given 2x2 matrix (m0), cell-by-cell""",
                         rider=rider, children=[cc[0]]))
   cc.append(QR.MeqNode (ns, path, meqclass='MatrixMultiply', name='MatrixMultiply(m0,m0inv)',
                         help="""Multply the matrix (m0) with its inverse (m0inv).
                         The result should be a unit matrix (cell-by-cell).""",
                         rider=rider, children=[cc[0],cc[1]]))
   cc.append(QR.MeqNode (ns, path, meqclass='ConjTranspose', name='ConjTranspose(m0)',
                         help="""Conjugate Transpose the given matrix (m0)""",
                         rider=rider, children=[cc[0]]))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)



#================================================================================
# binops_...
#================================================================================

def binops_two_children (ns, path, rider=None):
   """
   Binary operations on two children. The operation is performed cell-by-cell.
   If the first child (c0) has a result with multiple vellsets ("tensor-node"),
   there are two possibilities: If the second child (c1) is a "scalar node", its
   single vellset is applied to all the vellsets of c0. Otherwise, the Result of
   c1 must have the same number of vellsets as c0, and the operation is performed
   between corresponding vellsets. The final Result always has the same shape
   (number of vellsets) as c0.
   """
   bundle_help = binops_two_children.__doc__
   path = QR.add2path(path,'two_children')
   cc = []
   help = record(Subtract='c0-c1', Divide='c0/c1', Pow='c0^c1', Mod='c0%c1',
                 ToComplex='(real, imag)', Polar='(amplitude, phase)')
   for q in ['Subtract','Divide','Pow','ToComplex','Polar']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x,y)',
                            help=help[q], rider=rider, children=[ns.x,ns.y]))
   if False:
      # Problem: MeqMod() crashes the meqserver.... Needs integer children??
      cc.append(QR.MeqNode (ns, path, meqclass='Mod', name='Mod(x,y)',
                            help=help['Mod'], rider=rider, children=[ns.x,ns.y]))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)

#--------------------------------------------------------------------------------

def binops_one_or_more (ns, path, rider=None):
   """
   Math operations on one (!) or more children. The operation is performed
   cell-by-cell. If the number of children is two, the same rules apply as
   for binary operations (see binops_two_children).
   If the number of children is greater than two, the Results of all children
   must have the same shape (i.e. the same number of vellsets in their Results).
   If the number of of children is one.... 
   """
   bundle_help = binops_one_or_more.__doc__
   path = QR.add2path(path,'one_or_more')
   cc = []
   help = record(Add='c0+c1+c2+...', Multiply='c0*c1*c2*...',
                 NElements="""the number of cells in the domain.
                 Not quite safe if there are flags....""",
                 WSum="""Weighted sum: w[0]*c0 + w[1]*c1 + w[2]*c2 + ...
                 The weights vector (weights) is a vector of DOUBLES (!)""",
                 WMean="""Weighted mean, the same as WSum, but divides by
                 the sum of the weights (w[0]+w[1]+w[2]+....)""")
   for q in ['Add','Multiply']:
   # NElements gives problems with more than one child:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x,y,t)',
                            help=help[q], rider=rider,
                            children=[ns.x,ns.y,ns.t]))
   if False:
      # Problem: NElements() gives problems with more than one child:
      cc.append(QR.MeqNode (ns, path, meqclass='NElements', name='NElements(x,y,t)',
                            help=help['NElements'], rider=rider,
                            children=[ns.x,ns.y,ns.t]))
   for q in ['WSum','WMean']:
      weights = [2.0,3.0,4.0]
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x,y,t,weights=ww)',
                            help=help[q], rider=rider,
                            children=[ns.x,ns.y,ns.t], weights=weights))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)



#================================================================================
# leaves_...
#================================================================================

def leaves_constant (ns, path, rider=None):
   """
   A constant may be complex, or a tensor. There are various ways to define one.
   """
   bundle_help = leaves_constant.__doc__
   path = QR.add2path(path,'constant')
   cc = []
   help = 'Constant node created with: '
   cc.append(QR.MeqNode (ns, path, node=(ns << 2.5),
                         help=help+'ns << 2.5'))
   cc.append(QR.MeqNode (ns, path, node=(ns.xxxx << 2.4),
                         help=help+'ns.xxxx << 2.4'))
   cc.append(QR.MeqNode (ns, path, meqclass='Constant', name='Constant(real)',
                         help='', value=1.2))
   cc.append(QR.MeqNode (ns, path, meqclass='Constant', name='Constant(complex)',
                         help='', value=complex(1,2)))
   cc.append(QR.MeqNode (ns, path, meqclass='Constant', name='Constant(vector)',
                         help='produces a "tensor node"', value=range(4)))
   cc.append(QR.MeqNode (ns, path, meqclass='Constant', name='Constant(vector, shape=[2,2])',
                         help='produces a "tensor node"', value=range(4), shape=[2,2]))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)

#--------------------------------------------------------------------------------

def leaves_parm (ns, path, rider=None):
   """
   MeqParm nodes represent M.E. parameters, which may be solved for.
   """
   bundle_help = leaves_parm.__doc__
   path = QR.add2path(path,'parm')
   cc = []
   help = ''
   cc.append(QR.MeqNode (ns, path, meqclass='Parm',
                         help=help, default=2.5))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)


#--------------------------------------------------------------------------------

def leaves_noise (ns, path, rider=None):
   """
   Noise nodes generate noisy cell values. The arguments are passed as
   keyword arguments in the node constructor (or as children?)
   """
   bundle_help = leaves_noise.__doc__
   path = QR.add2path(path,'noise')
   cc = []
   help = 'Gaussian noise with given stddev (and zero mean)'
   cc.append(QR.MeqNode (ns, path, meqclass='GaussNoise',
                         name='GaussNoise(stddev=2)',
                         help=help, rider=rider,
                         stddev=2.0))
   help = 'Gaussian noise with given stddev and mean'
   # NB: mean does not work...
   cc.append(QR.MeqNode (ns, path, meqclass='GaussNoise',
                         name='GaussNoise(stddev=2,mean=-10)',
                         help=help, rider=rider,
                         mean=-10.0, stddev=2.0))
   if False:
      # Problem: The server crashes on this one...!
      help = 'Random noise between lower and upper bounds'
      cc.append(QR.MeqNode (ns, path, meqclass='RandomNoise',
                            name='RandomNoise(-2,4)',
                            help=help, rider=rider,
                            lower=-2.0, upper=4.0))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)


#--------------------------------------------------------------------------------

def leaves_grids (ns, path, rider=None):
   """
   Grid nodes fill in the cells of the requested domain with the
   values of the specified axis (time, freq, l, m, etc).
   See also the state forest....
   The two default axes (time and freq) have dedicated Grid nodes,
   called MeqTime and MeqFreq.
   """
   bundle_help = leaves_grids.__doc__
   path = QR.add2path(path,'grids')
   cc = []
   help = ''
   for q in ['Freq','Time']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'()',
                            help=help, rider=rider)) 
   for q in ['freq','time','L','M']:
      cc.append(QR.MeqNode (ns, path, meqclass='Grid',name='Grid(axis='+q+')',
                            help=help, rider=rider, axis=q))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)


#--------------------------------------------------------------------------------

def leaves_spigot (ns, path, rider=None):
   """
   The MeqSpigot reads data from an AIPS++/Casa Measurement Set (uv-data).
   It is twinned with the MeqSink, which writes uv-data back into the MS,
   and generates a sequence of requests with suitable time-freq domains
   (snippets). See also....
   MeqVisDataMux:
   MeqFITSSpigot:
   """
   bundle_help = leaves_spigot.__doc__
   path = QR.add2path(path,'spigot')
   cc = []
   help = ''
   cc.append(QR.MeqNode (ns, path, meqclass='Spigot', name='Spigot()',
                         help=help))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)

#--------------------------------------------------------------------------------

def leaves_FITS (ns, path, rider=None):
   """
   There are various nodes to read images from FITS files.
   MeqFITSReader:
   MeqFITSImage:
   MeqFITSSpigot:
   """
   bundle_help = leaves_FITS.__doc__
   path = QR.add2path(path,'FITS')
   cc = []
   help = ''
   cc.append(QR.MeqNode (ns, path, meqclass='FITSReader',
                         help=help))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)




#================================================================================
# unops_... (Unary operations)
#================================================================================


def unops_elementary (ns, path, rider=None):
   """
   Elementary unary operations.
   """
   bundle_help = unops_elementary.__doc__
   path = QR.add2path(path,'elementary')
   cc = [ns.x]
   help = ''
   for q in ['Negate','Invert','Exp','Log','Sqrt']:
      # NB: explain log...
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x)',
                            help=help, rider=rider, children=[ns.x]))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)

#--------------------------------------------------------------------------------

def unops_goniometric (ns, path, rider=None):
   """
   Goniometric functions turn an angle (rad) into a fraction.
   """
   bundle_help = unops_goniometric.__doc__
   path = QR.add2path(path,'goniometric')
   cc = [ns.x]
   cc = []
   help = record(Sin='(rad)', Cos='(rad)', Tan='(rad)',
                 Asin='abs(x)<1', Acos='abs(x)<1', Atan='')
   for q in ['Sin','Cos','Tan','Asin','Acos','Atan']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x)',
                            help=help[q], rider=rider, children=[ns.x]))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)

#--------------------------------------------------------------------------------

def unops_hyperbolic (ns, path, rider=None):
   """
   Hyperbolic functions convert a fraction into an angle (rad).
   """
   bundle_help = unops_hyperbolic.__doc__
   path = QR.add2path(path,'hyperbolic')
   cc = [ns.x]
   help = ''
   for q in ['Sinh','Cosh','Tanh']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x)',
                            help=help, rider=rider, children=[ns.x]))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)

#--------------------------------------------------------------------------------

def unops_complex (ns, path, rider=None):
   """
   Operations on a (usually) complex child.
   """
   bundle_help = unops_complex.__doc__
   path = QR.add2path(path,'complex')
   cc = [ns.cxy]
   help = record(Abs='', Norm='like Abs', Arg='-> rad', Real='', Imag='',
                 Conj='complex conjugate: a+bj -> a-bj',
                 Exp='exp(a+bj) = exp(a)*exp(bj), i.e. cos with increasing ampl',
                 Log='e-log (ln)')
   for q in ['Abs','Norm','Arg','Real','Imag','Conj','Exp','Log']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(cxy)',
                            help=help[q], rider=rider, children=[ns.cxy]))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)

#--------------------------------------------------------------------------------

def unops_power (ns, path, rider=None):
   """
   Nodes that take some power of its child.
   """
   bundle_help = unops_power.__doc__
   path = QR.add2path(path,'power')
   cc = [ns.x]
   help = ' of its single child'
   for q in ['Sqr','Pow2','Pow3','Pow4','Pow5','Pow6','Pow7','Pow8']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x)',
                            help=q+help, rider=rider, children=[ns.x]))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)

#--------------------------------------------------------------------------------

def unops_misc (ns, path, rider=None):
   """
   Miscellaneous unary operations.
   """
   bundle_help = unops_misc.__doc__
   path = QR.add2path(path,'misc')
   cc = [ns.x]
   help = record(Abs='Take the absolute value.',
                 Ceil='Round upwards to integers.',
                 Floor='Round downwards to integers.',
                 Stripper="""Remove all derivatives (if any) from the result.
                 This saves space and can be used to control solving.""",
                 Identity='Make a copy node with a different name.'
                 )
   for q in ['Abs','Ceil','Floor','Stripper','Identity']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x)',
                            help=help[q], rider=rider, children=[ns.x]))
   return QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)











#================================================================================
#================================================================================
#================================================================================
#================================================================================
# Local testing forest:
#================================================================================

TDLCompileMenu("QR_MeqNodes categories:",
               TDLOption('opt_allcats',"all",True),
               TDLOption('opt_unops',"Unary nodes (one child)",False),
               TDLOption('opt_binops',"Binary nodes",False),
               TDLOption('opt_leaves',"Leaf nodes (no children)",False),
               TDLOption('opt_tensor',"Tensor nodes (multiple vellsets)",False),
               TDLOption('opt_reduction',"reduction",False),
               TDLOption('opt_regridding',"regridding",False),
               TDLOption('opt_flagging',"flagging",False),
               TDLOption('opt_solving',"solving",False),
               TDLOption('opt_visualization',"visualization",False),
               TDLOption('opt_transforms',"transforms",False),
               TDLOption('opt_flowcontrol',"flowcontrol",False),
               # TDLOption('opt_',"",False),
               )

#--------------------------------------------------------------------------------

def _define_forest (ns, **kwargs):
   """Definition of a 'forest' of one or more trees"""

   trace = False
   # trace = True

   # Make some standard child-nodes with standard names
   scnodes = QR.standard_child_nodes(ns)

   # Make bundles of (bundles of) categories of nodes/subtrees:
   rootnodename = 'QR_MeqNodes'                 # The name of the node to be executed...
   path = rootnodename                          # Root of the path-string
   global rider                                 # used in tdl_jobs
   rider = QR.CollatedHelpRecord()              # Helper class
   cc = []
   cc = [scnodes]
   if opt_allcats:                              # All available categories
      cc.append(MeqNodes(ns, path, rider=rider))
   else:                                        # Selected categories only
      if opt_unops:
         cc.append(unops(ns, path, rider=rider))
      if opt_binops:
         cc.append(binops(ns, path, rider=rider))
      if opt_leaves:
         cc.append(leaves(ns, path, rider=rider))
      if opt_tensor:
         cc.append(tensor(ns, path, rider=rider))
      if opt_reduction:
         cc.append(reduction(ns, path, rider=rider))
      if opt_regridding:
         cc.append(regridding(ns, path, rider=rider))
      if opt_flagging:
         cc.append(flagging(ns, path, rider=rider))
      if opt_solving:
         cc.append(solving(ns, path, rider=rider))
      if opt_visualization:
         cc.append(visualization(ns, path, rider=rider))
      if opt_transforms:
         cc.append(transforms(ns, path, rider=rider))
      if opt_flowcontrol:
         cc.append(flowcontrol(ns, path, rider=rider))

   # Make the outer bundle (of node bundles):
   bundle_help = 'Local testing forest'
   QR.bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)

   if trace:
      rider.show('_define_forest()')

   # Finished:
   return True
   

#--------------------------------------------------------------------------------

def _tdl_job_execute_1D (mqs, parent):
   return QR._tdl_job_execute_1D (mqs, parent, rootnode='QR_MeqNodes')

def _tdl_job_execute_2D (mqs, parent):
   return QR._tdl_job_execute_2D (mqs, parent, rootnode='QR_MeqNodes')

def _tdl_job_execute_sequence (mqs, parent):
   return QR._tdl_job_execute_sequence (mqs, parent, rootnode='QR_MeqNodes')

def _tdl_job_print_doc (mqs, parent):
   return QR._tdl_job_print_doc (mqs, parent, rider, header='QR_MeqNodes')

def _tdl_job_popup_doc (mqs, parent):
   return QR._tdl_job_popup_doc (mqs, parent, rider, header='QR_MeqNodes')

def _tdl_job_save_doc (mqs, parent):
   return QR._tdl_job_save_doc (mqs, parent, rider, filename='QR_MeqNodes')



#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

   print '\n** Start of standalone test of: QR_MeqNodes.py:\n' 

   ns = NodeScope()

   import QuickRef as QR
   rider = QR.CollatedHelpRecord()
   MeqNodes(ns, 'test', rider=rider)

   if 0:
      rider.show('testing')

   if 0:
      subject = 'unops'
      subject = 'binops'
      subject = 'leaves'
      subject = 'leaves.constant'
   # cc.append(reduction (ns, path, rider=rider))
   # cc.append(regridding (ns, path, rider=rider))
   # cc.append(flagging (ns, path, rider=rider))
   # cc.append(solving (ns, path, rider=rider))
   # cc.append(visualization (ns, path, rider=rider))
   # cc.append(transforms (ns, path, rider=rider))
   # cc.append(flowcontrol (ns, path, rider=rider))
      path = 'test.MeqNodes.'+subject
      rr = rider.subrec(path, trace=True)
      rider.show('subrec',rr, full=False)
            
   print '\n** End of standalone test of: QR_MeqNodes.py:\n' 

#=====================================================================================





