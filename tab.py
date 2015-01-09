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
class scan_item(gtk.CheckButton):
	name=""
	token=""
	filename=""
	line=""

class tab_class(gtk.Table):
	
	lines=[]
	edit_list=[]
	file_name=""
	line_number=[]
	save_file_name=""
	def callback_edit(self, widget, data=None):
		line=self.line_number[data]
		self.lines[line]=self.edit_list[data].get_text()
		self.edit_list[data].set_text(self.lines[line])
		print "Written data to", self.save_file_name
		a = open(self.save_file_name, "w")
		for i in range(0,len(self.lines)):
			a.write(self.lines[i]+"\n")
		a.close()

	# This callback quits the program
	def delete_event(self, widget, event, data=None):
		gtk.main_quit()
		return False
	#def callback_checkbox(self, widget, event, data=None):
		#print data
		#print widget.get_active()
		#print widget.name
		#print widget.filename
		#print widget.token
		#print widget.line

	def wow(self,filename,fullname,check_list):
		self.file_name=filename
		self.edit_list=[]
		self.line_number=[]
		self.save_file_name=filename
		print "loading ",filename

		f = open(filename)
		self.lines = f.readlines()
		f.close()
		pos=0
		for i in range(0, len(self.lines)):
			self.lines[i]=self.lines[i].rstrip()

		n=0
		pos=0
		for i in range(0, len(self.lines)/2):

			show=False
			out_text=self.lines[pos]
			if out_text == "#mueffe":
				text_info="Electron mobility"
				show=True
			if out_text == "#mueffh":
				text_info="Hole mobility"
				show=True
			if out_text == "#Ntrape":
				text_info="Electron trap density"
				show=True
			if out_text == "#Ntraph":
				text_info="Hole trap density"
				show=True
			if out_text == "#Etrape":
				text_info="Electron tail slope"
				show=True
			if out_text == "#Etraph":
				text_info="Hole tail slope"
				show=True
			if out_text == "#epsilonr":
				text_info="Relative permittivity"
				show=True
			if out_text == "#srhsigman_e":
				text_info="Free electron->Trapped electron"
				show=True
			if out_text == "#srhsigmap_e":
				text_info="Trapped electron->Free hole"
				show=True
			if out_text == "#srhsigman_h":
				text_info="Trapped hole->Free electron"
				show=True
			if out_text == "#srhsigmap_h":
				text_info="Free hole->Trapped hole"
				show=True
			if out_text == "#Rshunt":
				text_info="Shunt resistance"
				show=True
			if out_text == "#Rcontact":
				text_info="Series resistance"
				show=True
			if out_text == "#lcharge":
				text_info="Charge on left contact"
				show=True
			if out_text == "#rcharge":
				text_info="Charge on right contact"
				show=True
			if out_text == "#Vstart":
				text_info="Start voltage"
				show=True
			if out_text == "#Vstop":
				text_info="Stop voltage"
				show=True
			if out_text == "#Vstep":
				text_info="Voltage step"
				show=True
			if out_text == "#Psun":
				text_info="Intensity of the sun"
				show=True
			if out_text == "#simplephotondensity":
				text_info="Photon density"
				show=True
			if out_text == "#simple_alpha":
				text_info="Absorption of material"
				show=True
			if out_text == "#plot":
				text_info="Plot bands etc.. "
				show=True
			if out_text == "#celiv_laser_eff":
				text_info="#celiv_laser_eff"
				show=True
			if out_text == "#doping":
				text_info="#doping"
				show=True
			if out_text == "#simmode":
				text_info="#simmode"
				show=True
			if out_text == "#Nc":
				text_info="Effective density of free electron states"
				show=True
			if out_text == "#Nv":
				text_info="Effective density of free hole states"
				show=True
			if out_text == "#maxelectricalitt":
				text_info="Max electical itterations"
				show=True
			if out_text == "#electricalclamp":
				text_info="Electrical clamp"
				show=True
			if out_text == "#posclamp":
				text_info="Poisson clamping"
				show=True
			if out_text == "#electricalerror":
				text_info="Minimum electrical error"
				show=True
			if out_text == "#free_to_free_recombination":
				text_info="Free to free recombination"
				show=True
			if out_text == "#sun":
				text_info="Sun's spectra"
				show=True
			if out_text == "#meshpoints":
				text_info="Mesh points (x)"
				show=True
			if out_text == "#lpoints":
				text_info="Mesh points (lambda)"
				show=True
			if out_text == "#lstart":
				text_info="Lambda start"
				show=True
			if out_text == "#lstop":
				text_info="Lambda stop"
				show=True
			if out_text == "#laserwavelength":
				text_info="Laser wavelength"
				show=True
			if out_text == "#spotx":
				text_info="#spotx"
				show=True
			if out_text == "#spoty":
				text_info="#spoty"
				show=True
			if out_text == "#pulseJ":
				text_info="#pulseJ"
				show=True
			if out_text == "#pulseL":
				text_info="#pulseL"
				show=True
			if out_text == "#gather":
				text_info="#gather"
				show=True
			if out_text == "#dlength":
				text_info="#dlength"
				show=True
			if out_text == "#electron_eff":
				text_info="#electron_eff"
				show=True
			if out_text == "#hole_eff":
				text_info="#hole_eff"
				show=True
			if out_text == "#function":
				text_info="#function"
				show=True
			if out_text == "#lr_pcontact":
				text_info="P contact on left or right"
				show=True
			if out_text == "#Vexternal":
				text_info="start voltage"
				show=True
			if out_text == "#Vmax":
				text_info="Max voltage"
				show=True
			if out_text == "#celiv_t0":
				text_info="#celiv_t0"
				show=True
			if out_text == "#celiv_t1":
				text_info="#celiv_t1"
				show=True
			if out_text == "#celiv_t2":
				text_info="#celiv_t2"
				show=True
			if out_text == "#Eg":
				text_info="Eg"
				show=True
			if out_text == "#start_stop_time":
				text_info="Time of pause"
				show=True
			if out_text == "#stopstart":
				text_info="Pause between iterations"
				show=True
			if out_text == "#invert_current":
				text_info="Invert output"
				show=True
			if out_text == "#lr_bias":
				text_info="Bias left or right"
				show=True
			if out_text == "#otherlayers":
				text_info="Other layers"
				show=True
			if out_text == "#dump_slices":
				text_info="Dump slices"
				show=True
			if out_text == "#tofstop":
				text_info="ToF stop time"
				show=True
			if out_text == "#toflaseroff":
				text_info="ToF laser off time"
				show=True
			if out_text == "#dt":
				text_info="ToF time step"
				show=True
			if out_text == "#tofdtmull":
				text_info="ToF dt multiplier"
				show=True
			if out_text == "#toflaserpower":
				text_info="ToF laser power"
				show=True
			if out_text == "#start_steps":
				text_info="ToF steps before start"
				show=True
			if out_text == "#tof_voltage":
				text_info="ToF voltage"
				show=True
			if out_text == "#tof_Rshort":
				text_info="Rshort"
				show=True


			pos=pos+1

			if show == True :

				label = gtk.Label(text_info)
				self.attach(label, 0, 1, n, n+1)
				label.show()

				self.line_number.append(pos)
				self.edit_list.append(gtk.Entry(max=0))
				self.edit_list[n].set_text(self.lines[pos]);
				self.attach(self.edit_list[n], 1, 2, n, n+1)
				self.edit_list[n].connect("changed", self.callback_edit, n)
				self.edit_list[n].show()
				#print "out -> %s %i",out_text,len(self.edit_list)


				check_list.append(scan_item(""))
				listpos=len(check_list)-1
				check_list[listpos].name=text_info
				check_list[listpos].filename=filename
				check_list[listpos].token=out_text
				check_list[listpos].line=pos
				
				self.attach(check_list[listpos], 2, 3, n, n+1)
			
				check_list[listpos].show()

				n=n+1

			pos=pos+1

