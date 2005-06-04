//# Request.cc: The request for an evaluation of an expression
//#
//# Copyright (C) 2002
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
//# $Id$

#include "Request.h"
// #include "Node.h"
#include "MeqVocabulary.h"

namespace Meq {

static DMI::Container::Register reg(TpMeqRequest,true);

//##ModelId=3F8688700056
Request::Request()
: pcells_(0),eval_mode_(0),has_rider_(false),service_flag_(false)
{
}

//##ModelId=3F8688700061
Request::Request (const DMI::Record &other,int flags,int depth)
: Record(), 
  pcells_(0),eval_mode_(0),has_rider_(false),service_flag_(false)
{
  Record::cloneOther(other,flags,depth,true);
}

//##ModelId=400E535403DD
Request::Request (const Cells& cells,int em,const HIID &id,int cellflags)
: has_rider_(false),service_flag_(false)
{
  setCells(cells,cellflags);
  setId(id);
  setEvalMode(em);
}

//##ModelId=400E53550016
Request::Request (const Cells * cells, int em, const HIID &id,int cellflags)
: has_rider_(false),service_flag_(false)
{
  setCells(cells,cellflags);
  setId(id);
  setEvalMode(em);
}

// Set the request id.
//##ModelId=3F8688700075
void Request::setId (const HIID &id)
{
  (*this)[FRequestId] = id_ = id;
}

void Request::setNextId (const HIID &id)
{
  (*this)[FNextRequestId] = next_id_ = id;
}

void Request::setEvalMode (int em)
{ 
  (*this)[FEvalMode] = eval_mode_ = em; 
}

void Request::setServiceFlag (bool flag)
{ 
  (*this)[FServiceFlag] = service_flag_ = flag; 
}

//##ModelId=3F868870006E
void Request::setCells (const Cells * cells,int flags)
{
  ObjRef ref(cells,flags);
  Field & field = Record::addField(FCells,ref,flags|DMI::REPLACE|Record::PROTECT);
  pcells_ = &(field.ref.ref_cast<Cells>());
}

//##ModelId=400E53550049
void Request::validateContent (bool)
{
  Thread::Mutex::Lock lock(mutex());
  // ensure that our record contains all the right fields, and that they're
  // indeed writable. Setup shortcuts to their contents
  try
  {
    // get cells field
    Field * pcf = findField(FCells);
    if( pcf )
    {
      pcells_ = &( pcf->ref.ref_cast<Cells>() );
      pcf->protect = true;
    }
    else
      pcells_ = 0;
    // request ID
    id_ = (*this)[FRequestId].as<HIID>(HIID());
    next_id_ = (*this)[FNextRequestId].as<HIID>(HIID());
    // flags
    eval_mode_ = (*this)[FEvalMode].as<int>(GET_RESULT);
    service_flag_ = (*this)[FServiceFlag].as<bool>(false);
    // rider
    validateRider();
  }
  catch( std::exception &err )
  {
    cerr<<"Failed request: "<<sdebug(10);
    Throw(string("validate of Request record failed: ") + err.what());
  }
  catch( ... )
  {
    Throw("validate of Request record failed with unknown exception");
  }  
}

void Request::validateRider ()
{
  has_rider_ = Record::hasField(FRider);
}

void Request::clearRider ()
{
  Thread::Mutex::Lock lock(mutex());
  Record::remove(FRider);
  has_rider_ = false;
}

void Request::copyRider (const Request &other)
{
  Thread::Mutex::Lock lock(mutex());
  const Field * fld = other.findField(FRider);
  if( fld )
  {
    Record::replace(FRider,fld->ref);
    has_rider_ = true;
  }
  else
    clearRider();
}

} // namespace Meq
