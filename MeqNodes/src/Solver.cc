//# Solver.cc: Base class for an expression node
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


// Needed for Aips++ array and matrix assignments for DMI
#define AIPSPP_HOOKS

#include <MEQ/Request.h>
#include <MEQ/Vells.h>
#include <MEQ/Function.h>
#include <MEQ/MeqVocabulary.h>
#include <MEQ/Forest.h>
#include <MeqNodes/Solver.h>
#include <MeqNodes/Condeq.h>
#include <MeqNodes/ParmTable.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <casa/Arrays/Matrix.h>
#include <casa/Arrays/Vector.h>
#include <DMI/List.h>

#include <iostream>

using namespace std;

using namespace casa;

namespace Meq {

InitDebugContext(Solver,"MeqSolver");

const HIID FTileSize = AidTile|AidSize;

const HIID FSolverResult = AidSolver|AidResult;
const HIID FIncrementalSolutions = AidIncremental|AidSolutions;

const HIID FIterationSymdeps = AidIteration|AidSymdeps;
const HIID FIterationDependMask = AidIteration|AidDepend|AidMask;

const HIID FDebugLevel = AidDebug|AidLevel;

#if LOFAR_DEBUG
const int DefaultDebugLevel = 100;
#else
const int DefaultDebugLevel = 0;
#endif

//##ModelId=400E53550260
Solver::Solver()
: flag_mask_        (-1),
  do_save_funklets_ (false),
  do_last_update_   (false),
  use_svd_          (true),
  max_num_iter_     (3),
  min_epsilon_      (0),
  debug_lvl_        (DefaultDebugLevel),
  parm_group_       (AidParm),
  solver_           (1),
  strides_          (0)
{
  // set Solver dependencies
  iter_symdeps_.assign(1,FIteration);
  const HIID symdeps[] = { FDomain,FResolution,FDataset,FIteration };
  setKnownSymDeps(symdeps,4);
  const HIID symdeps1[] = { FDomain,FResolution,FDataset };
  setActiveSymDeps(symdeps1,3);
}

//##ModelId=400E53550261
Solver::~Solver()
{
  if( strides_ )
    delete [] strides_;
}

//##ModelId=400E53550263
TypeId Solver::objectType() const
{
  return TpMeqSolver;
}

// do nothing here -- we'll do it manually in getResult()
//##ModelId=400E5355026B
int Solver::pollChildren (std::vector<Result::Ref> &chres,
                          Result::Ref &resref,const Request &request)
{
  // a request that has cells in it is a solve request -- do not pass it to the
  // children, as we'll be doing our own polling in getResult() below
  if( request.hasCells() )
    return 0;
  // A cell-less request contains commands and states only, and thus it should
  // passed on to the children as is. (This request will never make it to our
  // getResult())
  else
    return Node::pollChildren(chres,resref,request);
}

int Solver::populateSpidMap (const DMI::Record &spidmap_rec,const Cells &cells)
{
  parm_uks_.clear();
  spids_.clear();
  // convert spid map record into internal spid map, and count up the unknowns
  for( DMI::Record::const_iterator iter = spidmap_rec.begin(); 
      iter != spidmap_rec.end(); iter++ )
  {
    // each spidmap entry is expected to be a record
    const DMI::Record &rec = iter.ref().as<DMI::Record>();
        VellSet::SpidType spid = iter.id()[0].id();  // spid is first element of HIID
    // insert entry into spid table
    SpidInfo & spi = spids_[spid];     
    spi.uk_index  = num_unknowns_;
    spi.nuk = 1;
    // OK, figure out tiling
    memset(spi.tile_size,0,sizeof(spi.tile_size));
    int sz;
    const int *ptiles = rec[FTileSize].as_po<int>(sz);
    if( ptiles )
    {
      int rank = std::min(sz,Axis::MaxAxis);
      int stride = 1;
      for( int i=rank-1; i>=0; i-- )
      {
        int tsz = spi.tile_size[i] = ptiles[i];
        spi.tile_stride[i] = stride;
        // is this axis tiled by the spid?
        if( tsz )
        {
          int nc = cells.ncells(i);
          int ntiles = nc/tsz + ((nc%tsz)?1:0);     // a minimum of 1 tile always
          spi.nuk *= ntiles;
          stride *= ntiles;
        }
      }
    }
    // increment count of unknowns
    num_unknowns_ += spi.nuk;
    // add unknown's indices to map for this nodeindex
    IndexSet &iset = parm_uks_[rec[FNodeIndex].as<int>()];
    for( int i = spi.uk_index; i<num_unknowns_; i++ )
      iset.insert(i);
  }
  return num_unknowns_;
}

// This is a helper function for fillEquations(). Note that this function 
// encapsulates the only difference in the code between the double
// and the complex case. This allows us to have a single templated 
// definition of fillEquations() below which works for both cases.
template<typename T>
inline void Solver::fillEqVectors (int npert,int uk_index[],
      const T &diff,const std::vector<Vells::ConstStridedIterator<T> > &deriv_iter)
{
  // fill vectors of derivatives for each unknown 
  for( int i=0; i<npert; i++ )
    deriv_real_ [i] = *deriv_iter[i];
  if( Debug(4) )
  {
    cdebug(4)<<"equation: ";
    for( int i=0; i<npert; i++ )
      ::Debug::getDebugStream()<<uk_index[i]<<":"<<deriv_real_[i]<<" "; 
    ::Debug::getDebugStream()<<" -> "<<diff<<endl;
  }
  // add equation to solver
  solver_.makeNorm(npert,uk_index,&deriv_real_[0],1.,diff);
  num_equations_++;
}

// Specialization for complex case: each value produces two equations
template<>
inline void Solver::fillEqVectors (int npert,int uk_index[],
      const dcomplex &diff,const std::vector<Vells::ConstStridedIterator<dcomplex> > &deriv_iter)
{
  // fill vectors of derivatives for each unknown 
  for( int i=0; i<npert; i++ )
  {
    deriv_real_[i] = (*deriv_iter[i]).real();
    deriv_imag_[i] = (*deriv_iter[i]).imag();
  }
  if( Debug(4) )
  {
    cdebug(4)<<"equation: ";
    for( int i=0; i<npert; i++ )
    { 
      ::Debug::getDebugStream()<<uk_index[i]<<":"<<deriv_real_[i]<<","<<deriv_imag_[i]<<" "; 
    }
    ::Debug::getDebugStream()<<" -> "<<diff<<endl;
  }
  // add equation to solver
  solver_.makeNorm(npert,uk_index,&deriv_real_[0],1.,diff.real());
  num_equations_++;
  solver_.makeNorm(npert,uk_index,&deriv_imag_[0],1.,diff.imag());
  num_equations_++;
}

template<typename T>
void Solver::fillEquations (const VellSet &vs)
{
  int npert = vs.numSpids();
  FailWhen(npert>num_spids_,ssprintf("child %d returned %d spids, but only "
            "%d were reported during spid discovery",cur_child_,npert,num_spids_));
  const Vells &diffval = vs.getValue();

  // ok, this is where it gets hairy. The main val and each pertval 
  // could, in principle, have a different set of variability axes 
  // (that is, their shape along any axis can be equal to 1, to indicate
  // no variability). This is the same problem we deal with in Vells 
  // math, only on a grander scale, since here N+2 Vells have to 
  // be iterated over simultaneously (1 driving term, N derivatives,
  // 1 flag vells). Fortunately Vells math provides some help here
  // in the form of strided iterators
  SpidInfo *pspi[npert];    // spid map for each derivative looked up in advance
  Vells::Shape outshape;          // output shape: superset of input shapes
  // fill in shape arrays for computeStrides() below
  const Vells::Shape * shapes[npert+2];
  int uk_index[npert];            // index of current unknown per each 
  // derivative (since we may have multiple unknowns per spid due to tiling,
  // we keep track of the current one when filling equations)
  shapes[0] = &( diffval.shape() );
  shapes[1] = &( diffval.flagShape() ); // returns null shape if no flags
  int j=2;
  // go over derivatives, find spids in map, fill in shapes
  for( int i=0; i<npert; i++,j++ )
  {
    // find spid in map, and save pointer to map entry
    VellSet::SpidType spid = vs.getSpid(i);
    SpidMap::iterator iter = spids_.find(vs.getSpid(i));
    FailWhen(iter == spids_.end(),ssprintf("child %d returned spid %d that was "
            "not reported during spid discovery",cur_child_,spid));
    SpidInfo &spi = iter->second;
    pspi[i] = &spi;
    // init various indices
    uk_index[i] = spi.uk_index;
    for( int ii=0; ii<Axis::MaxAxis; ii++ )
    {
      spi.tile_index[ii] = 0;
      spi.tile_uk0[ii] = spi.uk_index;
    }
    // get shape of derivative
    shapes[j] = &( vs.getPerturbedValue(i).shape() );
  }
  // compute output shape (the union of all input shapes), and
  // strides for all vells 
  Vells::computeStrides(outshape,strides_,npert+2,shapes,"Solver::getResult");
  int outrank = outshape.size();
  // create strided iterators for all vells
  Vells::ConstStridedIterator<T> diff_iter(diffval,strides_[0]);
  Vells::ConstStridedFlagIterator flag_iter(diffval,strides_[1]);
  std::vector<Vells::ConstStridedIterator<T> > deriv_iter(npert);
  j=2;
  for( int i=0; i<npert; i++,j++ )
    deriv_iter[i] = Vells::ConstStridedIterator<T>(vs.getPerturbedValue(i),strides_[j]);
  // create counter for output shape
  Vells::DimCounter counter(outshape);
  // now start generating equations. repeat while counter is valid
  // (we break out below, when incrementing the counter)
  while( true )
  {
    // fill equations only if unflagged...
    if( !(*flag_iter&flag_mask_) )
      fillEqVectors(npert,uk_index,*diff_iter,deriv_iter);
    // increment counter and all iterators
    int ndim = counter.incr(); 
    if( !ndim )    // break out when counter is finished
      break;
    diff_iter.incr(ndim);
    flag_iter.incr(ndim);
    for( int ipert=0; ipert<npert; ipert++ )
    {
      deriv_iter[ipert].incr(ndim);
      // if this is a tiled spid, we need to figure out whether we
      // have changed tiles, and what the new uk_index is
      SpidInfo &spi = *pspi[ipert];
      if( spi.nuk > 1 )
      {
        // ndim tells us how many dimensions we have advanced over
        // (with the last dimension iterating the fastest)
        // That is, index N-ndim has been incremented, while indices
        // N-ndim+1 ... N-1 have been reset to 0. Work out our tile
        // numbers appropriately
        int idim = outrank - ndim;  // idim=N-ndim, the incremented dimension
        // Reset unknown index for this dimension to beginning of slice.
        // tile_uki0[i] is the index of the start of the slice for the
        // current values of tile indices 0...i-1.
        int uk0 = spi.tile_uk0[idim];
        if( spi.tile_size[idim] )
        {
          int ti = spi.tile_index[idim] = counter.counter(idim) / spi.tile_size[idim];
          // work out start of slice for indices 0...idim-1,idim
          uk0 += ti * spi.tile_stride[idim];
        }
        // this is the new uk_index then
        uk_index[ipert] = uk0;
        // reset the remaining tile indices to 0, and update
        // their slice starting points
        for( idim++; idim < outrank; idim++ )
        {
          spi.tile_uk0[idim] = uk0;
          spi.tile_index[idim] = 0;
        }
      }
    }
  }
}        


// Get the result for the given request.
//##ModelId=400E53550270
int Solver::getResult (Result::Ref &resref, 
                       const std::vector<Result::Ref> &,
                       const Request &request, bool newreq)
{
  // Use single derivative by default, or a higher mode if specified in request
  int eval_mode = std::max(request.evalMode(),int(Request::DERIV_SINGLE));
  // The result has no planes, all solver information is in extra fields
  Result& result = resref <<= new Result(0);
  DMI::Record &solveResult = result[FSolverResult] <<= new DMI::Record;
  // Keep a copy of the solver result in the state record, so that per-iteration metrics
  // can be tracked while debugging
  wstate()[FSolverResult].replace() <<= &solveResult;
  DMI::List & metricsList = solveResult[FMetrics] <<= new DMI::List;
  DMI::List * pDebugList = 0;
  if( debug_lvl_>0 )
    solveResult["Debug"] <<= pDebugList = new DMI::List;
  // get the request ID -- we're going to be incrementing the iteration index
  RequestId rqid = request.id();
  RqId::setSubId(rqid,iter_depmask_,0);      // current ID starts at 0
  RequestId next_rqid = rqid;  
  RqId::incrSubId(next_rqid,iter_depmask_);  // next ID is iteration 1
  // Now, generate a "service" request that will 
  // (a) setup our solvables
  // (b) do spid discovery
  Request::Ref reqref;
  Request &req = reqref <<= new Request(request.cells(),Request::DISCOVER_SPIDS,rqid);
  // rider of original request gets sent up along with it
  req.copyRider(request);
  req.setServiceFlag(true);
  // do we have a solvables spec in our state record?
  const DMI::Record *solvables = state()[FSolvable].as_po<DMI::Record>();
  if( solvables )
  {
    DMI::Record& rider = Rider::getRider(reqref);
    rider[parm_group_].replace() <<= wstate()[FSolvable].as_wp<DMI::Record>();
  } 
  else 
  {
    // no solvables specified -- clear the group record, and assume parms have been
    // set solvable externally somehow
    Rider::getGroupRec(reqref,parm_group_,Rider::NEW_GROUPREC);
  }
  reqref().validateRider();
  // send up request to figure out spids. We can poll syncronously since there's
  // nothing for us to do until all children have returned
  int retcode = Node::pollChildren(child_results_,resref,*reqref);
  if( retcode&(RES_FAIL|RES_WAIT) )
    return retcode;
  // Node's standard discoverSpids() implementation merges all child spids together
  // into a result object. This is exactly what we need here
  Result::Ref tmpres;
  Node::discoverSpids(tmpres,child_results_,req);
  // discard child results
  for( uint i=0; i<child_results_.size(); i++ )
    child_results_[i].detach();
  // ok, now we should have a spid map
  num_unknowns_ = 0;
  if( tmpres.valid() )
  {
    const DMI::Record * pspid_map = tmpres[FSpidMap].as_po<DMI::Record>();
    if( pspid_map )
    {
      // insert a copy of spid map record into the solver result
      solveResult[FSpidMap].replace() <<= pspid_map;
      // populate our map from the record
      populateSpidMap(*pspid_map,request.cells());
    }
  }
  if( !num_unknowns_ )
  {
    // no unknowns/spids discovered, so may as well fail...
    Throw("spid discovery did not return any solvable parameters");
  }
  num_spids_ = spids_.size();
  solver_.set(num_unknowns_);
  cdebug(2)<<"solver initialized for "<<num_unknowns_<<" unknowns\n";
  
  // resize temporaries used in fillEquations()
  deriv_real_.resize(num_unknowns_);
  deriv_imag_.resize(num_unknowns_);
  // ISO C++ won't allow a vector of Strides, hence this old-style kludge
  if( strides_ )
    delete [] strides_;
  strides_ = new Vells::Strides[num_spids_+2];
  // and other stuff used during solution
  Vector<double> solution(num_unknowns_);   // solution vector from solver
  
  // matrix of incremental solutions -- allocate directly in solver
  // result so that it stays visible in our state record (handy
  // when debugging trees, for instance)
  DMI::NumArray & allSolNA = solveResult[FIncrementalSolutions] 
        <<= new DMI::NumArray(Tpdouble,LoShape(max_num_iter_,num_unknowns_));
  LoMat_double & incr_solutions = allSolNA.getArray<double,2>();
  
  // OK, now create the "real" request object. This will be modified from 
  // iteration to iteration, so we keep it attached to reqref and rely on COW
  reqref <<= new Request(request.cells(),eval_mode);
  int step;
  for( step=0; step < max_num_iter_; step++ ) 
  {
    // increment the solve-dependent parts of the request ID
    rqid = next_rqid;
    RqId::incrSubId(next_rqid,iter_depmask_);
    // set request Ids in the request object
    reqref().setId(rqid);
    reqref().setNextId(next_rqid);
    num_equations_ = 0;
    // start async child poll
    startAsyncPoll(*reqref);
    int rescode;
    Result::Ref child_res;
    // wait for child results until all have been polled (await will return -1 when this is the case)
    std::list<Result::Ref> child_fails;  // any fails accumulated here
    while( (cur_child_ = awaitChildResult(rescode,child_res,*reqref)) >= 0 )
    {
      // tell child to hold cache if it doesn't depend on iteration
      getChild(cur_child_).holdCache(!(rescode&iter_depmask_));
//    setExecState(CS_ES_EVALUATING);
      // has the child failed? 
      if( rescode&RES_FAIL )
      {
        child_fails.push_back(child_res);
        continue;
      }
      // has the child asked us to wait?
      if( rescode&RES_WAIT )  // this never happens, so ok to return for now
        return rescode;
      // treat each vellset in the result independently
      for( int ivs = 0; ivs < child_res->numVellSets(); ivs++ )
      {
        const VellSet &vs = child_res->vellSet(ivs);
        // ignore failed or null vellsets
        if( vs.isFail() || vs.isNull() )
          continue;
        if( vs.getValue().isReal() )
          fillEquations<double>(vs);
        else
          fillEquations<dcomplex>(vs);
      }
    } // end of loop over children
    FailWhen(!num_equations_,"no equations were generated");
    cdebug(4)<<"accumulated "<<num_equations_<<" equations\n";
    // Solve the equation.
    DMI::Record * pSolRec = new DMI::Record;
    metricsList.addBack(pSolRec);
    DMI::Record * pDebug = 0;
    if( pDebugList )
      pDebugList->addBack(pDebug = new DMI::Record);
    solve(solution,reqref,*pSolRec,pDebug,do_save_funklets_ && step == max_num_iter_-1);
    // copy solutions vector to allSolutions row
    incr_solutions(step,LoRange::all()) = B2A::refAipsToBlitz<double,1>(solution);
  }
  // send up one final update if needed
  if( do_last_update_ && step == max_num_iter_ )
  {
    // reqref will have already been populated with updates by solve() above.
    // However, we want to clear out the cells to avoid re-evaluation, so
    // we create another request object here and copy over the rider
    Request::Ref lastref;
    Request &lastreq = lastref <<= new Request;
    lastreq.setId(next_rqid);
    // note that this is not a service request, since it doesn't imply 
    // any state changes
    lastreq.copyRider(*reqref);
    lastreq.setNextId(request.nextId());
    ParmTable::lockTables();
    Node::pollChildren(child_results_, resref, lastreq);
    ParmTable::unlockTables();
  }
  // if we broke out of the loop because of some other criterion, we need
  // to crop the incremental solutions matrix to [0:step-1,*]
  if( step < max_num_iter_ )
  {
    // create new array and copy subarray of incremental solutions into it
    DMI::NumArray::Ref arr_ref;
    arr_ref <<= new NumArray(Tpdouble,LoShape(step,num_unknowns_));
    arr_ref().getArray<double,2>() = incr_solutions(LoRange(0,step),LoRange::all());
    // replace incr_solutions in solver result
    solveResult[FIncrementalSolutions].replace() <<= arr_ref;
  }
  return 0;
}


// helper function to copy a triangular matrix (from solver object)
// to a proper square matrix
template<class T>
static DMI::NumArray::Ref triMatrix (T *tridata,int n)
{
  DMI::NumArray::Ref out(new DMI::NumArray(typeIdOf(T),LoShape(n,n)));
  blitz::Array<T,2> & arr = out().getArray<T,2>();
  for( int row=0; row<n; row++ )
  {
    int len = n-row;
    arr(row,LoRange(0,len-1)) = blitz::Array<T,1>(tridata,LoShape1(len),blitz::neverDeleteData);
    tridata += len;
  }
  return out;
}

//====================>>>  Solver::solve  <<<====================

void Solver::solve (Vector<double>& solution,Request::Ref &reqref,
                    DMI::Record& solRec,DMI::Record * pDebugRec,
                    bool saveFunklets)
{
  reqref().clearRider();
  solution = 0;
  // It looks as if in LSQ solveLoop and getCovariance
  // interact badly (maybe both doing an invert).
  // So make a copy to separate them.
  uint rank;
  double fit;
  Matrix<double> covar;
  Vector<double> errors;

  // Make a copy of the solver for the actual solve.
  // This is needed because the solver does in-place transformations.
  ////  FitLSQ solver = solver_;
  bool solFlag = solver_.solveLoop (fit, rank, solution, use_svd_);

  // {
  LSQaips tmpSolver(solver_);
    // both of these calls produce SEGV in certain situations; commented out until
    // Wim or Ger fixes it
    //cdebug(1) << "result_covar = solver_.getCovariance (covar);" << endl;
    //bool result_covar = solver_.getCovariance (covar);
   //cdebug(1) << "result_errors = solver_.getErrors (errors);" << endl;
   bool result_errors = tmpSolver.getErrors (errors);
    //cdebug(1) << "result_errors = " << result_errors << endl;
 // }
  
  
  cdebug(4)<<"solution after: " << solution << ", rank " << rank << endl;
  // Put the statistics in a record the result.
  solRec[FRank]   = int(rank);
  solRec[FFit]    = fit;
  solRec[FErrors] = errors;
  //solRec[FCoVar ] = covar; 
  solRec[FFlag]   = solFlag; 
  solRec[FMu]     = solver_.getWeightedSD();
  solRec[FStdDev] = solver_.getSD();
  //  solRec[FChi   ] = solver_.getChi());
  // Put debug info
  if( pDebugRec )
  {
    DMI::Record &dbg = *pDebugRec;
    uint nun,np,ncon,ner,rank;
    double * nEq,*known,*constr,*er,*sEq,*sol,prec,nonlin;
    uint * piv;
    solver_.debugIt(nun,np,ncon,ner,rank,nEq,known,constr,er,piv, sEq,sol,prec,nonlin);
    if( nEq )
      dbg["$nEq"] = triMatrix(nEq,nun);
    dbg["$known"] = LoVec_double(known,LoShape1(np),blitz::neverDeleteData);
    if( ncon )
      dbg["$constr"] = LoMat_double(constr,LoShape2(ncon,nun),blitz::neverDeleteData,blitz::ColumnMajorArray<2>());
    dbg["$er"] = LoVec_double(er,LoShape1(ner),blitz::neverDeleteData);
    dbg["$piv"] = LoVec_int(reinterpret_cast<int*>(piv),LoShape1(np),blitz::neverDeleteData);
    if( sEq )
      dbg["$sEq"] = triMatrix(sEq,np);
    dbg["$sol"] = LoVec_double(sol,LoShape1(np),blitz::neverDeleteData);
    dbg["$prec"] = prec;
    dbg["$nonlin"] = nonlin;
  }
  
  // Put the solution in the rider:
  //    [FRider][<parm_group>][CommandByNodeIndex][<parmid>]
  // will contain a DMI::Record for each parm 
  DMI::Record& grouprec = Rider::getCmdRec_ByNodeIndex(reqref,parm_group_,
                                                       Rider::NEW_GROUPREC);
  
  for( ParmUkMap::const_iterator iparm = parm_uks_.begin(); 
       iparm != parm_uks_.end(); iparm++ )
  {
    int nodeindex = iparm->first;
    // create command record for this parm
    DMI::Record & cmdrec = grouprec[nodeindex] <<= new DMI::Record;
    const IndexSet & idxset = iparm->second;
    // create vector of updates and get pointer to its data
    DMI::NumArray &arr = cmdrec[FUpdateValues] <<= new DMI::NumArray(Tpdouble,LoShape(idxset.size()));
    double *pupd = static_cast<double*>(arr.getDataPtr());
    int j=0;
    // fill updates for this node's spids, by fetching them from the solution 
    // vector one by one via the index set
    for( IndexSet::const_iterator ii = idxset.begin(); ii != idxset.end(); ii++ )
      pupd[j++] = solution(*ii);
    // add save command if requested
    if( saveFunklets )
      cmdrec[FSaveFunklets] = true;
  }
  // make sure the request rider is validated
  reqref().validateRider();
  ParmTable::unlockTables();
}

//##ModelId=400E53550267
void Solver::setStateImpl (DMI::Record::Ref & newst,bool initializing)
{
  Node::setStateImpl(newst,initializing);
  // get the parm group
  newst[FParmGroup].get(parm_group_,initializing);
  // get symdeps for iteration and solution
  // recompute depmasks if active sysdeps change
  if( newst[FIterationSymdeps].get_vector(iter_symdeps_,initializing) || initializing )
    wstate()[FIterationDependMask] = iter_depmask_ = computeDependMask(iter_symdeps_);
  // now reset the dependency mask if specified; this will override
  // possible modifications made above
  newst[FIterationDependMask].get(iter_depmask_,initializing);

  // get debug flag
  newst[FDebugLevel].get(debug_lvl_,initializing);
  // get other solver parameters
  newst[FFlagMask].get(flag_mask_,initializing);
  newst[FSaveFunklets].get(do_save_funklets_,initializing);  
  newst[FLastUpdate].get(do_last_update_,initializing);  
  newst[FUseSVD].get(use_svd_,initializing);  
  newst[FNumIter].get(max_num_iter_,initializing);  
  newst[FEpsilon].get(min_epsilon_,initializing);
}


} // namespace Meq

//# Instantiate the makeNorm template.
#include <scimath/Fitting/LSQFit2.cc>
template void casa::LSQFit::makeNorm<double, double*, int*>(unsigned,
int* const&, double* const&, double const&, double const&, bool, bool);

