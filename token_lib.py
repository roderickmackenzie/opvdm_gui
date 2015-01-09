#    Organic Photovoltaic Device Model - a drift diffusion base/Shockley-Read-Hall
#    model for organic solar cells. 
#    Copyright (C) 2012 Roderick C. I. MacKenzie
#
#	roderick.mackenzie@nottingham.ac.uk
#	www.opvdm.com
#	Room B86 Coates, University Park, Nottingham, NG7 2RD, UK
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import pygtk
pygtk.require('2.0')
import gtk
import sys
import os
import shutil
import signal
import subprocess

class my_data():
	token=""
	units=""
	info=""
	def __init__(self,a,b,c,d,e,f):
		self.token=a
		self.units=b
		self.info=c
		self.opt=d
		self.number_type=e
		self.number_mul=f

class tokens:
	lib=[]
	lib.append(my_data("#mueffe","m<sup>2</sup>V<sup>-1</sup>s<sup>-1</sup>","Electron mobility",["text"],"e",1.0))
	lib.append(my_data("#mueffh","m<sup>2</sup>V<sup>-1</sup>s<sup>-1</sup>","Hole mobility",["text"],"e",1.0))
	lib.append(my_data("#Ntrape","m<sup>-3</sup> eV<sup>-1</sup>","Electron trap density",["text"],"e",1.0))
	lib.append(my_data("#Ntraph","m<sup>-3</sup> eV<sup>-1</sup>","Hole trap density",["text"],"e",1.0))
	lib.append(my_data("#Etrape","eV","Electron tail slope",["text"],"e",1.0))
	lib.append(my_data("#Etraph","eV","Hole tail slope",["text"],"e",1.0))
	lib.append(my_data("#epsilonr","au","Relative permittivity",["text"],"e",1.0))
	lib.append(my_data("#srhsigman_e","m<sup>-2</sup>","Free electron to Trapped electron",["text"],"e",1.0))
	lib.append(my_data("#srhsigmap_e","m<sup>-2</sup>","Trapped electron to Free hole",["text"],"e",1.0))
	lib.append(my_data("#srhsigman_h","m<sup>-2</sup>","Trapped hole to Free electron",["text"],"e",1.0))
	lib.append(my_data("#srhsigmap_h","m<sup>-2</sup>","Free hole to Trapped hole",["text"],"e",1.0))
	lib.append(my_data("#Rshunt","Ohms","Shunt resistance",["text"],"e",1.0))
	lib.append(my_data("#Rcontact","Ohms","Series resistance",["text"],"e",1.0))
	lib.append(my_data("#lcharge","m<sup>-3</sup>","Charge on left contact",["text"],"e",1.0))
	lib.append(my_data("#rcharge","m<sup>-3</sup>","Charge on right contact",["text"],"e",1.0))
	lib.append(my_data("#Vstart","V","Start voltage",["text"],"e",1.0))
	lib.append(my_data("#Vstop","V","Stop voltage",["text"],"e",1.0))
	lib.append(my_data("#Vstep","V","Voltage step",["text"],"e",1.0))
	lib.append(my_data("#I0","Apms","I0",["text"],"e",1.0))
	lib.append(my_data("#nid","(a.u.)","ideality factor",["text"],"e",1.0))
	lib.append(my_data("#Psun","0/1000","Intensity of the sun",["text"],"e",1.0))
	lib.append(my_data("#simplephotondensity","m<sup>-2</sup>s<sup>-1</sup>","Photon density",["text"],"e",1.0))
	lib.append(my_data("#simple_alpha","m<sup>-1</sup>","Absorption of material",["text"],"e",1.0))
	lib.append(my_data("#plot","1/0","Plot bands etc.. ",["1","0"],"e",1.0))
	lib.append(my_data("#celiv_laser_eff","1/0","#celiv_laser_eff",["text"],"e",1.0))
	lib.append(my_data("#doping","m<sup>-3</sup>","Doping",["text"],"e",1.0))
	lib.append(my_data("#simmode","au","#simmode",["text"],"e",1.0))
	lib.append(my_data("#Nc","m<sup>-3</sup>","Effective density of free electron states",["text"],"e",1.0))
	lib.append(my_data("#Nv","m<sup>-3</sup>","Effective density of free hole states",["text"],"e",1.0))
	lib.append(my_data("#maxelectricalitt","au","Max electrical itterations",["text"],"e",1.0))
	lib.append(my_data("#electricalclamp","au","Electrical clamp",["text"],"e",1.0))
	lib.append(my_data("#posclamp","au","Poisson clamping",["text"],"e",1.0))
	lib.append(my_data("#electricalerror","au","Minimum electrical error",["text"],"e",1.0))
	lib.append(my_data("#free_to_free_recombination","m<sup>3</sup>s<sup>-1</sup>","Free to free recombination",["text"],"e",1.0))
	lib.append(my_data("#sun","filename","Sun's spectra",["text"],"e",1.0))
	lib.append(my_data("#meshpoints","au","Mesh points (x)",["text"],"e",1.0))
	lib.append(my_data("#lpoints","au","Mesh points (lambda)",["text"],"e",1.0))
	lib.append(my_data("#lstart","m","Lambda start",["text"],"e",1.0))
	lib.append(my_data("#lstop","m","Lambda stop",["text"],"e",1.0))
	lib.append(my_data("#laserwavelength","m","Laser wavelength",["text"],"e",1.0))
	lib.append(my_data("#spotx","m","#spotx",["text"],"e",1.0))
	lib.append(my_data("#spoty","m","#spoty",["text"],"e",1.0))
	lib.append(my_data("#pulseJ","J","#pulseJ",["text"],"e",1.0))
	lib.append(my_data("#pulseL","s","#pulseL",["text"],"e",1.0))
	lib.append(my_data("#gather","au","#gather",["text"],"e",1.0))
	lib.append(my_data("#dlength","m","#dlength",["text"],"e",1.0))
	lib.append(my_data("#electron_eff","0-1","#electron_eff",["text"],"e",1.0))
	lib.append(my_data("#hole_eff","0-1","#hole_eff",["text"],"e",1.0))
	lib.append(my_data("#function","au","#function",["text"],"e",1.0))
	lib.append(my_data("#lr_pcontact","left/right","P contact on left or right",["left","right"],"s",1.0))
	lib.append(my_data("#Vexternal","V","start voltage",["text"],"e",1.0))
	lib.append(my_data("#Vmax","V","Max voltage",["text"],"e",1.0))
	lib.append(my_data("#celiv_t0","s","#celiv_t0",["text"],"e",1.0))
	lib.append(my_data("#celiv_t1","s","#celiv_t1",["text"],"e",1.0))
	lib.append(my_data("#celiv_t2","s","#celiv_t2",["text"],"e",1.0))
	lib.append(my_data("#Eg","eV","Eg",["text"],"e",1.0))
	lib.append(my_data("#Xi","eV","Xi",["text"],"e",1.0))
	lib.append(my_data("#start_stop_time","s","Time of pause",["text"],"e",1.0))
	lib.append(my_data("#stopstart","1/0","Pause between iterations",["1","0"],"e",1.0))
	lib.append(my_data("#invert_current","true/false","Invert output",["text"],"e",1.0))
	lib.append(my_data("#lr_bias","left/right","Bias left or right",["left","right"],"s",1.0))
	lib.append(my_data("#otherlayers","m","Other layers",["text"],"e",1.0))
	lib.append(my_data("#dump_slices","1/0","Dump slices",["1","0"],"e",1.0))
	lib.append(my_data("#dump_dynamic","1/0","Dump dynamic",["1","0"],"e",1.0))
	lib.append(my_data("#dump_zip_files","1/0","Dump zip files",["1","0"],"e",1.0))
	lib.append(my_data("#tofstop","s","ToF stop time",["text"],"e",1.0))
	lib.append(my_data("#tof_cap_escape_fx","s<sup>-1</sup>","Capture to escape frequency",["text"],"e",1.0))
	lib.append(my_data("#toflaseroff","s","ToF laser off time",["text"],"e",1.0))
	lib.append(my_data("#dt","s","ToF time step",["text"],"e",1.0))
	lib.append(my_data("#tofdtmull","au","ToF dt multiplier",["text"],"e",1.0))
	lib.append(my_data("#toflaserpower","0-1","ToF laser power",["text"],"e",1.0))
	lib.append(my_data("#start_steps","1/0","ToF steps before start",["text"],"e",1.0))
	lib.append(my_data("#tof_voltage","V","ToF voltage",["text"],"e",1.0))
	lib.append(my_data("#tof_Rshort","Ohms","Rshort",["text"],"e",1.0))
	lib.append(my_data("#use_capacitor","1/0","Use capacitor",["1","0"],"e",1.0))
	lib.append(my_data("#stark_startime","s","startime",["text"],"e",1.0))
	lib.append(my_data("#stark_ea_factor","au","ea_factor",["text"],"e",1.0))
	lib.append(my_data("#stark_Np","1/0","Np",["text"],"e",1.0))
	lib.append(my_data("#stark_den","1/0","den",["text"],"e",1.0))
	lib.append(my_data("#stark_externalv","V","externalv",["text"],"e",1.0))
	lib.append(my_data("#stark_dt_neg_time","s","dt_neg_time",["text"],"e",1.0))
	lib.append(my_data("#stark_dt","s","dt",["text"],"e",1.0))
	lib.append(my_data("#stark_dt_mull","au","dt_mull",["text"],"e",1.0))
	lib.append(my_data("#stark_stop","s","stop",["text"],"e",1.0))
	lib.append(my_data("#stark_stark","1/0","stark",["text"],"e",1.0))
	lib.append(my_data("#stark_lasereff","1/0","lasereff",["text"],"e",1.0))
	lib.append(my_data("#stark_probe_wavelength","m","wavelength",["text"],"e",1.0))
	lib.append(my_data("#stark_sim_contacts","1/0","sim_contacts",["text"],"e",1.0))
	lib.append(my_data("#pulse_dt","s","dt",["text"],"e",1.0))
	lib.append(my_data("#pulse_t0","s","time<sub>0</sub>",["text"],"e",1.0))
	lib.append(my_data("#pulse_t1","s","time<sub>1</sub>",["text"],"e",1.0))
	lib.append(my_data("#pulse_t2","s","time<sub>2</sub>",["text"],"e",1.0))
	lib.append(my_data("#pulse_Vexternal","Volts","V<sub>external</sub>",["text"],"e",1.0))
	lib.append(my_data("#pulse_repeat","number","Repeat",["text"],"e",1.0))
	lib.append(my_data("#Rshort_pulse","Ohms","R<sub>short</sub>",["text"],"e",1.0))
	lib.append(my_data("#pulse_laser_on","s","laser_on",["text"],"e",1.0))
	lib.append(my_data("#pulse_laser_width","s","laser_width",["text"],"e",1.0))
	lib.append(my_data("#pulse_laser_power","J","laser_power",["text"],"e",1.0))
	lib.append(my_data("#pulse_light","1/0","pulse_light",["text"],"e",1.0))
	lib.append(my_data("#pulse_sun","J","pulse_sun",["text"],"e",1.0))
	lib.append(my_data("#pulse_shift","s","pulse_shift",["text"],"e",1.0))
	lib.append(my_data("#pulse_bigmeshstart","s","Big mesh start",["text"],"e",1.0))
	lib.append(my_data("#pulse_bigmeshstop","s","Big mesh stop",["text"],"e",1.0))
	lib.append(my_data("#pulse_bigdt","s","Big mesh dt",["text"],"e",1.0))
	lib.append(my_data("#photokit_points","s","points",["text"],"e",1.0))
	lib.append(my_data("#photokit_n","s","Wavelengths to simulate",["text"],"e",1.0))
	lib.append(my_data("#photokit_Vexternal","Volts","External voltage",["text"],"e",1.0))
	lib.append(my_data("#Rshort_photokit","Ohms","R<sub>short</sub>",["text"],"e",1.0))
	lib.append(my_data("#photokit_sun","1=1 Sun","Backgroud light bias",["text"],"e",1.0))
	lib.append(my_data("#photokit_modulation_max","1=1 Sun","Modulation depth",["text"],"e",1.0))
	lib.append(my_data("#photokit_modulation_fx","Hz","Modulation frequency",["text"],"e",1.0))
	lib.append(my_data("#Rshort_pulse_voc","Ohms","R short",["text"],"e",1.0))
	lib.append(my_data("#pulse_voc_laser_eff","0-1.0","Laser Efficiency",["text"],"e",1.0))
	lib.append(my_data("#pulse_voc_light_bias","0-1000","Light bias",["text"],"e",1.0))
	lib.append(my_data("#high_sun_scale","au","High light multiplyer",["text"],"e",1.0))
	lib.append(my_data("#Dphotoneff","0-1","Photon efficiency",["text"],"e",1.0))
	lib.append(my_data("#jv_step_mul","0-2.0","JV voltage step multiplyer",["text"],"e",1.0))
	lib.append(my_data("#dump_slices_by_time","1/0","dump slices by time",["1","0"],"e",1.0))
	lib.append(my_data("#dump_1d_slices","1/0","Dump 1D slices",["1","0"],"e",1.0))
	lib.append(my_data("#voc","V","V<sub>oc</sub>",["text"],"e",1.0))

	lib.append(my_data("#photokit_r","au","Re - Amps",["text"],"e",1.0))
	lib.append(my_data("#photokit_i","au","Im - Amps",["text"],"e",1.0))
	lib.append(my_data("#photokit_fx","Hz","Frequency",["text"],"e",1.0))
	lib.append(my_data("#Rscope","Ohms","Resistance of scope",["text"],"e",1.0))
	lib.append(my_data("#srh_bands","bands","Number of traps",["text"],"s",1.0))

	lib.append(my_data("#dostype","au","DoS distribution",["exponential","complex"],"s",1.0))

	lib.append(my_data("#sun_voc_single_point","1/0","Single point",["1","0"],"e",1.0))
	lib.append(my_data("#sun_voc_Psun_start","Suns","Start intensity",["text"],"e",1.0))
	lib.append(my_data("#sun_voc_Psun_stop","Suns","Stop intensity",["text"],"e",1.0))
	lib.append(my_data("#sun_voc_Psun_mul","au","step multiplier",["text"],"e",1.0))


	lib.append(my_data("#simplephotondensity","m<sup>-2</sup>s<sup>-1</sup>","Photon Flux",["text"],"e",1.0))
	lib.append(my_data("#simple_alpha","m<sup>-1</sup>","Absorption",["text"],"e",1.0))
	lib.append(my_data("#xlen","m","device width",["text"],"e",1.0))
	lib.append(my_data("#zlen","m","device breadth",["text"],"e",1.0))
	lib.append(my_data("#ver","","",["text"],"e",1.0))
	lib.append(my_data("#dostype","","",["text"],"e",1.0))
	lib.append(my_data("#me","","",["text"],"e",1.0))
	lib.append(my_data("#mh","","",["text"],"e",1.0))
	lib.append(my_data("#gendos","","",["text"],"e",1.0))
	lib.append(my_data("#notused","","",["text"],"e",1.0))
	lib.append(my_data("#notused","","",["text"],"e",1.0))
	lib.append(my_data("#Tstart","","",["text"],"e",1.0))
	lib.append(my_data("#Tstop","","",["text"],"e",1.0))
	lib.append(my_data("#Tpoints","","",["text"],"e",1.0))
	lib.append(my_data("#nstart","","",["text"],"e",1.0))
	lib.append(my_data("#nstop","","",["text"],"e",1.0))
	lib.append(my_data("#npoints","","",["text"],"e",1.0))
	lib.append(my_data("#nstart","","",["text"],"e",1.0))
	lib.append(my_data("#nstop","","",["text"],"e",1.0))
	lib.append(my_data("#npoints","","",["text"],"e",1.0))
	lib.append(my_data("#srhbands","","",["text"],"e",1.0))
	lib.append(my_data("#srh_start","","",["text"],"e",1.0))
	lib.append(my_data("#srhvth_e","","",["text"],"e",1.0))
	lib.append(my_data("#srhvth_h","","",["text"],"e",1.0))
	lib.append(my_data("#srh_cut","","",["text"],"e",1.0))
	lib.append(my_data("#lumodelstart","","",["text"],"e",1.0))
	lib.append(my_data("#lumodelstop","","",["text"],"e",1.0))
	lib.append(my_data("#homodelstart","","",["text"],"e",1.0))
	lib.append(my_data("#homodelstop","","",["text"],"e",1.0))
	lib.append(my_data("#gaus_mull","","",["text"],"e",1.0))
	lib.append(my_data("#Esteps","","",["text"],"e",1.0))
	lib.append(my_data("#dump_band_structure","","",["text"],"e",1.0))

	lib.append(my_data("#pulse_voc_dt","s","dt",["text"],"e",1.0))
	lib.append(my_data("#pulse_voc_dt_mul","au","dt multiplier",["text"],"e",1.0))
	lib.append(my_data("#pulse_voc_time_start","s","Start time",["text"],"e",1.0))
	lib.append(my_data("#pulse_voc_stop","s","Stop time",["text"],"e",1.0))
	lib.append(my_data("#pulse_voc_laser_pulse_width","s","Laser pulse width",["text"],"e",1.0))
	lib.append(my_data("#pulse_voc_Vexternal","V","V<sub>external</sub>",["text"],"e",1.0))
	lib.append(my_data("#pulse_voc_repeat","","",["text"],"e",1.0))
	lib.append(my_data("#pulse_voc_shift","","",["text"],"e",1.0))
	lib.append(my_data("#pulse_voc_use_big_mesh","1/0","Use a big mesh",["1","0"],"e",1.0))
	lib.append(my_data("#pulse_voc_bigmeshstart","s","Start of big mesh",["text"],"e",1.0))
	lib.append(my_data("#pulse_voc_bigmeshstop","s","Stop of big mesh",["text"],"e",1.0))
	lib.append(my_data("#pulse_voc_bigdt","s","dt for big mesh",["text"],"e",1.0))

	lib.append(my_data("#server_cpus","","",["text"],"e",1.0))
	lib.append(my_data("#server_stall_time","","",["text"],"e",1.0))
	lib.append(my_data("#server_exit_on_dos_error","","",["text"],"e",1.0))
	lib.append(my_data("#server_max_run_time","","",["text"],"e",1.0))
	lib.append(my_data("#server_auto_cpus","","",["text"],"e",1.0))
	lib.append(my_data("#server_min_cpus","","",["text"],"e",1.0))
	lib.append(my_data("#server_steel","","",["text"],"e",1.0))

	lib.append(my_data("#invert_applied_bias","","",["text"],"e",1.0))
	lib.append(my_data("#Rshort","","",["text"],"e",1.0))
	lib.append(my_data("#Dphoton","","",["text"],"e",1.0))
	lib.append(my_data("#interfaceleft","","",["text"],"e",1.0))
	lib.append(my_data("#interfaceright","","",["text"],"e",1.0))
	lib.append(my_data("#phibleft","","",["text"],"e",1.0))
	lib.append(my_data("#phibright","","",["text"],"e",1.0))
	lib.append(my_data("#vl_e","","",["text"],"e",1.0))
	lib.append(my_data("#vl_h","","",["text"],"e",1.0))
	lib.append(my_data("#vr_e","","",["text"],"e",1.0))
	lib.append(my_data("#vr_h","","",["text"],"e",1.0))
	lib.append(my_data("#jv_light_efficiency","","",["text"],"e",1.0))
	lib.append(my_data("#light_model","","",["text"],"e",1.0))
	lib.append(my_data("#NDfilter","","",["text"],"e",1.0))
	lib.append(my_data("#newton_dump","","",["text"],"e",1.0))
	lib.append(my_data("#plottime","","",["text"],"e",1.0))
	lib.append(my_data("#startstop","","",["text"],"e",1.0))
	lib.append(my_data("#dumpitdos","","",["text"],"e",1.0))
	lib.append(my_data("#plotfile","","",["text"],"e",1.0))
	lib.append(my_data("#dump_iodump","","",["text"],"e",1.0))
	lib.append(my_data("#dump_movie","","",["text"],"e",1.0))
	lib.append(my_data("#dump_optics","1/0","Dump optical information",["1","0"],"e",1.0))
	lib.append(my_data("#dump_optics_verbose","","",["text"],"e",1.0))
	lib.append(my_data("#dump_energy_slice_switch","1/0","Dump energy slices",["1","0"],"e",1.0))
	lib.append(my_data("#dump_energy_slice_pos","mesh position","Position of energy\nslice to dump",["text"],"e",1.0))
	lib.append(my_data("#dump_print_newtonerror","1/0","Print newton error",["1","0"],"e",1.0))
	lib.append(my_data("#dump_print_converge","","",["text"],"e",1.0))
	lib.append(my_data("#dump_print_pos_error","","",["text"],"e",1.0))
	lib.append(my_data("#dump_pl","","",["text"],"e",1.0))
	lib.append(my_data("#celiv_dt","","",["text"],"e",1.0))
	lib.append(my_data("#celiv_time_j0","","",["text"],"e",1.0))
	lib.append(my_data("#celiv_time_j1","","",["text"],"e",1.0))
	lib.append(my_data("#Rshort","","",["text"],"e",1.0))
	lib.append(my_data("#celiv_laser_on","","",["text"],"e",1.0))
	lib.append(my_data("#celiv_laser_width","","",["text"],"e",1.0))
	lib.append(my_data("#celiv_enable_time_mesh","","",["text"],"e",1.0))
	lib.append(my_data("#solve_at_Vbi","","",["text"],"e",1.0))
	lib.append(my_data("#maxelectricalitt_first","au","Max Electrical itterations (first step)",["text"],"e",1.0))

	lib.append(my_data("#electricalclamp_first","au","Electrical clamp (first step)",["text"],"e",1.0))
	lib.append(my_data("#newton_clever_exit","","",["text"],"e",1.0))
	lib.append(my_data("#newton_min_itt","","",["text"],"e",1.0))
	lib.append(my_data("#remesh","","",["text"],"e",1.0))
	lib.append(my_data("#newmeshsize","","",["text"],"e",1.0))
	lib.append(my_data("#epitaxy","","",["text"],"e",1.0))
	lib.append(my_data("#alignmesh","","",["text"],"e",1.0))
	lib.append(my_data("#stark_start_time","","",["text"],"e",1.0))

	lib.append(my_data("#jv_pmax_n","m<sup>-3</sup>","Average carrier density at P<sub>max</sub>",["text"],"e",1.0))
	lib.append(my_data("#jv_pmax_tau","m<sup>-1</sup>","Recombination time constant",["text"],"e",1.0))

	lib.append(my_data("#voc_nt","m<sup>-3</sup>","Trapped electrons at Voc",["text"],"e",1.0))
	lib.append(my_data("#voc_pt","m<sup>-3</sup>","Trapped holes at Voc",["text"],"e",1.0))
	lib.append(my_data("#voc_nf","m<sup>-3</sup>","Free electrons at Voc",["text"],"e",1.0))
	lib.append(my_data("#voc_pf","m<sup>-3</sup>","Free holes at Voc",["text"],"e",1.0))
	lib.append(my_data("#voc_np_tot","m<sup>-3</sup>","Total carriers (n+p)/2 at Voc",["text"],"e",1.0))
	lib.append(my_data("#voc_tau","s</sup>","Recombination time constant at Voc",["text"],"e",1.0))
	lib.append(my_data("#voc_R","m<sup>-3</sup>s<sup>-1</sup>","Recombination rate at Voc",["text"],"e",1.0))
	lib.append(my_data("#voc_J","A m<sup>-2</sup>","Current density at Voc",["text"],"e",1.0))
	lib.append(my_data("#voc_J_to_Jr","au","Ratio of conduction current to recombination current",["text"],"e",1.0))

	lib.append(my_data("#voc_i","au","Current",["text"],"e",1.0))
	lib.append(my_data("#kl_in_newton","1/0","Kirchhoff Current Law\nin Newton solver",["1","0"],"e",1.0))

	lib.append(my_data("#tpc_time_start","s","Start time",["text"],"e",1.0))
	lib.append(my_data("#tpc_stop","s","Stop time",["text"],"e",1.0))
	lib.append(my_data("#tpc_laser_pulse_width","s","Laser pulse width",["text"],"e",1.0))
	lib.append(my_data("#tpc_dtstart","s","dt",["text"],"e",1.0))
	lib.append(my_data("#tpc_dtmull","au","dt multiplier",["text"],"e",1.0))
	lib.append(my_data("#tpc_laser_eff","au","Laser power",["text"],"e",1.0))
	lib.append(my_data("#tpc_short","s","Sense resistor",["text"],"e",1.0))
	lib.append(my_data("#tpc_tsteps","Number of iterations","au",["text"],"e",1.0))
	lib.append(my_data("#tpc_pulsestart","au","Steps before laser",["text"],"e",1.0))
	lib.append(my_data("#tpc_pulselen","s","Number of laser on steps",["text"],"e",1.0))
	lib.append(my_data("#tpc_reprate","au","Repeat",["text"],"e",1.0))
	lib.append(my_data("#tpc_timeshift","s","Time shift",["text"],"e",1.0))
	lib.append(my_data("#tpc_externalv","Volts","External voltage",["text"],"e",1.0))
	lib.append(my_data("#tpc_simall","1/0","Include RC effects",["1","0"],"e",1.0))
	lib.append(my_data("#tpc_L","Henry","Inductance",["text"],"e",1.0))

#electricalclamp_first
	def find(self,token):
		for i in range(0, len(self.lib)):
			if self.lib[i].token==token.strip():
				if self.lib[i].units=="" and self.lib[i].info=="":
					return False
				else:
					return self.lib[i]

		#sys.stdout.write("Add -> lib.append(my_data(\""+token+"\",\"\",\"\",[\"text\"]))\n")
		return False
