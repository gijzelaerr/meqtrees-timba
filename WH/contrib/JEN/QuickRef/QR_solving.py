"""
QuickRef module: QR_solving.py
Demonstration(s) of solving for MeqParm values in MeqTrees.
It may be called from the module QuickRef.py.
But it may also be used stand-alone.
-- Load the TDL script into the meqbrowser.
-- Using TDL Options, select categories to be included,
.    and customize parameters and input children.
-- Compile: The tree will appear in the left panel.
.    (NB: the state record of each node has a quickref_help field)
-- Use the bookmarks to select one or more views.
-- Use TDL Exec to execute the tree: The views will come alive.
-- Use TDL Exec to show or print or save the hierarchical help
.    for the selected categories.
"""

# file: ../JEN/demo/QR_solving.py:
#
# Author: J.E.Noordam
#
# Short description:
#   Demonstration(s) of solving for MeqParm values in MeqTrees.
#
# History:
#   - 11 jun 2008: creation (from QR_MeqNodes.py)
#
# Description:
#
# Remarks:
#
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

from Timba.Contrib.JEN.QuickRef import QuickRefUtil as QRU
from Timba.Contrib.JEN.QuickRef import EasyTwig as ET
from Timba.Contrib.JEN.QuickRef import EasyNode as EN

# from Timba.Contrib.JEN.Expression import Expression

# import math
# import random
import numpy


#******************************************************************************** 
# TDLCompileMenu (included in QuickRef menu):
#********************************************************************************


TDLCompileMenu("QR_solving topics:",
               TDLOption('opt_alltopics',"override: include all topics",True),
               TDLMenu("basic",
                       TDLOption('opt_basic_twig',"input twig (lhs of condeq)",
                                 ET.twig_names(['gaussian'],first='gaussian_ft'),
                                 more=str),
                       TDLOption('opt_basic_tiling_time',"size (time-cells) of solving subtile",
                                 [None,1,2,3,4,5,10], more=int),
                       TDLOption('opt_basic_tiling_freq',"size (freq-cells) of solving subtile",
                                 [None,1,2,3,4,5,10], more=int),
                       TDLOption('opt_basic_mepfile',"name of mep table file",
                                 [None,'QR_solving'], more=str),
                       TDLMenu("basic_polyparm",
                               TDLOption('opt_basic_polyparm_poly',"polynomial to be fitted (rhs)",
                                         ET.twig_names(['polyparm']), more=str),
                               toggle='opt_basic_polyparm'),
                       TDLMenu("basic_Expression",
                               TDLOption('opt_basic_Expression_expr',"Expression to be fitted (rhs)",
                                         ET.twig_names(['Expression']), more=str),
                               toggle='opt_basic_Expression'),
                       TDLMenu("basic_onepolc",
                               TDLOption('opt_basic_onepolc_tdeg',"time deg of MeqParm polc",
                                         range(6), more=int),
                               TDLOption('opt_basic_onepolc_fdeg',"freq deg of MeqParm polc",
                                         range(6), more=int),
                               toggle='opt_basic_onepolc'),
                       toggle='opt_basic'),

               TDLMenu("help",
                       TDLOption('opt_helpnode_twig',"help on EasyTwig.twig()", False),
                       toggle='opt_helpnodes'),

               toggle='opt_QR_solving')



#********************************************************************************
# Top-level function, called from QuickRef.py:
#********************************************************************************


def QR_solving (ns, rider):
   """
   Solving...
   """
   stub = QRU.on_entry(ns, rider, QR_solving)
   cc = []
   if opt_alltopics or opt_basic:
      cc.append(basic (ns, rider))

   if opt_helpnodes:
      cc.append(make_helpnodes (ns, rider))

   return QRU.on_exit (ns, rider, cc)



#********************************************************************************
# 2nd tier: Functions called from the top function above:
#********************************************************************************

def make_helpnodes (ns, rider):
   """
   helpnodes...
   """
   stub = QRU.on_entry(ns, rider, make_helpnodes)
   
   cc = []
   if opt_alltopics or opt_helpnode_twig:
      cc.append(QRU.helpnode (ns, rider,
                              name='EasyTwig_twig',
                              help=ET.twig.__doc__, trace=False))

   return QRU.on_exit (ns, rider, cc)


#--------------------------------------------------------------------------------

def basic (ns, rider):
   """
   MeqSolver
   MeqCondeq
   MeqStripper (?)
   """
   stub = QRU.on_entry(ns, rider, basic)
   cc = []
   cc.append(basic_ab (ns, rider))                    # simplest, do always
   if opt_alltopics or opt_basic_polyparm:
      cc.append(basic_polyparm (ns, rider))
   if opt_alltopics or opt_basic_onepolc:
      cc.append(basic_onepolc (ns, rider))

   if opt_basic_Expression:
   # if opt_alltopics or opt_basic_Expression:                 # when Expression MeqParm problem solved...
      cc.append(basic_Expression (ns, rider))

   return QRU.on_exit (ns, rider, cc)




#********************************************************************************
#********************************************************************************
#********************************************************************************
# 3rd tier: Functions called from functions at the 2nd tier above
#********************************************************************************
#********************************************************************************


#================================================================================
# basic_... 
#================================================================================

def basic_ab (ns, rider):
   """
   Demonstration of solving for two unknown parameters (a,b),
   using two linear equations (one condeq child each):
   - condeq 0:  a + b = p (=10)
   - condeq 1:  a - b = q (=2)
   The result should be: a = (p+q)/2 (=6), and b = (p-q)/2 (=4)
   Condeq Results are the solution residuals, which should be small.
   """
   stub = QRU.on_entry(ns, rider, basic_ab)
   a = EN.unique_stub(ns, 'a') << Meq.Parm(0)
   b = EN.unique_stub(ns, 'b') << Meq.Parm(0)
   p = EN.unique_stub(ns, 'p') << Meq.Constant(10)
   q = EN.unique_stub(ns, 'q') << Meq.Constant(2)
   sum_ab = ns << Meq.Add(a,b) 
   diff_ab = ns << Meq.Subtract(a,b)
   drivers = EN.unique_stub(ns, 'driving_values_p_q') << Meq.Composer(p,q)
   parmset = EN.unique_stub(ns, 'solved_parameters_a_b') << Meq.Composer(a,b)

   condeqs = []
   condeqs.append(QRU.MeqNode (ns, rider, meqclass='Condeq',name='Condeq(a+b,p)',
                               help='Represents equation: a + b = p (=10)',
                               children=[sum_ab, p]))
   condeqs.append(QRU.MeqNode (ns, rider, meqclass='Condeq',name='Condeq(a-b,q)',
                               help='Represents equation: a - b = q (=2)',
                               children=[diff_ab, q]))

   solver = QRU.MeqNode (ns, rider, meqclass='Solver',
                         name='Solver(*condeqs, solvable=[a,b])',
                         help='Solver', show_recurse=True,
                         children=condeqs,
                         solvable=[a,b])  
   residuals = QRU.MeqNode (ns, rider, meqclass='Add', name='residuals',
                            help='The sum of the (abs) condeq residuals',
                            children=condeqs, unop='Abs')
   cc = [solver,residuals,drivers,parmset]
   return QRU.on_exit (ns, rider, cc,
                      parentclass='ReqSeq', result_index=0)

#--------------------------------------------------------------------------------

def basic_polyparm (ns, rider):
   """
   Demonstration of solving for the coefficients of a freq-time polynomial.
   It is fitted to the specified twig (e.g. a 2D gaussian).
   A separate equation is generated for each cell of the Request domain.

   The number of cells should be greater than the number of unknowns.
   In this case, this is the number of MeqParms, which have polcs with only
   a single coefficient (c00). NB: Try solving for freq-time polcs....)

   If the input (twig) function does not vary much over the domain, there
   is not enough information to solve for higher-order polynomial coeff.
   In this case, the solution will 'lose rank', which is indicated in the
   solver plot: the black line on the right leaves the right edge. 
   """
   stub = QRU.on_entry(ns, rider, basic_polyparm)
   twig = ET.twig(ns, opt_basic_twig)                       # move to solving()?
   poly = ET.twig(ns, opt_basic_polyparm_poly)
   parms = EN.find_parms(poly, trace=False)
   parmset = EN.unique_stub(ns,'solved_parms') << Meq.Composer(*parms)
   condeq = ns << Meq.Condeq(poly, twig)
   solver = QRU.MeqNode (ns, rider, meqclass='Solver',
                         name='Solver(condeq, solvable=parms)',
                         help='Solver', show_recurse=True,
                         children=[condeq],
                         solvable=parms)  
   cc = [solver,condeq,poly,twig,parmset]
   return QRU.on_exit (ns, rider, cc,
                      parentclass='ReqSeq', result_index=0)

#--------------------------------------------------------------------------------

def basic_Expression (ns, rider):
   """
   """
   stub = QRU.on_entry(ns, rider, basic_Expression)
   lhs = ET.twig(ns, opt_basic_twig)              
   print '** expr =',opt_basic_Expression_expr
   rhs = ET.twig(ns, opt_basic_Expression_expr)
   print '** rhs =',str(rhs)
   parms = EN.find_parms(rhs, trace=True)
   if len(parms)==0:
      s = '** the Expression: '+opt_basic_Expression_expr
      s += '\n  should have at least one {parm}...'
      raise ValueError,s
   elif len(parms)==1:
      parmset = parms[0]
   else:
      parmset = EN.unique_stub(ns,'solved_parms') << Meq.Composer(*parms)
   condeq = ns << Meq.Condeq(lhs,rhs)
   solver = QRU.MeqNode (ns, rider, meqclass='Solver',
                         name='Solver(condeq, solvable=parms)',
                         help='Solver', show_recurse=True,
                         children=[condeq],
                         solvable=parms)  
   cc = [solver,condeq,lhs,rhs,parmset]
   return QRU.on_exit (ns, rider, cc,
                      parentclass='ReqSeq', result_index=0)

#--------------------------------------------------------------------------------

def basic_onepolc (ns, rider):
   """
   Solving for the coeff of the polc of a single MeqParm.
   The single MeqCondeq child of the MeqSolver has two children:
   - The left-hand side (lhs) is the input twig node (e.g. a gaussian_ft)
   - The right-hand side (rhs) is a MeqParm:
   .      rhs = ns['MeqParm'] << Meq.Parm(meq.polc(coeff=numpy.zeros([tdeg+1,fdeg+1])))
   """
   stub = QRU.on_entry(ns, rider, basic_onepolc)
   lhs = ET.twig(ns, opt_basic_twig)
   tiling = record(freq=opt_basic_tiling_freq,
                   time=opt_basic_tiling_time)
   fdeg = opt_basic_onepolc_fdeg
   tdeg = opt_basic_onepolc_tdeg
   mepfile = opt_basic_mepfile
   pname = 'MeqParm(shape=[1+'+str(tdeg)+',1+'+str(fdeg)+'])'
   help = 'help'
   rhs = EN.unique_stub(ns,pname) << Meq.Parm(0.0,
                                              tags=['tag1','tag2'],
                                              shape=[tdeg+1,fdeg+1],
                                              tiling=tiling,
                                              table_name=mepfile,
                                              use_previous=True,
                                              quickref_help='...help...',
                                              node_groups='Parm')
   condeq = ns << Meq.Condeq(lhs,rhs)
   solver = QRU.MeqNode (ns, rider, meqclass='Solver',
                         name='Solver(condeq, solvable=MeqParm)',
                         help='Solver', show_recurse=True,
                         children=[condeq],
                         niter=10,
                         solvable=rhs)  
   cc = [solver,condeq,lhs,rhs]
   QRU.helpnode(ns, rider, node=rhs)
   return QRU.on_exit (ns, rider, cc,
                      parentclass='ReqSeq', result_index=0)


#--------------------------------------------------------------------------------










#================================================================================
#================================================================================
#================================================================================
#================================================================================
# Local testing forest:
#================================================================================

TDLRuntimeMenu(":")
TDLRuntimeMenu("QuickRef runtime options:", QRU)
TDLRuntimeMenu(":")

# For TDLCompileMenu, see the top of this module


#--------------------------------------------------------------------------------

def _define_forest (ns, **kwargs):
   """Definition of a 'forest' of one or more trees"""

   global rootnodename
   rootnodename = 'QR_solving'                  # The name of the node to be executed...
   global rider                                 # used in tdl_jobs
   rider = QRU.create_rider(rootnodename)       # CollatedHelpRecord object
   QRU.on_exit (ns, rider,
               nodes=[QR_solving(ns, rider)])

   # Finished:
   return True
   


#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------

def _tdl_job_execute_1D_f (mqs, parent):
   return QRU._tdl_job_execute_f (mqs, parent, rootnode=rootnodename)

def _tdl_job_execute_2D_ft (mqs, parent):
   return QRU._tdl_job_execute_ft (mqs, parent, rootnode=rootnodename)

def _tdl_job_execute_3D_ftL (mqs, parent):
   return QRU._tdl_job_execute_ftL (mqs, parent, rootnode=rootnodename)

def _tdl_job_execute_4D_ftLM (mqs, parent):
   return QRU._tdl_job_execute_ftLM (mqs, parent, rootnode=rootnodename)

def _tdl_job_execute_sequence (mqs, parent):
   return QRU._tdl_job_execute_sequence (mqs, parent, rootnode=rootnodename)

#--------------------------------------------------------------------------------

def _tdl_job_m (mqs, parent):
   return QRU._tdl_job_m (mqs, parent)

def _tdl_job_print_doc (mqs, parent):
   return QRU._tdl_job_print_doc (mqs, parent, rider, header='QR_solving')

def _tdl_job_print_hardcopy (mqs, parent):
   return QRU._tdl_job_print_hardcopy (mqs, parent, rider, header='QR_solving')

def _tdl_job_show_doc (mqs, parent):
   return QRU._tdl_job_show_doc (mqs, parent, rider, header='QR_solving')

def _tdl_job_save_doc (mqs, parent):
   return QRU._tdl_job_save_doc (mqs, parent, rider, filename='QR_solving')



#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

   print '\n** Start of standalone test of: QR_solving.py:\n' 

   ns = NodeScope()

   rider = QRU.create_rider()             # CollatedHelpRecord object
   if 1:
      QR_solving(ns, 'test')
      if 1:
         print rider.format()
            
   print '\n** End of standalone test of: QR_solving.py:\n' 

#=====================================================================================





