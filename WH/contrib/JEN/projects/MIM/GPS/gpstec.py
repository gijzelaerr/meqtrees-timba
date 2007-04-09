# file ../JEN/projects/MIM/GPS/gpstec.py

from Timba.TDL import *
from Timba.Meq import meq
# from Parameterization import *

import Meow

from Timba.Contrib.JEN.Grunt import display
from Timba.Contrib.JEN.Vector import Vector
from numarray import *

Settings.forest_state.cache_policy = 100

#================================================================

class GPSStation (Vector.Vector):
  """Represents a GPS station that measures TEC values"""

  def __init__(self, ns, name, pos=[],
               refpos=None,
               quals=[],kwquals={}):

    Vector.Vector.__init__(self, ns=ns, name=name,
                           elem=pos, axes=['X','Y','Z'], unit='m',
                           tags=['position','GPSStation'],
                           solvable=False, test=False,
                           typename='location',
                           quals=quals, kwquals=kwquals)

    if not isinstance(refpos,(list,tuple)) or not len(refpos)==3:
      refpos = [0.0,0.0,0.0]
    self._relpos = [pos[0]-refpos[0], pos[1]-refpos[1], pos[2]-refpos[2]]

    self._add_parm('TEC_bias', Meow.Parm(), tags=['GPSStation'])
    return None

  
  def oneliner (self):
    ss = 'GPSStation'
    ss += ' ('+str(self._typename)+')'
    ss += '  '+str(self.name)
    ss += '  (rel)pos='+str(self._relpos)
    return ss

  
  def bias (self):
    """Returns the station TEC bias (node)"""
    return self._parm('TEC_bias')


  def latlong (self, show=False):
    """Returns a two-pack with its latitude and longtitude (rad)"""
    node = self.ns['latlong']
    if not node.initialized():
      m = self.magnitude()
      z = self.element('Z')
      x = self.element('X')
      latid = node('latitude') << Meq.Divide(z,m)  
      longid = node('longitude') << Meq.Divide(x,m)
      node << Meq.Composer(latid,longid)
    if show:
      display.subtree(node)
    return node
        

#================================================================

class GPSSatellite (Vector.Vector):
  """Represents a GPS satellite"""

  def __init__(self, ns, name, pos=[],
               quals=[],kwquals={}):

    Vector.Vector.__init__(self, ns=ns, name=name,
                           elem=pos, axes=['X','Y','Z'], unit='m',
                           tags=['position','GPSSatellite'],
                           solvable=False, test=False,
                           typename='location',
                           quals=quals, kwquals=kwquals)

    self._add_parm('TEC_bias', Meow.Parm(), tags=['GPSSatellite'])
    return None


  def oneliner (self):
    ss = 'GPSSatellite'
    ss += ' ('+str(self._typename)+')'
    ss += '  '+str(self.name)
    return ss

  
  def bias (self):
    """Returns the satellite TEC bias (node)"""
    return self._parm('TEC_bias')
        

  def latlong (self, show=False):
    """Returns a two-pack with its latitude and longtitude (rad)"""
    node = self.ns['latlong']
    if not node.initialized():
      m = self.magnitude()
      z = self.element('Z')
      x = self.element('X')
      latid = node('latitude') << Meq.Divide(z,m)  
      longid = node('longitude') << Meq.Divide(x,m)
      node << Meq.Composer(latid,longid)
    if show:
      display.subtree(node)
    return node
        




#================================================================

class GPSPair (object):
  """Represents a combination of a GPSStation and GPSSatellite"""
  
  def __init__(self, ns, station, satellite,
               name=None, quals=[],kwquals={}):

    self._station = station
    self._satellite = satellite

    # The object name. By default a combination of its station/satellite
    # names, but it can be overridden with the user-defined name.
    self._name = str(self._station.name)+'|'+str(self._satellite.name)
    if isinstance(name, str): self._name = name

    # Add the station/satellite names to the nodescope qualifiers:
    if not isinstance(quals,(list,tuple)): quals = [quals]
    quals.append(self._station.name)
    quals.append(self._satellite.name)
    self.ns0 = ns
    self.ns = Meow.QualScope(ns, quals=quals, kwquals=kwquals)

    return None

  def name (self):
    """Return the pair name (station_satellite)"""
    return self._name

  def oneliner (self):
    ss = 'GPSPair: '+str(self.name())
    return ss
  
  def display(self, full=False):
    """Display a summary of this object"""
    print '\n** '+self.oneliner()
    print '  * '+self.station().oneliner()
    print '  * '+self.satellite().oneliner()
    print
    return True

  #-------------------------------------------------------

  def station(self):
    """Return its station object"""
    return self._station

  def satellite(self):
    """Return its satellite object"""
    return self._satellite

  #-------------------------------------------------------

  def TEC(self):
    """Return a node/subtree that produces a measured TEC value for
    a specified time-range (in the request). It gets its information
    from external GPS data in a file or something."""
    node = None
    return node

  #-------------------------------------------------------

  def zenith_angle(self, show=False):
    """Return the zenith angle (node) of its satellite, as seen
    from its station. This is time-dependent, of course."""
    zang = self.ns.zenith_angle
    if not zang.initialized():
      dxyz = self._satellite.binop('Subtract', self._station, show=show)
      zang = self._satellite.enclosed_angle(dxyz, show=show)
    return zang




#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    pos1 = array([1.0,-3.5,5.8])
    pos2 = array([10*pos1[0], 8*pos1[1], 6*pos1[2]])
    if False:
      # Zenith angle calculation (test of zang):
      dxyz = pos2-pos1
      norm1 = sqrt(sum(pos1*pos1))
      norm2 = sqrt(sum(dxyz*dxyz))
      print '**pos1:',pos1,': norm1 =',norm1
      print '**pos2:',pos2,': norm2 =',norm2
      print 'prod12=',pos1*dxyz
      dotprod = sum(pos1*dxyz)
      cosz = dotprod/(norm1*norm2)
      z = arccos(cosz)
      print dotprod,'** cosz=',cosz,' -> z=',z,' rad =',z*57,' deg'

    st1 = GPSStation(ns,'st1', pos1)
    sat1 = GPSSatellite(ns,'sat1', x=pos2[0], y=pos2[1], z=pos2[2])

    pair = GPSPair (ns, station=st1, satellite=sat1)
    pair.display(full=True)
    zang = pair.zenith_angle()
    
    cc.append(zang)

    ns.result << Meq.Composer(children=cc)
    return True

#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       
       

#================================================================
# Test program
#================================================================
    
if __name__ == '__main__':
    """Test program"""
    print
    ns = NodeScope()

    if 1:
      st1 = GPSStation(ns, 'st1', [1,2,12])
      print st1.oneliner()
      if 0:
        xyz = st1.node()
        display.subtree(xyz)
        bias = st1.bias()
        bias = st1.bias()
        display.subtree(bias)

      if 1:
        latlong = st1.latlong(show=True)

    if 1:
      sat1 = GPSSatellite(ns, 'sat1', [4,7,8])
      print sat1.oneliner()
      if 0:
        xyz = sat1.node()
        display.subtree(xyz)
        bias = sat1.bias()
        display.subtree(bias)

      if 1:
        latlong = sat1.latlong(show=True)


    if 0:
      pair = GPSPair (ns, station=st1, satellite=sat1)
      pair.display(full=True)

      if 0:
        zang = pair.zenith_angle(show=True)

    
