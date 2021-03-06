//
//% $Id$ 
//
//
// Copyright (C) 2002-2007
// The MeqTree Foundation & 
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>,
// or write to the Free Software Foundation, Inc., 
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

    // This file is generated automatically -- do not edit
    // Generated by /home/oms/LOFAR/autoconf_share/../Timba/DMI/aid/build_aid_maps.pl
    #include <DMI/AtomicID.h>
    #include <DMI/TypeInfo.h>
    #include <DMI/DynamicTypeManager.h>
    #include <DMI/Packer.h>
#include "NumArray.h"
DMI::BObj * __construct_DMINumArray (int n) { return n>0 ? new DMI::NumArray [n] : new DMI::NumArray; }
#include "Vec.h"
DMI::BObj * __construct_DMIVec (int n) { return n>0 ? new DMI::Vec [n] : new DMI::Vec; }
#include "List.h"
DMI::BObj * __construct_DMIList (int n) { return n>0 ? new DMI::List [n] : new DMI::List; }
#include "Record.h"
DMI::BObj * __construct_DMIRecord (int n) { return n>0 ? new DMI::Record [n] : new DMI::Record; }
#include "HIID.h"
        void * __new_DMIHIID  (int n) 
        { return new DMI::HIID [n]; }  
        void __delete_DMIHIID (void *ptr) 
        { delete [] static_cast<DMI::HIID*>(ptr); } 
        void __copy_DMIHIID (void *to,const void *from) 
        { *static_cast<DMI::HIID*>(to) = *static_cast<const DMI::HIID*>(from); } 
        size_t __pack_DMIHIID (const void *arr,int n,void * block,size_t &nleft ) 
        { return DMI::ArrayPacker<DMI::HIID>::pack(static_cast<const DMI::HIID*>(arr),n,block,nleft); } 
        void * __unpack_DMIHIID (const void *block,size_t sz,int &n) 
        { return DMI::ArrayPacker<DMI::HIID>::allocate(block,sz,n); } 
        size_t __packsize_DMIHIID (const void *arr,int n) 
        { return DMI::ArrayPacker<DMI::HIID>::packSize(static_cast<const DMI::HIID*>(arr),n); }
#include "Timestamp.h"
        void * __new_string  (int n) 
        { return new string [n]; }  
        void __delete_string (void *ptr) 
        { delete [] static_cast<string*>(ptr); } 
        void __copy_string (void *to,const void *from) 
        { *static_cast<string*>(to) = *static_cast<const string*>(from); } 
        size_t __pack_string (const void *arr,int n,void * block,size_t &nleft ) 
        { return DMI::ArrayPacker<string>::pack(static_cast<const string*>(arr),n,block,nleft); } 
        void * __unpack_string (const void *block,size_t sz,int &n) 
        { return DMI::ArrayPacker<string>::allocate(block,sz,n); } 
        size_t __packsize_string (const void *arr,int n) 
        { return DMI::ArrayPacker<string>::packSize(static_cast<const string*>(arr),n); }
#include "TypeId.h"
    using namespace DMI;
  
    int aidRegistry_DMI ()
    {
      static int res = 

        AtomicID::registerId(-1001,"A")+
        AtomicID::registerId(-1019,"B")+
        AtomicID::registerId(-1017,"C")+
        AtomicID::registerId(-1003,"D")+
        AtomicID::registerId(-1012,"E")+
        AtomicID::registerId(-1026,"F")+
        AtomicID::registerId(-1009,"G")+
        AtomicID::registerId(-1025,"H")+
        AtomicID::registerId(-1027,"I")+
        AtomicID::registerId(-1004,"J")+
        AtomicID::registerId(-1007,"K")+
        AtomicID::registerId(-1032,"L")+
        AtomicID::registerId(-1030,"M")+
        AtomicID::registerId(-1028,"N")+
        AtomicID::registerId(-1034,"O")+
        AtomicID::registerId(-1033,"P")+
        AtomicID::registerId(-1018,"Q")+
        AtomicID::registerId(-1023,"R")+
        AtomicID::registerId(-1015,"S")+
        AtomicID::registerId(-1011,"T")+
        AtomicID::registerId(-1006,"U")+
        AtomicID::registerId(-1014,"V")+
        AtomicID::registerId(-1022,"W")+
        AtomicID::registerId(-1024,"X")+
        AtomicID::registerId(-1005,"Y")+
        AtomicID::registerId(-1021,"Z")+
        AtomicID::registerId(-1029,"DMIObjRef")+
        TypeInfoReg::addToRegistry(-1029,TypeInfo(TypeInfo::OTHER,0))+
        AtomicID::registerId(-1269,"Message")+
        AtomicID::registerId(-1576,"Filename")+
        AtomicID::registerId(-1577,"LineNo")+
        AtomicID::registerId(-1578,"Function")+
        AtomicID::registerId(-1579,"Object")+
        AtomicID::registerId(-1085,"Type")+
        AtomicID::registerId(-1010,"DMINumArray")+
        TypeInfoReg::addToRegistry(-1010,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1010,__construct_DMINumArray)+
        AtomicID::registerId(-1008,"DMIVec")+
        TypeInfoReg::addToRegistry(-1008,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1008,__construct_DMIVec)+
        AtomicID::registerId(-1016,"DMIList")+
        TypeInfoReg::addToRegistry(-1016,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1016,__construct_DMIList)+
        AtomicID::registerId(-1031,"DMIRecord")+
        TypeInfoReg::addToRegistry(-1031,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1031,__construct_DMIRecord)+
        AtomicID::registerId(-1020,"DMIHIID")+
        TypeInfoReg::addToRegistry(-1020,TypeInfo(TypeInfo::SPECIAL,sizeof(DMI::HIID),__new_DMIHIID,__delete_DMIHIID,__copy_DMIHIID,
                __pack_DMIHIID,__unpack_DMIHIID,__packsize_DMIHIID))+
        AtomicID::registerId(-1013,"DMITimestamp")+
        TypeInfoReg::addToRegistry(-1013,TypeInfo(TypeInfo::BINARY,sizeof(DMI::Timestamp)))+
        AtomicID::registerId(-32,"bool")+
        TypeInfoReg::addToRegistry(-32,TypeInfo(TypeInfo::NUMERIC,sizeof(bool)))+
        AtomicID::registerId(-33,"char")+
        TypeInfoReg::addToRegistry(-33,TypeInfo(TypeInfo::NUMERIC,sizeof(char)))+
        AtomicID::registerId(-34,"uchar")+
        TypeInfoReg::addToRegistry(-34,TypeInfo(TypeInfo::NUMERIC,sizeof(uchar)))+
        AtomicID::registerId(-35,"short")+
        TypeInfoReg::addToRegistry(-35,TypeInfo(TypeInfo::NUMERIC,sizeof(short)))+
        AtomicID::registerId(-36,"ushort")+
        TypeInfoReg::addToRegistry(-36,TypeInfo(TypeInfo::NUMERIC,sizeof(ushort)))+
        AtomicID::registerId(-37,"int")+
        TypeInfoReg::addToRegistry(-37,TypeInfo(TypeInfo::NUMERIC,sizeof(int)))+
        AtomicID::registerId(-38,"uint")+
        TypeInfoReg::addToRegistry(-38,TypeInfo(TypeInfo::NUMERIC,sizeof(uint)))+
        AtomicID::registerId(-39,"long")+
        TypeInfoReg::addToRegistry(-39,TypeInfo(TypeInfo::NUMERIC,sizeof(long)))+
        AtomicID::registerId(-40,"ulong")+
        TypeInfoReg::addToRegistry(-40,TypeInfo(TypeInfo::NUMERIC,sizeof(ulong)))+
        AtomicID::registerId(-41,"longlong")+
        TypeInfoReg::addToRegistry(-41,TypeInfo(TypeInfo::NUMERIC,sizeof(longlong)))+
        AtomicID::registerId(-42,"ulonglong")+
        TypeInfoReg::addToRegistry(-42,TypeInfo(TypeInfo::NUMERIC,sizeof(ulonglong)))+
        AtomicID::registerId(-43,"float")+
        TypeInfoReg::addToRegistry(-43,TypeInfo(TypeInfo::NUMERIC,sizeof(float)))+
        AtomicID::registerId(-44,"double")+
        TypeInfoReg::addToRegistry(-44,TypeInfo(TypeInfo::NUMERIC,sizeof(double)))+
        AtomicID::registerId(-45,"ldouble")+
        TypeInfoReg::addToRegistry(-45,TypeInfo(TypeInfo::NUMERIC,sizeof(ldouble)))+
        AtomicID::registerId(-46,"fcomplex")+
        TypeInfoReg::addToRegistry(-46,TypeInfo(TypeInfo::NUMERIC,sizeof(fcomplex)))+
        AtomicID::registerId(-47,"dcomplex")+
        TypeInfoReg::addToRegistry(-47,TypeInfo(TypeInfo::NUMERIC,sizeof(dcomplex)))+
        AtomicID::registerId(-48,"string")+
        TypeInfoReg::addToRegistry(-48,TypeInfo(TypeInfo::SPECIAL,sizeof(string),__new_string,__delete_string,__copy_string,
                __pack_string,__unpack_string,__packsize_string))+
        AtomicID::registerId(-1002,"DMIAtomicID")+
        TypeInfoReg::addToRegistry(-1002,TypeInfo(TypeInfo::BINARY,sizeof(DMI::AtomicID)))+
    0;
    return res;
  }
  
  int __dum_call_registries_for_DMI = aidRegistry_DMI();

