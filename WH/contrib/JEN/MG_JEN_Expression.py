# MG_JEN_Expression.py

# Short description:
#   Demo and helper functions TDL_Expressions

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 22 jun 2006: creation

# Copyright: The MeqTree Foundation 


#********************************************************************************
#********************************************************************************
#**************** PART II: Preample and initialisation **************************
#********************************************************************************
#********************************************************************************

from Timba.TDL import *
from Timba.Meq import meq

MG = record(script_name='MG_JEN_Expression.py', last_changed = 'h22jun2006')

from random import *
from math import *
from numarray import *
# from string import *
from copy import deepcopy

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state

from Timba.Trees import TDL_Expression
from Timba.Trees import TDL_display


#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG['script_name'])






#********************************************************************************
#********************************************************************************
#**************** PART III: Required test/demo function *************************
#********************************************************************************
#********************************************************************************

# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.


def _define_forest (ns):
   """Definition of a MeqForest for demonstration/testing/experimentation
   of the subject of this MG script, and its importable functions"""

   # Perform some common functions, and return an empty list (cc=[]):
   cc = MG_JEN_exec.on_entry (ns, MG)

   Xbeam = WSRT_voltage_Xbeam_gaussian (ell=0.1)
   node = make_LMCompounder (ns, Xbeam, l=0.1, m=0.2, q='3c123')
   cc.append(node)
   node = make_Functional (ns, Xbeam, q='3c123')
   cc.append(node)

   # Ybeam = WSRT_voltage_Ybeam_gaussian (ell=0.1)


   ### cc.append(MG_JEN_exec.bundle(ns, bb, 'polclog_flux_3c286()'))

   # Finished: 
   return MG_JEN_exec.on_exit (ns, MG, cc)










#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************


def WSRT_voltage_Xbeam_gaussian (ell=0.1, plot=False, trace=False):
   """Xpol version of WSRT_voltage_beam_gaussian"""
   return WSRT_voltage_beam_gaussian (pol='X', ell=ell,
                                      plot=plot, trace=trace)

def WSRT_voltage_Ybeam_gaussian (ell=0.1, plot=False, trace=False):
   """Ypol version of WSRT_voltage_beam_gaussian"""
   return WSRT_voltage_beam_gaussian (pol='Y', ell=-ell,
                                      plot=plot, trace=trace)


def WSRT_voltage_beam_gaussian (pol='X', ell=0.1, plot=False, trace=False):
   """ Make an Expression object for a WSRT telescope voltage beam (gaussian)"""
   vbeam = TDL_Expression.Expression('{peak}*exp(-{Lterm}-{Mterm})', label='gauss'+pol+'beam',
                                     descr='WSRT '+pol+' voltage beam (gaussian)', unit=None)
   vbeam.parm ('peak', default=1.0, polc=[2,1], unit='Jy', help='peak voltage beam')
   Lterm = TDL_Expression.Expression('(([l]-{L0})*{_D}*(1+{_ell})/{lambda})**2', label='Lterm')
   Lterm.parm ('L0', default=0.0, unit='rad', help='pointing error in L-direction')
   vbeam.parm ('Lterm', default=Lterm)
   Mterm = TDL_Expression.Expression('(([m]-{M0})*{_D}*(1-{_ell})/{lambda})**2', label='Mterm')
   Mterm.parm ('M0', default=0.0, unit='rad', help='pointing error in M-direction')
   vbeam.parm ('Mterm', default=Mterm)
   vbeam.parm ('_D', default=25.0, unit='m', help='WSRT telescope diameter')
   vbeam.parm ('lambda', default=TDL_Expression.Expression('3e8/[f]', label='lambda',
                                                           descr='observing wavelength'), unit='m')
   vbeam.parm ('_ell', default=ell, help='Voltage beam elongation factor (1+ell)')

   # Finished:
   if trace: vbeam.expanded().display(full=True)
   if plot: vbeam.plot()
   return vbeam

#---------------------------------------------------------------------------------

def make_LMCompounder (ns, beam, l=0.1, m=0.2, q='3c123', trace=False):
   """Make a (l,m) MeqCompounder node of the given beam Expression""" 
   L = ns.L << l
   M = ns.M << m
   LM = ns.LM << Meq.Composer(L,M)
   node = beam.MeqCompounder(ns, qual=dict(q=q), extra_axes=LM,
                             common_axes=[hiid('l'),hiid('m')], trace=True)
   if trace:
      TDL_display.subtree(node, 'MeqCompounder', full=True, recurse=5)
   return node

#---------------------------------------------------------------------------------

def make_Functional (ns, beam, q='3c123', trace=False):
   """Make a MeqFunctional node of the given beam Expression""" 
   node = beam.MeqFunctional(ns, qual=dict(q=q), trace=trace)
   if trace:
      TDL_display.subtree(node, 'MeqFunctional', full=True, recurse=5)
   return node




#********************************************************************************
# Testing routines
# NB: this section should always be at the end of the script
#********************************************************************************


#-------------------------------------------------------------------------
# Meqforest execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.
# If not explicitly supplied, a default request will be used.

def _test_forest (mqs, parent):
  return MG_JEN_exec.meqforest (mqs, parent)
  # return MG_JEN_exec.meqforest (mqs, parent, nfreq=20, ntime=19, f1=0, f2=1, t1=0, t2=1, trace=False)
  # return MG_JEN_exec.meqforest (mqs, parent, nfreq=200, f1=1e6, f2=2e8, t1=-10, t2=10) 
  # return MG_JEN_exec.meqforest (mqs, parent, domain='lofar')



#-------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
    print '\n**',MG['script_name'],':\n'

    if 0:
        MG_JEN_exec.without_meqserver(MG['script_name'], callback=_define_forest)

    ns = NodeScope()

    if 1:
       Xbeam = WSRT_voltage_Xbeam_gaussian (ell=0.1, plot=False, trace=True)

    # MG_JEN_exec.display_subtree (rr, 'rr', full=1)
    print '\n** end of',MG['script_name'],'\n'

#********************************************************************************
#********************************************************************************




