//  Thread.h: basic header for the Thread package
//
//  Copyright (C) 2002-2007
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  and The MeqTree Foundation
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

#ifndef LOFAR_COMMON_THREAD_H
#define LOFAR_COMMON_THREAD_H
    
#include <TimBase/Thread/Thread.h>
#include <TimBase/Thread/Key.h>
#include <TimBase/Thread/Mutex.h>
#include <TimBase/CheckConfig.h>
    
// You should invoke CHECK_CONFIG_THREADS(id) in every header file 
// that defines a data structure that depends on USE_THREADs.
#ifdef USE_THREADS
  #define CHECK_CONFIG_THREADS(id) CHECK_CONFIG(id,UseThreads,yes);
#else
  #define CHECK_CONFIG_THREADS(id) CHECK_CONFIG(id,UseThreads,no);
#endif
    
#endif
    
