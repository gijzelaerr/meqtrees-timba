# Expression.py
#
# Author: J.E.Noordam
# 
# Short description:
#   Contains a mathematical expression that can be turned into
#   a funklet, a MeqFunctional node, or a subtree.
#
# History:
#    - 29 apr 2007: creation, from TDL_Expression.py
#
# Remarks:
#
# Description:
#
#  -) Expression objects
#     -) e0 = Expression ("{A} + {ampl}*cos({phase}*[t])" [, label='<label>'])
#     -) Variables in square brackets[]: [t],[time],[f],[fGHz],[l],[m],[RA],  etc
#     -) Parameters in curly brackets{}.
#     -) The expression is supplied to the Expression constructor
#     -) Extra information about parameters is supplied via a function:
#         -) e0.parm('{A}', 34)                         numeric, default value is 34
#         -) e0.parm('{ampl}', e1)                      another Expression object
#         -) e0.parm('{phase}', polc=[2,3])             A polc-type Expression generated internally
#         -) e0.parm('{A}', f1)                         A Funklet object
#         -) e0.parm('{A}', node)                       A node (child of a MeqFunctional node)
#         -) e0.parm('{A}', image)                      A FITS image
#     -) The Expression object may be converted to:
#         -) a Funklet                                  with p0,p1,p2,... and x0,x1,...
#         -) a MeqParm node (init_funklet=Funklet)
#         -) a MeqFunctional node                       (parms AND vars are its children)      
#         -) a MeqCompounder node                       needs extra children
#         -) ...
#     -) Easy to build up complex expressions (MIM, beamshape)
#     -) Should be very useful for LSM




#***************************************************************************************
# Preamble
#***************************************************************************************

from Timba.Meq import meq
from Timba.TDL import *                         # needed for type Funklet....

import Meow

# from Timba.Contrib.JEN.Grunt import SimulParm
from Timba.Contrib.JEN.Grunt import display
# from Timba.Contrib.JEN.util import JEN_bookmarks

Settings.forest_state.cache_policy = 100

# import numarray                               # see numarray.rank()
from numarray import *
# import numarray.linear_algebra                # redefines numarray.rank....
# import random
# import pylab
from copy import deepcopy


from Timba.Contrib.MXM.TDL_Funklet import *   # needed for type Funklet.... 
# from Timba.Contrib.MXM import TDL_Funklet
# from Timba.Contrib.JEN.util import TDL_Leaf
from Timba.Contrib.JEN.util import JEN_parse


# Replacement for is_numeric(): if isinstance(x, NUMMERIC_TYPES):
NUMERIC_TYPES = (int, long, float, complex)


#***************************************************************************************
#***************************************************************************************

class Expression (Meow.Parameterization):

    def __init__(self, ns, name, expr,
                 descr=None, unit=None,
                 quals=[], kwquals={}):
        """Create the object with a mathematical expression (string)
        of the form:  {aa}*[t]+cos({b}*[f]).
        Variables are enclosed in square brackets: [t],[f],[m],...
        Parameters are enclosed in curly brackets: {aa}, {b}, ...
        Simple information about parameters (type, default value)
        may be supplied via keyword arguments pp. More detailed
        information may be supplied via the function .parm()."""

        Meow.Parameterization.__init__(self, ns, str(name),
                                       quals=quals, kwquals=kwquals)

        self._descr = descr                       # optional description
        self._unit = unit                         # unit of the result
        self._expression = deepcopy(expr)         # never modified
        self._expanded = deepcopy(expr)           # working version
        self._locked = False                      # if true, do not modify
        self._last_solvable_tags = None           # used by .solvable()

        # Default values for the variable-modification constants:
        self._varmod = dict(t0=0.0, f0=1.0)

        # For each parameter in self._expression, make an entry in self._item.
        # These entries may be modified with extra info by self.parm().
        self._item = dict()
        self._item_order = []
        self._find_items(self._expression)

        # Some placeholders:
        self._MeqNode = None
        self._Funklet = None
        self._Funklet_funktion = None
        self._Functional = None
        self._Functional_function = None
        self._Functional_childmap = []
        self._Compounder = None
        self._Compounder_common_axes = None
        self._testexpr = None

        # Finished:
        return None


    #----------------------------------------------------------------------------
    # Some access functions:
    #----------------------------------------------------------------------------

    def unit (self):
        """Return the (string) unit of the result of the Expression object"""
        if not isinstance(self._unit, str): return ''
        return self._unit

    def descr (self):
        """Return the brief description of this Expression object"""
        return str(self._descr)

    def expression (self):
        """Return its (mathematical) expression."""
        return self._expression

    def item_order (self):
        """Return the order of parameters in the input expression"""
        return self._item_order


    #----------------------------------------------------------------------------
    # Some display functions:
    #----------------------------------------------------------------------------

    def oneliner(self, full=True):
        """Return a one-line summary of the Expression"""
        ss = '** Expression ('+str(self.name)+'):  '
        if self._unit: ss += '('+str(self._unit)+') '
        if self._descr:
            ss += str(self._descr)
        elif full:
            s1 = str(self._expression)
            if len(s1)>50: s1 = s1[:50]+' ...' 
            ss += s1
        if self._locked:
            ss += '  (locked) '
        return ss

    #----------------------------------------------------------------

    def display(self, txt=None, full=False):
        """Display a summary of this object"""
        print '\n** Summary of: '+self.oneliner(),
        if txt: print '  (*** '+str(txt)+' ***)',
        print
        print '  * description: '+str(self._descr)
        print '  * expression: '+str(self._expression)
        print '  * items ('+str(len(self._item))+'):'
        self._adjust_item_order()
        for key in self.item_order():
            rr = self._item[key]
            print '    - '+str(key)+':  ('+str(rr['type'])+'):  '+str(rr['item']),
            if rr['type']=='var':
                print '  '+str(rr['var']),
            if rr.has_key('from'):
                print '  <- '+str(rr['from']),
            print
        if full:
            for key in self.item_order():
                print '    - '+str(key)+':  '+str(self._item[key])
        print '  * varmod: '+str(self._varmod)
        print '  * last_solvable_tags: '+str(self._last_solvable_tags)
        v = self._testeval()
        print '  * testexpr: '+str(self._testexpr)
        print '    - .testeval() ->  '+str(v)+'  ('+str(type(v))+')'

        nmax = 100
        if len(self._expanded)>nmax: print
        print '  * expanded: '+str(self._expanded)
        if len(self._expanded)>nmax: print

        if full:
            for itemtype in ['MeqNode']:
                print '    - .has_itemtype('+str(itemtype)+') -> '+str(self.has_itemtype(itemtype))
        if self._MeqNode:
            print '  * MeqNode = '+str(self._MeqNode)
        if self._Funklet:
            print '  * Funklet = '+str(self._Funklet)
            print '    - funktion = '+str(self._Funklet_funktion)
        if self._Functional:
            print '  * Functional = '+str(self._Functional)
            print '    - function = '+str(self._Functional_function)
            if True or full:
                for k,rr in enumerate(self._Functional_childmap):
                    print '    - '+str(rr)
        if self._Compounder:
            print '  * Compounder = '+str(self._Compounder)
            print '    - common_axes = '+str(self._Compounder_common_axes)
        print '**\n'
        return True
        
    #-------------------------------------------------------------------------

    def _adjust_item_order(self):
        """Helper function to order the various items in categories"""
        order = []
        for it in ['subexpr','parm','MeqParm','MeqNode','var','numeric']:
            for key in self._item_order:
                if self._item[key]['type']==it: order.append(key)
        for key in self._item_order:
            if not key in order: order.append(key)
        self._item_order = order
        return True
        
    #============================================================================
    # Functions dealing with items, i.e. {parms} and [vars]:
    #============================================================================

    def _find_items (self, expr=None, trace=False):
        """Find the parameters (enclosed in {}) in the given expression string,
        and add them to self._item, avoiding duplication. By default, the parm
        items are of type 'parm', which will be turned into Funklets or MeqParms
        when necessary. They may be re-specified as something else by means of
        the function .parm().
        Also find the vars (enclosed in []) in the expression, and add them to
        self._item. These may be re-specified with the function .var()."""

        order = JEN_parse.find_enclosed(expr, brackets='{}')
        if not isinstance(order,(list,tuple)):
            s = '** order is not a list, but: '+str(type(order))
            raise TypeError,s
        for key1 in order:
            key = '{'+key1+'}'
            if not self._item.has_key(key):
                default = 2.0
                self._item[key] = dict(type='parm', item=None, index=[0],
                                       unit=None, default=default)
                parm = Meow.Parm(value=default, tags=['Functional'],
                                 tiling=None, time_deg=0, freq_deg=0)    # **kw
                self._add_parm(key, parm, solvable=True) 
                self._item_order.append(key)

        # Do the same for the vars [] in expr
        self._find_vars(expr)
        return True

    #-------------------------------------------------------------------------

    def _transfer_items (self, other=None, trace=False):
        """Transfer the items from the given (other) Expression object,
        and add them to self._item.
        - If a var item [] already exists, ignore the one from other.
        - If a parm item {} already exists, raise an error.
        """
        for key in other.item_order():
            if self._item.has_key(key):
                if key[0]=='{':
                    s = 'item {} already defined: '+str(key)
                    raise ValueError, s
            else:
                self._item[key] = other._item[key]
                self._item_order.append(key)
        # Finished: 
        return True

    #-------------------------------------------------------------------------

    def has_itemtype (self, itemtype='MeqNode', expr=None):
        """Helper function to test whether the given expr has any 'items' {}
        of the specified itemtype (default='MeqNode'). * is all types."""
        cc = []
        if expr==None: expr = self._expanded
        for key in self._item.keys():
            if key in expr:
                if itemtype=='*' or self._item[key]['type']==itemtype:
                    cc.append(key)
        if len(cc)==0: return False
        return cc

    #----------------------------------------------------------------------------

    def parm (self, key, item=None, arg=None, polc=None,
              redefine=False, unlock=False, **pp):
        """Define an existing {key} parameter as a numeric value, an expression,
        a MeqParm or another MeqNode, etc"""

        # First some checks:
        if self._locked and not unlock:
            s = '** Expression is locked: can no longer be modified'
            raise ValueError, s
        if not self._item.has_key(key):
            s = '** parameter key not recognised: '+str(key)
            raise ValueError, s
        rr = self._item[key]

        # Unless specified explicitly, only allow redefinition of the
        # 'undefined' items, i.e. the ones with the default type 'parm'
        if not redefine:
            if not rr['type']=='parm':
                s = '** duplicate definition of parameter: '+str(key)
                raise ValueError, s

        # Some types require extra arguments:
        if not isinstance(pp, dict): pp = dict()

        # OK, go ahead:
        if item==None:
            # Assume item-type=='parm' (i.e. undefined).
            # Just supply a new (numeric!) default value
            if not pp.has_key('default'):
                raise ValueError,'** parm needs default=value'
            rr['default'] = float(pp['default'])

        elif item=='MeqParm':                            # ..... obsolete since 'parm' ....?
            if not pp.has_key('default'):
                if isinstance(arg, (int, long, float)):
                    pp['default'] = arg
                else:
                    raise ValueError,'** MeqParm needs a default value'
            rr['item'] = self.ns[key] << Meq.Parm(**pp)  # use Meow....
            rr['type'] = 'MeqNode'
            if isinstance(pp['default'], (int, long, float)):
                rr['default'] = float(pp['default'])

        elif isinstance(item, str):                      # assume sub-expr
            rr['item'] = item
            rr['type'] = 'subexpr'
            self._find_items(item)

        elif isinstance(item, (int, long, float, complex)):
            rr['item'] = item
            rr['type'] = 'numeric'

        elif is_node(item):
            rr['item'] = item
            rr['type'] = 'MeqNode'
            if item.classname=='MeqParm':
                rr['default'] = item.initrec()['init_funklet']['coeff']
            elif item.classname=='MeqConstant':          # ....?
                rr['value'] = item.initrec()['value']

        elif isinstance(item, Funklet):                  # ....obsolete....?
            rr['item'] = item
            rr['type'] = 'Funklet'
            # qnode << Meq.Parm(funklet=funklet,       # new MXM 28 June 2006
            #                       node_groups=['Parm'])

        elif isinstance(item, Expression):
            expr = item._expand()                        # ....??
            rr['item'] = expr
            rr['type'] = 'subexpr'
            rr['from'] = 'Expression: '+str(item.name)
            self._transfer_items(item)

        else:
            s = '** parameter type not recognised: '+str(type(item))
            raise TypeError, s

        # Finished:
        return True


    #============================================================================
    # Functions dealing with variables []:
    #============================================================================

    def var (self, key, xn=None, axis=None, unit=None, nodeclass=None):
        """Specify fields of the var-record in the item definition record.
        This is used for non-standard varaibles, i.e. other than the ones
        (like [t],[f] etc) that are recognised in _find_vars()"""

        if not key in self._item:
            s ='** variable not recognised: '+str(key)
            raise ValueError, s
        elif key in ['[t]','[f]','[l]','[m]']:
            s ='** standard variable cannot be modified: '+str(key)
            raise ValueError, s                   # <-- ??
        
        # Only replace the specified fields:
        rr = self._item[key]
        if isinstance(nodeclass, str):
            rr['var']['nodeclass'] = nodeclass    # default: 'MeqGrid'
        if isinstance(xn, str):
            rr['var']['funktion'] = xn            # e.g. 'x2' or 'x7'
        if isinstance(axis, str):
            rr['var']['axis'] = axis              # e.g. 'x' or 'lat'
        if isinstance(unit, str):
            rr['unit'] = unit                     # e.g. 'rad'
        return True

    #----------------------------------------------------------------------------

    def _find_vars (self, expr=None):
        """Find the variables (enclosed in []) in the given expression string,
        and add them to self._item, avoiding duplication"""
        vv = JEN_parse.find_enclosed(expr, brackets='[]')
        for key in vv:
            kk = key.split('^')                     # e.g. t^4
            key = '['+key+']'
            key0 = '['+kk[0]+']'                    # e.g. [t]
            
            if not self._item.has_key(key):
                rr = dict(type='var', item=None, index=[0],
                          unit=None, default=10.0)
                var = dict(nodeclass='MeqGrid', key0=key0,
                           axis=None, funktion=None)

                
                # Deal with some standard variables:
                if key=='[t]' or key=='[dt]':                
                    var['nodeclass'] = 'MeqTime' 
                    var['funktion'] = 'x0'          # used in Funklet
                    var['axis'] = 'time'    
                    rr['unit'] = 's'
                    if key=='[dt]':                 # relative time (t-t0)
                        t0 = self._varmod['t0']     
                        var['subtract'] = t0
                        var['funktion'] = '(x0-'+str(t0)+')'
                elif key=='[f]' or key=='[ff]':              
                    var['nodeclass'] = 'MeqFreq'  
                    var['funktion'] = 'x1'          # used in Funklet
                    var['axis'] = 'freq'    
                    rr['unit'] = 'Hz'
                    if key=='[ff]':                 # normalized freq (f/f0)
                        f0 = self._varmod['f0']     
                        var['divide'] = f0
                        var['funktion'] = '(x1/'+str(f0)+')'
                elif key=='[l]':                    # celestial l-coordinate
                    var['nodeclass'] = 'MeqGrid'   
                    var['funktion'] = 'x2'          # used in Funklet
                    var['axis'] = 'l'      
                    rr['unit'] = 'rad'
                elif key=='[m]':                    # celestial m-coordinate
                    var['nodeclass'] = 'MeqGrid'  
                    var['funktion'] = 'x3'          # used in Funklet
                    var['axis'] = 'm'        
                    rr['unit'] = 'rad'

                # Variables can be functions of the basic one
                elif len(kk)>1:                     # e.g. [t^4]
                    var['nodeclass'] = 'MeqPow'     # for MeqFunctional
                    var['power'] = int(kk[1])
                    rr['unit'] = str(self._item[key0]['unit'])+'^'+kk[1]
                    funktion = self._item[key0]['var']['funktion']       # e.g. [t]
                    funktion = '('+str(funktion)+'**'+kk[1]+')'          # e.g. ([t]**4)
                    var['funktion'] = funktion      # used in Funklet

                rr['var'] = var                     # attach the var definition record
                self._item[key] = rr                # attach the item definition record
                self._item_order.append(key)        # include the key
        # Finished
        return True

    #-------------------------------------------------------------------------------

    def _nodes2vars (self):
        """The reverse of _vars2nodes(). Just change the item-type of the
        items that represent variables [] from 'MeqNode' to 'var'."""
        for key in self.item_order():
            rr = self._item[key]                           # item definition record
            if rr.has_key('var'):                          # var definition record
                rr['type'] = 'var'                         # just change type to var
        return True

    #-------------------------------------------------------------------------------
    
    def _vars2nodes (self):
        """Change the item-type of the variables from 'var' to 'MeqNode',
        while creating MeqGrid nodes for them if necessary."""
        expr = self._expand()
        for key in self.item_order():
            rr = self._item[key]                           # item definition record
            if rr.has_key('var'):                          # var definition record
                if not rr['item']:                         # only if not yet defined
                    var = rr['var']
                    nodeclass = var['nodeclass']           # e.g. 'MeqTime'
                    key0 = var['key0']                     # e.g. [t]
                    axis = var['axis']                     # e.g. 'freq', or 'm'
                    qnode = self.ns[key]
                    if nodeclass=='MeqTime':
                        if var.has_key('subtract') and var['subtract']:
                            tnode = self.ns['[t]'] << Meq.Time()
                            qnode << Meq.Subtract(tnode,var['subtract'])
                        else:
                            qnode << Meq.Time()
                    elif nodeclass=='MeqFreq':
                        if var.has_key('divide') and var['divide']:
                            fnode = self.ns['[f]'] << Meq.Freq()
                            qnode << Meq.Divide(fnode,var['divide'])
                        else:
                            qnode << Meq.Freq()
                    elif nodeclass=='MeqGrid':
                        qnode << Meq.Grid(axis=axis)
                    elif nodeclass=='MeqPow':
                        node = self._item[key0]['item']    # e.g. MeqTime
                        power = var['power']               # e.g. 2
                        qnode << Meq.Pow(node,power)   

                    else:
                        s = 'nodeclass not recognised:'+str(nodeclass)
                        raise TypeError,s

                    rr['item'] = qnode                     # attach the node
                # Just change the item type:
                rr['type'] = 'MeqNode'
        # Finished:
        self._locked = True                                # no more modifications
        return True
 

    #================================================================================
    # Expansion and evaluation:
    #================================================================================

    def _expand (self, replace_numeric=True, trace=False):
        """Expand its expression by replacing the sub-expressions.
        If replace_numeric==True, also replace the numeric ones (for eval())."""
        expr = deepcopy(self._expression)
        repeat = True
        count = 0
        while repeat:
            count += 1
            repeat = False
            for key in self.item_order():
                rr = self._item[key]
                if rr['type']==None:
                    s = '** expand(): parameter not yet defined: '+str(key)
                    raise ValueError, s  
                elif rr['type']=='subexpr':
                    if key in expr:
                        subexpr = '('+rr['item']+')'
                        expr = expr.replace(key, subexpr)
                        if trace:
                            print '**',count,': replace:',key,' with:',subexpr
                        repeat = True
                elif replace_numeric and rr['type']=='numeric':
                    expr = expr.replace(key, '('+str(rr['item'])+')')
            # Guard against an infinite loop:
            if count>10:
                print '\n** current expr =',expr
                s = '** expand(): maximum count exceeded '+str(count)
                raise ValueError, s
        # Finished:    
        self._expanded = expr
        self._locked = True                              # no more modifications
        return expr

    #---------------------------------------------------------------------------

    def _testeval(self, trace=False):
        """Test-evaluation of its expression, in which all the non-numeric
        parameters have been replaced with their test-values. This is primarily
        a syntax check (brackets etc), but it may have other uses too"""
        expr = self._expand(replace_numeric=True)
        for key in self.item_order():
            if key in expr:
                replace = '('+str(self._item[key]['default'])+')'
                expr = expr.replace(key, replace)
                if trace:
                    print '** replace:',key,' with:',replace,' ->',expr
        # Finished:
        self._testexpr = expr
        v = eval(expr)
        return v
                                    

    #============================================================================
    # The Expression can be converted into various other objects:
    #============================================================================

    def MeqFunctional (self, show=False):
        """Turn the expression into a MeqFunctional node,
        i.e. an expression of its children."""

        self._vars2nodes()        
        qnode = self.ns['Expr_MeqFunctional']
        if not qnode.initialized():
            function = deepcopy(self._expanded)
            children = []
            nodenames = []
            child_map = []            
            k = -1
            for key in self.item_order():
                if key in self._expanded:                           # extra check...
                    rr = self._item[key]                            # item definition record
                    if rr['type']=='parm':                          # undefined item
                        rr['type'] = 'MeqNode'                      # turn into MeqParm node
                        rr['item'] = self._parm(key)                # Meow (Parameterization)

                    if rr['type']=='MeqNode':
                        k += 1                                      # increment
                        xk = 'x'+str(k)                             # x0, x1, x2, ..
                        function = function.replace(key, xk)
                        nodename = rr['item'].name
                        if not nodename in nodenames:               # once only
                            nodenames.append(nodename)
                            children.append(rr['item'])
                        child_num = nodenames.index(nodename)       # 0-based(!)
                        qq = record(child_num=child_num,
                                    index=rr['index'],              # usually: [0]
                                    nodename=nodename)
                        child_map.append(qq)

            qnode << Meq.Functional(children=children,
                                    function=function,
                                    child_map=child_map)
            self._Functional = qnode
            self._Functional_childmap = child_map
            self._Functional_function = function

        # Finished:
        self._last_solvable_tags = ['Functional']        # used by .solvable()
        self._locked = True                              # no more modifications
        if show: display.subtree(qnode)
        return qnode


    #--------------------------------------------------------------------------


    def MeqCompounder (self, extra_axes=None, common_axes=None, show=False):
        """Make a MeqCompounder node from the Expression. The extra_axes argument
        should be a MeqComposer that bundles the extra (coordinate) children,
        described by the common_axes argument (e.g. [hiid('l'),hiid('m')]."""                   

        qnode = self.ns['MeqCompounder']
        if not qnode.initialized():

            if extra_axes==None:
                # Kludge for convenient testing of the Compounder
                # Assume (l,m), and provide automatic L and M nodes
                # with some variation by using MeqFreq and MeqTime
                extra_axes = self.ns.LM << Meq.Composer(self.ns.L<<Meq.Freq(),
                                                        self.ns.M<<Meq.Time())
                common_axes = [hiid('l'),hiid('m')]

            # Make a 'single' node from the Expression, i.e.
            # either a MeqParm(Funklet), or a MeqFunctional:
            node = self.MeqNode()

            # Check whether there are extra axes defined for all variables
            # in the expression other than [t] and [f]:
            #    NB:   str(hiid('m')) -> 'M'   ............!
            if False:
                caxes = []
                for cax in common_axes:
                    caxes.append('['+str(cax)+']')
                for key in self.item_order():
                    if key[0]=='[' and key in self._expanded:
                        print key,caxes
                        if not key in ['[t]','[f]']:
                            pass
                    #if not key in caxes:
                    #    s = '** missing cax:',key
                    #    raise ValueError, s
                
            qnode << Meq.Compounder(children=[extra_axes, node],
                                    common_axes=common_axes)
            self._Compounder = qnode
            self._Compounder_common_axes = str(common_axes)

        # Finished
        self._locked = True                              # no more modifications
        if show: display.subtree(qnode)
        return qnode


    #============================================================================

    def Funklet (self, plot=False):
        """Return the corresponding Funklet object. Make one if necessary."""

        # Avoid double work:
        if self._Funklet:
            return self._Funklet

        self._nodes2vars()        
        if self.has_itemtype ('MeqNode'):
            # If there are MeqNode children, the Expression should be turned into
            # a MeqFunctional node. It is not possible to make a Funklet.
            return False
        
        funktion = deepcopy(self._expanded)
        coeff = []
        k = -1
        for key in self.item_order():
            rr = self._item[key]
            if rr['type']=='parm':                     # ....!!
                # Replace the undefined parameters {} with pk = p0,p1,p2,...
                # and fill the coeff-list with their default values
                k += 1
                pk = 'p'+str(k)
                funktion = funktion.replace(key, pk)
                value = rr['default']         
                value = float(value)                   # required by Funklet...!?
                coeff.append(value)

            elif rr['type']=='var':
                # Replace the valiables [] with x0 (time), x1(freq) etc
                funktion = rr['var']['funktion']
                funktion = funktion.replace(key, funktion)
                # print '- replace:',key,'by:',funktion,'\n  ->',funktion


        # Make the Funklet, and attach it:
        # if self._expression_type=='MeqPolc':         # see polc_Expression()
        # elif self._expression_type=='MeqPolcLog':    # see polc_Expression()
        # else:
        #-----------------------------------------------------
        if True:
            # type: isinstance(f0, Funklet) -> True
            f0 = Funklet(funklet=record(function=funktion, coeff=coeff),
                         name=self.name)
        else:
            # Alternative: type(meq.polc(0)) 
            f0 = meq.polc(coeff=coeff, subclass=meq._funklet_type)
            f0.function = funktion
        #-----------------------------------------------------

        if plot:
            # NB: The following plots WITHOUT execution!
            dom = meq.gen_domain(time=(0.0,1.0),freq=(100e6,110e6),l=(-0.1,0.1),m=(-0.1,0.1))
            cells = meq.gen_cells(domain=dom,num_time=4,num_freq=5, num_l=6, num_m=7)
            f0.plot(cells=cells)

        # Finished:
        self._last_solvable_tags = ['Funklet']           # used by .solvable()
        self._locked = True                              # no more modifications
        self._Funklet = f0
        self._Funklet_funktion = funktion         
        return self._Funklet





    #===========================================================================
    # Turn the Expression into a single node/subtree:
    #===========================================================================

    def MeqNode (self, show=False):
        """Make a single node/subtree from the Expression. In most cases,
        this will be a MeqParm, with the expression Funklet as init_funklet.
        But if the expression has at least one parameter that is a node,
        the result will be a MeqFunctional node."""

        self._nodes2vars()
        # self.display('MeqNode(): after nodes2vars()')

        if self.has_itemtype ('MeqNode'):
            # As soon as some parm items are nodes, it is no longer
            # possible to turn the Expression into a Funklet. So if
            # the latter is required, it should be done BEFORE the
            # function .MeqFunctional() is called....
            # In any case, return a Functional here:
            
            qnode = self.ns['Expr_MeqNode']
            if not qnode.initialized():
                qnode = self.MeqFunctional()

        elif self.has_itemtype ('parm'):
            qnode = self.ns['Expr_MeqParm']
            if not qnode.initialized():
                f0 = self.Funklet()
                if isinstance(f0, bool):
                    s = '** Funklet is '+str(type(f0))
                    raise TypeError,s
                funklet = f0.get_meqfunklet()
                # print '\n** funklet =',funklet
                # print dir(f0),'\n'
                if len(funklet['coeff'])==0:
                    s = '** coeff is empty'
                    raise ValueError,s
                qnode << Meq.Parm(init_funklet=funklet,       # new MXM 28 June 2006
                                  tags=['Funklet'],
                                  node_groups=['Parm'])

        elif self.has_itemtype ('var'):
            # Special case: only variables [] in the expression.
            # Since a Funklet requires at least one 'parm', make
            # a MeqFunctional after turning the vars into MeqGrid nodes.
            self._vars2nodes()
            qnode = self.ns['Expr_MeqNode']
            if not qnode.initialized():
                qnode = self.MeqFunctional()

        else:
            s = 'cannot make a MeqNode'
            raise ValueError,s

        # Finished:
        self._MeqNode = qnode
        if show: display.subtree(qnode)
        self._locked = True                          # inhibit further modifications
        return qnode

    #--------------------------------------------------------------------------
    # MXM: 28 June 2006
    # Ok, ik heb een functie get_meqfunklet() toegevoegd, die kun je gebruiken om
    # het funklet_type object te krijgen, nodig als je het 'init_funklet' veld zelf
    # met de hand zet (zoals je nu doet in Expression). Als je Meq.Parm
    # aanroept met als eerste variable het Funklet object (of: funklet =  funklet,
    # ipv init_funklet=funklet), gaat het ook goed, de Meq.Parm functie roept dan
    # zelf get_meqfunklet() aan.
    # WEl lijkt het om vreemde import redenen niet te werken, dit komt omdat je
    # Timba.TDL niet direkt geimporteerd hebt, als je :
    #            from Timba.TDL import *
    # toevoegt werkt het.
    #--------------------------------------------------------------------------

    

    #===========================================================================
    # Functions dealing with the available MeqParms (for solving etc)
    #===========================================================================


    def solvable (self, tags='last', trace=False):
        """Return a list of solvable MeqParm nodes. If tags='last',
        it will use the tags of the MeqParm(s) that were generated
        in the last operation (e.g. MeqNode() or MeqFunctional()."""
        tagsin = deepcopy(tags)
        if tags=='last':
            tags = self._last_solvable_tags
        elif tags in ['Functional','Funklet']:
            tags = [tags]
        elif isinstance(tags,(list,tuple)):
            pass
        else:
            tags = [tags]
        ss = self.ns.Search(class_name='MeqParm', tags=tags,
                            return_names=False)
        if trace:
            print '\n** solvable(',tagsin,tags,'):',type(ss)
            if isinstance(ss,(list,tuple)):
                for s in ss: print '-',str(s)
            print
        return ss







#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = [ns.dummy<<45]

    if 0:
        e0 = Expression(ns, 'e0', '{a}+{b}*[t]-{e}**{f}')
        e0.parm('{a}', '[f]*{c}/{b}+{d}')
        e0.parm('{b}', (ns << Meq.Add(ns<<13,ns<<89)))
        e0.parm('{c}', 47)
        e0.parm('{d}', (ns << Meq.Parm(-56)))
        e0.parm('{f}', 'MeqParm', default=-56)
        e1 = 111
        if False:
            e1 = Expression(ns,'e1','{A}+{B}/[m]')
            e1.parm('{A}', 45)
            e1.parm('{B}', -45)
        e0.parm('{e}', e1)    
        e0.display()
    
        if 1:
            cc.append(e0.MeqNode())   
            e0.display()

        if 0:                       
            cc.append(e0.MeqFunctional(show=True))
            e0.display()


    #------------------------------------------------------------

    if 0:
        # e4 = Expression(ns, 'e4', '[l]-[m]+{a}+[long]')
        e4 = Expression(ns, 'e4', '[l]-[m]')
        # e4 = Expression(ns, 'e4', '[l]-[m]+{a}')
        # e4.parm('{a}','MeqParm', default=9)
        # e4.var('[long]', xn='x6', axis='long')
        e4.display()

        if 0:
            f0 = e4.Funklet(plot=True)
            print '** f0 =',f0

        if 1:
            # LM = ns.LM << Meq.Composer(ns.L<<0.1, ns.M<<-0.2)
            LM = ns.LM << Meq.Composer(ns.L<<Meq.Freq(), ns.M<<Meq.Time())
            node = e4.MeqCompounder(extra_axes=LM,
                                    common_axes=[hiid('l'),hiid('m')],        # Time, Freq, L, M, 4, 5, 6, 7
                                    # common_axes=[hiid('lat'),hiid('long')],     # Time, Freq, $lat, long, L, M, 6, 7
                                    # common_axes=[hiid('q'),hiid('m')],        # Time, Freq, q, M, L, 5, 6, 7
                                    # common_axes=[hiid('m')],                  # kernel crash
                                    show=True)
            cc.append(node)
            e4.display()

        if 0:
            cc.append(e4.MeqNode())   
            e4.display()


    if 1:
        e5 = Expression(ns, 'e5', '[long]-[$lat]+{p}')
        e5.parm('{p}', 'MeqParm', default=-56)
        e5.var('[long]', xn='x2', axis='long')
        e5.var('[$lat]', xn='x3', axis='$lat')
        e5.display()
        if 1:
            cc.append(e5.MeqNode())   
            e5.display()


    ns.result << Meq.Composer(children=cc)
    return True



#---------------------------------------------------------------

def _tdl_job_2D_tf (mqs, parent):
    """Execute the forest with a 2D request (freq,time), starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,0,2000)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       

def _tdl_job_4D_tflm (mqs, parent):
    """Execute the forest with a 4D request (freq,time,l,m).
    NB: This does NOT work on a Compounder node!"""
    domain = meq.gen_domain(time=(0.0,1.0),freq=(100e6,110e6),l=(-0.1,0.1),m=(-0.1,0.1))
    cells = meq.gen_cells(domain=domain, num_time=4, num_freq=5, num_l=6, num_m=7)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       
def _tdl_job_4D_tf_lat_long (mqs, parent):
    """Execute the forest with a 4D request (freq,time,$lat,long).
    NB: This does NOT work on a Compounder node!"""
    domain = meq.gen_domain(time=(0.0,1.0),freq=(100e6,110e6),
                            lat=(-0.1,0.1),long=(-0.1,0.1))
    cells = meq.gen_cells(domain=domain, num_time=4, num_freq=5,
                          num_lat=6, num_long=7)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       





#========================================================================
# Test routine (without meqbrowser):
#========================================================================


if __name__ == '__main__':
    print '\n*******************\n** Local test of: Expression.py:\n'
    ns = NodeScope()

        
    if 1:
        fp = polc_Expression([2,3], 56, trace=True)
        fp.display()
        if 1:
            fp.Funklet()
            fp.display()


    #===============================================================================

    if 0:
        e0 = Expression(ns, 'e0')
        e0.display()
        if 0:
            print '** dir(e0) ->',dir(e0)
            print '** e0.__doc__ ->',e0.__doc__
            print '** e0.__str__() ->',e0.__str__()
            print '** e0.__module__ ->',e0.__module__
            print

    if 0:
        # e1 = Expression(ns,'e1','{A}+{B')
        # e1 = Expression(ns,'e1','45')
        e1 = Expression(ns,'e1','xx')
        e1.display()

    if 0:
        e0 = Expression(ns, 'e0', '{a}+{b}*[t]-{e}**{f}')
        e0.parm('{b}', (ns << Meq.Add(ns<<13,ns<<89)))
        e1 = 111.111
        if True:
            e0.parm('{a}', '[f]*{c}/{b}+{d}')
            e0.parm('{c}', 47)
            e1 = Expression(ns,'e1','{A}+{B}/[m]')
            e1.parm('{A}', 45)
            e1.parm('{B}', -45)
        e0.parm('{e}', e1)
        # e0.parm('{d}', (ns << Meq.Parm(-56)))
        # e0.parm('{f}', 'MeqParm', default=-56)
        e0.display()

        if 1:
            e0.MeqNode()
            e0.display()
        if 0:
            e0._vars2nodes()
            e0.display()
        if 0:
            e0._nodes2vars()
            e0.display()
        if 0:
            e0.MeqFunctional(show=True)
            e0.display()

    if 0:
        # e2 = Expression(ns, 'e2', '{a}*[t]-{a}**{f}+[m]+[Xat]')
        e2 = Expression(ns, 'e2', '{a}*[t]-{a}**{f}')
        e2.parm('{a}', '[f]*{c}/{b}+{d}')
        e2.parm('{b}', 447)
        e2.parm('{c}', 47)
        e2.parm('{d}', (ns << Meq.Parm(-56)))
        e2.parm('{f}', 'MeqParm', default=-56)
        e2.display()
        if 0:
            e2.MeqNode()
            e2.display()
        if 0:
            e2.Funklet()
            e2.display()
        if 0:
            e2.MeqCompounder(show=True)
            e2.display()

    if 0:
        e4 = Expression(ns, 'e4', '[l]-[m]+{p}')
        # e4 = Expression(ns, 'e4', '[l]-[m]')
        # e4.parm('{p}', 'MeqParm', default=-56)
        # e4.var('[m]', xn='x10', axis='mcoord')
        e4.display()
        if 0:
            e4.MeqNode(show=True)
            e4.display()
        if 0:
            e4.MeqFunctional(show=True)
            e4.display()
        if 1:
            L = ns.L << 0.1
            M = ns.M << -0.2
            LM = ns.LM << Meq.Composer(L,M)
            node = e4.MeqCompounder(extra_axes=LM,
                                    # common_axes=[hiid('l'),hiid('m')],
                                    common_axes=[hiid('m')],
                                    show=True)
            e4.display()

    if 0:
        e5 = Expression(ns, 'e5', '[long]-[$lat]+{p}')
        # e5.parm('{p}', 'MeqParm', default=-56)
        e5.var('[long]', xn='x2', axis='long')
        e5.var('[$lat]', xn='x3', axis='$lat')
        e5.display()
        if 1:
            e5.MeqNode(show=True)
            e5.display()
        if 0:
            e5.MeqFunctional(show=True)
            e5.display()
        if 0:
            L = ns.L << 0.1
            M = ns.M << -0.2
            LM = ns.LM << Meq.Composer(L,M)
            node = e5.MeqCompounder(extra_axes=LM,
                                    # common_axes=[hiid('l'),hiid('m')],
                                    common_axes=[hiid('m')],
                                    show=True)
            e5.display()


    print '\n*******************\n** End of local test of: Expression.py:\n'




#============================================================================================

    
