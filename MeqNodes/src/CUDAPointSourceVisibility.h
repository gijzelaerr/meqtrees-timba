//# CUDAPointSourceVisibility.h: The point source DFT component for a station
//#
//# Copyright (C) 2002-2007
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# and The MeqTree Foundation
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
//# $Id: CUDAPointSourceVisibility.h 5418 2007-07-19 16:49:13Z oms $

#ifndef MEQNODES_CUDAPOINTSOURCEVISIBILITY_H
#define MEQNODES_CUDAPOINTSOURCEVISIBILITY_H

//# Includes
#include <MEQ/TensorFunction.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::CUDAPointSourceVisibility
#pragma aid LMN UVW B

namespace Meq {    


    
class CUDAPointSourceVisibility: public TensorFunction
{
public:
  //! The default constructor.
  CUDAPointSourceVisibility();

  virtual ~CUDAPointSourceVisibility();

  virtual TypeId objectType() const
    { return TpMeqCUDAPointSourceVisibility; }

  // this is for the cdebug() mechanism
  LocalDebugContext;

protected:
  // method required by TensorFunction
  // Returns shape of result.
  // Also check child results for consistency
  virtual LoShape getResultDims (const vector<const LoShape *> &input_dims);
    
  // method required by TensorFunction
  // Evaluates for a given set of children values
  virtual void evaluateTensors (std::vector<Vells> & out,   
       const std::vector<std::vector<const Vells *> > &args);
       
  int num_sources_;
       
};

} // namespace Meq

#endif
