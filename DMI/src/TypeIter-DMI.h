    // This file is generated automatically -- do not edit
    // Generated by /home/oms/LOFAR/autoconf_share/../Timba/DMI/aid/build_aid_maps.pl
    #ifndef _TypeIter_DMI_h
    #define _TypeIter_DMI_h 1



#define DoForAllOtherTypes_DMI(Do,arg,separator) \
        Do(DMI::ObjRef,arg)

#define DoForAllBinaryTypes_DMI(Do,arg,separator) \
        Do(DMI::Timestamp,arg) separator \
        Do(DMI::AtomicID,arg)

#define DoForAllSpecialTypes_DMI(Do,arg,separator) \
        Do(DMI::HIID,arg) separator \
        Do(string,arg)

#define DoForAllIntermediateTypes_DMI(Do,arg,separator) \
        

#define DoForAllDynamicTypes_DMI(Do,arg,separator) \
        Do(DMI::NumArray,arg) separator \
        Do(DMI::Vec,arg) separator \
        Do(DMI::List,arg) separator \
        Do(DMI::Record,arg)

#define DoForAllNumericTypes_DMI(Do,arg,separator) \
        Do(bool,arg) separator \
        Do(char,arg) separator \
        Do(uchar,arg) separator \
        Do(short,arg) separator \
        Do(ushort,arg) separator \
        Do(int,arg) separator \
        Do(uint,arg) separator \
        Do(long,arg) separator \
        Do(ulong,arg) separator \
        Do(longlong,arg) separator \
        Do(ulonglong,arg) separator \
        Do(float,arg) separator \
        Do(double,arg) separator \
        Do(ldouble,arg) separator \
        Do(fcomplex,arg) separator \
        Do(dcomplex,arg)
#endif
