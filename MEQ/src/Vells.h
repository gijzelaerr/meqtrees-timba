//# Vells.h: Values for Meq expressions
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

#ifndef MEQ_VELLS_H
#define MEQ_VELLS_H

#include <DMI/NumArray.h>
#include <MEQ/Meq.h>
#include <MEQ/Axis.h>

#pragma type #Meq::Vells

// This provides a list of operators and functions defined over Vells objects
// All of these will only work with double or dcomplex Vells, and throw
// an exception on any other type.

// Unary operators
#define DoForAllUnaryOperators(Do,x) \
          Do(-,UNARY_MINUS,x)

// Binary operators
#define DoForAllBinaryOperators(Do,x) \
          Do(+,ADD,x) Do(-,SUB,x) Do(*,MUL,x) Do(/,DIV,x) 

// In-place operators
#define DoForAllInPlaceOperators(Do,x) \
          Do(+,ADD1,x) Do(-,SUB1,x) Do(*,MUL1,x) Do(/,DIV1,x) 

// Unary functions are split up several groups
#define DoForAllUnaryFuncs(Do,x)  DoForAllUnaryFuncs1(Do,x)  \
                                  DoForAllUnaryFuncs2(Do,x)  \
                                  DoForAllUnaryFuncs3(Do,x)  \
                                  DoForAllUnaryFuncs4(Do,x)  
                                
// Unary group 1: defined for all Vells. Preserves real/complex
#define DoForAllUnaryFuncs1(Do,x) \
  Do(cos,x) Do(cosh,x) Do(exp,x) Do(log,x) Do(sin,x) Do(sinh,x) \
  Do(sqr,x) Do(sqrt,x) Do(tan,x) Do(tanh,x) \
  Do(pow2,x) Do(pow3,x) Do(pow4,x) Do(pow5,x) Do(pow6,x) Do(pow7,x) Do(pow8,x)
// Do(log10,x) commented out for now -- doesn't seem to have a complex version

// Unary group 2: defined for real Vells only, returns real
#define DoForAllUnaryFuncs2(Do,x) \
  Do(ceil,x) Do(floor,x) Do(acos,x) Do(asin,x) Do(atan,x) 

// Unary group 3: defined for all Vells, result is always real
#define DoForAllUnaryFuncs3(Do,x) \
  Do(abs,x) Do(fabs,x) Do(norm,x) Do(arg,x) Do(real,x) Do(imag,x) 
  
// Unary group 4: others functions requiring special treatment
#define DoForAllUnaryFuncs4(Do,x) \
  Do(conj,x) 
  
// Unary reduction functions not requiring a shape.
// Called as func(vells[,flagmask]).
// These return a constant Vells (i.e. reduction along all axes)
// In the future, we'll support reduction along a designated axis
#define DoForAllUnaryRdFuncs(Do,x) \
  Do(min,x) Do(max,x) Do(mean,x) 

// Unary reduction functions requiring a shape.
// Called as func(vells,shape[,flagmask]).
// A shape argument is required because a Vells that is constant
// along some axis must be treated as N distinct points with the same value
// for the purposes of these functions.
// These return a constant Vells (i.e. reduction along all axes).
// In the future, we'll support reduction along a designated axis.
#define DoForAllUnaryRdFuncsWS(Do,x) \
  Do(sum,x) Do(product,x) Do(nelements,x)

// Binary functions
#define DoForAllBinaryFuncs(Do,x) \
  Do(posdiff,x) Do(tocomplex,x) Do(polar,x) Do(pow,x) Do(atan2,x)

// Binary functions using flags
#define DoForAllBinaryFuncsWF(Do,x) \
  Do(min,x) Do(max,x) 

// Finally, VellsFlagType Vells define bitwise logical operators:
// unary  ~ (NOT)
#define DoForAllUnaryFlagOperators(Do,x) \
          Do(~,NOT,x) 
// Binary and in-place | & and ^ (OR AND XOR). The second operand may be a 
// Vells or a VellsFlagType scalar.
#define DoForAllBinaryFlagOperators(Do,x) \
          Do(|,OR,x) Do(&,AND,x) Do(^,XOR,x) 
#define DoForAllInPlaceFlagOperators(Do,x) \
          Do(|,OR1,x) Do(&,AND1,x) Do(^,XOR1,x)
          


namespace Meq 
{ 
using namespace DMI;
using namespace DebugMeq;


// dataflag type
typedef int  VellsFlagType;  
const VellsFlagType VellsFullFlagMask = 0xFFFFFFFF;
const TypeId VellsFlagTypeId = typeIdOf(VellsFlagType);


// Conditionally include declarations for Vells math.
// Skipping these functions saves time/memory when compiling code that
// doesn't need them (such as the Meq service classes, and Vells itself).
// Note that the functions go into their own separate namespace. This keeps 
// the compiler from tripping over abs() and such.
#ifndef MEQVELLS_SKIP_FUNCTIONS
class Vells;
namespace VellsMath 
{
  #define declareUnaryFunc(FUNCNAME,x) \
    Vells FUNCNAME (const Vells &);
  DoForAllUnaryFuncs(declareUnaryFunc,);
  #define declareUnaryRdFunc(FUNCNAME,x) \
    Vells FUNCNAME (const Vells &,VellsFlagType flagmask=VellsFullFlagMask);
  DoForAllUnaryRdFuncs(declareUnaryRdFunc,);
  #define declareUnaryRdFuncWS(FUNCNAME,x) \
    Vells FUNCNAME (const Vells &,const Axis::Shape &,VellsFlagType flagmask=VellsFullFlagMask);
  DoForAllUnaryRdFuncsWS(declareUnaryRdFuncWS,);
  #define declareBinaryFunc(FUNCNAME,x) \
    Vells FUNCNAME (const Vells &,const Vells &);
  DoForAllBinaryFuncs(declareBinaryFunc,);
  #define declareBinaryFuncWF(FUNCNAME,x) \
    Vells FUNCNAME (const Vells &,const Vells &,VellsFlagType flagmask=VellsFullFlagMask);
  DoForAllBinaryFuncsWF(declareBinaryFuncWF,);
  #undef declareUnaryFunc
  #undef declareUnaryRdFunc
  #undef declareUnaryRdFuncWS
  #undef declareBinaryFunc
  #undef declareBinaryFuncWF
};
#endif

// we provide two versions of each operation (real and complex)
const int VELLS_LUT_SIZE = 2;

namespace VellsTraits
{
  // this is a traits-type structure that defines parameters and return types
  template<typename T,int N>
  class DataType
  {
    public:
        typedef const typename NumArray::Traits<T,N>::Array & ParamType;
        typedef const typename NumArray::Traits<T,N>::Array & ConstRetType;
        typedef typename NumArray::Traits<T,N>::Array & RetType;
  };
  template<typename T>
  class DataType<T,0>
  {
    public:
        typedef T ParamType;
        typedef T ConstRetType;
        typedef T & RetType;
  };
  template<>
  class DataType<dcomplex,0>
  {
    public:
        typedef const dcomplex & ParamType;
        typedef dcomplex ConstRetType;
        typedef dcomplex & RetType;
  };
};

//##ModelId=3F86886E0229
//##Documentation
// The Vells class contains a sampling (or integration) of a function over
// an arbitrary N-dimensional grid. 
// It is essentially a specialization of DMI::NumArray.
class Vells : public DMI::NumArray
{
private:
  template<class T>
  inline void init_scalar (T value)
  { *static_cast<T*>(const_cast<void*>(getConstDataPtr())) = value; }

  template<class T>
  inline void init_array (T value)
  { T *ptr = static_cast<T*>(const_cast<void*>(getConstDataPtr())),
      *end = ptr + nelements();
    for( ; ptr != end; ptr++ )
     *ptr = value;
  }
  
public:
  //##ModelId=400E530400F0
  typedef CountedRef<Vells> Ref;
  typedef Axis::Shape       Shape;
    
  //##ModelId=3F86887001D4
  //##Documentation
  // A null Vells with no data
  Vells();
    
  // Creates a (temp by default) scalar Vells
  inline Vells(double value,bool temp=true)
  : NumArray(Tpdouble,LoShape(1),DMI::NOZERO,TpMeqVells),is_temp_(temp)
  { init_scalar(value); }
  
  inline Vells(const dcomplex &value,bool temp=true)
  : NumArray(Tpdcomplex,LoShape(1),DMI::NOZERO,TpMeqVells),is_temp_(temp)
  { init_scalar(value); }
  
  // Create a Vells of given shape.
  // If the init flag is true, the Vells is initialized to the given value.
  // Otherwise value only determines type, and Vells is initialized with zeroes.
  // NB: the argument type really ought to be VellsTraits::DataType<T,0>::ParamType
  // and not just T, but stupid compiler won't recognize it for some reason...
  inline Vells(double value,const Shape &shape,bool init=true)
  : NumArray(Tpdouble,shape,DMI::NOZERO,TpMeqVells),is_temp_(false)
  { 
    if( init )
      init_array(value);
  }
  inline Vells(const dcomplex &value,const Shape &shape,bool init=true)
  : NumArray(Tpdcomplex,shape,DMI::NOZERO,TpMeqVells),is_temp_(false)
  { 
    if( init )
      init_array(value);
  }
  
  // Create a flag Vells of the given shape
  // Note that order of constructor arguments is reversed here to avoid 
  // confusion with other constructors: otherwise it's too easy to 
  // unintentionally create a flag vells when a normal one was intended 
  // simply by using Vells(0,shape).
  inline Vells(const Shape &shape,VellsFlagType value,bool init=true)
  : NumArray(VellsFlagTypeId,shape,DMI::NOZERO,TpMeqVells),is_temp_(false)
  { 
    if( init )
      init_array(value);
  }

  //##ModelId=3F868870022A
  // Copy constructor (reference semantics, unless DMI::DEEP or depth>0 is 
  // specified). A Vells may be created from a NumArray of a compatible type
  Vells (const DMI::NumArray &other,int flags=0,int depth=0);
  Vells (const Vells &other,int flags=0,int depth=0);
  
  // Construct from array
  template<class T,int N>
  Vells (const blitz::Array<T,N> &arr)
  : DMI::NumArray(arr,TpMeqVells)
  { validateContent(false); }

    //##ModelId=3F8688700238
  ~Vells();

  // Assignment (reference semantics).
    //##ModelId=3F868870023B
  Vells& operator= (const Vells& other);

      //##ModelId=400E530403C1
  virtual TypeId objectType () const
  { return TpMeqVells; }
  
  // implement standard clone method via copy constructor
    //##ModelId=400E530403C5
  virtual CountedRefTarget* clone (int flags=0,int depth=0) const
  { return new Vells(*this,flags,depth); }
  
  // validate array contents and setup shortcuts to them. This is called 
  // automatically whenever a Vells object is made from a DMI::NumArray
    //##ModelId=400E530403DB
  virtual void validateContent (bool recursive);

  // is it a null vells?
    //##ModelId=3F8688700280
  bool isNull() const
  { return ! NumArray::valid(); }
  
  // does this Vells have flags attached?
  bool hasDataFlags () const
  { return dataflags_.valid(); }
  
  // returns flags of this Vells
  const Vells & dataFlags () const
  { return *dataflags_; }
  
  // sets the dataflags of a Vells
  void setDataFlags (const Vells::Ref &flags)
  { dataflags_ = flags; }
  void setDataFlags (const Vells &flags)
  { dataflags_.attach(flags); }
  void setDataFlags (const Vells *flags)
  { dataflags_.attach(flags); }
  
  void clearDataFlags ()
  { dataflags_.detach(); }

  // Is the Vells a temporary object? The constructors above always
  // produce a non-temp Vells. Vells math (below) uses the private
  // constructors to produce temp Vells. Temp Vells allow for efficient 
  // re-use of storage.
    //##ModelId=400E53560092
  bool isTemp () const
  { return is_temp_; }
  
  // changes the temp property
    //##ModelId=400E5356009D
  Vells & makeTemp (bool temp=true) 
  { is_temp_ = temp; return *this; }
  
    //##ModelId=400E535600A9
  Vells & makeNonTemp () 
  { is_temp_ = false; return *this; }
  
  static int extent (const Vells::Shape &shp,uint idim)
  { return idim < shp.size() ? shp[idim] : 1; }
  
  int extent (uint idim) const
  { return extent(shape(),idim); }
  
    //##ModelId=3F868870027E
  int nelements() const
  { return NumArray::size(); }
  
  bool isScalar () const
  { return nelements() == 1; }

    //##ModelId=3F868870028A
  bool isReal() const
  { return elementType() == Tpdouble; }
  
    //##ModelId=400E535600B5
  bool isComplex() const
  { return elementType() == Tpdcomplex; }
  
  bool isFlags() const
  { return elementType() == VellsFlagTypeId; }
  
  // Returns true if a sub-shape is compatible with the specified main shape.
  // A sub-shape is compatible if it does not have greater variability, i.e.:
  // 1. Its rank is not higher
  // 2. Its extent along each axis is either 1, or equal to the shape's extent
  static bool isCompatible (const Axis::Shape &subshape,const Axis::Shape &mainshape)
  {
    int rank = subshape.size();
    if( rank > int(mainshape.size()) )
      return false;
    for( int i=0; i<rank; i++ )
      if( subshape[i] != 1 && subshape[i] != mainshape[i] )
        return false;
    return true;
  }

  // Returns true if Vells is compatible with the specified mainshape.
  bool isCompatible (const Axis::Shape &mainshape) const
  { return isCompatible(shape(),mainshape); }
  
  // Two Vells shapes are congruent if the extents of each dimension are
  // congruent. Congruency of extents means both are equal, or either one is 1.
  // (An extent of 1 means that the value is constant along that axis).
  // Vells of congruent shape may have math operations performed on them.
  static bool isCongruent (const Axis::Shape &a,const Axis::Shape &b)
  {
    if( a.size() != b.size() )
      return false;
    for( uint i=0; i<a.size(); i++ )
      if( a[i] != b[i] && a[i]>1 && b[i]>1 )
        return false;
    return true;
  }

  // returns true if shape matches the one specified
  bool isCongruent (const Axis::Shape &shp) const
  { return isCongruent(shape(),shp); }

  // returns true if type/shape matches the one specified
  //##ModelId=400E535600E7
  bool isCongruent (TypeId type,const Axis::Shape &shp) const
  { return elementType() == type && isCongruent(shape(),shp); }

  // returns true if type/shape matches other Vells
  //##ModelId=400E535600CE
  bool isCongruent (const Vells &other) const
  { return isCongruent(other.elementType(),other.shape()); }
    
  // Define templated getStorage<T>() function
  // Default version will produce a compile-time error; specializations
  // are provided below for double & dcomplex
  template<class T>
  const T* getStorage ( Type2Type<T> = Type2Type<T>() ) const
  { 
    const TypeId tid = typeIdOf(T);
    FailWhen(elementType()!=tid,"can't access "+elementType().toString()+" Vells as "+tid.toString());
    return static_cast<const T*>(NumArray::getConstDataPtr());
  }
  template<class T>
  T* getStorage ( Type2Type<T> = Type2Type<T>() )
  { 
    const TypeId tid = typeIdOf(T);
    FailWhen(elementType()!=tid,"can't access "+elementType().toString()+" Vells as "+tid.toString());
    return static_cast<T*>(NumArray::getDataPtr());
  }
  
  // begin<T> is same as getStorage()
  // end<T> is begin<T> + nelements()
  template<class T>
  const T* begin ( Type2Type<T> = Type2Type<T>() ) const
  { return getStorage(Type2Type<T>()); }
  template<class T>
  T* begin ( Type2Type<T> = Type2Type<T>() )
  { return getStorage(Type2Type<T>()); }
  template<class T>
  const T* end ( Type2Type<T> = Type2Type<T>() ) const
  { return getStorage(Type2Type<T>()) + nelements(); }
  template<class T>
  T* end ( Type2Type<T> = Type2Type<T>() )
  { return getStorage(Type2Type<T>()) + nelements(); }
  
  // begin_flags() and end_flags() return pointer to flags, or to nil flag
  // if there are none
  const VellsFlagType * beginFlags () const
  { return hasDataFlags() ? dataFlags().begin<VellsFlagType>() : &null_flag_; }
  
  const VellsFlagType * endFlags () const
  { return hasDataFlags() ? dataFlags().end<VellsFlagType>() : &(null_flag_)+1; }
  
  int nflags () const
  { return hasDataFlags() ? dataFlags().nelements() : 1; }
  
  int flagRank () const
  { return hasDataFlags() ? dataFlags().rank() : 1; }
  
  const Shape & flagShape () const
  { return hasDataFlags() ? dataFlags().shape() : null_flag_shape_; }
  
  
// NumArray already defines templated getArray<T>() and getConstArray<T>() functions
//   template<class T,int N>
//   const typename Traits<T,N>::Array & getArray (Type2Type<T> =Type2Type<T>(),Int2Type<N> =Int2Type<N>()) const
//   { return NumArray::getConstArray(Type2Type<T>(),Int2Type<N>()); }
//   template<class T,int N>
//   typename Traits<T,N> & getArray (Type2Type<T> =Type2Type<T>(),Int2Type<N> =Int2Type<N>())
//   { return *static_cast<typename Traits<T,N>::Array*>(
//                 NumArray::getArrayPtr(typeIdOf(T),N)); }
  
  template<class T>
  T getScalar (Type2Type<T> =Type2Type<T>()) const
  { 
    FailWhen(!isScalar(),"can't access this Meq::Vells as scalar"); 
    return *static_cast<const T *>(getStorage(Type2Type<T>())); 
  }
  template<class T>
  T & getScalar (Type2Type<T> =Type2Type<T>()) 
  { 
    FailWhen(!isScalar(),"can't access this Meq::Vells as scalar"); 
    return *static_cast<T*>(getStorage(Type2Type<T>())); 
  }
 
  
  // Define templated as<T,N>() functions, returning arrays or scalars (N=0)
  // Default version maps to getArray
  template<class T,int N>
  typename VellsTraits::DataType<T,N>::ConstRetType as (Type2Type<T> =Type2Type<T>(),Int2Type<N> = Int2Type<N>()) const
  { return getArray(Type2Type<T>(),Int2Type<N>()); }
  
  template<class T,int N>
  typename VellsTraits::DataType<T,N>::RetType as (Type2Type<T> =Type2Type<T>(),Int2Type<N> = Int2Type<N>()) 
  { return getArray(Type2Type<T>(),Int2Type<N>()); }
  
  template<class T>
  T as (Type2Type<T> =Type2Type<T>()) const
  { return getScalar(Type2Type<T>()); }
  
  template<class T>
  T & as (Type2Type<T> =Type2Type<T>()) 
  { return getScalar(Type2Type<T>()); }

  // Provides access to array storage
    //##ModelId=3F8688700295
  const double* realStorage() const
  { return getStorage<double>(); }
    //##ModelId=3F8688700298
  double* realStorage()
  { return getStorage<double>(); }
    //##ModelId=3F8688700299
  const dcomplex* complexStorage() const
  { return getStorage<dcomplex>(); }
    //##ModelId=3F868870029B
  dcomplex* complexStorage()
  { return getStorage<dcomplex>(); }
  
  // copies data from other Vells. Checks for matching shape/type
    //##ModelId=400E53560110
  void copyData (const Vells &other);
  
  // zeroes data
    //##ModelId=400E5356011C
  void zeroData ();
  
  // dumps to output
    //##ModelId=3F8688700282
  void show (std::ostream& os) const;

    //##ModelId=400E5356011F
  string sdebug (int detail=1,const string &prefix="",const char *nm=0) const;
  
  // helper funtion to compute output shape and data strides, given two
  // input shapes. Used throughout Vells math
  static void computeStrides (Vells::Shape &outshape,
                       int strides[][Axis::MaxAxis],
                       int nshapes,const Vells::Shape * shapes[],
                       const string &opname);
  
  // convenience version for two shape arguments
  static void computeStrides (Vells::Shape &shape,
                       int strides[2][Axis::MaxAxis],
                       const Vells::Shape &a,const Vells::Shape &b,
                       const string &opname);
  
  // convenience version for two Vells arguments with optional flags
  // strides filled as follows: 0/1 Vells a/b, 2/3 flags a/b
  static void computeStrides (Vells::Shape &shape,
                       int strides[4][Axis::MaxAxis],
                       const Vells &a,const Vells &b,
                       const string &opname);

private:
    
  Vells::Ref  dataflags_;

  static VellsFlagType null_flag_;
  static Shape null_flag_shape_;

  //##ModelId=400E5356002F
  bool    is_temp_;
//  void *  storage_;
  
  // temp storage for scalar Vells -- big enough for biggest scalar type
//  char scalar_storage_[sizeof(dcomplex)];
  
  // OK, now it gets hairy. Implement math on Vells
  // The following flags may be supplied to the constructors below:
    //##ModelId=400E530400FC
  typedef enum { 
    VF_REAL         = 0x01, // result is forced real 
    VF_COMPLEX      = 0x02, // result is forced complex 
    VF_SCALAR       = 0x04, // result is forced scalar
    VF_CHECKREAL    = 0x08, // operand(s) must be real
    VF_CHECKCOMPLEX = 0x10, // operand(s) must be complex
    VF_FLAGTYPE     = 0x20, // result and operand(s) are VellsFlagType
    VF_FLAG_STRIDES = 0x40, // compute strides for dataflags too
  } VellsFlags;
  // Special constructor for a result of a unary Vells operation.
  // If other is a temporary Vells, will re-use its storage if possible,
  // otherwise, will create new storage. 
  // By default, the Vells will have the same type/shape as 'other', but
  // flags may override it:
  //    flags&VF_REAL     forces a real Vells
  //    flags&VF_COMPLEX  forces a complex Vells
  //    flags&VF_SCALAR   forces a scalar Vells
  //    flags&VF_CHECKxxx input must be real/complex (exception otherwise)
  // The opname argument is used for error reporting
    //##ModelId=3F8688700231
  Vells (const Vells &other,int flags,const std::string &opname);

  // Special constructor for a result of a binary Vells operation.
  // If either a or b is a temporary Vells, will re-use its storage if possible.
  // Otherwise, will create new storage. 
  // By default, the type/shape of the Vells will be chosen via type/shape
  // promotion, but flags may override it:
  //    flags&VF_REAL     forces a real Vells
  //    flags&VF_COMPLEX  forces a complex Vells
  //    flags&VF_SCALAR   forces a scalar Vells
  //    flags&VF_CHECKxxx input must be real/complex (exception otherwise)
  // The opname argument is used for error reporting
    //##ModelId=400E53560174
  Vells (const Vells &a,const Vells &b,int flags,
         int strides[][Axis::MaxAxis],const std::string &opname);

  // helper functions for these two constructors
    //##ModelId=400E5356019D
  bool tryReference (const Vells &other);

  static TypeId getResultType (int flags,bool arg_is_complex);

  bool canApplyInPlace (const Vells &other,int strides[Axis::MaxAxis],const std::string &opname);

  //##ModelId=400E535601CB
  int getLutIndex () const
  { 
    if( isComplex() )
      return 1;
    else if( isReal() )
      return 0;
    else
      Throw("can't apply math operation to Vells of type "+elementType().toString());
  }
  
  
public:
// pointer to function implementing an unary operation 
    //##ModelId=400E53040108
  typedef void (*UnaryOperPtr)(Vells &,const Vells &);
  typedef void (*UnaryRdFuncPtr)(Vells &,const Vells &,VellsFlagType);
  typedef void (*UnaryRdFuncWSPtr)(Vells &,const Vells &,const Shape &,VellsFlagType);
// pointer to function implementing a binary operation 
    //##ModelId=400E53040116
  typedef void (*BinaryOperPtr)(Vells &out,const Vells &,const Vells &,
                                const int [2][Axis::MaxAxis]);
  typedef void (*BinaryFuncWFPtr)(Vells &out,const Vells &,const Vells &,
                                  VellsFlagType,const int [4][Axis::MaxAxis]);
// pointer to function implementing an unary in-place operation 
  typedef void (*InPlaceOperPtr)(Vells &out,const Vells &,const int [Axis::MaxAxis]);
  
// Declares inline unary operator OPER (internally named OPERNAME),
// plus lookup table for implementations
// This: 1. Creates a result Vells (using the special constructor to
//          decide whether to duplicate or reuse the storage), and 
//       2. Calls the method in the OPERNAME_lut lookup table, using the
//          LUT index of this Vells object. 
#define declareUnaryOperator(OPER,OPERNAME,x) \
  private: static UnaryOperPtr unary_##OPERNAME##_lut[VELLS_LUT_SIZE];  \
  public: Vells operator OPER () const \
          { Vells result(*this,0,"operator "#OPER); \
            (*unary_##OPERNAME##_lut[getLutIndex()])(result,*this);  \
            return result; }

// unary flag operators implemented explicitly (no LUT needed)
#define declareUnaryFlagOperator(OPER,OPERNAME,x) \
  public: Vells operator OPER () const;
          
// Declares binary operator OPER (internally named OPERNAME)
// plus lookup table for implementations
// This: 1. Creates a result Vells (using the special constructor to
//          decide whether to duplicate or reuse the storage, and to init
//          strides) 
//       2. Calls the method in the OPERNAME_lut lookup table, using the
//          LUT index generated from the two Vells operands
#define declareBinaryOperator(OPER,OPERNAME,x) \
  private: static BinaryOperPtr binary_##OPERNAME##_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE];  \
  public: Vells operator OPER (const Vells &right) const \
          { int strides[2][Axis::MaxAxis]; \
            Vells result(*this,right,0,strides,"operator "#OPER); \
            (*binary_##OPERNAME##_lut[getLutIndex()][right.getLutIndex()])(result,*this,right,strides);  \
            return result; }

            
// Declares in-place (i.e. += and such) operator OPER (internally named OPERNAME)
// plus lookup table for implementations
// This just calls the method in the OPERNAME_lut lookup table, using the
// LUT index of this Vells object. The Vells itself is used as the result
// storage.
#define declareInPlaceOperator(OPER,OPERNAME,x) \
  private: static InPlaceOperPtr inplace_##OPERNAME##_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE];  \
  public: Vells & operator OPER##= (const Vells &right) \
          { int strides[Axis::MaxAxis]; \
            if( canApplyInPlace(right,strides,#OPERNAME) ) \
              (*inplace_##OPERNAME##_lut[getLutIndex()][right.getLutIndex()])(*this,right,strides); \
            else \
              (*this) = (*this) OPER right; \
            return *this; \
          }

// in-place flag operators implemented explicitly (no LUT needed)
#define declareInPlaceFlagOperator(OPER,OPERNAME,x) \
  public: Vells & operator OPER##= (const Vells &right); \
          Vells & operator OPER##= (VellsFlagType right); 

// binary flag operators implemented explicitly (no LUT needed)
#define declareBinaryFlagOperator(OPER,OPERNAME,x) \
  public: Vells operator OPER (const Vells &right) const; \
          Vells operator OPER (VellsFlagType right) const;

// Defines lookup tables for implementations of unary math functions
#define declareUnaryFuncLut(FUNCNAME,x) \
  private: static UnaryOperPtr unifunc_##FUNCNAME##_lut[VELLS_LUT_SIZE];  

#define declareUnaryRdFuncLut(FUNCNAME,x) \
  private: static UnaryRdFuncPtr unifunc_##FUNCNAME##_lut[VELLS_LUT_SIZE];  

#define declareUnaryRdFuncWSLut(FUNCNAME,x) \
  private: static UnaryRdFuncWSPtr unifunc_##FUNCNAME##_lut[VELLS_LUT_SIZE];  
  
// Declares binary function FUNCNAME
// Defines lookup tables for implementations of binary math functions
#define declareBinaryFuncLut(FUNCNAME,x) \
  private: static BinaryOperPtr binfunc_##FUNCNAME##_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE];  
#define declareBinaryFuncWFLut(FUNCNAME,x) \
  private: static BinaryFuncWFPtr binfunc_##FUNCNAME##_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE];  

// insert all declarations using the macros above  
    //##ModelId=400E535601D0
  DoForAllUnaryOperators(declareUnaryOperator,);
  DoForAllUnaryFlagOperators(declareUnaryFlagOperator,);
    //##ModelId=400E535601D9
  DoForAllInPlaceOperators(declareInPlaceOperator,);
  DoForAllInPlaceFlagOperators(declareInPlaceFlagOperator,);
    //##ModelId=400E535601E3
  DoForAllBinaryOperators(declareBinaryOperator,);
  DoForAllBinaryFlagOperators(declareBinaryFlagOperator,);
    //##ModelId=400E535601EC
  DoForAllUnaryFuncs(declareUnaryFuncLut,);
  DoForAllUnaryRdFuncs(declareUnaryRdFuncLut,);
  DoForAllUnaryRdFuncsWS(declareUnaryRdFuncWSLut,);
    //##ModelId=400E535601F6
  DoForAllBinaryFuncs(declareBinaryFuncLut,);
  DoForAllBinaryFuncsWF(declareBinaryFuncWFLut,);

#undef declareUnaryOperator
#undef declareUnaryFlagOperator
#undef declareInPlaceOperator
#undef declareInPlaceFlagOperator
#undef declareBinaryOperator
#undef declareBinaryFlagOperator
#undef declareUnaryFuncLut
#undef declareBinaryFuncLut
#undef declareBinaryFuncWFLut
  
// Conditionally include friend declarations for Vells math.
// Skipping them saves time/memory when compiling code that
// doesn't need them (such as the Meq service classes, and Vells itself).
// Also, it avoids namespace pollution and leads to more sensible compiler
// errors.
#ifndef MEQVELLS_SKIP_FUNCTIONS
  #define declareUnaryFunc(FUNCNAME,x) \
    public: friend Vells VellsMath::FUNCNAME (const Vells &);
    //##ModelId=400E53560200
  DoForAllUnaryFuncs(declareUnaryFunc,);
  #define declareUnaryRdFunc(FUNCNAME,x) \
    public: friend Vells VellsMath::FUNCNAME (const Vells &,VellsFlagType); 
  DoForAllUnaryRdFuncs(declareUnaryRdFunc,);
  #define declareUnaryRdFuncWS(FUNCNAME,x) \
    public: friend Vells VellsMath::FUNCNAME (const Vells &,const Vells::Shape &,VellsFlagType); 
  DoForAllUnaryRdFuncsWS(declareUnaryRdFuncWS,);
  
  #define declareBinaryFunc(FUNCNAME,x) \
    public: friend Vells VellsMath::FUNCNAME (const Vells &,const Vells &);
    //##ModelId=400E5356020A
  DoForAllBinaryFuncs(declareBinaryFunc,);
  
  #define declareBinaryFuncWF(FUNCNAME,x) \
    public: friend Vells VellsMath::FUNCNAME (const Vells &,const Vells &,VellsFlagType);
    //##ModelId=400E5356020A
  DoForAllBinaryFuncsWF(declareBinaryFuncWF,);
  
  #undef declareUnaryFunc
  #undef declareUnaryRdFunc
  #undef declareUnaryRdFuncWS
  #undef declareBinaryFunc
  #undef declareBinaryFuncWF
#endif
};

// Convenience function to create uninitialized flag Vells of given shape
inline Vells FlagVells (const LoShape &shp)
{ return Vells(shp,VellsFlagType(),false); }

// Convenience function to create & initialize a flag Vells of given shape
inline Vells FlagVells (VellsFlagType value,const LoShape &shp,bool init=true)
{ return Vells(shp,value,init); }
    

// Conditionally include inline definitions of Vells math functions
#ifndef MEQVELLS_SKIP_FUNCTIONS

#define defineUnaryFunc(FUNCNAME,flags) \
  inline Vells VellsMath::FUNCNAME (const Vells &arg) \
  { Vells result(arg,flags,#FUNCNAME); \
    (*Vells::unifunc_##FUNCNAME##_lut[arg.getLutIndex()])(result,arg); \
    return result; }
#define defineUnaryRdFunc(FUNCNAME,flags) \
  inline Vells VellsMath::FUNCNAME (const Vells &arg,VellsFlagType flagmask) \
  { Vells result(arg,flags,#FUNCNAME); \
    (*Vells::unifunc_##FUNCNAME##_lut[arg.getLutIndex()])(result,arg,flagmask); \
    return result; }
#define defineUnaryRdFuncWS(FUNCNAME,flags) \
  inline Vells VellsMath::FUNCNAME (const Vells &arg,const Vells::Shape &shape,VellsFlagType flagmask) \
  { Vells result(arg,flags,#FUNCNAME); \
    (*Vells::unifunc_##FUNCNAME##_lut[arg.getLutIndex()])(result,arg,shape,flagmask); \
    return result; }

DoForAllUnaryFuncs1(defineUnaryFunc,0);
DoForAllUnaryFuncs2(defineUnaryFunc,Vells::VF_REAL|Vells::VF_CHECKREAL);
DoForAllUnaryFuncs3(defineUnaryFunc,Vells::VF_REAL);
// group 4: define explicitly
defineUnaryFunc(conj,0);
// group 5: reduction to scalar, no shape
defineUnaryRdFunc(min,Vells::VF_SCALAR|Vells::VF_REAL|Vells::VF_CHECKREAL);
defineUnaryRdFunc(max,Vells::VF_SCALAR|Vells::VF_REAL|Vells::VF_CHECKREAL);
defineUnaryRdFunc(mean,Vells::VF_SCALAR);
// group 6: reduction to scalar, with shape
defineUnaryRdFuncWS(sum,Vells::VF_SCALAR);
defineUnaryRdFuncWS(product,Vells::VF_SCALAR);
defineUnaryRdFuncWS(nelements,Vells::VF_SCALAR|Vells::VF_REAL);

#define defineBinaryFunc(FUNCNAME,flags) \
  inline Vells VellsMath::FUNCNAME (const Vells &left,const Vells &right) \
  { int strides[2][Axis::MaxAxis]; \
    Vells result(left,right,flags,strides,#FUNCNAME); \
    (*Vells::binfunc_##FUNCNAME##_lut[left.getLutIndex()][right.getLutIndex()])(result,left,right,strides);  \
    return result; }
defineBinaryFunc(pow,0);
defineBinaryFunc(tocomplex,Vells::VF_COMPLEX|Vells::VF_CHECKREAL);
defineBinaryFunc(polar,Vells::VF_COMPLEX|Vells::VF_CHECKREAL);
defineBinaryFunc(posdiff,Vells::VF_REAL|Vells::VF_CHECKREAL);
defineBinaryFunc(atan2,Vells::VF_REAL|Vells::VF_CHECKREAL);

#define defineBinaryFuncWF(FUNCNAME,flags) \
  inline Vells VellsMath::FUNCNAME (const Vells &left,const Vells &right,VellsFlagType flagmask) \
  { int strides[4][Axis::MaxAxis]; \
    Vells result(left,right,flags|Vells::VF_FLAG_STRIDES,strides,#FUNCNAME); \
    (*Vells::binfunc_##FUNCNAME##_lut[left.getLutIndex()][right.getLutIndex()])(result,left,right,flagmask,strides);  \
    return result; }
defineBinaryFuncWF(min,Vells::VF_REAL|Vells::VF_CHECKREAL);
defineBinaryFuncWF(max,Vells::VF_REAL|Vells::VF_CHECKREAL);

#undef defineUnaryFunc
#undef defineUnaryRdFunc
#undef defineUnaryRdFuncWS
#undef defineBinaryFunc
#undef defineBinaryFuncWF

// declare versions of binary operators where the first argument is
// a scalar
#define defineBinaryOper(OPER,OPERNAME,dum) \
  inline Vells operator OPER (double left,const Vells &right) \
  { return Vells(left) OPER right; } \
  inline Vells operator OPER (const dcomplex &left,const Vells &right) \
  { return Vells(left) OPER right; } 

DoForAllBinaryOperators(defineBinaryOper,);

#undef defineBinaryOper

// declare versions of binary flag operators where the first argument is
// a scalar. All of them commute, so this is trivial
#define defineBinaryFlagOper(OPER,OPERNAME,dum) \
  inline Vells operator OPER (VellsFlagType left,const Vells &right) \
  { return right OPER left; } \

DoForAllBinaryFlagOperators(defineBinaryFlagOper,);

#undef defineBinaryFlagOper
#endif


inline std::ostream& operator<< (std::ostream& os, const Vells& vec)
  { vec.show (os); return os; }

} // namespace Meq

#endif
