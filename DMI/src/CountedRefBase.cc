//  CountedRefBase.h: generic linked/counted ref implementation
//
//  Copyright (C) 2002
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//
//  This program is free software; you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation; either version 2 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//  $Id$

#include "CountedRefBase.h"

#include <iomanip>

#undef VERIFY
#if COUNTEDREF_VERIFY
  #define VERIFY verify()
#else
  #define VERIFY 
#endif

// The threadLock(target) macro sets a lock on the target's mutex, by instantiating
// a Mutex::Lock object. The lock will be released when the object goes
// out of scope.
// If compiled w/o thread support, this is defined as nothing.
#ifdef USE_THREADS
  #define threadLock(t) Thread::Mutex::Lock _thread_lock(t->cref_mutex)
#else
  #define threadLock(t) 
#endif

// Note that CRefs themselves are not thread-safe, but targets are.
// I.e. different threads should never access the same CRef, but both
// can hold different refs to the same target.
// The only exception is ref.copy(): this is thread-safe.
// This means that containers need only set a read-lock when accessing
// their contents via ref.copy().


InitDebugContext(CountedRefBase,"CRef");


// cloneTarget
//   Helper function called to actually clone a ref's target
//   (either from privatize directly, or via delayed-cloning)
//##ModelId=3DB9346500B5
void CountedRefBase::cloneTarget () const
{
  threadLock(target);
  if( !valid() )
    return;
  VERIFY;
  dprintf1(2)("  %s: cloning target\n",debug(0));
  // clone the target
  CountedRefTarget *newtarget = target->clone(delayed_clone_flags,delayed_clone_depth);
  // detach from old list
  if( prev ) 
    prev->next = next;
  else // no previous ref, so update ptr from target
    target->owner_ref = next;
  if( next )
    next->prev = prev;
  #if COUNTEDREF_VERIFY
  verify(target->owner_ref);
  #endif
  // attach ourselves to new reflist
  prev = next = 0;
  target = newtarget;
  target->owner_ref = const_cast<CountedRefBase*>(this);
  target->anon = True;
  // clear delayed-clone flag
  delayed_clone = False;
  VERIFY;
}

// verify
//   Checks the reference chain for consistency. 
//##ModelId=3DB934600330
void CountedRefBase::verify (const CountedRefBase *start)
{
  if( !start )
    return;
  const CountedRefTarget *target = start->target;
  if( !target )
    return;
  threadLock(target);
  // run through & verify ref chain
  const CountedRefBase *ref = target->owner_ref;
  Assert1(ref);
  Assert1(ref->prev == 0);
  bool found_start = False;
  while( ref )
  {
    Assert1( ref->target == target );
    if( ref == start )
      found_start = True;
    if( ref->next )
      Assert1(ref->next->prev == ref);
    ref = ref->next;
  }
  Assert1(found_start);
}

//##ModelId=3C0CDEE2018A


// Class CountedRefBase 


void CountedRefBase::copy (const CountedRefBase& other, int flags, int depth)
{
  dprintf(2)("copying from %s(%x,%d)\n",other.debug(),flags,depth);
  detach();
  if( !other.valid() ) // copying invalid ref?
    empty();
  else
  {
    int privatize_flags;
    // are we doing a deep copy (with auto-privatize?)
    // do we have explicit or infinite depth?
    if( depth >=0 || flags&(DMI::DEEP|DMI::PRIVATIZE) )
    {
      // depth >= 0 or DMI::DEEP enables privatization
      // DMI::PRIVATIZE effectively sets depth to max(depth,0)
      if( depth<0 )
        depth = 0;
      dprintf(2)("  copy-and-privatize requested\n");
      // if so, then do a simple readonly copy, and pass all other
      // flags to privatize below
      privatize_flags = flags & ~DMI::PRIVATIZE;
      flags = DMI::READONLY;
    }
    threadLock(other.target);
#if COUNTEDREF_VERIFY
    other.verify();
#endif
    // if the other ref is delayed-clone, then resolve it now
    if( other.delayed_clone )
    {
      dprintf(2)("  performing delayed cloning\n");
      ((CountedRefBase*)&other)->cloneTarget();
    }
    if( flags&DMI::READONLY )
      flags &= ~DMI::WRITE;
    else
      FailWhen( flags&DMI::WRITE && (!other.isWritable() || other.isExclusiveWrite()),
             "r/w access violation: copy(WRITABLE)");
    // insert copy into list after other
    target = other.target;
    prev = const_cast<CountedRefBase*>(&other);
    next = other.next;
    const_cast<CountedRefBase&>(other).next = this;
    if( next )
      next->prev = this;
    VERIFY;
    // deep copy? do a privatize now
    if( depth >=0 )
    {
      // clear all properties (privatize() will set them up according to flags)
      locked = exclusiveWrite = persistent = False;
      privatize(privatize_flags,depth);
    }
    // else use remaining flags to set up ref properties
    else
    {
      // setup properties
      locked = (flags&DMI::LOCKED) != 0;
      // writable property is inherited unless exclusive, or READONLY is specified
      // (guard condition above already checks for access violations)
      writable = (flags&DMI::WRITE) != 0 ||
                 ( (flags&DMI::PRESERVE_RW) && other.isWritable() );
      persistent = (flags&DMI::PERSIST) != 0;
      exclusiveWrite = delayed_clone = False;
    }
  }
  dprintf1(2)("  made %s\n",debug(Debug(3)?3:2,"  "));
}

//##ModelId=3C0CDEE20180
void CountedRefBase::xfer (const CountedRefBase& other)
{
  dprintf(3)("xferring from %s\n",other.debug());
  detach();
  if( !other.valid() )
    empty();
  else
  {
    threadLock(other.target);
#if COUNTEDREF_VERIFY
    other.verify();
#endif
    FailWhen( other.isLocked(),"can't transfer a locked ref" );
    FailWhen( other.isPersistent(),"can't transfer a persistent ref" );
    // insert myself into list in place of other
    if( (prev = other.prev) !=0 )
      other.prev->next = this;
    else if( other.target )
      other.target->owner_ref = this;
    else
      Throw("transfer of corrupted ref");
    if( (next = other.next) != 0 )
      other.next->prev = this;
    VERIFY;
    // copy all fields
    target = other.target;
    locked = False;
    writable = other.isWritable();
    exclusiveWrite = other.isExclusiveWrite();
    delayed_clone = False;
    // invalidate other ref (const violation here, but that's a consequence
    // of our destructive semantics)
    const_cast<CountedRefBase&>(other).empty();
  }
  dprintf(3)("  is now %s\n",debug(-1));
}

//##ModelId=3C0CDEE20164
CountedRefBase& CountedRefBase::privatize (int flags, int depth)
{
  // This is a mask of all flags used by privatize. These flags are interpreted
  // here and _NOT_ passed on to target->privatize.
  // All other flags (WRITE, READONLY, etc.) are passed on. 
  const int local_flags =
      DMI::FORCE_CLONE|DMI::DEEP_DLY_CLONE|
      DMI::LOCKED|DMI::UNLOCKED|
      DMI::EXCL_WRITE|DMI::NONEXCL_WRITE|
      DMI::PERSIST;
  
  dprintf1(2)("%s: privatizing to depth %d, target:\n",debug(),flags&DMI::DEEP?-1:depth);
  FailWhen( !valid(),"can't privatize an invalid ref" );
  threadLock(target);
  dprintf1(2)("  %s\n",target->debug(2,"  "));
  // readonly overrides writable and disables delayed cloning
  if( flags&DMI::READONLY )
    flags &= ~(DMI::DLY_CLONE|DMI::WRITE);
  // forcing a clone disables delayed cloning
  if( flags&DMI::FORCE_CLONE )
    flags &= ~DMI::DLY_CLONE;
  // no cloning is done if the object is anon, and either
  //   (1) we are the only ref, or
  //   (2) cloning is read-only, and all other refs are read-only.
  // but the FORCE_CLONE flag can force a clone anyway
  bool do_clone=False;
  if( !(flags&DMI::FORCE_CLONE) && isAnonObject() )
  {
    if( prev || next )  // other refs exist? Scan for writable ones
    {
      if( flags&DMI::WRITE )  // clone will be writable?
        do_clone = True;
      else
      {
        // readonly clone -- make ourselves readonly, and do a clone
        // if any writable refs are left.
        writable = False;
        if( target->refCountWrite() )
          do_clone=True;
      }
    }
  }
  else // non-anon is always cloned
    do_clone=True;
  
  if( do_clone )
  {
    delayed_clone_flags = flags & ~local_flags;
    delayed_clone_depth = depth;
    if( flags&DMI::DLY_CLONE ) // mark for delayed cloning, if requested
    {
      delayed_clone = True;
      // if deep-delay is not specified, turn off delay for target flags
      if( flags&DMI::DEEP_DLY_CLONE != DMI::DEEP_DLY_CLONE )
        delayed_clone_flags &= ~DMI::DLY_CLONE;
      dprintf(2)("  marked for delayed cloning\n");
    }
    else // else clone now
      cloneTarget();
  }
  else
  {
    // we are sole reference to target, so privatize it
    target->privatize(flags & ~local_flags,depth);
    delayed_clone = False;
  }
  // now setup ref properties
  if( flags&DMI::LOCKED )
    locked = True;
  else if( flags&DMI::UNLOCKED )
    locked = False;
  // writable remains as-is unless overridden by flags
  if( flags&DMI::WRITE )
    writable = True;
  else 
    writable = False;
  // exclusiveWrite remains as-is unless overridden
  if( flags&DMI::EXCL_WRITE )
    exclusiveWrite = True;
  else if( flags&DMI::NONEXCL_WRITE )
    exclusiveWrite = False;
  // persistent flag may be raised explicitly
  if( flags&DMI::PERSIST )
    persistent = True;
  
  dprintf(2)("has been privatized\n");
  return *this;
}

//##ModelId=3C18873600E9
CountedRefBase& CountedRefBase::change (int flags)
{
  // readonly downgrade
  dprintf(3)("changing to ");
  FailWhen( !valid(),"changing an invalid ref");
  if( flags&DMI::READONLY )
    writable = False;
  else if( flags&DMI::WRITE )
  {
    FailWhen(!isWritable(),"can't upgrade read-only ref to read-write");
  }
  // lock/unlock
  if( flags&DMI::LOCKED )
    locked = True;
  else if( flags&DMI::UNLOCKED )
    locked = False;
  // persist
  if( flags&DMI::PERSIST )
    persistent = True;
  // exclusive/non-exclusive write
  if( flags&DMI::NONEXCL_WRITE )
  {
    FailWhen(!isWritable(),"ref is read-only, can't make it nonexclusive-write");
    exclusiveWrite = False;
  }
  else if( flags&DMI::EXCL_WRITE )
    setExclusiveWrite();
  
  dprintf1(3)("%s\n",debug(-1));
  return *this;
}

//##ModelId=3C1888B001A1
CountedRefBase& CountedRefBase::setExclusiveWrite ()
{
  dprintf(3)("setExclusiveWrite\n");
  if( !isExclusiveWrite() )
  {
    FailWhen( !valid(),"ref is invalid");
    FailWhen( !isWritable(),"ref is read-only, can't make it exclusive-write");
    threadLock(target);
    FailWhen( hasOtherWriters(),"can't make exclusive because other writable refs exist");
    writable = exclusiveWrite = True;
  }
  return *this;
}

//##ModelId=3C0CDEE20171
CountedRefBase& CountedRefBase::attach (CountedRefTarget* targ, int flags)
{
  // detach from old target, if any
  dprintf(3)("attaching to %s\n",targ->debug());
  if( valid() )
    detach();
  // refuse to attach to NULL targets
  FailWhen( !targ,"can't attach to null target" );
  // If anon/external specified explicitly, check for consistency with
  // other refs to same object. Otherwise, inherit property from other refs.
  // If no other refs and nothing specified, assume external.
  bool anon = (flags&DMI::ANON);
  threadLock(targ);
  CountedRefBase *owner = targ->getOwner();
  if( owner )
  {
    bool external = (flags&DMI::EXTERNAL);
    bool other_anon = targ->anon;
    FailWhen( anon && !other_anon,"object already referenced as external, can't attach as anon" );
    FailWhen( external && other_anon,"object already referenced as anon, can't attach as external" );
    anon = other_anon;
  }
  // setup properties
  if( flags&DMI::WRITE && !(flags&DMI::READONLY) ) // writable attach?
  {
    FailWhen( targ->refWriteExclusions(),"can't attach writeable ref: exclusivity violation");
    writable = True;
  }
  else
    writable = False;
  locked = (flags&DMI::LOCKED)!=0;
  targ->anon = anon;
  if( flags&DMI::EXCL_WRITE )
    setExclusiveWrite();
  // persistent flag may be raised explicitly
  persistent = (flags&DMI::PERSIST) != 0;

  // add to list 
  target = targ;
  prev = 0;
  if( owner )
    (next=owner)->prev = this;
  target->owner_ref = this;

  VERIFY;

  dprintf(3)("  ref target now %s\n",target->debug(2,"  "));
  return *this;
}

//##ModelId=3C1612A60137
void CountedRefBase::detach ()
{
  if( !valid() )
    return;
  dprintf1(3)("%s: detaching\n",debug());
  // locked refs can't be detached (only destroyed)
  FailWhen( isLocked(),"can't detach a locked ref");
  // delete object if anon, and we are last ref to it
  threadLock(target);
  VERIFY;
  if( !prev && !next ) 
  {
    if( isAnonObject() ) 
    {
      dprintf(3)("last ref, anon target will be deleted\n");
      target->owner_ref = 0;
#ifdef USE_THREADS
      // explicitly release target mutex prior to destroying it (otherwise,
      // we'll be destroying a locked mutex, which is in bad taste). Since
      // the target is anon, no-one else can be legally referencing it at 
      // this point. Which means it's OK to release the mutex: no-one else
      // can [legally] grab it.
      _thread_lock.release();
#endif      
      delete target;
    }
  }
  else  // else just detach ourselves from list
  {
    if( prev ) 
      prev->next = next;
    else // no previous ref, so update ptr from target
      target->owner_ref = next;
    if( next )
      next->prev = prev;
#if COUNTEDREF_VERIFY
    target->owner_ref->verify();
#endif
    dprintf(3)("  old target is now: %s\n",target->debug(2,"  "));
  }
  empty();
}

//##ModelId=3C583B9F03B8
bool CountedRefBase::hasOtherWriters ()
{
  if( !valid() )
    return False;
  threadLock(target);
  for( const CountedRefBase *ref = target->getOwner(); ref != 0; ref = ref->next )
    if( ref != this && ref->isWritable() )
      return True;
  return False;
}

//##ModelId=3C1611C702DB
void CountedRefBase::privatizeOther (const CountedRefBase& other, int flags, int depth)
{
  // to make a clone, first do a read-only copy, then clone that
  copy(other,DMI::READONLY);
  privatize(flags,depth);
}



// Additional Declarations
//##ModelId=3DB934620030
string CountedRefBase::sdebug ( int detail,const string &prefix,const char *name ) const
{
  static int nesting=0;
  if( nesting++>1000 )
  {
    cerr<<"Too many nested CountedRefBase::sdebug() calls";
    abort();
  }
  string out;
  // low detail
  if( detail>=0 )
  {
    Debug::appendf(out,"%s/%08x",name?name:"CRef",(int)this);
    if( valid() )
    {
      out += Debug::ssprintf(">%08x",(int)target); 
      if( delayed_clone )
      {
        out += "*";
        if( delayed_clone_flags&DMI::DLY_CLONE )
          out += "/";
      }
    }
    else
    {
      out += ">-";
    }
  }
  if( detail >= 1 || detail == -1 && valid() )   // normal detail
  {
    if( valid() )
    {
      Debug::appendf(out,"%c%c%c%c%c",
                         isAnonObject() ? 'A' : '-', 
                         isWritable() ? 'W' : '-', 
                         isExclusiveWrite() ? 'E' : '-', 
                         isPersistent() ? 'P' : '-',
                         isLocked() ? 'L' : '-');
      if( prev )
        Debug::appendf(out,"p/%08x",(int)prev);
      else
        Debug::appendf(out,"p/-");
      if( next )
        Debug::appendf(out,"n/%08x",(int)next);
      else
        Debug::appendf(out,"n/-");
    }
  }
  if( detail >= 2 || detail <= -2 ) // high detail - include target info
  {
    if( valid() )
    {
      if( out.length() )
        out += "\n"+prefix+"  ";
      out += "->" + target->sdebug(abs(detail)-1,prefix+"  ");
    }
  }
  nesting--;
  return out;
}

void CountedRefBase::print (std::ostream &str) const
{
  if( valid() )
  {
    str<<"CRef->@"<<std::hex<<int(target)<<std::dec<<":";
    target->print(str);
  }
  else
    str<<"CRef->0";
}

void CountedRefBase::print () const
{ 
  print(std::cout); 
  std::cout<<endl;
}

