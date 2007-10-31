#
#% $Id$
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation &
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

 # standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

import Meow
import Meow.StdTrees
from Meow import Context
from Meow import ParmGroup

# MS options first
mssel = Context.mssel = Meow.MSUtils.MSSelector(has_input=True,tile_sizes=None,flags=False,hanning=True);
# MS compile-time options
TDLCompileOptions(*mssel.compile_options());
# MS run-time options
TDLRuntimeMenu("MS/data selection options",*mssel.runtime_options());
## also possible:

# output mode menu
TDLCompileMenu("What do we want to do",
  TDLMenu("Calibrate",
     TDLOption('cal_vis',"Calibrate visibilities",True),
     TDLOption('cal_ampl',"Calibrate amplitudes",False),
     TDLOption('cal_log_ampl',"Calibrate log-amplitudes",False),
     TDLOption('cal_phase',"Calibrate phases",False),
     TDLOption('cal_corr',"Use correlations",["all","XX YY","XY YX"]),
     toggle='do_solve',open=True,exclusive='solve_type'
  ),
  TDLOption('do_subtract',"Subtract sky model and generate residuals",True),
  TDLOption('do_correct',"Correct the data or residuals",True),
   );
do_correct_sky = False;
  #TDLOption('do_correct_sky',"...include sky-Jones correction for first source in model",True));

# now load optional modules for the ME maker
from Meow import MeqMaker
meqmaker = MeqMaker.MeqMaker(solvable=True);

#%# Need to make this more specific, implement my own models and OR_GSM
# specify available sky models
# these will show up in the menu automatically
import central_point_source
import model_3C343
import Meow.LSM
lsm = Meow.LSM.MeowLSM(include_options=False);

meqmaker.add_sky_models([central_point_source,model_3C343,lsm]);

# now add optional Jones terms
# these will show up in the menu automatically

#%# This can be removed
# E - beam
import wsrt_beams
meqmaker.add_sky_jones('E','beam',[wsrt_beams]);

#%# This is the ionosphere bit
# Z - iono
import solvable_ionosphere
# label = Z, the label is used to name the NodeStub
# name = iono, the name is used to ??? do what ???
# module = solvable_ionosphere.Iono() (this is a list, needs the brackets!)
meqmaker.add_sky_jones('Z','iono',[solvable_ionosphere.Iono()]);

#%# This can be removed
# D - leakage
import polarization_jones
meqmaker.add_uv_jones('D','polarization leakage',
  [ polarization_jones.CoupledLeakage(),
    polarization_jones.DecoupledLeakage() ]);

#%# This can be removed
# B - bandpass, G - gain 
import solvable_jones
meqmaker.add_uv_jones('B','bandpass',
  [ solvable_jones.DiagAmplPhase(),
    solvable_jones.FullRealImag() ]);
meqmaker.add_uv_jones('G','receiver gains/phases',solvable_jones.DiagAmplPhase());

# very important -- insert meqmaker's options properly
TDLCompileOptions(*meqmaker.compile_options());

#%# Now set-up the forest
def _define_forest (ns):
  #%# First define the array setup (we are now working with WSRT!)
  #%# Need to adjust this for VLS MS, use all 27 antennas
  ANTENNAS = mssel.get_antenna_set(range(1,15));
  array = Meow.IfrArray(ns,ANTENNAS,mirror_uvw=False);
  observation = Meow.Observation(ns);
  Meow.Context.set(array,observation);
  stas = array.stations();

  #%# The ParmGroup is initialized in the solvable_ionosphere.py module
  #%# or the solvable_jones module. They both need to have a compute_jones
  #%# function to do this.
  # make a ParmGroup and solve jobs for source fluxes
  srcs = meqmaker.get_source_list(ns);
  if srcs:
    # make dictionary of source parameters. Use a dict since
    # sources may share paramaters, so we don't want them in the list twice
    #%# What is a dictionary? Some sort of class, but what does it do?
    #%# This section also seems to solve for source parms, which we don't
    #%# need at the moment. Leave it in?
    parms = {};
    for src in srcs:
      for p in src.visibilities().search(tags="source solvable"):
        parms[p.name] = p;
    if parms:
      pg_src = ParmGroup.ParmGroup("source",parms.values(),
                  table_name="sources.mep",
                  individual=True,bookmark=True);
      # now make a solvejobs for the source
      ParmGroup.SolveJob("cal_source","Calibrate source model",pg_src);

  # make spigot nodes
  spigots = spigots0 = outputs = array.spigots();
  # ...and an inspector for them
  Meow.StdTrees.vis_inspector(ns.inspector('input'),spigots,bookmark="Inspect input data");
  inspectors = [ ns.inspector('input') ];

  # make a predict tree using the MeqMaker
  if do_solve or do_subtract:
    predict = meqmaker.make_tree(ns);

  # make nodes to compute residuals
  if do_subtract:
    residuals = ns.residuals;
    for p,q in array.ifrs():
      residuals(p,q) << spigots(p,q) - predict(p,q);
    outputs = residuals;

  # and now we may need to correct the outputs
  if do_correct:
    if do_correct_sky:
      srcs = meqmaker.get_source_list(ns);
      sky_correct = srcs and srcs[0];
    else:
      sky_correct = None;
    outputs = meqmaker.correct_uv_data(ns,outputs,sky_correct=sky_correct);

  # make solve trees
  if do_solve:
    # extract selected correlations
    if cal_corr != "all":
      if cal_corr == "XX YY":
        index = [0,3];
      else:
        index = [1,2];
      for p,q in array.ifrs():
        ns.sel_predict(p,q) << Meq.Selector(predict(p,q),index=index,multi=True);
        ns.sel_spigot(p,q)  << Meq.Selector(spigots(p,q),index=index,multi=True);
      spigots = ns.sel_spigot;
      predict = ns.sel_predict;
    # inputs to the solver are based on calibration type
    # if calibrating visibilities, feed them to condeq directly
    if solve_type == 'cal_vis':
      observed = spigots;
      model    = predict;
    # else take ampl/phase component
    else:
      model = ns.model;
      observed = ns.observed;
      if solve_type == 'cal_ampl':
        for p,q in array.ifrs():
          observed(p,q) << Meq.Abs(spigots(p,q));
          model(p,q)  << Meq.Abs(predict(p,q));
      elif solve_type == 'cal_log_ampl':
        for p,q in array.ifrs():
          observed(p,q) << Meq.Log(Meq.Abs(spigots(p,q)));
          model(p,q)  << Meq.Log(Meq.Abs(predict(p,q)));
      elif solve_type == 'cal_phase':
        for p,q in array.ifrs():
          observed(p,q) << 0;
          model(p,q)  << Meq.Abs(predict(p,q))*Meq.FMod(Meq.Arg(spigots(p,q))-Meq.Arg(predict(p,q)),2*math.pi);
      else:
        raise ValueError,"unknown solve_type setting: "+str(solve_type);
    # make a solve tree
    solve_tree = Meow.StdTrees.SolveTree(ns,model);
    # the output of the sequencer is either the residuals or the spigots,
    # according to what has been set above
    outputs = solve_tree.sequencers(inputs=observed,outputs=outputs);

  # make sinks and vdm.
  # The list of inspectors must be supplied here
  inspectors += meqmaker.get_inspectors() or [];
  Meow.StdTrees.make_sinks(ns,outputs,spigots=spigots0,post=inspectors);

  # very important -- insert meqmaker's runtime options properly
  # this should come last, since runtime options may be built up during compilation.
  TDLRuntimeOptions(*meqmaker.runtime_options(nest=False));
  # and insert all solvejobs
  TDLRuntimeOptions(*ParmGroup.get_solvejob_options());
  # finally, setup imaging options
  imsel = mssel.imaging_selector(npix=512,arcmin=meqmaker.estimate_image_size());
  TDLRuntimeMenu("Imaging options",*imsel.option_list());


