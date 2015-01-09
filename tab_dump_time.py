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
from scan_item import scan_item
from inp import inp_get_token_value
from inp import inp_update_token_value

class tab_dump_time(gtk.VBox):

	lines=[]
	edit_list=[]
	file_name=""
	line_number=[]
	name=""
	visible=1
	def callback_edit(self, widget):
		mylist=[]
		text=self.textbuffer.get_text(self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter(),False)
		mylist=text.split()
		
		#line=self.line_number[data]
		#self.lines[line]=self.edit_list[data].get_text()
		#self.edit_list[data].set_text(self.lines[line])
		print "Sim dir",self.sim_dir+'dump_time.inp'
		a = open(self.sim_dir+'dump_time.inp', "w")
		a.write(str(len(mylist))+"\n")
		for i in range(0,len(mylist)):
			a.write(mylist[i]+"\n")
		a.close()

	def callback_toggled(self, widget):
		ans=0
		if self.check_button.get_active()==True:
			ans=1
		else:
			ans=0

		inp_update_token_value("dump.inp", "#dump_slices", str(ans))


	def wow(self,sim_dir):
		self.main_box=gtk.VBox()
		self.sim_dir=sim_dir
		self.edit_list=[]
		self.line_number=[]

		f = open(self.sim_dir+"dump_time.inp")
		self.lines = f.readlines()
		f.close()

		clean=[]
		del self.lines[0]

		for i in range (0,len(self.lines)):
			if self.lines[i]!="\n":
				clean.append(self.lines[i])


		mytext=''.join(clean)


		self.text = gtk.TextView()
		self.text.set_editable(True)
		self.textbuffer = self.text.get_buffer()

	        self.textbuffer.set_text(mytext)
		#self.text.set_text(mytext)

		#self.text.connect("insert-at-cursor", self.callback_edit)
		self.textbuffer.connect("changed", self.callback_edit)

		self.text.show()
		self.main_box.add(self.text)

		self.check_button=gtk.CheckButton("Dump the band structure as a the simulation proceeds")
		self.check_button.connect("toggled", self.callback_toggled)
		self.check_button.set_active(int(inp_get_token_value("dump.inp", "#dump_slices")))
		self.check_button.show()
		self.main_box.add(self.check_button)

		self.add(self.main_box)
		self.main_box.show()
#
		#n=0
		#pos=0
		#for i in range(0, len(self.lines)/2):

		#	show=False
		#	units="Units"
		#	out_text=self.lines[pos]
		#	if out_text == "#mueffe":
		#		units="m<sup>2</sup>V<sup>-1</sup>s<sup>-1</sup>"
		#		text_info="Electron mobility"
		#		show=True


