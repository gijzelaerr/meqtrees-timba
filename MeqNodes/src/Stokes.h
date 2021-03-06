//# Stokes.h: Application of the Stokes Matrix
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
//# $Id$

#ifndef MEQNODES_STOKES_H
#define MEQNODES_STOKES_H

//# Includes
#include <MEQ/Node.h>
//#include <images/Images/PagedImage.h>
#include <MeqNodes/ReductionFunction.h>


#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::Stokes

namespace Meq {
  
class Stokes: public Node
	       //class Stokes: public ReductionFunction
{
public:
  // The default constructor.
  // The object should be filled by the init method.
  Stokes();

  virtual ~Stokes();

  virtual TypeId objectType() const
  { return TpMeqStokes; }

  // Get the requested result of the Node.
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);

  
 protected:

  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);
   
  double scale_;
};


} // namespace Meq

#endif
