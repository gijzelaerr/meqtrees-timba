#
# lofar_xerces.m4
#
#
# lofar_XERCES
#
# Macro to check for XERCES (XML parser) installation
#
# lofar_XERCES([DEFAULT-PREFIX])
#
# e.g. lofar_XERCES(["/usr/local/xerces"])
#
# If uses the library name libxerces. If needed, one has to create a
# a symlink after installing xerces. E.g.
#    cd  xerces-c1_7_0-linux7.2/lib
#    ln -s libxerces-c1_7_0.so libxerces.so
# -------------------------
#
AC_DEFUN(lofar_XERCES,dnl
[dnl
AC_PREREQ(2.13)dnl
ifelse($1, [], define(DEFAULT_XERCES_PREFIX,[/usr/local/xerces]), define(DEFAULT_XERCES_PREFIX,$1))
AC_ARG_WITH(xerces,
	[  --with-xerces[=PFX]     prefix where Xerces is installed (default=]DEFAULT_XERCES_PREFIX[)],
	[with_xerces=$withval],
	[with_xerces="no"])
[
if test "$with_xerces" = "no"; then
  enable_xerces=no
else
  if test "$with_xerces" = "yes"; then
    xerces_prefix=]DEFAULT_XERCES_PREFIX
[
  else
    xerces_prefix=$withval
  fi
  enable_xerces=yes
]
##
## Check in normal location and suggested location
##
AC_CHECK_FILE([$xerces_prefix/include/xercesc/sax2/],
			[lofar_cv_header_xerces=yes],
			[lofar_cv_header_xerces=no])dnl
[
  if test $lofar_cv_header_xerces = yes ; then

	XERCES_PATH="$xerces_prefix"

	XERCES_CPPFLAGS="-I$XERCES_PATH/include"
	XERCES_LDFLAGS="-L$XERCES_PATH/lib"
	XERCES_LIBS="-lxerces"

	CPPFLAGS="$CPPFLAGS $XERCES_CPPFLAGS"
	LDFLAGS="$LDFLAGS $XERCES_LDFLAGS"
	LIBS="$LIBS $XERCES_LIBS"
]
dnl
AC_SUBST(CPPFLAGS)dnl
AC_SUBST(LDFLAGS)dnl
AC_SUBST(LIBS)dnl
dnl
AC_DEFINE(HAVE_XERCES, 1, [Define if Xerces is installed])dnl
[
  else]
AC_MSG_ERROR([Could not find Xerces in $xerces_prefix])
[
    enable_xerces=no
  fi
fi]
AM_CONDITIONAL(HAVE_XERCES, [test "$enable_xerces" = "yes"])
])
