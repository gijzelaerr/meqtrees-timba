script_name = 'MG_JEN_twig.py'

# Short description:
#   Various input subtrees (twigs)  

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 22 aug 2005: creation

# Copyright: The MeqTree Foundation 


# Import Python modules:
from Timba.TDL import *
from Timba.Meq import meq

import MG_JEN_template 
import MG_JEN_forest_state

import MG_JEN_autoper

from random import *
from numarray import *
from string import *
from copy import deepcopy



#================================================================================
# Required functions:
#================================================================================


#--------------------------------------------------------------------------------
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.

def _define_forest (ns):

   # Generate a list (cc) of one or more root nodes:
   cc = []

   # Test/demo of importable function: .freqtime()
   bb = []
   bb.append(freqtime (ns))
   bb.append(freqtime (ns, combine='ToComplex')) 
   bb.append(freqtime (ns, combine='Add', unop=['Cos','Sin']))  
   cc.append(MG_JEN_template.bundle(ns, bb, 'freqtime'))

   # Test/demo of importable function: .wavelength()
   bb = []
   bb.append(wavelength (ns))
   bb.append(wavelength (ns, unop='Sqr'))
   cc.append(MG_JEN_template.bundle(ns, bb, 'wavelength'))

   # Test/demo of importable function: .gaussnoise()
   dims = [1]
   dims = [2,2]
   bb = []
   bb.append(gaussnoise (ns, stddev=1, mean=0, complex=True, dims=dims)) 
   bb.append(gaussnoise (ns, stddev=1, mean=0, complex=True, dims=dims, unop='Exp'))
   bb.append(gaussnoise (ns, stddev=1, mean=0, complex=True, dims=dims, unop=['Exp','Exp']))
   cc.append(MG_JEN_template.bundle(ns, bb, 'gaussnoise'))

   # Test/demo of importable function: .cloud()
   bb = cloud (ns, n=3, name='pnt', qual='auto', stddev=1, mean=0, complex=True)
   cc.append(MG_JEN_template.bundle(ns, bb, 'cloud'))

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

#-------------------------------------------------------------------------------
# Make a node that varies with freq and time

freqtime_counter = 0                 # used for automatic qualifiers

def freqtime (ns, qual='auto', combine='Add', unop=False):
    """Make an input node that varies with freq and time:"""
 
   # If necessary, make an automatic qualifier:
    if isinstance(qual, str) and qual=='auto':
	global freqtime_counter
	freqtime_counter += 1
        qual = str(freqtime_counter)


    # Make the basic freq-time nodes:
    freq = ns.time(qual) << Meq.Freq()
    time = ns.freq(qual) << Meq.Time()

    # Combine them (e.g. e.g. adding):
    output = ns.freqtime(qual) << getattr(Meq,combine)(children=[freq, time])

    # Optional: Apply zero or more unary operations on the output:
    output = MG_JEN_autoper.apply_unop (ns, unop, output) 

    # Finished:
    return output

#----------------------------------------------------------------------
# Calculate unop(wavelength):

wavelength_counter = 0                 # used for automatic qualifiers

def wavelength (ns, qual='auto', unop=0):

   # If necessary, make an automatic qualifier:
    if isinstance(qual, str) and qual=='auto':
	global wavelength_counter
	wavelength_counter += 1
        qual = str(wavelength_counter)

    clight = 2.997925e8
    freq = ns.freq << Meq.Freq()
    wvl = ns.wavelength(qual) << (2.997925e8/freq)
    if isinstance(unop, str):
        wvl = (ns << getattr(Meq,unop)(wvl))
    return wvl


#-------------------------------------------------------------------------------
# Make a node with gaussian noise

gaussian_counter = 0                  # used for automatic qualifiers

def gaussnoise (ns, qual='auto', stddev=1, mean=0, complex=False, dims=[1], unop=False):
    """makes gaussian noise"""

    # If necessary, make an automatic qualifier:
    if isinstance(qual, str) and qual=='auto':
	global gaussian_counter
	gaussian_counter += 1
        qual = str(gaussian_counter)

    # Determine the nr (nel) of tensor elements:
    if not isinstance(dims, (list, tuple)): dims = [dims]
    nel = sum(dims)
    # print 'nel =',nel

    # NB: What about making/giving stddev as a MeqParm...?

    # The various tensor elements have different noise, of course:
    # NB: Is this strictly necessary? A single GaussNoise node would
    #     be requested separately by each tensor element, and produce
    #     a separate set of values (would it, for the same request..........?)
    #     So a single GaussNoise would be sufficient (for all ifrs!)
    #     provided they would have the same stddev
    cc = []
    for i in range(nel):
	if complex:
		real = ns.real(qual,i) << Meq.GaussNoise(stddev=stddev)
		imag = ns.imag(qual,i) << Meq.GaussNoise(stddev=stddev)
		cc.append (ns.gaussnoise(qual,i) << Meq.ToComplex(children=[real, imag]))
	else:
		cc.append (ns.gaussnoise(qual,i) << Meq.GaussNoise(stddev=stddev))

    # Make into a tensor node, if necessary:
    output = cc[0]
    if nel>1: 
	output = ns.gaussnoise(qual) << Meq.Composer(children=cc, dims=dims)

    # Optional: Add the specified mean:
    if abs(mean)>0:
	if not complex and isinstance(mean, complex): mean = mean.real
	output = output + mean

    # Optional: Apply zero or more unary operations on the output (e.g Exp):
    output = MG_JEN_autoper.apply_unop (ns, unop, output) 

    return output


#----------------------------------------------------------------------
# Make a 'cloud' of points (cc) scattered (stddev) around a mean

def cloud (ns, n=3, name='pnt', qual='auto', stddev=1, mean=0, complex=True):
    cc = []
    v = array([[1,.3,.1],[.3,.1,0.03]])
    for i in range(n):
        dflt = funklet(v, mean=mean, stddev=stddev)
        cc.append(ns[name](i) << Meq.Parm (dflt, node_groups='Parm'))
    return cc


#----------------------------------------------------------------------
# Make sure that the funklet is a funklet.
# Perturb the c00 coeff, if required

# array([[1,.3,.1],[.3,.1,0.03]])

def funklet (funkin, mean=0, stddev=0):
    if isinstance(funkin, dmi_type('MeqFunklet')):
        funklet = deepcopy(funkin)
    elif isinstance(funkin,type(array(0))):
        funklet = meq.polc(deepcopy(funkin))
    else:
        funklet = meq.polc(deepcopy(funkin))

    if mean != 0 or stddev > 0:
        if (funklet['coeff'].rank==0):
            funklet['coeff'] += gauss(mean, stddev)
        elif (funklet['coeff'].rank==1):
            funklet['coeff'][0] += gauss(mean, stddev)
        elif (funklet['coeff'].rank==2):
            funklet['coeff'][0,0] += gauss(mean, stddev)
        elif (funklet['coeff'].rank==3):
            funklet['coeff'][0,0,0] += gauss(mean, stddev)
        elif (funklet['coeff'].rank==4):
            funklet['coeff'][0,0,0,0] += gauss(mean, stddev)
        else:
            print '\n** JEN_funklet error: rank =',funklet['coeff'].rank

    return funklet


#********************************************************************************




