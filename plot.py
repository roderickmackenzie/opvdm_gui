import pygtk
pygtk.require('2.0')
import gtk
import sys
import os
import shutil
from token_lib import tokens
from numpy import *
from util import pango_to_gnuplot
from plot_info import plot_info
from util import zip_get_data_file

def load_graph(path):
	cmd = '/usr/bin/gnuplot -persist '+path
	print cmd
	os.system(cmd)

def check_info_file(search_string):
	files=["dos0.inp","dos1.inp","photokit_ri.dat","photokit_real.dat","photokit_imag.dat","jv_psun_voc.dat","jv_voc_nt.dat","jv_voc_pt.dat","jv_psun_nf_nt.dat","jv_psun_pf_pt.dat","jv_psun_np_tot.dat","sim_info.dat","light.inp"]
	if files.count(search_string)> 0:
		return True
	else:
		return False

def file_name_to_latex(in_string):
	out_string=in_string.replace("_","\\_")
	return out_string


class plot_data:

	
	pos=0
	def __init__(self):
		self.files=[]
#CELIV
		self.files.append(plot_info("subsection","CELIV","False","","",1e6,1.0,"",0,0,""))

		self.files.append(plot_info("celiv_i.dat","Time","us","Current","Amps",1e6,1.0,"none",0,0,"CELIV - Time - Current"))

#optical
		self.files.append(plot_info("subsection","Optical","True","","",1e6,1.0,"",0,0,""))
 		self.files.append(plot_info("alpha.inp","Wavelength","nm","Absorption","m^{-1}",1e9,1.0,"n.inp",0,0,"Absorption"))
 		self.files.append(plot_info("n.inp","Wavelength","nm","Refractive index","au",1e9,1.0,"alpha.inp",0,0,"Refractive index"))

#jv
		self.files.append(plot_info("subsection","Current Voltage","True","","",1e6,1.0,"",0,0,""))
		self.files.append(plot_info("ivexternal.dat","Applied Bias","Volts","Current","Amps",1.0,1.0,"none",0,0,"Current - Voltage"))
		self.files.append(plot_info("jvexternal.dat","Applied Bias","Volts","Current Density","Am^{-2}",1.0,1.0,"none",0,0,"Current Density - Voltage"))
		self.files.append(plot_info("charge.dat","Applied Bias","Volts","Charge density"," m^{-3}",1.0,1.0,"none",0,0,"Applied Bias - Charge density"))

		self.files.append(plot_info("jv_psun_voc.dat","Light intensity","Suns","Open circuit voltage","(Volts)",1e-3,1.0,"none",0,0,"Light intensity - Open circuit voltage"))

		self.files.append(plot_info("jv_voc_nt.dat","Open circuit voltage","V","Trapped electron density","m^{-3}",1.0,1.0,"none",0,0,"Open circuit voltage - Trapped Electrons"))

		self.files.append(plot_info("jv_voc_pt.dat","Open circuit voltage","V","Trapped hole density","m^{-3}",1.0,1.0,"none",0,0,"Open circuit voltage - Trapped Holes"))

		self.files.append(plot_info("jv_psun_nf_nt.dat","Suns","au","nf/nt","au",1.0,1.0,"none",0,0,"Open circuit voltage - Trapped Electrons"))

		self.files.append(plot_info("jv_psun_pf_pt.dat","Suns","au","pf/pt","au",1.0,1.0,"none",0,0,"Open circuit voltage - Trapped Holes"))

		self.files.append(plot_info("jv_psun_np_tot.dat","Suns","au","total charge","au",1.0,1.0,"none",0,0,"Sun - Total charge"))
#tof
		self.files.append(plot_info("subsection","Time of Flight","True","","",1e6,1.0,"",0,0,""))
		self.files.append(plot_info("tof_i.dat","Time","s","Current"," Amps",1.0,1.0,"none",1,1,"ToF - Time - Current"))
		self.files.append(plot_info("tof_dos.dat","Energy","eV","Magnitude","au",1.0,1.0,"none",0,1,"ToF extracted DoS i*t"))
		self.files.append(plot_info("pulse_i_pos.dat","Time","us","Current","Amps",1e6,1.0,"none",0,0,"ToF - Time - |Current|"))
		self.files.append(plot_info("pulse_i.dat","Time","us","Current","Amps",1e6,1.0,"none",0,0,"Time - Current"))
		self.files.append(plot_info("pulse_i_norm.dat","Time","us","Current","au",1e6,1.0,"none",0,0,"Time - |Current|"))
		self.files.append(plot_info("pulse_v.dat","Time","us","Voltage","Volts",1e6,1.0,"none",0,0,"Time - voltage"))
		self.files.append(plot_info("pulse_mue.dat","Time","us","Electron Mobility","m^{2}V^{-1}s^{-1}",1e6,1.0,"none",0,0,"Time - electon mobility"))
		self.files.append(plot_info("pulse_muh.dat","Time","us","Hole Mobility","m^{2}V^{-1}s^{-1}",1e6,1.0,"none",0,0,"Time - hole mobility"))

#photokit
		self.files.append(plot_info("subsection","Photokit","False","","",1e6,1.0,"",0,0,""))
		self.files.append(plot_info("photokit_i.dat","Time","us","Current","Amps",1e6,1.0,"photokit_psun.dat",0,0,"Time - Current"))
		self.files.append(plot_info("photokit_i_norm.dat","Time","us","Current","au",1e6,1.0,"none",0,0,"Time - |Current|"))
		self.files.append(plot_info("photokit_v.dat","Time","us","Voltage","Volts",1e6,1.0,"none",0,0,"Time - Voltage"))
		self.files.append(plot_info("photokit_mue.dat","Time","us","Electron Mobility","m^{2}V^{-1}s^{-1}",1e6,1.0,"none",0,0,"Time - Electron Mobility"))
		self.files.append(plot_info("photokit_muh.dat","Time","us","Hole Mobility","m^{2}V^{-1}s^{-1}",1e6,1.0,"none",0,0,"Time - Hole Mobility"))
		self.files.append(plot_info("photokit_psun.dat","Time","us","Suns","Suns",1e6,1e-3,"none",0,0,"Time - Sun Intensity"))
		self.files.append(plot_info("photokit_ri.dat","Re","Amps","Im","Amps",1.0,1.0,"none",0,0,"Re(I) - Im(I)"))
		self.files.append(plot_info("photokit_real.dat","Hz","Hz","Re","Amps",1.0,1.0,"none",1,0,"Frequency - Re(I)"))
		self.files.append(plot_info("photokit_imag.dat","Hz","Hz","Im","Amps",1.0,1.0,"none",1,0,"Frequency - Im(I)"))
		self.files.append(plot_info("photokit_i_norm_x.dat","Time","s","Current","Amps",1.0,1.0,"none",0,0,"Wave scaled"))
		self.files.append(plot_info("pulse_voc_v.dat","Time","us","Voltage","Volts",1e6,1.0,"none",0,0,"Time - voltage"))

#pulse voc
		self.files.append(plot_info("subsection","Pulse Voc","False","","",1e6,1.0,"",0,0,""))
		self.files.append(plot_info("pulse_voc_v_norm.dat","Time","us","Voltage","Volts",1e6,1.0,"none",0,0,"Time - voltage (normalized)"))

#slices
		self.files.append(plot_info("subsection","Slice","","True","",1e6,1.0,"",0,0,""))
		self.files.append(plot_info("mu_n.dat","Position","nm","Electron Mobility","m^{2}V^{-1}s^{-1}",1e9,1.0,"none",0,0,"Position - Electron Mobility"))
		self.files.append(plot_info("mu_p.dat","Position","nm","Hole Mobility","m^{2}V^{-1}s^{-1}",1e9,1.0,"none",0,0,"Position - Hole Mobility"))
		self.files.append(plot_info("mu_n_ft.dat","Position","nm","Average electron mobility","m^{2}V^{-1}s^{-1}",1e9,1.0,"none",0,0,"Position - Electron Mobility"))
		self.files.append(plot_info("mu_p_ft.dat","Position","nm","Average hole mobility","m^{2}V^{-1}s^{-1}",1e9,1.0,"none",0,0,"Position - Hole Mobility"))

		self.files.append(plot_info("phi.dat","Position","nm","Potential","V",1e9,1.0,"none",0,0,"Potential - position"))
		self.files.append(plot_info("Fn.dat","Position","nm","Energy","eV",1e9,1.0,"none",0,0,"Electron Fermi level - position"))
		self.files.append(plot_info("Fp.dat","Position","nm","Energy","eV",1e9,1.0,"none",0,0,"Hole Fermi level - position"))
		self.files.append(plot_info("nt_map.dat","Position","nm","Energy","eV",1e9,1.0,"none",0,0,"Electron density - Energy - position"))
		self.files.append(plot_info("pt_map.dat","Position","nm","Energy","eV",1e9,1.0,"none",0,0,"Electron density - Energy - position"))
		self.files.append(plot_info("nf.dat","Position","nm","Free electron density","m^{-3}",1e9,1.0,"none",0,1,"Electron density - position"))
		self.files.append(plot_info("nt.dat","Position","nm","Electron density","m^{-3}",1e9,1.0,"none",0,1,"Electron density - position"))
		self.files.append(plot_info("pf.dat","Position","nm","Free hole density","m^{-3}",1e9,1.0,"none",0,1,"Hole density - position"))
		self.files.append(plot_info("pt.dat","Position","nm","Hole density","m^{-3}",1e9,1.0,"none",0,1,"Hole density - position"))

		self.files.append(plot_info("n.dat","Position","nm","Electron density","m^{-3}",1e9,1.0,"none",0,1,"Electron density - position"))
		self.files.append(plot_info("p.dat","Position","nm","Hole density","m^{-3}",1e9,1.0,"none",0,1,"Hole density - position"))

		self.files.append(plot_info("Jn.dat","Position","nm","Electron Flux","m^{-2}s^{-1}",1e9,1.0,"none",0,0,"Electron Flux - position"))
		self.files.append(plot_info("Jp.dat","Position","nm","Hole Flux","m^{-2}s^{-1}",1e9,1.0,"none",0,0,"Hole Flux - position"))
		self.files.append(plot_info("Rn.dat","Position","nm","Electron Recombination rate","m^{-3}s^{-1}",1e9,1.0,"none",0,0,"Electron recombination rate - position"))
		self.files.append(plot_info("Rp.dat","Position","nm","Electron Recombination rate","m^{-3}s^{-1}",1e9,1.0,"none",0,0,"Electron recombination rate - position"))

		self.files.append(plot_info("dcharge.dat","Position","nm","Total charge","m^{-3}",1e9,1.0,"none",0,0,"holes-electrons - position"))
		self.files.append(plot_info("nt_to_pf.dat","Position","nm","Trapped electrons to free holes","m^{-3}s^{-1}",1e9,1.0,"none",0,0,"Trapped electrons to free holes - position"))
		self.files.append(plot_info("pt_to_nf.dat","Position","nm","Trapped holes to free electrons","m^{-3}s^{-1}",1e9,1.0,"none",0,0,"Trapped holes to free electrons - position"))
		self.files.append(plot_info("prelax.dat","Position","nm","prelax","m^{-3}s^{-1}",1e9,1.0,"none",0,0,"prelax - position"))
		self.files.append(plot_info("nrelax.dat","Position","nm","nrelax","m^{-3}s^{-1}",1e9,1.0,"none",0,0,"nrelax - position"))
		
#dynamic
		self.files.append(plot_info("subsection","Dynamic output files","True","","",1e6,1.0,"",0,0,""))
		self.files.append(plot_info("subsubsection","Free and trapped carrier populations","","","",1e6,1.0,"",0,0,""))
		self.files.append(plot_info("dynamic_nt.dat","Time","us","Electron density","m^{-3}",1e6,1.0,"dynamic_pt.dat",0,0,"Time - Trapped electron density"))
		self.files.append(plot_info("dynamic_pt.dat","Time","us","Hole density","m^{-3}",1e6,1.0,"dynamic_nt.dat",0,0,"Time - Trapped hole density"))
		self.files.append(plot_info("dynamic_nf.dat","Time","us","Electron density","m^{-3}",1e6,1.0,"none",0,0,"Time - Free electron density"))
		self.files.append(plot_info("dynamic_pf.dat","Time","us","Hole density","m^{-3}",1e6,1.0,"none",0,0,"Time - Free hole density"))
		self.files.append(plot_info("dynamic_np.dat","Time","us","Charge density","m^{-3}",1e6,1.0,"none",0,0,"Time - Charge in device (- equlibrium charge)"))
		self.files.append(plot_info("dynamic_np_norm.dat","Time","us","Charge due to photogeneration","au",1e6,1.0,"none",0,0,"Time - Charge in device"))

		self.files.append(plot_info("dynamic_n.dat","Time","us","Electron density","m^{-3}",1e6,1.0,"none",0,0,"Time - Average electron density (- equlibrium charge)"))

		self.files.append(plot_info("dynamic_p.dat","Time","us","Hole density","m^{-3}",1e6,1.0,"none",0,0,"Time - Average holes density (- equlibrium charge)"))

		self.files.append(plot_info("dynamic_filledn.dat","Time","us","Filled electron traps","Percent",1e6,1.0,"none",0,0,"Time - Filled electron traps"))
		self.files.append(plot_info("dynamic_filledp.dat","Time","us","Filled hole traps","Percent",1e6,1.0,"none",0,0,"Time - Filled hole traps"))

		self.files.append(plot_info("dynamic_pf_to_nt.dat","Time","us","Free hole to trapped electrons","au",1e6,1.0,"none",0,0,"Time - Free hole to trapped electron rate"))

		self.files.append(plot_info("dynamic_nf_to_pt.dat","Time","us","Free electron to trapped hole","au",1e6,1.0,"none",0,0,"Time - Free electron to trapped hole recombination rate"))


		self.files.append(plot_info("subsubsection","Current flux","","","",1e6,1.0,"",0,0,""))
		self.files.append(plot_info("dynamic_jn_mid.dat","Time","s","Electron current flux (mid device)","A m^{-2}",1.0,1.0,"none",1.0,1.0,"Electron current flux - Time"))

		self.files.append(plot_info("dynamic_jp_mid.dat","Time","s","Hole current flux (mid device)","A m^{-2}",1.0,1.0,"none",1.0,1.0,"Hole current flux - Time"))

		self.files.append(plot_info("dynamic_j.dat","Time","s","Current flux","A m^{-2}",1.0,1.0,"none",1.0,1.0,"Current flux - Time"))

		self.files.append(plot_info("dynamic_j.dat","Time","s","Current","A",1.0,1.0,"none",1.0,1.0,"Current - Time"))

		self.files.append(plot_info("dynamic_djp.dat","Time","s","dynamic djp mid over dt","A m^{-2}s^{-1}",1.0,1.0,"none",1.0,1.0,"Current - Time"))

		self.files.append(plot_info("dynamic_djn.dat","Time","s","dynamic djn mid over dt","A m^{-2}s^{-1}",1.0,1.0,"none",1.0,1.0,"Current - Time"))



		self.files.append(plot_info("subsubsection","Recombination and generation","","","",1e6,1.0,"",0,0,""))
		self.files.append(plot_info("dynamic_Rn.dat","Time","us","Rn","au",1e6,1.0,"none",0,0,"Time - Rn"))

		self.files.append(plot_info("dynamic_Rp.dat","Time","us","Rp","au",1e6,1.0,"none",0,0,"Time - Rp"))

		self.files.append(plot_info("dynamic_gex.dat","Time","ns","Carrier Generation rate)","m^{-3}s^{-1}",1e9,1.0,"none",0.0,0.0,"time - Carrier generation rate"))

#equlib
		self.files.append(plot_info("subsection","Equilibrium","True","","",1e6,1.0,"",0,0,""))
		self.files.append(plot_info("equ_Ec.dat","Position","nm","Energy","eV",1e9,1.0,"none",0,0,"LUMO - position (equilibrium)"))
		self.files.append(plot_info("equ_Ev.dat","Position","nm","Energy","eV",1e9,1.0,"none",0,0,"HOMO - position (equilibrium)"))
		self.files.append(plot_info("equ_Fn.dat","Position","nm","Energy","eV",1e9,1.0,"none",0,0,"Electron Fermi level - position (equilibrium)"))
		self.files.append(plot_info("equ_Fp.dat","Position","nm","Energy","eV",1e9,1.0,"none",0,0,"Hole Fermi level - position (equilibrium)"))


#sun_voc
		self.files.append(plot_info("subsection","Sun Voc","False","","",1e6,1.0,"",0,0,""))
		self.files.append(plot_info("sun_voc.dat","Intensity","Suns","Voc","Volts",1.0,1.0,"none",1,0,"Sun - Voc"))


#pl

		self.files.append(plot_info("subsection","PL","False","","",1e6,1.0,"",0,0,""))
		self.files.append(plot_info("dynamic_pl.dat","Time","ns","PL intensity","m^{-3}",1e9,1.0,"none",1.0,1.0,"Time - PL intensity"))
		self.files.append(plot_info("dynamic_pl_norm.dat","Time","ns","PL intensity","m^{-3}",1e9,1.0,"none",1.0,1.0,"Time - PL intensity"))
		self.files.append(plot_info("Efield.dat","Position","nm","E-field","V s^{-1}",1e9,1.0,"none",0,0,"Electric field - position"))

		self.files.append(plot_info("energy_slice_nt.dat","Energy","eV","Carrier density","m^{-3} eV^{-1}",1.0,1.0,"none",0,0,"Carrier density - energy"))
		self.files.append(plot_info("energy_slice_pt.dat","Energy","eV","Carrier density","m^{-3} eV^{-1}",1.0,1.0,"none",0,0,"Carrier density - energy"))
		self.local=plot_info("","","","","",1.0,1.0,"none",0,0,"")

	def dump_file(self):
		enable=True
		for i in range(0, len(self.files)):
			if self.files[i].file_name=="subsection":
				if self.files[i].x_units=="True":
					print "\subsection{"+self.files[i].x_label+"}"
					enable=True
				else:
					enable=False
			elif self.files[i].file_name=="subsubsection":
				if enable==True:
					print "\subsubsection{"+self.files[i].x_label+"}"
			else:
				if enable==True:
					print "\\textbf{"+file_name_to_latex(self.files[i].file_name)+"}: "+self.files[i].title+"\\newline"
					print "x-axis: "+self.files[i].x_label+" ($"+self.files[i].x_units+"$)\\newline"
					print "y-axis: "+self.files[i].y_label+" ($"+self.files[i].y_units+"$)\\newline"
					print "\\newline"

		#raw_input("Press Enter to continue...")

	def find_file(self,file_name,plot_token):
		found,lines=zip_get_data_file(file_name)

		for i in range(0, len(lines)):
			lines[i]=lines[i].rstrip()

		if lines[0]=="#opvdm":
			for i in range(0, len(lines)):
				if (lines[i][0]!="#"):
					break
				else:
					command=lines[i].split(" ",1)
					if len(command)<2:
						command.append("")
					if (command[0]=="#x_mul"):
						self.local.x_mul=float(command[1])
					if (command[0]=="#y_mul"):
						self.local.y_mul=float(command[1])
					if (command[0]=="#x_label"):
						self.local.x_label=command[1]
					if (command[0]=="#y_label"):
						self.local.y_label=command[1]
					if (command[0]=="#x_units"):
						self.local.x_units=command[1]
					if (command[0]=="#y_units"):
						self.local.y_units=command[1]
					if (command[0]=="#logscale_x"):
						self.local.logscale_x=bool(int(command[1]))
					if (command[0]=="#logscale_y"):
						self.local.logscale_y=bool(int(command[1]))
					if (command[0]=="#type"):
						self.local.type=command[1]


			self.read=self.local
			#print "Data read from file"
			return True

		name=os.path.basename(file_name)

		for i in range(0, len(self.files)):
			#print "'",self.files[i].file_name,"'",name.strip(),"'"
			if self.files[i].file_name==name.strip():
				self.read=self.files[i]
				return True
		print "Can not find",name,"in xy data lib"

		#check to see if I have been provided with a token

		if plot_token!=None:
			my_token_lib=tokens()
			result0=my_token_lib.find(plot_token.tag0)
			result1=my_token_lib.find(plot_token.tag1)
			print "one=",plot_token.tag0,result0
			print "two=",plot_token.tag1,result1
			if result0!=False:
				ret=plot_info("","","","","",1.0,1.0,"none",0,0,"")
				ret.x_label=result0.info
				ret.x_units=result0.units
				ret.y_label=result1.info
				ret.y_units=result1.units
				ret.title=result0.info+" "+result1.info

				print "Found tokens",plot_token.tag0,plot_token.tag1
				self.read=ret
				return True
			else:
				print "Tokens not found",plot_token.tag0,plot_token.tag1

		return False
	
