//# Function.cc: Base class for an expression node
//#
//# Copyright (C) 2003
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

#include <MEQ/Function.h>
    

namespace MEQ {

Function::Function()
{}

Function::~Function()
{}

TypeId Function::objectType() const
{
  return TpMEQFunction;
}

void Function::checkChildren()
{
  if (itsChildren.size() == 0) {
    int nch = numChildren();
    itsChildren.resize (nch);
    for (int i=0; i<nch; i++) {
      itsChildren[i] = &(getChild(i));
    }
  }
}

bool Function::convertChildren (int nchild)
{
  if (itsChildren.size() > 0) {
    return false;
  }
  testChildren(nchild);
  Function::checkChildren();
  return true;
 }

bool Function::convertChildren (const vector<HIID>& childNames, int nchild)
{
  if (itsChildren.size() > 0) {
    return false;
  }
  if (nchild == 0) {
    nchild = childNames.size();
  }
  testChildren(nchild);
  int nch = numChildren();
  itsChildren.resize (nch);
  int nhiid = childNames.size();
  // Di it in order of the HIIDs given.
  for (int i=0; i<nhiid; i++) {
    itsChildren[i] = &(getChild(childNames[i]));
  }
  // It is possible that there are more children than HIIDs.
  // In that case the remaining children are appended at the end.
  if (nch > nhiid) {
    int inx = nhiid;
    for (int i=0; i<nch; i++) {
      Node * ptr = &(getChild(childNames[i]));
      bool fnd = false;
      for (int j=0; j<nhiid; j++) {
	if (ptr == itsChildren[j]) {
	  fnd = true;
	}
      }
      if (!fnd) {
	itsChildren[inx++] = ptr;
      }
    }
  }
  return true;
}

void Function::testChildren (int nchild) const
{
  if (nchild > 0) {
    Assert (numChildren() == nchild);
  } else if (nchild < 0) {
    Assert (numChildren() > -nchild);
  }
}

void Function::testChildren (const vector<TypeId>& types) const
{
  int nch = std::min (types.size(), itsChildren.size());
  for (int i=0; i<nch; i++) {
    AssertStr (itsChildren[i]->objectType() == types[i],
	       "expected type " << types[i] << ", but found "
	       << itsChildren[i]->objectType());
  }
}

int Function::getResultImpl (Result::Ref &resref, const Request& request, bool)
{
  int nrch = itsChildren.size();
  vector<Result::Ref> results(nrch);
  vector<Vells*> values(nrch);
  int flag = 0;
  for (int i=0; i<nrch; i++) {
    flag |= itsChildren[i]->getResult (results[i], request);
    results[i].persist();
    values[i] = &(results[i].dewr().getValueRW());
  }
  if (flag & Node::RES_WAIT) {
    return flag;
  }
  // Create result object and attach to the ref that was passed in
  Result& result = resref <<= new Result();
  // Evaluate the main value.
  Vells vells = evaluate (request, values);
  bool useVells;
  int nx,ny;
  bool isReal;
  if (vells.nelements() > 0) {
    useVells = false;
    result.setValue (vells);
  } else {
    useVells = true;
    isReal = resultTypeShape (nx, ny, request, values);
    evaluateVells (result.setValue(isReal,nx,ny), request, values);
  }
  // Find all spids from the children.
  vector<int> spids = findSpids (results);
  // Evaluate all perturbed values.
  vector<Vells*> perts(nrch);
  vector<int> indices(nrch, 0);
  for (unsigned int j=0; j<spids.size(); j++) {
    perts = values;
    for (int i=0; i<nrch; i++) {
      int inx = results[i].dewr().isDefined (spids[j], indices[i]);
      if (inx >= 0) {
	perts[i] = &(results[i].dewr().getPerturbedValueRW(inx));
      }
    }
    if (useVells) {
      evaluateVells (result.setPerturbedValue(j,isReal,nx,ny), request,values);
    } else {
      result.setPerturbedValue (j, evaluate(request,values));
    }
  }
  return flag;
}

bool Function::resultTypeShape (int& nx, int& ny, const Request&,
				const vector<Vells*>& values)
{
  Assert (values.size() > 0);
  nx = values[0]->nx();
  ny = values[0]->ny();
  bool isReal = values[0]->isReal();
  for (unsigned int i=0; i<values.size(); i++) {
    nx = std::max(nx, values[i]->nx());
    ny = std::max(ny, values[i]->ny());
    isReal &= values[0]->isReal();
  }
  return isReal;
}

Vells Function::evaluate (const Request&, const vector<Vells*>&)
{
  return Vells();
}

void Function::evaluateVells (Vells&, const Request&, const vector<Vells*>&)
{
  AssertMsg (false, "evaluate or getResultImpl not implemented in class "
	     "derived from MeqFunction");
}

vector<int> Function::findSpids (const vector<Result::Ref>& results) const
{
  // Determine the maximum number of spids.
  int nrspid = 0;
  int nrch = results.size();
  for (int i=0; i<nrch; i++) {
    nrspid += results[i]->getSpids().size();
  }
  // Allocate a vector of that size.
  // Exit immediately if nothing to be done.
  vector<int> spids(nrspid);
  if (nrspid == 0) {
    return spids;
  }
  // Merge all spids by doing that child by child.
  // The merged spids are stored from the end of the spids vector, so
  // eventually all resulting spids are at the beginning of the vector.
  int stinx = nrspid;          // start at end
  nrspid = 0;                  // no resulting spids yet
  // Loop through all children.
  for (int ch=0; ch<nrch; ch++) {
    const vector<int>& chspids = results[ch]->getSpids();
    int nrchsp = chspids.size();
    if (nrchsp > 0) {
      // Only handle a child with spids.
      // Get a direct pointer to its spids (is faster).
      const int* chsp = &(chspids[0]);
      int inx = stinx;       // index where previous merge result starts.
      int lastinx = inx + nrspid;
      stinx -= nrchsp;       // index where new result is stored.
      int inxout = stinx;
      int lastspid = -1;
      // Loop through all spids of the child.
      for (int i=0; i<nrchsp; i++) {
	// Copy spids until exceeding current child's spid.
	int spid = chsp[i];
	while (inx < lastinx  &&  spids[inx] <= spid) {
	  lastspid = spids[inx++];
	  spids[inxout++] = lastspid;
	}
	// Only store child's spid if different.
	if (spid != lastspid) {
	  spids[inxout++] = spid;
	}
      }
      // Copy possible remaining spids.
      while (inx < lastinx) {
	spids[inxout++] = spids[inx++];
      }
      nrspid = inxout - stinx;
    }
  }
  spids.resize (nrspid);
  return spids;
}

} // namespace MEQ
