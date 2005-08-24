script_name = 'MG_JEN_visualise.py'

# Short description:
#   Some visualisation subtrees

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation

# Copyright: The MeqTree Foundation 

#================================================================================
# How to use this template:
# - Copy it to a suitably named script file (e.g. MG_JEN_xyz.py)
# - Fill in the correct script_name at the top
# - Fill in the author and the short description
# - Enable the MG_JEN_template. calls in the required functions
# - Replace the importable functions with specific ones
# - Make the specific _define_forest() function


#================================================================================
# Import of Python modules:

from Timba.TDL import *
from Timba.Meq import meq

import MG_JEN_template 
import MG_JEN_forest_state
# import MG_JEN_util

import MG_JEN_twig
# import MG_JEN_autoper

from numarray import *
# from string import *
from copy import deepcopy



#================================================================================
# Required functions:
#================================================================================


#--------------------------------------------------------------------------------
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.

def _define_forest (ns):

   # Generate a list (cc) of one or more node bundles (bb):
   cc = []

   # Make a 'cloud' of nodes scattered (stddev) around mean:
   nodes = MG_JEN_twig.cloud (ns, n=3, name='pnt', qual='auto', stddev=1, mean=10, complex=True)
 
   nsub = ns.Subscope('sub1')
   dc = dcoll(ns, nodes, scope='scope1', tag='tag1', errorbars=True)
   cc.append(dc['dcoll'])
 
   nsub = ns.Subscope('sub2')
   dc = dcoll(nsub, nodes, type='spectra') 
   cc.append(dc['dcoll'])

   # Finished: 
   return MG_JEN_template.on_exit (ns, cc)



#--------------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(script_name)


#--------------------------------------------------------------------------------
# Tree execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.

def _test_forest (mqs, parent):
   return MG_JEN_template.execute_forest (mqs, parent)


#--------------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
   MG_JEN_template.execute_without_mqs(script_name)









#================================================================================
# Importable function(s): The essence of a MeqGraft (MG) script.
# To be imported into user scripts. 
#================================================================================


def dcoll (ns, node=[], **pp):
   """visualises the given node(s) and return a dcoll dict"""

   # Supply default arguments:
   pp.setdefault('scope', '<scope>')    # 'scope (e.g. rawdata)'
   pp.setdefault('tag', '<tag>')        # plot tag (e.g. allcorrs)
   pp.setdefault('title',False )        # plot title
   pp.setdefault('insert', False)       # if node given, insert dconc node
   pp.setdefault('xlabel', '<xlabel>')  # x-axis label
   pp.setdefault('ylabel', '<ylabel>')  # y-axis label
   pp.setdefault('color', 'red')        # plot color
   pp.setdefault('style','dot' )        # plot style
   pp.setdefault('size', 10)            # plot size
   pp.setdefault('type', 'realvsimag')  # plot type (realvsimag or spectra)
   pp.setdefault('errorbars', False)    # if True, plot stddev as crosses around mean
   pp.setdefault('bookmark', False)     # name of dcoll bookmark (False=none)
   pp.setdefault('bookpage', False)     # name of bookpage to be used (False=none)
   pp = record(pp)
   
   
   # Initialise the output dict:
   dcoll = dict(stripped=[], mean=[], stddev=[], input=pp, attrib=None,
                dcoll_mean=None, dcoll_stddev=None, dcoll=None)
   
   # Make sure that the input is a list:
   if not isinstance(node, (list, tuple)): node = [node]
   
   # Make the visualisation chains per node:
   for i in range(len(node)):
      stripped = ns << Meq.Stripper (node[i])
      dcoll['stripped'].append (stripped)
      if pp.type == 'realvsimag':
         dcoll['mean'].append (ns << Meq.Mean(stripped))
         if pp.errorbars:
            dcoll['stddev'].append (ns << Meq.StdDev(stripped))
            

   # Make dataCollection node(s):
   # Initialise the plot attribute record (changed below):
   scope_tag = 'dcoll_'+str(pp.scope)+'_'+str(pp.tag)
   if not isinstance(pp.title, str): pp.title = scope_tag
   attrib = record(plot=record(), tag=pp.tag)
   if pp.type == 'spectra':
      attrib['plot'] = record(type=pp.type, title=pp.title,
                              spectrum_color='hippo',
                              x_axis=pp.xlabel, y_axis=pp.ylabel)
      dcoll['dcoll'] = ns[scope_tag] << Meq.DataCollect(children=dcoll['stripped'],
                                                        top_label=hiid('visu'),
                                                        attrib=attrib)

   else:
      # Assume pp.type == 'realvsimag'
      attrib['plot'] = record(type=pp.type, title=pp.title,
                              color=pp.color, symbol='circle', symbol_size=pp.size,
                              mean_circle=1, mean_circle_color=pp.color,
                              mean_circle_style='DashLine', mean_arrow=1)
    
    
      if not pp.errorbars:
         # Indicate just the mean values of the child results:
         dcoll['dcoll'] = ns[scope_tag] << Meq.DataCollect(children=dcoll['mean'],
                                                           top_label=hiid('visu'),
                                                           attrib=attrib)
      else:
         # Indicate the stddev of the child results with 'error bars':

         # Make a separate dcoll for the means:
         attr = deepcopy(attrib)
         if not isinstance(attr.tag, list): attr.tag = [attr.tag]
         attr.tag.append('Mean')
         dc_mean = ns[scope_tag+'_mean'] << Meq.DataCollect(children=dcoll['mean'],
                                                            top_label=hiid('visu'),
                                                            attrib=attr)
         dcoll['dcoll_mean'] = dc_mean
         
         # Make a separate dcoll for the stddevs:
         attr = deepcopy(attrib)
         if not isinstance(attr.tag, list): attr.tag = [attr.tag]
         attr.tag.append('StdDev')
         dc_stddev = ns[scope_tag+'_stddev'] << Meq.DataCollect(children=dcoll['stddev'],
                                                                top_label=hiid('visu'),
                                                                attrib=attr)
         dcoll['dcoll_stddev'] = dc_stddev
         
         # Combine the mean and stddev dcolls:
         attr = deepcopy(attrib)
         attr.plot.stddev_circle=1
         attr.plot.stddev_circle_color=pp.color
         attr.plot.stddev_circle_style='DotLine'
         attr.plot.value_tag = 'Mean'
         attr.plot.error_tag = 'StdDev'
         dcoll['dcoll'] = ns[scope_tag] << Meq.DataCollect(children=[dc_mean, dc_stddev],
                                                           top_label=hiid('visu'),
                                                           attrib=attr)

   # Attach the attribute record to the output record, for later use:
   dcoll['attrib'] = attrib
   dcoll['tag'] = dcoll['attrib']['tag']            # used by JEN_dconc() below
   
   # Optionally, make a bookmark for the dconc node:
   if isinstance(pp.bookpage, str):
      bm = MG_JEN_forest_state.bookmark (dconc['dcoll'], page=pp.bookpage)
   elif isinstance(pp.bookmark, str):
      bm = MG_JEN_forest_state.bookmark (dconc['dcoll'], pp.bookmark)
      
   # Progress message:
   # if pp.trace:
      # JEN_display_subtree (dcoll['dcoll'], 'dcoll', full=1)
      # JEN_display(dcoll, 'dcoll', 'after JEN_dcoll()')

   # If an insert-node is specified, make the dconc node a step-child of a
   # MeqSelector node just before it, to issue requests:
   if not isinstance(pp.insert, bool):
      output = ns[scope_tag+'_branch'] << Meq.Selector(insert, step_children=dcoll['dcoll'])
      return output

   return dcoll



#=========================================================================================
# Concatenate the given dcolls (dicts, see above) into a dconc node
#=========================================================================================

def JEN_dconc (ns, dcoll, **pp):

   # Supply default arguments:
   pp.setdefault('scope', '<scope>')    # 'scope (e.g. rawdata)'
   pp.setdefault('tag', '<tag>')        # plot tag (e.g. allcorrs)
   pp.setdefault('title',False )        # plot title
   pp.setdefault('insert', False)       # if node given, insert dconc node
   pp.setdefault('xlabel', '<xlabel>')  # x-axis label
   pp.setdefault('ylabel', '<ylabel>')  # y-axis label
   pp.setdefault('bookmark', False)     # name of dcoll bookmark (False=none)
   pp.setdefault('bookpage', False)     # name of bookpage to be used (False=none)
   pp = record(pp)


   # Initialise the output dict:
   dconc = dict(input=pp, cc=[], attrib=None, dcoll=None)

   scope_tag = 'dconc_'+str(pp.scope)+'_'+str(pp.tag)
   if not isinstance(pp.title, str): pp.title = scope_tag
   
   attrib = record(plot=record(), tag=['dconc'])
   attrib.plot.title = pp.title
   
   # Collect the dcoll nodes in a list (cc):
   if not isinstance(dcoll, (list, tuple)): dcoll = [dcoll]
   for i in range(len(dcoll)):
      dconc['cc'].append(dcoll[i]['dcoll'])     # 
      attrib['tag'].append(dcoll[i]['tag'])     # concatenate the dcoll tags (unique?)
    
   # Make concatenations (dconc) node:
   dconc['dcoll'] = (ns[scope_tag] << Meq.DataCollect(children=dconc['cc'],
                                                      top_label=hiid('visu'),
                                                      attrib=attrib))

   # Optionally, make a bookmark for the dconc node:
   if isinstance(pp.bookpage, str):
      bm = MG_JEN_forest_state.bookmark (dconc['dcoll'], page=pp.bookpage)
   elif isinstance(pp.bookmark, str):
      bm = MG_JEN_forest_state.bookmark (dconc['dcoll'], pp.bookmark)


   # Progress message:
   # if pp.trace:
      # JEN_display_subtree (dconc['dcoll'], 'dconc', full=1)
      # JEN_display(dcoll, 'dconc', 'after JEN_dconc('+scope_tag,')')
    
   # If an insert-node is specified, make the dconc node a step-child of a
   # MeqSelector node just before it, to issue requests:
   if not isinstance(pp.insert, bool):
      output = ns[scope_tag+'_branch'] << Meq.Selector(insert, step_children=dconc['dcoll'])
      return output

   return dconc



#********************************************************************************




