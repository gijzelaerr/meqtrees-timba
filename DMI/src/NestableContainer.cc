//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC830069.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC830069.cm

//## begin module%3C10CC830069.cp preserve=no
//## end module%3C10CC830069.cp

//## Module: NestableContainer%3C10CC830069; Package body
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar8\oms\LOFAR\DMI\src\NestableContainer.cc

//## begin module%3C10CC830069.additionalIncludes preserve=no
//## end module%3C10CC830069.additionalIncludes

//## begin module%3C10CC830069.includes preserve=yes
#include <list>
//## end module%3C10CC830069.includes

// NestableContainer
#include "NestableContainer.h"
//## begin module%3C10CC830069.declarations preserve=no
//## end module%3C10CC830069.declarations

//## begin module%3C10CC830069.additionalDeclarations preserve=yes
DefineRegistry(NestableContainer,False);
//## end module%3C10CC830069.additionalDeclarations


// Class NestableContainer::ConstHook 

// Additional Declarations
  //## begin NestableContainer::ConstHook%3C614FDE0039.declarations preserve=yes
  //## end NestableContainer::ConstHook%3C614FDE0039.declarations

// Class NestableContainer::Hook 


//## Other Operations (implementation)
bool NestableContainer::Hook::isWritable () const
{
  //## begin NestableContainer::Hook::isWritable%3C87665E0178.body preserve=yes
  TypeId tid; bool write;
  const void *target = collapseIndex(tid,write,0,False);
  // doesn't exist? It's writable if our container is writable
  if( !target )
    return nc->isWritable();
  // is it a reference? Deref it then
  if( tid == TpObjRef )
  {
    if( !static_cast<const ObjRef*>(target)->isWritable() ) // non-writable ref?
      return False;
    target = &static_cast<const ObjRef*>(target)->deref();
    tid = static_cast<const BlockableObject*>(target)->objectType();
  }
  // is it a sub-container? Return its writable property
  if( NestableContainer::isNestable(tid) )
    return static_cast<const NestableContainer*>(target)->isWritable();
  // otherwise, it's writable according to what collapseIndex() returned
  return write;
  //## end NestableContainer::Hook::isWritable%3C87665E0178.body
}

const NestableContainer::Hook & NestableContainer::Hook::init (TypeId tid) const
{
  //## begin NestableContainer::Hook::init%3C8739B5017B.body preserve=yes
  FailWhen(addressed,"unexpected '&' operator");
  TypeId target_tid;
  prepare_put(target_tid,tid);
  return *this;
  //## end NestableContainer::Hook::init%3C8739B5017B.body
}

const NestableContainer::Hook & NestableContainer::Hook::privatize (int flags) const
{
  //## begin NestableContainer::Hook::privatize%3C8739B5017C.body preserve=yes
  FailWhen(addressed,"unexpected '&' operator");
  bool dum; TypeId tid;
  if( index<0 )
    nc->get(id,tid,dum,0,False,flags);
  else
    nc->getn(index,tid,dum,0,False,flags);
  return *this;
  //## end NestableContainer::Hook::privatize%3C8739B5017C.body
}

ObjRef NestableContainer::Hook::remove () const
{
  //## begin NestableContainer::Hook::remove%3C876DCE0266.body preserve=yes
  FailWhen(!nc->isWritable(),"r/w access violation");
  ObjRef ret;
  if( isRef() )
  {
    // cast away const here: even though ref may be read-only, as long as the 
    // container is writable, we're allowed to detach it
    ObjRef *ref0 = const_cast<ObjRef*>( asRef(False) );
    ret.xfer(ref0->unlock());
  }
  index >= 0 ? nc->removen(index) : nc->remove(id);
  return ret;
  //## end NestableContainer::Hook::remove%3C876DCE0266.body
}

const NestableContainer::Hook & NestableContainer::Hook::detach (ObjRef* ref) const
{
  //## begin NestableContainer::Hook::detach%3C876E140018.body preserve=yes
  FailWhen(!nc->isWritable(),"r/w access violation");
  // cast away const here: even though ref may be read-only, as long as the 
  // container is writable, we can still detach it
  ObjRef *ref0 = const_cast<ObjRef*>( asRef(False) );
  ref0->unlock();
  if( ref )
    ref->xfer(*ref0);
  else
    ref0->detach();
  return *this;
  //## end NestableContainer::Hook::detach%3C876E140018.body
}

// Additional Declarations
  //## begin NestableContainer::Hook%3C8739B50135.declarations preserve=yes
  //## end NestableContainer::Hook%3C8739B50135.declarations

// Class NestableContainer 


//## Other Operations (implementation)
NestableContainer::Hook NestableContainer::setBranch (const HIID &id, int flags)
{
  //## begin NestableContainer::setBranch%3CB2B438020F.body preserve=yes
  FailWhen(!isWritable(),"write access violation");
  // auto-privatize everything for write -- let Hook do it
  if( flags&DMI::PRIVATIZE && flags&DMI::WRITE )
  {
    dprintf(2)("privatizing branch %s\n",id.toString().c_str());
    // auto-privatizing hook
    Hook hook(*this,id,DMI::WRITE);
    if( flags&DMI::DEEP )
      hook.privatize(DMI::WRITE|DMI::DEEP);
    return hook;
  }
  // else it's a privatize only as needed
  FailWhen( !flags&DMI::WRITE,"invalid flags");
  dprintf(2)("ensuring writability of branch %s\n",id.toString().c_str());
  // During first pass, we go down the branch to figure out the writability
  // of each container. To privatize the final element (if this is required), 
  // we need to privatize everything starting from the _last_ writable container 
  // in the chain.
  list<BranchEntry> branch;
  HIID id0,id1=id;    
  NestableContainer *nc = this;
  bool writable = isWritable();
  // note that if entire branch is to be privatized read-only, we'll 
  // auto-privatize it for writing during the first pass. This more or less 
  // insures that a clone is made.
  Hook hook(*this,-2); 
  // form list of branch elements
  int index=0,last_writable=-1,last_ref=-1;
  while( id1.size() )
  {
    // split off next subscript
    BranchEntry be;
    be.id = id1.splitAtSlash();
    if( id0.size() )
      id0 |= AidSlash;
    id0 |= be.id;
    if( !be.id.size() ) // ignore if null
      continue;
    // cast away const but that's OK since we track writability
    be.nc = const_cast<NestableContainer*>(hook.asNestable());  // container pointed to by current hook
    // apply subscript to current hook 
    if( be.nc && be.nc->isWritable() )
      last_writable = index; // keeps track of last writable container in chain
    hook[be.id];
    writable = be.writable = hook.isWritable();
    branch.push_back(be);
    index++;
  }
  // is the last hook writable? Just return it
  if( hook.isWritable() )
  {
    dprintf(2)("last branch element is writable already\n");
    return hook;
  }
  // else restart at the last writable container
  // Start with initial hook again, and apply subscripts until we
  // reach the writable container
  FailWhen( last_writable<0,"unable to privatize: complete branch is read-only");
  dprintf(2)("privatizing starting from branch element %d\n",last_writable);
  Hook hook1(*this,-2); 
  list<BranchEntry>::const_iterator iter = branch.begin();
  for( int i=0; i<last_writable; i++,iter++ )
    hook1[iter->id];
  Assert(iter != branch.end() && iter->nc->isWritable() );
  hook1.autoprivatize = DMI::WRITE;  // enable auto-privatize
  // apply remaining subscripts
  for( ; iter != branch.end(); iter++ )
    hook1[iter->id];
  // return the hook
  return hook1;
  //## end NestableContainer::setBranch%3CB2B438020F.body
}

bool NestableContainer::select (const HIIDSet &)
{
  //## begin NestableContainer::select%3BE982760231.body preserve=yes
  return False;
  //## end NestableContainer::select%3BE982760231.body
}

void NestableContainer::clearSelection ()
{
  //## begin NestableContainer::clearSelection%3BFBDC0D025A.body preserve=yes
  //## end NestableContainer::clearSelection%3BFBDC0D025A.body
}

int NestableContainer::selectionToBlock (BlockSet& )
{
  //## begin NestableContainer::selectionToBlock%3BFBDC1D028F.body preserve=yes
  return 0;
  //## end NestableContainer::selectionToBlock%3BFBDC1D028F.body
}

// Additional Declarations
  //## begin NestableContainer%3BE97CE100AF.declarations preserve=yes

// Attempts to treat the hook target as an NC, by collapsing subscripts,
// dereferencing ObjRefs, etc.
const NestableContainer * NestableContainer::ConstHook::asNestable (const void *targ=0,TypeId tid=0) const
{
  if( index<-1 ) // uninitialized -- just return nc
    return nc;
  if( !targ )
  {
    bool dum;
    targ = collapseIndex(tid,dum,0,False);
    if( !targ )
      return 0;
  }
  if( tid == TpObjRef )
  {
    if( !static_cast<const ObjRef*>(targ)->valid() )
      return 0;
    targ = &static_cast<const ObjRef*>(targ)->deref();
    tid = static_cast<const BlockableObject*>(targ)->objectType();
  }
  return NestableContainer::isNestable(tid) 
    ? static_cast<const NestableContainer*>(targ) 
    : 0;
}

// Same thing, but insures writability
NestableContainer * NestableContainer::ConstHook::asNestableWr (void *targ=0,TypeId tid=0) const
{
  if( !targ )
  {
    bool dum;
    targ = const_cast<void*>( collapseIndex(tid,dum,0,True) );
    if( !targ )
      return 0;
  }
  if( !targ )
    return 0;
  if( tid == TpObjRef )
  {
    if( !static_cast<ObjRef*>(targ)->valid() )
      return 0;
    targ = &static_cast<ObjRef*>(targ)->dewr();
    tid = static_cast<BlockableObject*>(targ)->objectType();
  }
  return NestableContainer::isNestable(tid) 
    ? static_cast<NestableContainer*>(targ) 
    : 0;
}

// This is called to get a value, for built-in scalar types only
void NestableContainer::ConstHook::get_scalar( void *data,TypeId tid,bool ) const
{
  // check for residual index
  FailWhen(addressed,"unexpected '&' operator");
  TypeId target_tid; bool dum; 
  const void *target;
  if( index>=0 || id.size() )
  {
    target = collapseIndex(target_tid,dum,0,False);
    FailWhen(!target,"uninitialized element");
  }
  else
  {
    target = nc;
    target_tid = nc->type();
  }
  // if referring to a non-dynamic type, attempt the conversion
  if( !TypeInfo::isDynamic(target_tid) && target_tid != TpObjRef )
  {
    FailWhen(!convertScalar(target,target_tid,data,tid),
             "can't convert "+target_tid.toString()+" to "+tid.toString());
    return;
  }
  // if target is a container, then try to access it in scalar mode
  // // ...but not implicitly
  // // FailWhen(implicit,"can't implicitly convert "+target_tid.toString()+" to "+tid.toString());
  const NestableContainer *nc = asNestable(target,target_tid);
  FailWhen(!nc,"can't convert "+target_tid.toString()+" to "+tid.toString());
  // access in scalar mode, checking that type is built-in
  FailWhen(!nc->isScalar(tid),"target container can't be accessed as a scalar "+tid.toString());
  target = nc->get(HIID(),target_tid,dum,TpNumeric,False,autoprivatize);
  FailWhen( !convertScalar(target,target_tid,data,tid),
            "can't convert "+target_tid.toString()+" to "+tid.toString());
}

// This is called to access by reference, for all types
// If pointer is True, then a pointer type is being taken
const void * NestableContainer::ConstHook::get_address(TypeId tid,bool must_write,bool,bool pointer ) const
{
  TypeId target_tid; bool dum; 
  const void *target;
  if( index>=0 || id.size() )
  {
    target = collapseIndex(target_tid,dum,0,False);
    FailWhen(!target,"uninitialized element");
  }
  else
  {
    target = nc;
    target_tid = nc->type();
  }
  // If types don't match, then try to treat target as a container, 
  // and return pointer to first element (if this is allowed)
  if( tid != target_tid )
  {
    const NestableContainer *nc = asNestable(target,target_tid);
    FailWhen(!nc,"can't convert "+target_tid.toString()+" to "+tid.toString()+"*");
    FailWhen(pointer && !nc->type(),"this container does not support pointers");
    // check for scalar/vector violation
    if( !nc->isScalar(tid) )
    {
      FailWhen(!pointer,"can't access this container as scalar");
      FailWhen(!nc->isContiguous(),"can't take pointer: container is not contiguous");
    }
    // access first element, verifying type & writability
    return nc->get(HIID(),target_tid,dum,tid,must_write,autoprivatize);
  }
  return target;
}

// This prepares the hook for assignment, by resolving to the target element,
// and failing that, trying to insert() a new element.
// The actual type of the target element is returned via target_tid. 
// Normally, this will be ==tid (or an exception will be thrown by the
// container), unless:
// (a) tid & container type are both dynamic (then target must be an ObjRef)
// (b) tid & container type are both numeric (Hook will do conversion)
// For other type categories, a strict match should be enforced by the container.
void * NestableContainer::Hook::prepare_put( TypeId &target_tid,TypeId tid ) const
{
  FailWhen(addressed,"unexpected '&' operator");
  bool dum; 
  void *target = const_cast<void*>( collapseIndex(target_tid,dum,0,True) );
  // non-existing object: try to a insert new one
  if( !target  )
  {
    // The resulting target_tid may be different from the requested tid
    // in the case of scalars (where conversion is allowed)
    target = index>=0 ? nc->insertn(index,tid,target_tid)
                      : nc->insert(id,tid,target_tid);
    if( TypeInfo::isDynamic(target_tid) )
      target_tid = TpObjRef;
  }
  else
  {
    // have we resolved to an existing sub-container, and we're not explicitly
    // trying to assign the same type of sub-container? Try to init the container
    // with whatever is being assigned
    NestableContainer *nc1 = asNestableWr(target,target_tid);
    if( nc1 && nc1->objectType() != tid )
    {
      target = nc1->insert(HIID(),tid,target_tid);
      if( TypeInfo::isDynamic(target_tid) )
        target_tid = TpObjRef;
    }
  }
  return target;
}

// This is called to assign a value, for scalar & binary types
const void * NestableContainer::Hook::put_scalar( const void *data,TypeId tid,size_t sz ) const
{
  TypeId target_tid;
  void *target = prepare_put(target_tid,tid);
  // if types don't match, assume standard conversion
  if( tid != target_tid )
    FailWhen( !convertScalar(data,tid,target,target_tid),
          "can't assign "+tid.toString()+" to "+target_tid.toString() )
  else // else a binary type
    memcpy(const_cast<void*>(target),data,sz);
  return target;
}

// Helper function to assign an object.  
void NestableContainer::Hook::assign_object( BlockableObject *obj,TypeId tid,int flags ) const
{
  TypeId target_tid;
  void *target = prepare_put(target_tid,tid);
  FailWhen(target_tid!=TpObjRef,"can't attach "+tid.toString()+" to "+target_tid.toString());
  static_cast<ObjRef*>(target)->unlock().attach(obj,flags).lock();
}

// Helper function assigns an objref     
ObjRef & NestableContainer::Hook::assign_objref ( const ObjRef &ref,int flags ) const
{
  FailWhen(addressed,"unexpected '&' operator");
  TypeId target_tid;
  void *target = prepare_put(target_tid,ref->objectType());
  FailWhen(target_tid!=TpObjRef,"can't assign ObjRef to "+target_tid.toString());
  if( flags&DMI::COPYREF )
    return static_cast<ObjRef*>(target)->unlock().copy(ref,flags).lock();
  else
    return static_cast<ObjRef*>(target)->unlock().xfer(const_cast<ObjRef&>(ref)).lock();
}

string NestableContainer::ConstHook::sdebug ( int detail,const string &prefix,const char *name ) const
{
  if( !name )
    name = "CHook";
  string out;
  out = ssprintf("%s%s[%s]",name,addressed?"&":"",nc->sdebug(detail,prefix).c_str());
  out += index >= 0 
      ? ssprintf("[%d]",index) 
      : "["+id.toString()+"]"; 
  return out;  
}

    
  //## end NestableContainer%3BE97CE100AF.declarations
//## begin module%3C10CC830069.epilog preserve=yes
//## end module%3C10CC830069.epilog
