//  CountedRefTarget.h: abstract prototype for a ref target
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

#ifndef DMI_CountedRefTarget_h
#define DMI_CountedRefTarget_h 1

#include <DMI/Common.h>
#include <DMI/DMI.h>
#include <Common/Thread.h>
#include <Common/CheckConfig.h>

#include <ostream>

class CountedRefBase;

CHECK_CONFIG_THREADS(DMI);


//##ModelId=3C0CDF41029F
//##Documentation
//## Abstract base class for anything that can be referenced by a Counted
//## Ref.
class CountedRefTarget 
{
  public:
    //##ModelId=3DB93466002B
      CountedRefTarget();

    //##ModelId=3DB934660053
      CountedRefTarget(const CountedRefTarget &right);

    //##ModelId=3DB9346600F3
      virtual ~CountedRefTarget();


      //##ModelId=3C0CE728002B
      //##Documentation
      //## Abstract method for cloning an object. Should allocate a new object
      //## with "new" and return pointer to it. If DMI::WRITE is specified,
      //## then a writable clone is required.
      //## The depth argument specifies cloning depth (the DMI::DEEP flag
      //## means infinite depth). If depth=0, then any nested refs should only
      //## be copy()d. ). If depth>0, then nested refs should be copied and
      //## privatize()d , with depth=depth-1.
      //## The DMI::DEEP flag  corresponds to infinitely deep cloning. If this
      //## is set, then depth should be ignored, and nested refs should be
      //## privatize()d with DMI::DEEP.
      //## 
      //## Otherwise, nested refs should be copied & privatized  with
      //## depth=depth-1 and the DMI::DEEP flag passed on.
      virtual CountedRefTarget* clone (int flags = 0, int depth = 0) const = 0;

      //##ModelId=3C3EDD7D0301
      //##Documentation
      //## Virtual method for privatization of an object.
      //## The depth argument determines the depth of privatization and/or
      //## cloning (see CountedRefBase::privatize()). If depth>0, then any
      //## nested refs should be privatize()d as well, with depth=depth-1.
      //## The DMI::DEEP flag  corresponds to infinitely deep privatization. If
      //## this is set, then depth should be ignored, and nested refs should be
      //## privatize()d with DMI::DEEP.
      //## If depth=0 (and DMI::DEEP is not set), then privatize() is
      //## effectively a no-op. However, if your class has a 'writable'
      //## property, it should be changed in accordance with the DMI::WRITE
      //## and/or DMI::READONLY flags.
      virtual void privatize (int flags = 0, int depth = 0);

      //##ModelId=3C18899002BB
      //##Documentation
      //## Returns a reference count. Note that the ref count methods may be
      //## redefined in derived classes (i.e. SmartBlock) to support, e.g.,
      //## shared memory (i.e. refs from multiple processes), in which case
      //## they are only compelled to be accurate to 0, 1 or 2 ("more").
      virtual int refCount () const;

      //##ModelId=3C18C69A0120
      //##Documentation
      //## Returns a count of writable refs.
      virtual int refCountWrite () const;

      //##ModelId=3C18C6A603DA
      //##Documentation
      //## Returns True is exclusive-write refs to the object exist.
      virtual bool refWriteExclusions () const;

      //##ModelId=3C63B97601B9
      bool hasExternalRefs () const;

      //##ModelId=3C63BA8800B9
      bool hasAnonRefs () const;

    //##ModelId=3DB934660201
      const CountedRefBase * getOwner () const;

    // Additional Public Declarations
    //##ModelId=3DB934660265
      CountedRefBase * getOwner ();
      
    //##ModelId=3DB9346602A2
      Thread::Mutex & crefMutex();
      
      virtual void print (std::ostream &str) const
      { str << "CountedRefTarget"; }
      
      // prints to cout, with endline. Not inlined, so that it can
      // be called from a debugger. This uses the virtual print, above,
      // hence it need not be redefined by child classes.
      void print () const;
      
      // This is a typical debug() method setup. The sdebug()
      // method creates a debug info string at the given level of detail.
      // If detail<0, then partial info is returned: e.g., for detail==-2,
      // then only level 2 info is returned, without level 0 or 1.
      // Other conventions: no trailing \n; if newlines are embedded
      // inside the string, they are followed by prefix.
      // If class name is not specified, a default one is inserted.
      // It is sometimes useful to have a virtual sdebug().
    //##ModelId=3DB9346602E8
      virtual string sdebug ( int detail = 1,const string &prefix = "",
                      const char *name = 0 ) const;
      // The debug() method is an alternative interface to sdebug(),
      // which copies the string to a static buffer (see Debug.h), and returns 
      // a const char *. Thus debug()s can't be nested, while sdebug()s can.
    //##ModelId=3DB934670163
      const char * debug ( int detail = 1,const string &prefix = "",
                           const char *name = 0 ) const
      { return Debug::staticBuffer(sdebug(detail,prefix,name)); }
      
  private:
    // Data Members for Associations

      //##ModelId=3C0CDF6503B9
      //##Documentation
      //## First ref in list of refs to this target
      mutable CountedRefBase *owner_ref;

  private:
    // Additional Implementation Declarations
    //##ModelId=3DB934650322
      mutable bool anon;
  
    //##ModelId=3DB93465039B
      Thread::Mutex cref_mutex;

    friend class CountedRefBase;
};

//##ModelId=3C8CDBB901EB
//##Documentation
//## SingularRefTarget is simply a CountedRefTarget with clone()
//## redefined to throw an exception (hence the name 'singular', since
//## such a target cannot be cloned). You can derive your classes from
//## SingularRefTarget if you just want to make use of CountedRefs as
//## auto pointers (i.e., to automatically delete an object once the last
//## ref has been detached), but do not want to implement cloning or
//## privatization.
class SingularRefTarget : public CountedRefTarget
{
  public:

      //##ModelId=3C8CDBF40236
      //##Documentation
      //## Abstract method for cloning an object. Should allocate a new object
      //## with "new" and return pointer to it. If DMI::WRITE is specified,
      //## then a writable clone is required.
      //## The depth argument specifies cloning depth (the DMI::DEEP flag
      //## means infinite depth). If depth=0, then any nested refs should only
      //## be copy()d. ). If depth>0, then nested refs should be copied and
      //## privatize()d , with depth=depth-1.
      //## The DMI::DEEP flag  corresponds to infinitely deep cloning. If this
      //## is set, then depth should be ignored, and nested refs should be
      //## privatize()d with DMI::DEEP.
      //## 
      //## Otherwise, nested refs should be copied & privatized  with
      //## depth=depth-1 and the DMI::DEEP flag passed on.
      virtual CountedRefTarget* clone (int  = 0, int  = 0) const;

};

inline std::ostream & operator << (std::ostream &str,const CountedRefTarget &target)
{
  target.print(str);
  return str;
}


//##ModelId=3DB934660201
inline const CountedRefBase * CountedRefTarget::getOwner () const
{
  return owner_ref;
}

// Class SingularRefTarget 


//##ModelId=3C8CDBF40236
inline CountedRefTarget* SingularRefTarget::clone (int , int ) const
{
  Throw("can't clone a singular target");
}

//##ModelId=3DB934660265
inline CountedRefBase * CountedRefTarget::getOwner () 
{
  return owner_ref;
}

//##ModelId=3DB9346602A2
inline Thread::Mutex & CountedRefTarget::crefMutex()
{
  return cref_mutex;
}


#endif
