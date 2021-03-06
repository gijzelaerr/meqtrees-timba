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

#include <OCTOPUSSY/Dispatcher.h>
#include <OCTOPUSSY/Gateways.h>
#include <OCTOPUSSY/GWClientWP.h>
#include <OCTOPUSSY/ListenerWP.h>
#include <DMI/Global-Registry.h>
#include <DMI/Exception.h>
#include <sys/types.h>
#include <unistd.h>    

using namespace Octopussy;

int aidRegistry_Meq();
int aidRegistry_MeqNodes();
int aidRegistry_MeqServer();

static int dum = aidRegistry_Global() +
                 aidRegistry_Meq() +
                 aidRegistry_MeqNodes() +
                 aidRegistry_MeqServer();
    

int main (int argc,const char *argv[])
{
  Debug::initLevels(argc,argv);
  OctopussyConfig::initGlobal(argc,argv);
  
  try 
  {
    Dispatcher dsp;
    dsp.attach(new ListenerWP);
    initGateways(dsp);
    dsp.start();
    dsp.pollLoop();
    dsp.stop();
  }
  catch( std::exception &err ) 
  {
    cerr<<"\nCaught exception: "<<exceptionToString(err);
    return 1;
  }
  cerr<<"Exiting normally\n";
  return 0;
}

