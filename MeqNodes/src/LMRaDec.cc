//# LMRaDec.cc: Calculate source Ra and Dec from L and M
//#
//# Copyright (C) 2006
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//# This program is free software; you can redistribute it and/or modify
//# it under the terms of the GNU General Public License as published by
//# the Free Software Foundation; either version 2 of the License, or
//# (at your option) any later version.
//#
//# This program is distributed in the hope that it will be useful,
//# but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//# GNU General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License
//# along with this program; if not, write to the Free Software
//# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//# $Id: LMRaDec.cc 3568 2006-05-15 14:11:19Z smirnov $

#include <math.h>
#include <MeqNodes/LMRaDec.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Vells.h>
#include <MEQ/AID-Meq.h>
#include <casa/Arrays/Matrix.h>
#include <casa/Arrays/Vector.h>
#include <coordinates/Coordinates/CoordinateUtil.h>
#include <coordinates/Coordinates/CoordinateSystem.h>
#include <coordinates/Coordinates/DirectionCoordinate.h>
#include <coordinates/Coordinates/Projection.h>
#include <measures/Measures/MDirection.h>
#include <MeqNodes/AID-MeqNodes.h>

using namespace casa;

namespace Meq {

// make sure the following is commented out as we
// don't want VellsMath for the sin / cos computations
// for the xform matrix below.

// using namespace VellsMath;

const HIID child_labels[] = { AidRADec|0,AidLM };
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);

const HIID FDomain = AidDomain;

using Debug::ssprintf;

//##ModelId=400E535502D1
LMRaDec::LMRaDec()
: TensorFunction(num_children,child_labels)
{
}

//##ModelId=400E535502D2
LMRaDec::~LMRaDec()
{}


LoShape LMRaDec::getResultDims (const vector<const LoShape *> &input_dims)
{
  Assert(input_dims.size()==2);
  // inputs are 2-vectors
  for( int i=0; i<2; i++ )
  {
    const LoShape &dim = *input_dims[i];
    FailWhen(dim.size()!=1 || dim[0]!=2,"child '"+child_labels[i].toString()+"': 2-vector expected");
  }
  // result is a 2-vector
  return LoShape(2);
}
    
void LMRaDec::evaluateTensors (std::vector<Vells> & out,   
     const std::vector<std::vector<const Vells *> > &args )
{
  // thanks to checks in getResultDims(), we can expect all 
  // vectors to have the right sizes
  
  // phase center position
  const Vells & vra0  = *(args[0][0]);
  const Vells & vdec0 = *(args[0][1]);
  // L and M coordinates (radians)
  const Vells & L   = *(args[1][0]);
  const Vells & M  = *(args[1][1]);
  // outputs
  Vells & vra = out[0];
  Vells & vdec = out[1];

  Matrix<double> xform(2,2);                                    
// xform = 0.0; 
// xform.diagonal() = 1.0;                         
// lets allow for possible future coordinate system rotations
// by specifying individual elements of the xform matrix rather
// than just setting diagonals to 1.0
  double pos_ang_radians = 0.0;
  xform(0,0)= cos(pos_ang_radians);
  xform(0,1)= sin(pos_ang_radians);
  xform(1,0)= -sin(pos_ang_radians);
  xform(1,1)= cos(pos_ang_radians);

  DirectionCoordinate *DirCoord = new DirectionCoordinate(MDirection::J2000,
                          Projection(Projection::SIN),       
                          vra0.getScalar<double>(), vdec0.getScalar<double>(),
                          1.0, 1.0, xform, 0.0, 0.0);                   
  Vector<double> pixel(2);
  pixel(0) = L.getScalar<double>();
  pixel(1) = M.getScalar<double>();
  Vector<double> world(2);
  DirCoord->toWorld(world,pixel);
  vra = world(0);
  vdec = world(1);
}

} // namespace Meq