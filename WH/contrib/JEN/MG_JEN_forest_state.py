script_name = 'MG_JEN_forest_state.py'

# Short description:
# Some functions to deal with the forest state record

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 22 aug 2005: creation

# Copyright: The MeqTree Foundation 


# Standard preamble
from Timba.TDL import *
from Timba.Meq import meq

from numarray import *
from copy import deepcopy
from string import *

import MG_JEN_template



#================================================================================
# Required functions:
#================================================================================

#--------------------------------------------------------------------------------
# Forest definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.

def _define_forest (ns):

   # Parameters:
   a = ns.a << Meq.Parm(array([[1,0.2],[-0.3,0.1]]))
   b = ns.b << Meq.Parm(array([[1,-0.2],[0.3,0.1]]))
   sum = ns.sum << Meq.Add (a, b)

   # Make single bookmarks:
   bm = bookmark (a)
   bm = bookmark (b)
 
   # Make a named page with views of diferent nodes:
   page_name = 'nodes'
   bookmark (a, page=page_name)
   bookmark (b, page=page_name)
   bookmark (sum, page=page_name)
 
   # Make a named page with multiple views of the same node:
   page_name = 'sum'
   bookmark (sum, page=page_name)
   bookmark (sum, page=page_name, viewer='ParmFiddler')
   bookmark (sum, page=page_name, viewer='Record Browser')
   bookmark (sum, page=page_name, viewer='Executor')

   # Append items to the forest state record:
   for i in [1,2]:
     rr = record(i=i, a=4, b=True)
     trace(i, 'a', [1,2], (3,4), x=False, rr=rr)
     error(i, 'b', [1,2], (3,4))
     warning(x=False, rr=rr)
     history(i)

   return MG_JEN_template.on_exit (ns, sum)     # recommended
   
   


#--------------------------------------------------------------------------------
# Test routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.

def _test_forest (mqs, parent):
   return MG_JEN_template.execute_forest (mqs, parent)

#--------------------------------------------------------------------------------
# Test routine to check the tree for consistency, in the absence of a browser

if __name__ == '__main__':
   MG_JEN_template.execute_without_mqs (script_name)

   


#================================================================================
# Importable function(s): The essence of a MeqGraft script.
# To be imported into user scripts (see _def_forest() below) 
#================================================================================


def init (script='<MG_JEN_xyz.py>', mode='MeqGraft'):

   # Reset the forest history record (retained otherwise...?)	 
   Settings.forest_state.forest_history = record()

   # Reset the bookmarks (if not, the old ones are retained) 
   Settings.forest_state.bookmarks = []
     
   # The default name for the .meqforest save file:
   s1 = split(script,'.')
   if isinstance(s1, (list, tuple)): s1 = s1[0]
   Settings.forest_state.savefile = s1

   if mode == 'MeqGraft':
      # Cache all node results:
      Settings.forest_state.cache_policy = 100
      # Orphan nodes should be retained:
      Settings.orphans_are_roots = True
   
 
   # Some stuff related to MS (kludge!):
   if False:
      selection = record(channel_start_index=10,
			 channel_end_index=50)
      inputrec = record(ms_name='D1.MS',
			data_column_name='DATA',
			selection=selection,
			tile_size=1)
      outputrec = record(predict_column='MODEL_DATA')
      Settings.forest_state.stream = record(input=inputrec, output=outputrec)
	
   return 

#--------------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...
# NB: Only in this particular script this is done AFTER the function definition

init(script_name)

#------------------------------------------------------------------------------- 
# Save the forest to a binary file

def save (mqs, filename=False):
   if not isinstance(filename, str):
      filename = Settings.forest_state.savefile+'.meqforest'
   mqs.meq('Save.Forest',record(file_name=filename));
   return filename



#------------------------------------------------------------------------------- 
# Create a bookmark:


def bookmark (node=0, name=0, udi=0, viewer='Result Plotter',
              page=0, save=True, clear=0, trace=0):
  if clear: Settings.forest_state.bookmarks = [] 
  if isinstance(node, int): return T                     # e.g. clear only

  bm = record(viewer=viewer, publish=True)
  bm.udi = '/node/'+node.name
  if isinstance(udi, str):  bm.udi = bm.udi+'/'+udi                 

  # The name in the bookmark menu:
  bm.name = node.name                                    # automatic
  if isinstance(name, str): bm.name = name;              # override
  if trace: print '\n** JEN_bookmark:',bm,'\n'

  # If a bookpage is specified, do not make a separate bookmark (save),
  # but add it to the named page:

  if isinstance(page, str):
    # Add the bookmark (bm) to the named page
    bookpage (bm, name=page, trace=trace)
  elif save:
    # Save the bookmark in the forest_state record
    Settings.forest_state.setdefault('bookmarks',[]).append(bm)

  return bm


#----------------------------------------------------------------------
# Access/display/clear the bookmarks:

def bookmarks (clear=0, trace=0):
  if clear: Settings.forest_state.bookmarks = [] 
  Settings.forest_state.setdefault('bookmarks',[])
  bms = Settings.forest_state.bookmarks
  # if trace: JEN_display(bms,'bms')
  return bms


#----------------------------------------------------------------------
# Add the given bookmark to the named page, and reconfigure it

def bookpage (bm={}, name='page', trace=0):
  # if trace: print '\n** MG_JEN_bookmark.bookpage(',bm,')'
  Settings.forest_state.setdefault('bookmarks',[])
  bms = Settings.forest_state.bookmarks

  # Check whether the specified page already exists:
  found = 0
  # bmc = record(bm.copy())
  bmc = deepcopy(bm)
  for i in range(len(bms)):
    if bms[i].has_key('page'):
      if bms[i].name == name:
        found = 1                                # used below

        # Automatic placement of the panel:
        n = len(bms[i].page)                     # current length
        if n==0: bmc.pos = [0,0]                 # superfluous

        # 1st col:
        if n==1: bmc.pos = [1,0]

        # 2nd col:
        if n==2: bmc.pos = [0,1]
        if n==3: bmc.pos = [1,1]

        # 3rd row:
        if n==4: bmc.pos = [2,0]
        if n==5: bmc.pos = [2,1]

        # 3rd col:
        if n==6: bmc.pos = [0,2]
        if n==7: bmc.pos = [1,2]
        if n==8: bmc.pos = [2,2]

        # 4th row:
        if n==9: bmc.pos = [3,0]
        if n==10: bmc.pos = [3,1]
        if n==11: bmc.pos = [3,2]

        # 4th col:
        if n==12: bmc.pos = [0,3]
        if n==13: bmc.pos = [1,3]
        if n==14: bmc.pos = [2,3]
        if n==15: bmc.pos = [3,3]


        bms[i].page.append(bmc)
        if trace: print '- appended (',n,') to existing page:',bmc

  # Make a new one, if not yet exists
  if not found:
    bmc.pos = [0,0]
    if trace: print '- created new bookpage:',bmc
    bms.append(record(name=name, page=[bmc]))
      
  Settings.forest_state.bookmarks = bms
  return bms


#---------------------------------------------------------------------------
# Add the given named (kwitem) and unnamed (item) items to the forest_state

def trace (*item, **kwitem):
  field = '_trace'
  return append (field, item, kwitem)

def history (*item, **kwitem):
  field = '_history'
  return append (field, item, kwitem)

def error (*item, **kwitem):
  field = '_ERROR'
  return append (field, item, kwitem)

def warning (*item, **kwitem):
  field = '_WARNING'
  return append (field, item, kwitem)

def append (field, item, kwitem):
  Settings.forest_state.setdefault(field,record())
  rr = Settings.forest_state[field]
  key = str(len(rr))
  kwitem = record(kwitem)
  if len(item)>0: kwitem['unnamed'] = item
  rr[key] = kwitem
  Settings.forest_state[field] = rr
  return rr

#****************************************************************************






