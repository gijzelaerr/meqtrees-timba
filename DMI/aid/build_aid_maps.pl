#!/usr/bin/perl

# Mame of auto-generated AID and Type ID headers
# (%s is substituded for aidgroup name)
my $aidheadername = "AID-%s.h";
my $tidheadername = "TID-%s.h";
# Name of auto-generated registry map file 
my $mapfilename = "AID-%s-Registry.cc";
# Name of auto-generated type categories macro file. 
my $typeitername = "TypeIter-%s.h";
# Name of global cache file
# (The full path to this file should be given in the command-line
# arguments)
my $global_listfile = "Global.aidlist";

# ID maps. here, IDs keys are defined in uppercase, and
# without the "Aid" or "Tp" prefix
my %id_idmap;          # map: ID -> number
my %id_nummap;         # map: number -> ID
my %id_defined_at;     # map: ID -> where it's defined (path:line)
my %id_typequalifier;  # map: ID -> type category
my %id_typeheader;     # map: ID -> corresponding header file (for types only)
my %id_qualified_typename;
                       # map: ID -> fully quailfied type name (with namespaces, etc.)

my @newids;         # list of newly generated IDs

# Group maps
# An ID group corresponds to a package or directory. There can only be one
# group per directory. 
# The name of the group is defined by a #pragma aidgroup declaration
# appearing somewhere in that directory.
my %grouplist;        # dir -> list of IDs belonging to group
                      # IDs here can be a mix of upper and lowercase; this is
                      # what is actually used C++ identifiers
my %groupname;        # dir -> group name
my %group_defined_at; # dir -> where its group name was defined
my %group_regen;      # dir -> flag, should this dir be regenerated
my %group_newids;     # dir -> count of new IDs in it

# Lists of type by category (i.e. qualifier). A type ID in a #pragma types
# declaration should be prefixed by one of four qualifiers:
# "+" are built-in numerics. Size information is generated in the type registry.
#     No constructors are generated.
# "-" are special cases like 'string' or 'array_whatever'. No constructor or
#     size information generated.
# ":" are binary structs, available for bitwise copying. Size information is
#     generated but no constructors.
# "%" are intermediate objects. Nothing is generated.
# "#" are dynamic objects.  Constructors are generated, but no size information.
#
# Finally, the "/" prefix is used - with AIDs only - to indicate that a 
# prefix-less constant should be generated. This prefix is not used with types.
my %qualnames = ( "+" => "Numeric", "=" => "Special", 
                  "-" => "Other",   ":" => "Binary", 
                  "#" => "Dynamic", "%" => "Intermediate" );

# list of types (uppercase) for each qualifier
my %typesbyqual;
for( keys %qualnames ) {
  $typesbyqual{$_} = [];
}                  

# IDs start at 1000
my $maxid = 1000;
my $total = 0;

# some global variables
my $path;  # current file
my $line;  # current line (used for error reports and such)
my $today = `date`;

my %group_prefix = ( aid=>"AID", type=>"TID",types=>"TID" );
my %id_prefix = ( aid=>"Aid", type=>"Tp",types=>"Tp" );


# parse command line
#
@ARGV>1 or die "Usage: $0 [<global list file>] <list of .h files>";

for( @ARGV )
{
  # list file specified
  if( /^(.*)\/$global_listfile$/ ) {
    $global_listdir = $1;
    -d $1 or die "No such directory: $1";
  } else {
    push @sources,$_;           # else it's a source file to be scanned
  }
}
$global_listdir or die "Path to global list file not specified";
@sources or die "No source files specified, nothing to do";

# cvs update the global list file
#
print STDERR "=== Updating $global_listdir/$global_listfile\n";
print STDERR "    I will now attempt a cvs update on it, hold on\n"; 
my $cmd = "(cd $global_listdir && cvs update $global_listfile)";
print STDERR "    Running: $cmd\n";
system "$cmd";
$exit_value = $?>>8;
$exit_value == 0 or die "The cvs update command failed with exit code $exit_value";
print STDERR "    Looks like the cvs update succeeded\n";

#
# Define various handy functions for file processing
#
sub SplitPath {
  if( $_[0] =~ /^(.+)\/([^\/]+)$/ ) {
    return ($1,$2);
  } else {
    return (".",$_[0]);
  }
}

sub BasePath {
  my ($dir,$file) = SplitPath(@_);
  return $dir;
}

sub FileName {
  my ($dir,$file) = SplitPath(@_);
  return $file;
}

# This sub assigns a type qualifier
sub QualifyType {
  my ($id,$qual,$dir) = @_;
  $id = lc $id;
  # check that qualifier does not conflict with previous declaration
  if( $id_typequalifier{$id} ) 
  {
    $id_typequalifier{$id} ne $qual and die
      "$path:$line: type $id already declared as $id_typequalifier{$id} at $id_defined_at{$id}"; 
  }
  else 
  {
    $id_typequalifier{$id} = $qual;
  }
  # check that group does not conflict with previous declaration
  if( $typegroup{$id} )
  {
    $typegroup{$id} ne $dir and die
      "$path:$line: type $id already declared in $typegroup{$id} at $id_defined_at{$id}"; 
  }
  else
  {
    $typegroup{$id} = $dir;
  }
  # add to list of types for this qualifier
  push @{$typesbyqual{$qual}},$id;
}

# This sub reserves an ID. Arguments: ("[qualifier_char]name",number,directory)
sub ReserveId {
  my ($id,$num,$dir) = @_;
  my $id = lc $id; # to uppercase
  # strip off type qualifier, if any
  my $qualifier;
  $id =~ s/^([+%#:=-])// and $qualifier = $1; 
  # check for consistency with existing declarations
  my $id1 = $id_nummap{$num};
  my $num1 = $id_idmap{$id};
  !$id1 or $id1 eq $id or
      die "$path:$line: $num already assigned to $id1 from $id_defined_at{$id1}";
  !$num1 or $num1 == $num or
      die "$path:$line: $id already defined as $num1 at $id_defined_at{$id}";
  # place into maps
  $id_idmap{$id} = $num;
  $id_nummap{$num} = $id;
  $id_defined_at{$id} = "$path:$line";
  # qualify type if is a type
  QualifyType($id,$qualifier,$dir) if $qualifier;
  # update max ID number
  $maxid > $num or $maxid = $num;
}

#
# This sub reads existing IDs from a list file
#
sub ReadListFile 
{
  $path = $_[0];  
  my ($dir,$file) = SplitPath($path);
  my $count = 0;
  unless( open INFILE,"<$path" ) {
    warn "=== Can't open $path: $!\n";
    return 0;
  }
  # scan the list file
  $line = 0;
  while( <INFILE> )
  {
    $line++;
    next if /^\s*$/ or /^\s*;/;
    if( /\s*(\w+)\s+(\d+)\s*(; from (.*))?$/ ) {
      my ($id,$num,$dum,$from) = (lc $1,$2,$3,$4);
      ReserveId($id,$num,$dir);
      $id_defined_at{$id} = "$from"; # override the from line with stuff from file
      $count++;
    } else {
      print STDERR "$path:$line: warning: unable to parse this line, skipping\n";
    }
  }
  close INFILE;
  print STDERR "=== $path contains $count IDs\n";
  return $count;
}

#
# This sub reads ID declarations (#pragma aid, #pragma type, etc.)
# from a source file
#
sub ReadSourceFile {
  $path = $_[0];  
  my ($dir,$file) = SplitPath($path);
  my @aidgroups = ();
  my @typegroups = ();
  my $declcount = 0;
  open INFILE,"<$path" or die "open($path): $!";

  $group_regen{$dir} = 1;
  $line = 0;
  while(<INFILE>)
  {
    $line++;
    next unless /^\s*#pragma\s+(\w+)\s+(.*)$/;
    my $keyword = $1;
    my @tokens = split /\s+/,$2;
    
    if( $keyword eq "aidgroup" or $keyword eq "typegroup" ) {
      # group name? Check that it matches any previous declarations
      if( $groupname{$dir} ) {
        $groupname{$dir} eq $tokens[0] or die "$file:$line: group name '$tokens[0]' ".
            "conflicts '$groupname{$dir}' declared at $group_defined_at{$dir}";
      } else { # declares new group name
        $groupname{$dir} = $tokens[0];
        $group_defined_at{$dir} = "$path:$line";
      }
      next;
    }
    # process an aid or types keyword
    my $istype = 0;
    if( $keyword =~ /^types?$/ )  {
      $path =~ /\.h$/ or die "$path:$line: type declarations can only be inserted in .h files"; 
      $istype = 1;
    }
    elsif( $keyword !~ "aids?" ) {
      # skip any other pragmas
      next;
    }
    # now, process the IDs
    $declcount++;
    my $id;
    my $include = 1;
    foreach $id (@tokens) 
    {
      # check for noinclude keyword
      if( $id eq "noinclude" )
      {
        $include = 0;
        next;
      }
      # check for type qualifier & strip it
      my $qualifier = "";
      if( $istype ) {
        if( $id =~ s/^([+%#:=-])// ) {
          $qualifier = $1; 
        } else {
          die "$file:$line: missing type qualifier for $id";
        }
      }
      # strip off number, if assigned
      $explicit_number = ($id =~ s/=(\d+)$//) ? $1 : 0;
      # print $id,$explicit_number,"\n";
      # strip off namespace, if specified
      if( $istype )
      {
        if( $id =~ /(.*)::([^:]+)$/ ) {
          $full_id = $id;
          $id =~ s/:://g; 
          $id_qualified_typename{lc $id} = $full_id;
        } else {
          $id_qualified_typename{lc $id} = $id;
        }
      }
      # ID is lowercase id (duh!)
      my $ID = lc $id;
      # remember where it was defined
      $id_defined_at{$ID} = "$path:$line" unless $id_defined_at{$ID};
      $group_newids{$dir}++ unless $id_idmap{$ID};  # count as new?
      # assign ID to group      
      if( $explicit_number )  # number assigned?
      { 
        ReserveId($id,$explicit_number,$dir);
      }
      else              # number will be allocated, if not already defined
      {
        unless( $id_idmap{$ID} )
        {
          $id_idmap{$ID} = -1;           # will allocate later
          push @newids,$id;
        }
      }
      # assign ID to group
      defined $grouplist{$dir} or $grouplist{$dir} = [];
      # add to group list (if not yet there)
      push @{$grouplist{$dir}},$id  unless grep /^$id$/,@{$grouplist{$dir}};
      # assign type qualifier
      if( $istype ) {
        QualifyType($id,$qualifier,$dir);
        # if dynamic type or special or structure, then add to type header map
        # (unless disabled by the noinclude keyword)
        if( $qualifier =~ /^[:#=]$/ and $include ) {
          $id_typeheader{$ID} and die "$path:$line: type $id already declared in $id_typeheader{$ID}"; 
          $id_typeheader{$ID} = $file;
        }
      }
    } # end foreach $id (@tokens)
  } # end while(<INFILE>)
  close INFILE;
  return $declcount;
}

# Scan existing AIDs from global list file
#
ReadListFile("$global_listdir/$global_listfile");

# Scan for new AIDs in source files
#
print STDERR "=== Scanning source files:\n";
my $decl = 0;
for( @sources ) {
  $decl += ReadSourceFile($_);
}
# Print results
print STDERR "    $decl #pragmas processed\n";
for( keys %grouplist )
{
  printf STDERR "    aidgroup %s: %d IDs, %d new%s\n",$groupname{$_},
    scalar @{$grouplist{$_}},$group_newids{$_},
    $group_regen{$_} ? ", will refresh" : "";
}

# Assign new numbers to any remaining unassigned IDs
if( @newids ) {
  print STDERR "=== Assigning new IDs: ",join(",",@newids),"\n";
} else {
  print STDERR "=== Assigning new IDs: none\n";
}
for( keys %id_idmap ) {
  if( $id_idmap{$_} < 0 ) {
    $id_idmap{$_} = ++$maxid;
  }
}

# 
# This sub compares a new file with an older version,
# and replaces them if there are any differences
#
sub ReplaceIfDiff {
  my ($old,$new) = @_;
  if( -f $old and system("diff $old $new >/dev/null") == 0 ) {
    print STDERR "    $old: no change\n";
    unlink($new);
    return 0;
  } else {
    system("mv -f $new $old"); 
    return 1;
  }
}

# [re]generate the global list file
#
if( @newids )
{
  print STDERR "=== Regenerating the global list file:\n";
  $path = "$global_listdir/$global_listfile";
  printf STDERR "    $path: [re]generating with %d IDs\n",scalar keys %id_idmap;
  open(OUTFILE,">$path.new") or die "open($path.new): $!";
  for( sort keys %id_idmap ) {
    printf OUTFILE "%-32s %-10d ; from %s\n",$id_typequalifier{$_}.$_,$id_idmap{$_},$id_defined_at{$_};
  }
  close OUTFILE;
  if( ReplaceIfDiff($path,"$path.new") )
  {
    print STDERR "    I will now attempt a cvs commit on it, hold on\n"; 
    my $cmd = "(cd $global_listdir && cvs commit -m'%[ER: 42]%' $global_listfile)";
    print STDERR "    Running: $cmd\n";
    system "$cmd";
    $exit_value = $?>>8;
    $exit_value == 0 or die "The cvs commit command failed with exit code $exit_value";
    print STDERR "    Looks like the cvs commit succeeded\n";
  }
}
  
# Now, write out updated files
#
print STDERR "=== Generating source files:\n";
foreach $dir ( keys %group_regen )
{
  next unless @{$grouplist{$dir}};
  my $group = $groupname{$dir};
  $group or die "$dir: no group name declaration found anywahere\n";
  #  
  # generate AID-group.h and TID-group.h files  
  #
  foreach $is_tid (0,1) 
  {
    my $headername = sprintf($is_tid ? $tidheadername : $aidheadername,$group);
    my $idtypename = $is_tid ? "TypeId" : "AtomicID";
    
    $path = "$dir/$headername";
    print STDERR "    $path: [re]generating: ";
    my $idcount = 0;

    open(OUTFILE,">$path.new") or die "open($path.new): $!";
    $headername =~ s/\W/_/g;
    my $include = $is_tid ? "DMI/TypeId.h" : "DMI/AtomicID.h";

    print OUTFILE <<______END_OF_QUOTE;
      #ifndef $headername
      #define $headername 1

      // This file is generated automatically -- do not edit
      // Generated by $0
      #include "$include"

      // should be called somewhere in order to link in the registry
      int aidRegistry_$group ();

______END_OF_QUOTE
    foreach $id ( sort @{$grouplist{$dir}} ) 
    {
      my $name = $id =~ /^\/(.*)$/ ? $1 : ( $is_tid ? "Tp$id" : "Aid$id" );
      my $codename = $name;
      $ID = lc $id;
      my $qual = $id_typequalifier{$ID};
      next if $is_tid and not $qual;  # TID -- only generate types
      $idcount++;
      # protect from re-declaring
      print OUTFILE "#ifndef _defined_id_$codename\n#define _defined_id_$codename 1\n";
      # generate constant definition
      printf OUTFILE "%-50s// from %s\n",
             sprintf("const %s %s(%d);",$idtypename,$codename,-$id_idmap{$ID}),
             $id_defined_at{$ID};
      printf OUTFILE "const int %s_int = %d;\n",$codename,-$id_idmap{$ID};
      if( $is_tid )
      {
        # for classes & structs, add a forward declaration
        # (but not for 'noinclude' types, such as std::string)
        my $fqid = $id_qualified_typename{$ID};
        if( $qual =~ /^[:#=]$/ and $id_typeheader{$ID} ) 
        {
          # does the type include a namespace? generate surrounding declarations
          if( $fqid ne $id )  
          {
            @names = split /::/,$fqid;
            $decl = "class " . (pop @names) . ";"; # pop off classname
            while( @names )
            {
              $decl = "namespace " . (pop @names) . " { " . $decl . " };";
            }
          }
          else {
            $decl = "class $id;";
          }
          print OUTFILE "$decl\n";
        }
        # generate type traits
        my $category = "";
        my $rettype = "const $fqid &";
        my $byref = "true";
        for( $qual )
        {
          /^\+/ and do { $category = "NUMERIC"; $rettype = "$fqid"; $byref="false" };
          /^:/ and $category = "BINARY";
          /^=/ and $category = "SPECIAL";
          /^#/ and $category = "DYNAMIC";
        }
        if( $category ne "" )
        {
          print OUTFILE <<______END_OF_QUOTE;
            template<>
            class DMIBaseTypeTraits<$fqid> : public TypeTraits<$fqid>
            {
              public:
              enum { isContainable = true };
              enum { typeId = ${codename}_int };
              enum { TypeCategory = TypeCategories::$category };
              enum { ParamByRef = $byref, ReturnByRef = $byref };
              typedef $rettype ContainerReturnType;
              typedef $rettype ContainerParamType;
            };
______END_OF_QUOTE
        }
      }
      print OUTFILE "#endif\n";
    }
    print OUTFILE "\n\n#endif\n";
    close OUTFILE;
    print STDERR "$idcount IDs\n";
    ReplaceIfDiff($path,"$path.new");
  }
  #
  # [re]generate a registry file
  #
  $path = "$dir/" . sprintf $mapfilename,$group;
  printf STDERR "    $path: [re]generating with %d IDs\n",scalar @{$grouplist{$dir}};
  open OUTFILE,">$path.new" or die "open($path.new): $!";
  # generate header
  print OUTFILE <<______END_OF_QUOTE;
    // This file is generated automatically -- do not edit
    // Generated by $0
    #include <DMI/AtomicID.h>
    #include <DMI/TypeInfo.h>
    #include <DMI/DynamicTypeManager.h>
    #include <DMI/Packer.h>
    
______END_OF_QUOTE
  # define constructors and packers for various types
  my %included = ();
  foreach $id (@{$grouplist{$dir}}) 
  {
    my $name = $id =~ /^\/(.*)$/ ? $1 : $id;
    my $codename = $name;
    $ID = lc $id;
    # if it's a type, register its type info and perhaps generate a constructor
    for( $id_typequalifier{$ID} )
    {
      my $fqid = $id_qualified_typename{$ID};
      last unless $_;
      if( $id_typeheader{$ID} ) {
        unless( $included{$id_typeheader{$ID}} ) {
          print OUTFILE "#include \"$id_typeheader{$ID}\"\n";
          $included{$id_typeheader{$type}} = 1;
        }
      }
      # generate methods for special types
      /^=/ and print OUTFILE <<______END_OF_QUOTE;
        void * __new_$codename  (int n) 
        { return new $fqid [n]; }  
        void __delete_$codename (void *ptr) 
        { delete [] static_cast<$fqid*>(ptr); } 
        void __copy_$codename (void *to,const void *from) 
        { *static_cast<$fqid*>(to) = *static_cast<const $fqid*>(from); } 
        size_t __pack_$codename (const void *arr,int n,void * block,size_t &nleft ) 
        { return ArrayPacker<$fqid>::pack(static_cast<const $fqid*>(arr),n,block,nleft); } 
        void * __unpack_$codename (const void *block,size_t sz,int &n) 
        { return ArrayPacker<$fqid>::allocate(block,sz,n); } 
        size_t __packsize_$codename (const void *arr,int n) 
        { return ArrayPacker<$fqid>::packSize(static_cast<const $fqid*>(arr),n); }
______END_OF_QUOTE
      # generate TypeInfo entry    
      /^#/ and print OUTFILE 
          "BlockableObject * __construct_$codename (int n) { return n>0 ? new $fqid [n] : new $fqid; }\n";
    }
  }
  # now, add stuff to various registries  
  print OUTFILE <<______END_OF_QUOTE;
  
    int aidRegistry_$group ()
    {
      static int res = 

______END_OF_QUOTE
  
  my %included = ();
  foreach $id (@{$grouplist{$dir}})
  {
    my $name = $id =~ /^\/(.*)$/ ? $1 : $id;
    my $codename = $name;
    $ID = lc $id;
    my $fqid = $id_qualified_typename{$ID};
    my $num = -$id_idmap{$ID};
    print OUTFILE "        AtomicID::registerId($num,\"$name\")+\n";
    # if it's a type, register its type info 
    for( $id_typequalifier{$ID} )
    {
      last unless $_;
      print OUTFILE "        TypeInfoReg::addToRegistry($num,TypeInfo(";
      
      /^\+/ and print OUTFILE "TypeInfo::NUMERIC,sizeof($name)))+\n",;
      /^:/ and print OUTFILE "TypeInfo::BINARY,sizeof($name)))+\n",;
      /^=/ and print OUTFILE "TypeInfo::SPECIAL,sizeof($name),__new_$codename,__delete_$codename,__copy_$codename,\n".
                     "                __pack_$codename,__unpack_$codename,__packsize_$codename))+\n";
      /^-/ and print OUTFILE "TypeInfo::OTHER,0))+\n";
      /^%/ and print OUTFILE "TypeInfo::INTERMEDIATE,0))+\n";
      /^#/ and print OUTFILE "TypeInfo::DYNAMIC,0))+\n" . 
          "        DynamicTypeManager::addToRegistry($num,__construct_$codename)+\n";
    }
  }
  print OUTFILE <<______END_OF_QUOTE;
    0;
    return res;
  }
  
  int __dum_call_registries_for_$group = aidRegistry_$group();

______END_OF_QUOTE
  
  close OUTFILE;
  ReplaceIfDiff($path,"$path.new");

  #
  # [re]generate a typeiter file
  #
  $path = "$dir/" . sprintf $typeitername,$group;
  printf STDERR "=== Generating typelists\n";
  printf STDERR "    $path: [re]generating with %d IDs\n",scalar @{$grouplist{$dir}};
  open OUTFILE,">$path.new" or die "open($path.new): $!";
  # generate iterator macros
  print OUTFILE <<______END_OF_QUOTE;
    // This file is generated automatically -- do not edit
    // Generated by $0
    #ifndef _TypeIter_${group}_h
    #define _TypeIter_${group}_h 1

______END_OF_QUOTE

  my $sep = "\\\n        ";
  foreach $qual (keys %qualnames)
  {
    # get all types for this qualifier defined in this dir
    @types = map { $typegroup{$_} eq $dir ? $_ : () } @{$typesbyqual{$qual}};
    @types = sort {$a <=> $b} map { $id_qualified_typename{$_} } @types;
    # produces macro deinfitions
    printf STDERR "      %-14s%s","${qualnames{$qual}}: ",
                  join(" ",@types) . "\n";
    print OUTFILE "\n\n#define DoForAll${qualnames{$qual}}Types_$group(Do,arg,separator) $sep",
              join(" separator $sep",map { "Do($_,arg)" } @types)
  }
  
  print OUTFILE "\n#endif\n";
  close OUTFILE;
  ReplaceIfDiff($path,"$path.new");
}

