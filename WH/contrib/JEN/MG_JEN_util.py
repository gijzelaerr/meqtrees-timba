script_name = 'MG_JEN_util.py'

# Short description:
#   A collection of useful utility functions 

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 22 aug 2005: creation

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

# import MG_JEN_twig
# import MG_JEN_autoper

from numarray import *
# from string import *
# from copy import deepcopy



#================================================================================
# Required functions:
#================================================================================


#--------------------------------------------------------------------------------
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.

def _define_forest (ns):

   # Generate a list (cc) of one or more node bundles (bb):
   cc = []

   rr = {}
   history (rr, 'item1', 'item2', 4, 5, show=True, trace=1)
   history (rr, show=True, trace=1)

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
   MG_JEN_template.execute_without_mqs()









#================================================================================
# Importable function(s): The essence of a MeqGraft (MG) script.
# To be imported into user scripts. 
#================================================================================

 
#--------------------------------------------------------------------------------
# Deal with input arguments (pp):

def inarg (pp={}, _funcall='<funcall>', _help={}, _prompt={}, **default):

    # Create missing fields in pp with the default values given in **default:
    for key in default.keys():
        if not pp.has_key(key): pp[key] = default[key]

    # Identifying info:
    pp['_funcall'] = _funcall
    
    # Eventually, this record may evolve into a input GUI:
    # NB: This field appears to be dropped in pp = record(pp)....?
    # print '_help =',_help
    if len(_help) > 0: pp['_help'] = _help
    if len(_prompt) > 0: pp['_prompt'] = _prompt

    # Make sure of some default fields:
    if not pp.has_key('trace'):
        pp['trace'] = 0
        if pp.has_key('_help'): pp['_help']['trace'] = 'if >0, trace execution'

    if pp['trace']: display(pp, 'pp', txt='exit of inarg()')
    return pp

#-----------------------------------------------------------------------------------------
# use: if no arguments, return inarg_noexec(pp)
# NB: After record(inarg()), _help etc have disappeared.....!

def inarg_noexec (pp={}, txt='util.inarg_noexec(pp)', trace=0):
    if trace: display(pp, 'pp', txt=txt)
    return pp



#--------------------------------------------------------------------------------
# Append an log/error/warning message to the given dict/record

def history (rr=0, *item, **pp):
    
    # Deal with input arguments (pp):
    pp = record(inarg (pp, 'MG_JEN_util.history(ns, *item, **pp)',
                        _help=dict(error='if True, an error has occured',
                                   warning='if True, issue a warning',
                                   show='if True, show the accumulated history',
                                   hkey='field-name in rr',
                                   htype='if record, fill a record',
                                   level='indentation level'),
                        error=False, warning=False, show=False,
                        level=1, hkey='_history', htype='dict')) 
    if isinstance(rr, int): return inarg_noexec(pp, trace=pp.trace)
    
    print '*item =',type(item),len(item),item
    print 'str(item) =',str(item)
    return
    
    indent = pp.level*'..'
    if not isinstance(pp.hkey, str): pp.hkey = '_history'
    s1 = '** '+pp.hkey+':'

    if not rr.has_key(pp.hkey):
        if pp.htype=='record':
            rr[pp.hkey] = record(log=record(), ERROR=record(), WARNING=record())
        else:
            rr[pp.hkey] = dict(log={}, ERROR={}, WARNING={})

    if isinstance(item, str):
        s = indent+str(item)
        if trace: print s1,s
        n = len(rr[pp.hkey]['log'])
        rr[hkey]['log'][n] = s

    if isinstance(pp.error, str):
        s2 = ' ** ERROR ** '
        s = indent+str(pp.error)
        n = len(rr[pp.hkey]['ERROR'])
        print s1,s2,s
        rr[hkey]['ERROR'][n] = s
        n = len(rr[pp.hkey]['log'])
        rr[hkey]['log'][n] = s+s2

    if isinstance(pp.warning, str):
        s2 = ' ** WARNING ** '
        s = indent+str(pp.warning)
        n = len(rr[pp.hkey]['WARNING'])
        print s1,s2,s
        rr[hkey]['WARNING'][n] = s
        n = len(rr[pp.hkey]['log'])
        rr[pp.hkey]['log'][n] = s+s2

    if pp.show:
        display (rr[pp.hkey], pp.hkey, pp.hkey)
    return rr



#--------------------------------------------------------------------------------
# Display the contents of a given class

def display_class (klass, txt='<txt>', trace=1):
    print '\n***** Display of class(',txt,'):'
    print '** - klass.__class__ ->',klass.__class__
    rr = dir(klass)
    for attr in rr:
        v = klass[attr]
        print '** - ',attr,':',type(v),':',v
        v = eval('klass.'+attr)
        print '** - ',attr,':',type(v),':',v
    print '***** End of class\n'
    

#--------------------------------------------------------------------------------
# Display any Python object/variable (v):

def display (v, name='<name>', txt='', full=0, indent=0):
    if indent==0: print '\n** display of Python object:',name,': (',txt,'):'
    print '**',indent*'.',name,':',
    
    if isinstance(v, (str, list, tuple, dict, record)):
        # sizeable types (otherwise, len(v) gives an error):
        vlen = len(v)
        slen = '['+str(vlen)+']'

        if isinstance(v, str):
            print 'str',slen,
            print '=',v
      
        elif isinstance(v, list):
            print 'list',slen,
            separate = False
            types = {}
            for i in range(vlen):
                stype = str(type(v[i]))
                types[stype] = 1
                s1 = stype.split(' ')
                if s1[0] == '<class': separate = True
                if isinstance(v[i], (dict, record)): separate = True
            if len(types) > 1: separate = True

            if separate:
                print ':'
                for i in range(vlen): display (v[i], '['+str(i)+']', indent=indent+2)
            elif vlen == 1:
                print '=',[v[0]]
            elif vlen < 5:
                print '=',v
            else:
                print '=',[v[0],'...',v[vlen-1]]

        elif isinstance(v, tuple):
            print 'tuple',slen,
            print '=',v
          
        elif isinstance(v, (dict, record)):
            if isinstance(v, record):
                print 'record',slen,':'
            elif isinstance(v, dict):
                print 'dict',slen,':'
            keys = v.keys()
            n = len(keys)
            types = {}
            for key in keys: types[str(type(v[key]))] = 1
            if len(types) > 1:
                for key in v.keys(): display (v[key], key, indent=indent+2)
            elif n < 10:
                for key in v.keys(): display (v[key], key, indent=indent+2)
            elif full:
                for key in v.keys(): display (v[key], key, indent=indent+2)
            else:
                for key in [keys[0]]: display (v[key], key, indent=indent+2)
                if n > 20:
                    print '**',(indent+2)*' ','.... (',n-2,'more fields of the same type )'
                else:
                    print '**',(indent+2)*' ','.... ( skipped keys:',keys[1:n-1],')'
                for key in [keys[n-1]]: display (v[key], key, full=full, indent=indent+2) 
        

        else: 
            print type(v),'=',v

    else: 
        # All other types:
        print type(v),'=',v

    if indent == 0: print


#-----------------------------------------------------------------------

def get_initrec (node, trace=0):
    initrec = node.initrec()
    if trace: print '\n** JEN_get_initrec(',node.name,'):',initrec,'\n'
    return initrec

#-----------------------------------------------------------------------

def get_dims (node, trace=0):
    initrec = JEN_get_initrec (node)
    if not isinstance(initrec, record):
        dims = [-1]
    elif initrec.has_key('dims'):
        dims = initrec.dims
    elif node.classname == 'MeqSpigot':
        dims = [2,2]
    elif node.classname == 'MeqParm':
        dims = [1]
    elif node.classname == 'MeqConstant':
        dims = list(initrec.value.shape);
    elif node.classname == 'MeqComposer':
        dims = [len(node.children)];
    elif node.classname == 'MeqSelector':
        dims = [1]
        # if initrec.has_key('multi') and initrec.multi:
        if initrec.has_key('index'):
            dims = [len(initrec.index)];
    else:
        dims = [-1]
    if trace: print '\n** JEN_get_dims(',node.name,'): ->',dims,'\n'
    return dims

#------------------------------------------------------------------
# Extract kwquals and quals from lists of nodes

def kwquals (cc=[], trace=0):
    if isinstance(cc, tuple): cc = list(cc)
    if not isinstance(cc, list): cc = [cc]
    kwquals = {}
    for i in range(len(cc)):
       kwquals.update(cc[i].kwquals)
       if trace: print '-',i,cc[i],': kwquals =',kwquals
    return kwquals

def quals (cc=[], trace=0):
    if isinstance(cc, tuple): cc = list(cc)
    if not isinstance(cc, list): cc = [cc]
    quals = []
    for i in range(len(cc)):
       quals.extend(list(cc[i].quals))
       if trace: print '-',i,cc[i],': quals =',quals
    return JEN_unique(quals)

#------------------------------------------------------------------
# Make sure that the elements of the list cc are unique 

def unique (cc=[], trace=0):
    if not isinstance(cc, list): return cc
    bb = []
    for c in cc:
        if not bb.__contains__(c): bb.append(c)
    if trace: print '** JEN_unique(',cc,') -> ',bb
    return bb




#********************************************************************************




