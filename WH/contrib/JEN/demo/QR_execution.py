"""
QuickRef module: QR_execution.py:

MeqTree execution issues (Request, Result etc)

This module may be called from the module QuickRef.py.
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

# file: ../JEN/demo/QR_execution.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 11 jun 2008: creation (from QR-template.py)
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

import QuickRefUtil as QRU
import EasyTwig as ET

# import math
# import random
import numpy


#******************************************************************************** 
# TDLCompileMenu (included in QuickRef menu):
#********************************************************************************


TDLCompileMenu("QR_execution topics:",
               TDLOption('opt_alltopics',"override: include all topics",True),
               TDLMenu("request",
                       TDLOption('opt_request_twig',"input twig (lhs of condeq)",
                                 ET.twig_names(), more=str),
                       TDLMenu("request_xxx",
                               TDLOption('opt_request_xxx_a',"option a",
                                         range(3), more=int),
                               TDLOption('opt_request_xxx_b',"option b",
                                         ['the','rain','in','Spain'], more=str),
                               toggle='opt_request_xxx'),
                       toggle='opt_request'),

               TDLMenu("help",
                       TDLOption('opt_helpnode_twig',"help on EasyTwig.twig()", False),
                       toggle='opt_helpnodes'),

               toggle='opt_QR_execution')



#********************************************************************************
# Top-level function, called from QuickRef.py:
#********************************************************************************


def QR_execution (ns, path, rider):
   """
   ...
   """
   rr = QRU.on_entry(QR_execution, path, rider)
 
   cc = []
   if opt_alltopics or opt_request:
      cc.append(request (ns, rr.path, rider))

   if opt_helpnodes:
      cc.append(make_helpnodes (ns, rr.path, rider))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)



#********************************************************************************
# 2nd tier: Functions called from the top function above:
#********************************************************************************

def make_helpnodes (ns, path, rider):
   """
   It is possible to define nodes that have no other function than to carry
   a help-text. The latter may be consulted in the quickref_help field in the
   state record of this node (a bookmark is generated automatically). It is
   also added to the subset of documentation that is accumulated by the rider.
   """
   rr = QRU.on_entry(make_helpnodes, path, rider)
   
   cc = []
   if opt_alltopics or opt_helpnode_twig:
      cc.append(QRU.helpnode (ns, rr.path, rider, name='EasyTwig_twig',
                             help=ET.twig.__doc__, trace=False))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)


#--------------------------------------------------------------------------------

def request (ns, path, rider):
   """
   .....
   """
   rr = QRU.on_entry(request, path, rider)
   cc = []
   if opt_alltopics or opt_request_domain:
      cc.append(request_domain (ns, rr.path, rider))
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)




#********************************************************************************
#********************************************************************************
#********************************************************************************
# 3rd tier: Functions called from functions at the 2nd tier above
#********************************************************************************
#********************************************************************************


#================================================================================
# request_... 
#================================================================================

def request_domain (ns, path, rider):
   """
   ...
   """
   rr = QRU.on_entry(request_domain, path, rider)
   cc = []
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)











#================================================================================
#================================================================================
#================================================================================
#================================================================================
# It is possible to define a standalone forest (i.e. not part of QuickRef.py) of
# this QR_module. Just load it into the browser, and compile/execute it.
#================================================================================

def _define_forest (ns, **kwargs):
   """Define a standalone forest for standalone use of this QR module"""

   global rider                                 # global because it is used in tdl_jobs
   rider = QRU.create_rider()                   # the rider is a CollatedHelpRecord object
   rootnodename = 'QR_execution'                 # The name of the node to be executed...
   path = rootnodename                          # Root of the path-string
   QRU.bundle (ns, path, rider,
              nodes=[QR_execution(ns, path, rider)],
              help=__doc__)

   # Finished:
   return True


#--------------------------------------------------------------------------------

# A 'universal TDLRuntimeMenu is defined in QuickRefUtil.py (QRU):

TDLRuntimeMenu(":")
TDLRuntimeMenu("QuickRef runtime options:", QRU)
TDLRuntimeMenu(":")

# For the TDLCompileMenu, see the top of this module


#--------------------------------------------------------------------------------
# Functions that execute the demo tree of this module with different requests.
# Many such functions are defined in QuickRefUtil.py (QRU).
# Make a selection that is suitable for this particular QR module.
#--------------------------------------------------------------------------------

def _tdl_job_execute_1D (mqs, parent):
   return QRU._tdl_job_execute_1D (mqs, parent, rootnode='QR_execution')

def _tdl_job_execute_2D (mqs, parent):
   return QRU._tdl_job_execute_2D (mqs, parent, rootnode='QR_execution')

def _tdl_job_execute_3D (mqs, parent):
   return QRU._tdl_job_execute_3D (mqs, parent, rootnode='QR_execution')

def _tdl_job_execute_4D (mqs, parent):
   return QRU._tdl_job_execute_4D (mqs, parent, rootnode='QR_execution')

def _tdl_job_execute_sequence (mqs, parent):
   return QRU._tdl_job_execute_sequence (mqs, parent, rootnode='QR_execution')

#--------------------------------------------------------------------------------
# Some functions to dispose of the specified subset of the documentation:
#--------------------------------------------------------------------------------

def _tdl_job_m (mqs, parent):
   """Dummy tdl job that acts as separator in the TDL exec menu.""" 
   return QRU._tdl_job_m (mqs, parent)

def _tdl_job_print_doc (mqs, parent):
   """Print the specified subset of the help doc on the screen"""
   return QRU._tdl_job_print_doc (mqs, parent, rider, header='QR_execution')

def _tdl_job_print_hardcopy (mqs, parent):
   """Print a hardcopy of the specified subset of the help doc on the printer.
   NB: The printer may be customized with the runtime options."""
   return QRU._tdl_job_print_hardcopy (mqs, parent, rider, header='QR_execution')

def _tdl_job_show_doc (mqs, parent):
   """Show the specified subset of the help doc in a popup"""
   return QRU._tdl_job_show_doc (mqs, parent, rider, header='QR_execution')

def _tdl_job_save_doc (mqs, parent):
   """Save the specified subset of the help doc in a file"""
   return QRU._tdl_job_save_doc (mqs, parent, rider, filename='QR_execution')



#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

   print '\n** Start of standalone test of: QR_execution.py:\n' 

   ns = NodeScope()

   rider = QRU.create_rider()             # CollatedHelpRecord object
   if 1:
      QR_execution(ns, 'test', rider=rider)
      if 1:
         print rider.format()
            
   print '\n** End of standalone test of: QR_execution.py:\n' 

#=====================================================================================




