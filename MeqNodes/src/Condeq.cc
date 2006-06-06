//# Condeq.cc: Base class for an expression node
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

#include <MeqNodes/AID-MeqNodes.h>
#include <MeqNodes/Condeq.h>
#include <MEQ/Function.h>
#include <MEQ/Vells.h>
    

namespace Meq {

const HIID FModulo = AidModulo;

//##ModelId=400E5305005F
Condeq::Condeq()
  : Function(2),modulo_(0)
{
  children().setMissingDataPolicy(AidAbandonPropagate);
  setAutoResample(RESAMPLE_FAIL); // children must return the same cells
}

//##ModelId=400E53050060
Condeq::~Condeq()
{}

//##ModelId=400E53050062
TypeId Condeq::objectType() const
{
  return TpMeqCondeq;
}

//##ModelId=400E53550233
void Condeq::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  rec[FModulo].get(modulo_,initializing);
  is_modulo_ = ( modulo_ != 0 );
}

// helper func to compute derivative 
inline double Condeq::calcDerivative (Vells &deriv,const VellSet &vs,int index,bool minus)
{
  double pert;
  int npertsets = vs.numPertSets();
  if( npertsets == 1 )
  {
    pert = vs.getPerturbation(index);
    deriv = ( minus 
              ? vs.getValue() - vs.getPerturbedValue(index) 
              : vs.getPerturbedValue(index) - vs.getValue() );


  }
  else if( npertsets == 2 )
  {
    pert = vs.getPerturbation(index,0) - vs.getPerturbation(index,1);
    deriv = ( minus 
              ? vs.getPerturbedValue(index,1) - vs.getPerturbedValue(index,0) 
              : vs.getPerturbedValue(index,0) - vs.getPerturbedValue(index,1) );
  }
  else
  {
    NodeThrow1("illegal number of perturbation sets in result");
  }
  if( is_modulo_ )
    deriv = VellsMath::remainder(deriv,modulo_);
  deriv /= pert;
  return pert;
}

using VellsMath::tocomplex;

//##ModelId=400E53050066
int Condeq::getResult (Result::Ref &resref, 
                       const std::vector<Result::Ref> &child_result,
                       const Request &request,bool)
{
  int nrch = child_result.size();
  Assert(nrch==2);
  // Figure out the dimensions of the output result, and see that children
  // match these dimensions. 
  Result::Dims out_dims = child_result[0]->dims();
  if( !child_result[1]->dims().empty() ) // child 1 is a tensor
  {
    if( out_dims.empty() )               // child 0 is a scalar
      out_dims = child_result[1]->dims();
    else         // both tensors, verify match
    {
      FailWhen(out_dims != child_result[1]->dims(),"dimensions of tensor child results do not match");
    }
  }
  // Create result object and attach to the ref that was passed in
  Result & result = resref <<= new Result(out_dims);
  int nplanes = result.numVellSets(); // total number of output elements
  
  vector<const VellSet*> child_vs(nrch);
  for( int iplane=0; iplane<nplanes; iplane++ )
  {
    Vells::Ref flagref;
    // collect vector of pointers to children, and vector
    // of pointers to main value
    vector<const Vells*> values(nrch);
    int npertsets;
    bool missing_data = false;
    for( int i=0; i<nrch; i++ )
    {
      const Result &chres = *child_result[i];
      const VellSet &vs = chres.vellSet(chres.tensorRank()>0 ? iplane : 0);
      if( !vs.hasValue() )
      {
        missing_data = true;
        break;
      }
      child_vs[i] = &vs;
      // merge in flags, if any
      if( vs.hasDataFlags() )
        if( flagref.valid() )
          flagref() |= vs.dataFlags();
        else
          flagref.attach(vs.dataFlags());
      values[i] = &( vs.getValue() );
    }
    // null vellsert on any child produces null output
    if( missing_data )
    {
      result.setNewVellSet(iplane);
      continue;
    }
    // Find all spids from the children.
    vector<int> spids = Function::findSpids(npertsets,child_vs);
    // allocate new result object with given number of spids, add to set
    // note that result always has 1 perturbation set (i.e., double-perts
    // are collapsed into a single pert)
    VellSet &vellset = result.setNewVellSet(iplane,spids.size(),1);
    // The main value is measured-predicted.
    Vells mainval = *values[1] - *values[0];
    if( is_modulo_ )
      mainval = VellsMath::remainder(mainval,modulo_);
    vellset.setValue(mainval);
    bool force_complex = mainval.isComplex();
    // set flags if any
    if( flagref.valid() )
      vellset.setDataFlags(flagref);
    // Evaluate all perturbed values.
    vector<Vells*> perts(nrch);
    vector<int> indices(nrch, 0);
    Vells::Ref deriv_ref;
    for( uint j=0; j<spids.size(); j++ )
    {
      Vells & deriv = deriv_ref <<= new Vells;
      int inx0 = child_vs[0]->isDefined(spids[j],indices[0]);
      int inx1 = child_vs[1]->isDefined(spids[j],indices[1]);
      double pert = 0;
      if (inx1 >= 0) 
      {
        pert = calcDerivative(deriv,*child_vs[1],inx1,true);
        if (inx0 >= 0) 
        {
          Vells d1;
          calcDerivative(d1,*child_vs[0],inx0,true);
          deriv -= d1;
        }
      }
      else if (inx0 >= 0) 
      {
        pert = calcDerivative(deriv,*child_vs[0],inx0);
      }      
      else 
        deriv = Vells(0.);
      // check if we need to cast to complex
      if( force_complex )
      {
        if( !deriv.isComplex() )
          deriv = tocomplex(deriv,0);
      }
      else if( deriv.isComplex() ) // started not complex, but found a complex derivative, so need to convert everything
      {
        force_complex = true;
        vellset.setValue(tocomplex(mainval,0));
        for( uint j1=0; j1<j; j1++ )
          vellset.setPerturbedValue(j1,tocomplex(vellset.getPerturbedValue(j1),0));
      }
      vellset.setPerturbedValue(j,deriv_ref);
      vellset.setPerturbation(j,pert);
    }
    vellset.setSpids (spids);
  }
  // no dependencies introduced
  return 0;
}


} // namespace Meq
