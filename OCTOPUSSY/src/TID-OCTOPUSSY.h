      #ifndef TID_OCTOPUSSY_h
      #define TID_OCTOPUSSY_h 1
      
      // This file is generated automatically -- do not edit
      // Generated by /home/oms/LOFAR/autoconf_share/../Timba/DMI/aid/build_aid_maps.pl
      #include <DMI/TypeId.h>

      // should be called somewhere in order to link in the registry
      int aidRegistry_OCTOPUSSY ();

#ifndef _defined_id_TpOctopussyMessage
#define _defined_id_TpOctopussyMessage 1
const DMI::TypeId TpOctopussyMessage(-1049);      // from /home/oms/LOFAR/Timba/OCTOPUSSY/src/Message.h:29
const int TpOctopussyMessage_int = -1049;
namespace Octopussy { class Message; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Octopussy::Message> : public TypeTraits<Octopussy::Message>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpOctopussyMessage_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Octopussy::Message & ContainerReturnType;
                typedef const Octopussy::Message & ContainerParamType;
              };
            };
#endif


#endif
