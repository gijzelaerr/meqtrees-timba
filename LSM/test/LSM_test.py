#!/usr/bin/python

########
## This script needs to be run in the MeqBrowser,
## So the LSM is created within the define_forest() function
#from Timba.Contrib   import JEN
from Timba.LSM.LSM import *
from Timba.TDL import Settings
from Timba.LSM.LSM_GUI import *
# Meqtree stuff
#from Timba.Contrib.JEN.JEN_lsm import *
from Timba.Contrib.JEN.JEN_lsm  import *
import re
import math

# to force caching put 100
Settings.forest_state.cache_policy = 0


# Create Empty LSM - global
lsm=LSM()

########################################################
def define_forest(ns):
 global lsm
 # please change this according to your setup
 infile=open('/home/sarod/LOFAR/Timba/LSM/test/3C343_nvss.txt','r')
 all=infile.readlines()
 infile.close()

 # regexp pattern
 pp=re.compile(r"""
   ^(?P<col1>\S+)  # column 1 'NVSS'
   \s*             # skip white space
   (?P<col2>[A-Za-z]\w+\+\w+)  # source name i.e. 'J163002+631308'
   \s*             # skip white space
   (?P<col3>\d+)   # RA angle - hr 
   \s*             # skip white space
   (?P<col4>\d+)   # RA angle - min 
   \s*             # skip white space
   (?P<col5>\d+(\.\d+)?)   # RA angle - sec
   \s*             # skip white space
   (?P<col6>\d+(\.\d+)?)   # eRA angle - sec
   \s*             # skip white space
   (?P<col7>\d+)   # Dec angle - hr 
   \s*             # skip white space
   (?P<col8>\d+)   # Dec angle - min 
   \s*             # skip white space
   (?P<col9>\d+(\.\d+)?)   # Dec angle - sec
   \s*             # skip white space
   (?P<col10>\d+(\.\d+)?)   # eDec angle - sec
   \s*             # skip white space
   (?P<col11>\d+)   # freq
   \s*             # skip white space
   (?P<col12>\d+(\.\d+)?)   # brightness - Flux
   \s*             # skip white space
   (?P<col13>\d*\.\d+)   # brightness - eFlux
   \s*
   \S+
   \s*$""",re.VERBOSE)
 from random import *
 linecount=0
 # read each source and insert to LSM
 for eachline in all:
  v=pp.search(eachline)
  if v!=None:
   linecount+=1
   #print v.group('col2'), v.group('col12')
   s=Source(v.group('col2'))
   source_RA=float(v.group('col3'))+(float(v.group('col5'))/60.0+float(v.group('col4')))/60.0
   source_RA*=math.pi/12.0
   source_Dec=float(v.group('col7'))+(float(v.group('col9'))/60.0+float(v.group('col8')))/60.0
   source_Dec*=math.pi/180.0

   sixpack=lsm_NEWSTAR_source(ns,name=s.name,I0=eval(v.group('col12')), SI=[random()],f0=1e6,RA=source_RA, Dec=source_Dec,trace=0)
   iquv=sixpack['iquv']
   radec=sixpack['radec']
   # create SixPack trees using JEN code,
   # note: only I,RA,Dec subtrees have non-zero value right now
   SourceRoot=ns[s.name]<<Meq.Composer(radec['RA'],radec['Dec'],iquv['StokesI'],iquv['StokesQ'],iquv['StokesU'],iquv['StokesV'])
   lsm.add_source(s,brightness=eval(v.group('col12')),
          SP=SourceRoot,
     RA=source_RA, Dec=source_Dec)
 
 print "Inserted %d sources" % linecount 


########################################################################

def test_forest(mqs,parent):
 global lsm
 #display LSM within MeqBrowser
 #l.display()
 # set the MQS proxy of LSM
 lsm.setMQS(mqs)

 # create a cell
 from Timba.Meq import meq

 f0 = 1200e6
 f1 = 1600e6
 t0 = 0.0
 t1 = 1.0
 nfreq = 3
 ntime = 2
 # create cells
 freqtime_domain = meq.domain(startfreq=f0, endfreq=f1, starttime=t0, endtime=t1);
 cells =meq.cells(domain=freqtime_domain, num_freq=nfreq,  num_time=ntime);
 # set the cells to LSM
 lsm.setCells(cells)
 # query the MeqTrees using these cells
 lsm.updateCells()
 # display results
 lsm.display()

   

#####################################################################

if __name__=='__main__':
  ns=NodeScope()
  define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
  #display LSM without MeqBrowser
  # create cell
  freqtime_domain = meq.domain(10,1000,0,1);
  cells =meq.cells(domain=freqtime_domain, num_freq=2,  num_time=3);
  lsm.setCells(cells)
  lsm.display(app='create')


