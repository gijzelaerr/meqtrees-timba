//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC820124.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC820124.cm

//## begin module%3C10CC820124.cp preserve=no
//## end module%3C10CC820124.cp

//## Module: DataField%3C10CC820124; Package specification
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\DataField.h

#ifndef DataField_h
#define DataField_h 1

//## begin module%3C10CC820124.additionalIncludes preserve=no
#include "Common.h"
#include "DMI.h"
//## end module%3C10CC820124.additionalIncludes

//## begin module%3C10CC820124.includes preserve=yes
#include "TypeInfo.h"
#include "HIID.h"
//## end module%3C10CC820124.includes

// BlockSet
#include "BlockSet.h"
// BlockableObject
#include "BlockableObject.h"
//## begin module%3C10CC820124.declarations preserve=no
//## end module%3C10CC820124.declarations

//## begin module%3C10CC820124.additionalDeclarations preserve=yes

#pragma typegroup Global
#pragma types DataField
//## end module%3C10CC820124.additionalDeclarations


//## begin DataField%3BB317D8010B.preface preserve=yes
class DataField;
class DataRecord;
//## end DataField%3BB317D8010B.preface

//## Class: DataField%3BB317D8010B
//## Category: PSCF::DMI%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3BEBD95D007B;BlockSet { -> }

class DataField : public BlockableObject  //## Inherits: <unnamed>%3C1F711B0122
{
  //## begin DataField%3BB317D8010B.initialDeclarations preserve=yes
  private:
      // Define standard accessor methods (they should be visible so
      // that we can pull in DataAcc-*.h)
      const void * put_scalar( const void *data,TypeId tid,int index=-1 );
      void get_scalar( void *data,TypeId tid,int index=-1 ) const;
      const void *get_reference(TypeId check_tid,bool must_write,int index=-1) const;
      const void *get_address(TypeId check_tid,bool must_write,bool implicit=False,int index=-1) const;
      DataField & attach_object( BlockableObject *obj,int flags,int index=-1 );
      
  //## end DataField%3BB317D8010B.initialDeclarations

  public:
    //## begin DataField::ConstHook%3C614FDE0039.preface preserve=yes
    //## end DataField::ConstHook%3C614FDE0039.preface

    //## Class: ConstHook%3C614FDE0039
    //	DataField::Hook is a helper class generated by the [n] operator of
    //	DataField. Essentially, a Hook refers to a single data element of a
    //	DataField. Hook implements assignment and conversion operators for
    //	data elements.
    //## Category: PSCF::DMI%3BEAB1F2006B; Global
    //## Subsystem: DMI%3C10CC810155
    //## Persistence: Transient
    //## Cardinality/Multiplicity: n



    class ConstHook 
    {
      //## begin DataField::ConstHook%3C614FDE0039.initialDeclarations preserve=yes
      protected:
           // Define standard accessor methods (they should be visible so
           // that we can pull in DataAccessors.h)
           void get_scalar( void *data,TypeId tid ) const;
           const void *get_reference(TypeId check_tid,bool must_write) const;
           const void *get_address(TypeId check_tid,bool must_write,bool implicit=False) const;
      //## end DataField::ConstHook%3C614FDE0039.initialDeclarations

      public:

        //## Other Operations (specified)
          //## Operation: operator &%3C61542A02E4
          const DataField::ConstHook & operator & () const;

          //## Operation: operator []%3C6BB09C02E9
          const DataField::ConstHook & operator [] (int n) const;

        // Additional Public Declarations
          //## begin DataField::ConstHook%3C614FDE0039.public preserve=yes
          // Pull in bulk definitions of accessor operators.
          // This defines conversion to the standard scalar types, also
          // const pointers
          #include "DataAcc-Const.h"

          // Returns read-only copy of object reference (for dynamic types). 
          // const version returns a read-only ref.
          operator ObjRef () const;

          // dereferences to a subrecord 
          // (throws exception if contents are not a DataRecord)
          const DataRecord * operator -> () const;

          // dereferencing to a field of a subrecord 
          // (throws exception if contents are not a DataRecord)
          const DataField & operator [] ( const HIID &id ) const;
          
          friend DataField;
          friend DataRecord;

          //## end DataField::ConstHook%3C614FDE0039.public
      protected:
        //## Constructors (specified)
          //## Operation: ConstHook%3C629A110053
          ConstHook (const DataField *par, int num);

        // Data Members for Class Attributes

          //## Attribute: index%3C6150F2014E
          //## begin DataField::ConstHook::index%3C6150F2014E.attr preserve=no  protected: int {UM} 
          mutable int index;
          //## end DataField::ConstHook::index%3C6150F2014E.attr

          //## Attribute: addressed%3C61536902E6
          //## begin DataField::ConstHook::addressed%3C61536902E6.attr preserve=no  protected: bool {UM} 
          mutable bool addressed;
          //## end DataField::ConstHook::addressed%3C61536902E6.attr

        // Data Members for Associations

          //## Association: PSCF::DMI::-parent%3C6298CD0012
          //## Role: ConstHook::parent%3C6298CD01FC
          //## begin DataField::ConstHook::parent%3C6298CD01FC.role preserve=no  private: DataField { -> 1RHgNM}
          mutable DataField *parent;
          //## end DataField::ConstHook::parent%3C6298CD01FC.role

        // Additional Protected Declarations
          //## begin DataField::ConstHook%3C614FDE0039.protected preserve=yes
          //## end DataField::ConstHook%3C614FDE0039.protected

      private:
        //## Constructors (generated)
          ConstHook();

          ConstHook(const ConstHook &right);

        //## Assignment Operation (generated)
          ConstHook & operator=(const ConstHook &right);

        // Additional Private Declarations
          //## begin DataField::ConstHook%3C614FDE0039.private preserve=yes
          //## end DataField::ConstHook%3C614FDE0039.private

      private: //## implementation
        // Additional Implementation Declarations
          //## begin DataField::ConstHook%3C614FDE0039.implementation preserve=yes
          //## end DataField::ConstHook%3C614FDE0039.implementation

    };

    //## begin DataField::ConstHook%3C614FDE0039.postscript preserve=yes
    //## end DataField::ConstHook%3C614FDE0039.postscript

    //## begin DataField::Hook%3C62A13101C9.preface preserve=yes
    //## end DataField::Hook%3C62A13101C9.preface

    //## Class: Hook%3C62A13101C9
    //	DataField::Hook is a helper class generated by the [n] operator of
    //	DataField. Essentially, a Hook refers to a single data element of a
    //	DataField. Hook implements assignment and conversion operators for
    //	data elements.
    //## Category: PSCF::DMI%3BEAB1F2006B; Global
    //## Subsystem: DMI%3C10CC810155
    //## Persistence: Transient
    //## Cardinality/Multiplicity: n



    class Hook : public ConstHook  //## Inherits: <unnamed>%3C62A15F005C
    {
      //## begin DataField::Hook%3C62A13101C9.initialDeclarations preserve=yes
      protected:
           const void * put_scalar( const void *data,TypeId tid ) const;
           DataField & attach_object( BlockableObject *obj,int flags ) const;
      //## end DataField::Hook%3C62A13101C9.initialDeclarations

      public:

        //## Other Operations (specified)
          //## Operation: operator &%3C63E98E0228
          const DataField::Hook & operator & () const;

          //## Operation: operator []%3C6BB0BF019E
          const DataField::Hook & operator [] (int n) const;

        // Additional Public Declarations
          //## begin DataField::Hook%3C62A13101C9.public preserve=yes
          
          // Pull in bulk definitions of assignment operators.
          #define ForceConstDefinitions 1
          #include "DataAcc-NonConst.h"
          
          // Assigns object to field element, by making a _copy_ of the reference
          DataField & operator = ( const ObjRef &ref) const;
          // Same, but it xfers the ref
          DataField & operator <<= ( ObjRef &ref) const;
          
          // dereferences to a subrecord 
          // (throws exception if contents are not a DataRecord)
          DataRecord * operator -> () const;

          // dereferencing to a field of a subrecord 
          // (throws exception if contents are not a DataRecord)
          DataField & operator [] ( const HIID &id ) const;
          
          // Returns a possibly writable ref to object
          operator ObjRef () const;
          
          friend DataField;
          friend DataRecord;
          //## end DataField::Hook%3C62A13101C9.public
      protected:
        //## Constructors (specified)
          //## Operation: Hook%3C62A13101FC
          Hook (DataField *par, int num);

        // Additional Protected Declarations
          //## begin DataField::Hook%3C62A13101C9.protected preserve=yes
          //## end DataField::Hook%3C62A13101C9.protected

      private:
        //## Constructors (generated)
          Hook();

          Hook(const Hook &right);

        //## Assignment Operation (generated)
          Hook & operator=(const Hook &right);

        // Additional Private Declarations
          //## begin DataField::Hook%3C62A13101C9.private preserve=yes
          //## end DataField::Hook%3C62A13101C9.private

      private: //## implementation
        // Additional Implementation Declarations
          //## begin DataField::Hook%3C62A13101C9.implementation preserve=yes
          //## end DataField::Hook%3C62A13101C9.implementation

    };

    //## begin DataField::Hook%3C62A13101C9.postscript preserve=yes
    //## end DataField::Hook%3C62A13101C9.postscript

    //## Constructors (specified)
      //## Operation: DataField%3C3D64DC016E
      explicit DataField (int flags = DMI::WRITE);

      //## Operation: DataField%3C3EE3EA022A
      DataField (const DataField &right, int flags = 0);

      //## Operation: DataField%3BFA54540099
      //	Constructs an empty data field
      explicit DataField (TypeId tid, int num = 1, int flags = DMI::WRITE);

    //## Destructor (generated)
      ~DataField();

    //## Assignment Operation (generated)
      DataField & operator=(const DataField &right);


    //## Other Operations (specified)
      //## Operation: init%3C6161190193
      DataField & init (TypeId tid, int num = 1, const void *data = 0);

      //## Operation: valid%3C627A64008E
      bool valid () const;

      //## Operation: resize%3C62961D021B
      void resize (int newsize);

      //## Operation: objectType%3C3EC27F0227
      //	Returns the class TypeId
      virtual TypeId objectType () const;

      //## Operation: clear%3C3EAB99018D
      void clear (int flags = DMI::WRITE);

      //## Operation: isValid%3C3EB9B902DF
      bool isValid (int n = 0);

      //## Operation: get%3C5FB272037E
      const void * get (int n, TypeId& tid, bool& can_write, TypeId check_tid, bool must_write) const;

      //## Operation: get%3C56B1DA0057
      const void * get (int n = 0, TypeId check = 0, Bool must_write = False) const;

      //## Operation: getWr%3BFCFA2902FB
      void* getWr (int n = 0, TypeId check = 0);

      //## Operation: objwr%3C0E4619019A
      ObjRef objwr (int n = 0, int flags = DMI::PRESERVE_RW);

      //## Operation: objref%3C3C8D7F03D8
      ObjRef objref (int n = 0) const;

      //## Operation: put%3C3C84A40176
      //	Inserts an object (by ref) into field at poisition n. This will
      //	transfer the ref to the field, so pass in a ref.copy() if you need
      //	to retain one.
      DataField & put (const ObjRef &obj, int n = 0, int flags = DMI::XFER);

      //## Operation: put%3C691E8B0034
      DataField & put (const BlockableObject *obj, int n = 0, int flags = DMI::READONLY);

      //## Operation: put%3C691E11031D
      DataField & put (BlockableObject *obj, int n = 0, int flags = DMI::WRITE);

      //## Operation: remove%3C3EC3470153
      //	Removes object from field at position n, and returns ref to it.
      ObjRef remove (int n = 0);

      //## Operation: fromBlock%3C3D5F2001DC
      //	Creates object from a set of block references. Appropriate number of
      //	references are removed from the head of the BlockSet. Returns # of
      //	refs removed.
      virtual int fromBlock (BlockSet& set);

      //## Operation: toBlock%3C3D5F2403CC
      //	Stores an object into a set of blocks. Appropriate number of refs
      //	added to tail of BlockSet. Returns # of block refs added.
      virtual int toBlock (BlockSet &set) const;

      //## Operation: clone%3C3EC77D02B1; C++
      //	Clones a data field. (See CountedRefTarget::clone() for semantics)
      virtual CountedRefTarget* clone (int flags = 0) const;

      //## Operation: cloneOther%3C3EE42D0136
      void cloneOther (const DataField &other, int flags = 0);

      //## Operation: privatize%3C3EDEBC0255
      //	Makes a private snapshot of the field, by privatizing all contents.
      //	Use DMI::WRITE to make a writable field.
      void privatize (int flags = 0);

    //## Get and Set Operations for Class Attributes (generated)

      //## Attribute: mytype%3BB317E3002B
      const TypeId type () const;

      //## Attribute: mysize%3C3D60C103DA
      const int size () const;

      //## Attribute: selected%3BEBE89602BC
      const bool isSelected () const;

      //## Attribute: writable%3BFCD90E0110
      const bool isWritable () const;

  public:
    // Additional Public Declarations
      //## begin DataField%3BB317D8010B.public preserve=yes
      typedef CountedRef<DataField> Ref;
      
//       // templated getf() and getfwr() methods provide an alternative interface
//       template<class T> const T * getf( int n = 0 ) const
//       { return (const T *) get(n,type2id(T)); }
//       template<class T> T * getfwr( int n = 0 ) 
//       { return (T *) getWr(n,type2id(T)); }
      
      // Pull in bulk definitions of scalar accessor operators.
      // This defines assignment of and conversion to the standard
      // scalar types, for use with scalar (size=1) fields.
      #define NoImplicitConversions 1
      #include "DataAcc-Const.h"
      #define NoImplicitConversions 1
      #include "DataAcc-NonConst.h"

      // Returns copy of object reference (for scalar fields containing
      // dynamic types). const version returns a read-only ref.
      operator ObjRef ();
      operator ObjRef () const;
      
      // dereferences to a subrecord (throws exception if contents are not a DataRecord)
      DataRecord * operator -> ();
      const DataRecord * operator -> () const;
      
      // dereferencing to a field of a subrecord 
      // (throws exception if contents are not a DataRecord)
      DataField & operator [] ( const HIID &id );
      const DataField & operator [] ( const HIID &id ) const;
      
      // Assigns object to field, by making a _copy_ of the reference
      // Field must be either empty, or containing 1 object of the same type.
      DataField & operator = ( const ObjRef &ref);
      // Same thing, but xfers the ref
      DataField & operator <<= ( ObjRef &ref);
       
      // Hook is a helper class that provides similar ops for 
      // elements of a vector (size>1) field. Note that using the [n] 
      // operator with n==size (i.e.
      // one past the end of the field) will automatically resize the field
      // by one element. (This is not very efficient, it's much better to
      // call resize in advance to reserve the appropriate amount of space).
      Hook operator [] (int n);
      ConstHook operator [] (int n) const;
      
      friend Hook;
      friend ConstHook;

      // standard debug info method
      string sdebug ( int detail = 1,const string &prefix = "",
                      const char *name = 0 ) const;

      // helper function for making a type[num] string
      inline static string typeString (TypeId tid,int size) 
      { return Debug::ssprintf("%s[%d]",tid.toString().c_str(),size); };
      
      
      //## end DataField%3BB317D8010B.public
  protected:

    //## Other Operations (specified)
      //## Operation: resolveObject%3C3D8C07027F
      ObjRef & resolveObject (int n, bool write) const;

    // Additional Protected Declarations
      //## begin DataField%3BB317D8010B.protected preserve=yes
      // Used by various puts() to get the ObjRef at position n.
      // Inits/auto-extends field if necessary, checks types, does
      // various housekeeping.
      ObjRef & prepareForPut (TypeId tid,int n,int flags);
      
      // gets sub-record at position n, throws exception if field
      // does not contain a DataRecord
      const DataRecord * getSubRecord( bool write,int n=0 ) const;
      //## end DataField%3BB317D8010B.protected
  private:
    // Additional Private Declarations
      //## begin DataField%3BB317D8010B.private preserve=yes
      // verifies that index is in range
      void checkIndex ( int n ) const;
      
      // header block, maintained as a SmartBlock. Contains type and size
      // info. For built-in types, also contains the data block itself.
      // For dynamic objects, contains info on # of blocks per each object
      mutable BlockRef headref;
      
      // state of each object - still in block / unblocked / modified
      typedef enum { UNINITIALIZED=0,INBLOCK=1,UNBLOCKED=2,MODIFIED=3 } ObjectState;
      mutable vector<int> objstate;

      // vector of strings, for the special case of a Tpstring field
      vector<string> strvec;
      mutable bool strvec_modified; // flag: has been modified
      typedef vector<string>::iterator VSI;
      typedef vector<string>::const_iterator CVSI;
      
      // flag: field contains a simple type handled by binary copying
      // (TypeInfo category NUMERIC or BINARY)
      bool    binary_type,dynamic_type;
      // size of binary representation for this type
      size_t  typesize;
      
      // inlines for accessing the header block
      int & headerType () const { return ((int*)headref->data())[0]; }
      int & headerSize () const { return ((int*)headref->data())[1]; }
      int & headerBlockSize (int n) const { return ((int*)headref->data())[2+n]; }
      void * headerData () const { return &headerBlockSize(0); }
      
      //## end DataField%3BB317D8010B.private
  private: //## implementation
    // Data Members for Class Attributes

      //## begin DataField::mytype%3BB317E3002B.attr preserve=no  public: TypeId {U} 
      TypeId mytype;
      //## end DataField::mytype%3BB317E3002B.attr

      //## begin DataField::mysize%3C3D60C103DA.attr preserve=no  public: int {U} 
      int mysize;
      //## end DataField::mysize%3C3D60C103DA.attr

      //## begin DataField::selected%3BEBE89602BC.attr preserve=no  public: bool {U} 
      bool selected;
      //## end DataField::selected%3BEBE89602BC.attr

      //## begin DataField::writable%3BFCD90E0110.attr preserve=no  public: bool {U} 
      bool writable;
      //## end DataField::writable%3BFCD90E0110.attr

    // Data Members for Associations

      //## Association: PSCF::DMI::<unnamed>%3BEBD9640021
      //## Role: DataField::blocks%3BEBD96601BE
      //## begin DataField::blocks%3BEBD96601BE.role preserve=no  private: BlockSet {0..* -> 0..*VHgN}
      mutable vector<BlockSet> blocks;
      //## end DataField::blocks%3BEBD96601BE.role

      //## Association: PSCF::DMI::<unnamed>%3BEBD97703D5
      //## Role: DataField::objects%3BEBD9780228
      //## begin DataField::objects%3BEBD9780228.role preserve=no  private: BlockableObject {0..* -> 0..*RHN}
      mutable vector<ObjRef> objects;
      //## end DataField::objects%3BEBD9780228.role

    // Additional Implementation Declarations
      //## begin DataField%3BB317D8010B.implementation preserve=yes
      //## end DataField%3BB317D8010B.implementation

};

//## begin DataField%3BB317D8010B.postscript preserve=yes
typedef DataField::Ref DataFieldRef;

// Copies scalar from field
inline void DataField::get_scalar( void *data,TypeId tid,int n ) const
{
  FailWhen(!valid(),"uninitialized DataField");
  if( n<0 ) // called from DataField context (rather than Hook context)
    n = 0;
  checkIndex(n);
  // this will throw an exception when types are illegal
  convertScalar(get(n,0,False),mytype,data,tid);
}

// returns address of field element in access-by-reference context
inline const void * DataField::get_reference(TypeId check_tid,bool must_write,int n) const
{
  FailWhen(!valid(),"uninitialized DataField");
  if( n<0 ) // called from DataField context (rather than Hook context)
    n = 0;
  checkIndex(n);
  return get(0,check_tid,must_write);
}

// returns address of field element
inline const void * DataField::get_address(TypeId check_tid,bool must_write,bool,int n) const
{
  return get_reference(check_tid,must_write,n); 
}

// Hook (see below) is a helper class that provides similar ops for 
// elements of a vector (size>1) field. Note that using the [n] 
// operator with n==size (i.e.
// one past the end of the field) will automatically resize the field
// by one element. (This is not very efficient, it's much better to
// call resize in advance to reserve the appropriate amount of space).
inline DataField::Hook DataField::operator [] (int n)
{
  return Hook( this, n<0 ? size()-n : n );
}

inline DataField::ConstHook DataField::operator [] (int n) const
{
  return ConstHook( this,n<0 ? size()-n : n );
}

// some inlined ops
inline void DataField::ConstHook::get_scalar( void *data,TypeId tid ) const
{
  FailWhen1(addressed,"unexpected '&' operator");
  return parent->get_scalar(data,tid,index);
}

// returns reference to field element
inline const void * DataField::ConstHook::get_reference(TypeId check_tid,bool must_write) const
{
  FailWhen1(addressed,"unexpected '&' operator");
  return parent->get_reference(check_tid,must_write,index);
}

// returns address -- checks that address is expected in current context
inline const void * DataField::ConstHook::get_address(TypeId check_tid,bool must_write,bool implicit) const
{ 
  FailWhen1(implicit && !addressed,"must use the & operator to get a pointer"); 
  return parent->get_reference(check_tid,must_write); 
}

// writes a scalar
inline const void * DataField::Hook::put_scalar( const void *data,TypeId tid ) const
{
  FailWhen1(addressed,"unexpected '&' operator");
  return parent->put_scalar(data,tid,index);
}

// attaches object
inline DataField & DataField::Hook::attach_object( BlockableObject *obj,int flags ) const
{ 
  FailWhen1(addressed,"unexpected '&' operator");
  return parent->attach_object(obj,flags,index);
}

// assigns objref to field, copying the ref
inline DataField & DataField::operator = ( const ObjRef &ref)
{ 
  FailWhen(size()>1,"can't assign scalar to vector field"); 
  return put(ref,0,DMI::COPYREF|DMI::AUTOEXTEND); 
}

// Same thing, but xfers the ref
inline DataField & DataField::operator <<= ( ObjRef &ref)
{ 
  FailWhen(size()>1,"can't assign scalar to vector field"); 
  return put(ref,0,DMI::XFER|DMI::AUTOEXTEND); 
}

inline DataField & DataField::Hook::operator = ( const ObjRef &ref) const
{
  FailWhen1(addressed,"unexpected '&' operator");
  return parent->put(ref,index,DMI::COPYREF|DMI::AUTOEXTEND);
}
    
inline DataField & DataField::Hook::operator <<= ( ObjRef &ref) const
{
  FailWhen1(addressed,"unexpected '&' operator");
  return parent->put(ref,index,DMI::XFER|DMI::AUTOEXTEND);
}

//## end DataField%3BB317D8010B.postscript

// Class DataField::ConstHook 

inline DataField::ConstHook::ConstHook (const DataField *par, int num)
  //## begin DataField::ConstHook::ConstHook%3C629A110053.hasinit preserve=no
  //## end DataField::ConstHook::ConstHook%3C629A110053.hasinit
  //## begin DataField::ConstHook::ConstHook%3C629A110053.initialization preserve=yes
  : index(num),addressed(False),parent((DataField*)par)
  //## end DataField::ConstHook::ConstHook%3C629A110053.initialization
{
  //## begin DataField::ConstHook::ConstHook%3C629A110053.body preserve=yes
  //## end DataField::ConstHook::ConstHook%3C629A110053.body
}



//## Other Operations (inline)
inline const DataField::ConstHook & DataField::ConstHook::operator & () const
{
  //## begin DataField::ConstHook::operator &%3C61542A02E4.body preserve=yes
  FailWhen1(addressed,"operator & applied twice to element of "+parent->sdebug());
  addressed=True; return *this;
  //## end DataField::ConstHook::operator &%3C61542A02E4.body
}

inline const DataField::ConstHook & DataField::ConstHook::operator [] (int n) const
{
  //## begin DataField::ConstHook::operator []%3C6BB09C02E9.body preserve=yes
  FailWhen1(index>=0,"unexpected '[]' operator");
  index = n;
  return *this;
  //## end DataField::ConstHook::operator []%3C6BB09C02E9.body
}

// Class DataField::Hook 

inline DataField::Hook::Hook (DataField *par, int num)
  //## begin DataField::Hook::Hook%3C62A13101FC.hasinit preserve=no
  //## end DataField::Hook::Hook%3C62A13101FC.hasinit
  //## begin DataField::Hook::Hook%3C62A13101FC.initialization preserve=yes
    : ConstHook(par,num)
  //## end DataField::Hook::Hook%3C62A13101FC.initialization
{
  //## begin DataField::Hook::Hook%3C62A13101FC.body preserve=yes
  //## end DataField::Hook::Hook%3C62A13101FC.body
}



//## Other Operations (inline)
inline const DataField::Hook & DataField::Hook::operator & () const
{
  //## begin DataField::Hook::operator &%3C63E98E0228.body preserve=yes
  FailWhen1(addressed,"operator & applied twice to element of "+parent->sdebug());
  addressed=True; return *this;
  //## end DataField::Hook::operator &%3C63E98E0228.body
}

inline const DataField::Hook & DataField::Hook::operator [] (int n) const
{
  //## begin DataField::Hook::operator []%3C6BB0BF019E.body preserve=yes
  FailWhen1(index>=0,"unexpected '[]' operator");
  index = n;
  return *this;
  //## end DataField::Hook::operator []%3C6BB0BF019E.body
}

// Class DataField 


//## Other Operations (inline)
inline bool DataField::valid () const
{
  //## begin DataField::valid%3C627A64008E.body preserve=yes
  return mytype.id() != 0;
  //## end DataField::valid%3C627A64008E.body
}

inline TypeId DataField::objectType () const
{
  //## begin DataField::objectType%3C3EC27F0227.body preserve=yes
  return TpDataField;
  //## end DataField::objectType%3C3EC27F0227.body
}

inline const void * DataField::get (int n, TypeId check, Bool must_write) const
{
  //## begin DataField::get%3C56B1DA0057.body preserve=yes
  TypeId dum1; bool dum2;
  return get(n,dum1,dum2,check,must_write);
  //## end DataField::get%3C56B1DA0057.body
}

inline void* DataField::getWr (int n, TypeId check)
{
  //## begin DataField::getWr%3BFCFA2902FB.body preserve=yes
  return (void*)get(n,check,True);
  //## end DataField::getWr%3BFCFA2902FB.body
}

inline DataField & DataField::put (const BlockableObject *obj, int n, int flags)
{
  //## begin DataField::put%3C691E8B0034.body preserve=yes
  // casting away const here, but that's OK, since we enforce READONLY flags
  return attach_object(const_cast<BlockableObject*>(obj),n,flags|DMI::READONLY);
  //## end DataField::put%3C691E8B0034.body
}

inline DataField & DataField::put (BlockableObject *obj, int n, int flags)
{
  //## begin DataField::put%3C691E11031D.body preserve=yes
  return attach_object(obj,n,flags);
  //## end DataField::put%3C691E11031D.body
}

//## Get and Set Operations for Class Attributes (inline)

inline const TypeId DataField::type () const
{
  //## begin DataField::type%3BB317E3002B.get preserve=no
  return mytype;
  //## end DataField::type%3BB317E3002B.get
}

inline const int DataField::size () const
{
  //## begin DataField::size%3C3D60C103DA.get preserve=no
  return mysize;
  //## end DataField::size%3C3D60C103DA.get
}

inline const bool DataField::isSelected () const
{
  //## begin DataField::isSelected%3BEBE89602BC.get preserve=no
  return selected;
  //## end DataField::isSelected%3BEBE89602BC.get
}

inline const bool DataField::isWritable () const
{
  //## begin DataField::isWritable%3BFCD90E0110.get preserve=no
  return writable;
  //## end DataField::isWritable%3BFCD90E0110.get
}

//## begin module%3C10CC820124.epilog preserve=yes
inline void DataField::checkIndex ( int n ) const
{
  FailWhen( n < 0 || n >= mysize,"index out of range");
}
//## end module%3C10CC820124.epilog


#endif
