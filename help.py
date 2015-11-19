#    Organic Photovoltaic Device Model - a drift diffusion base/Shockley-Read-Hall
#    model for organic solar cells. 
#    Copyright (C) 2012 Roderick C. I. MacKenzie
#
#	roderick.mackenzie@nottingham.ac.uk
#	www.opvdm.com
#	Room B86 Coates, University Park, Nottingham, NG7 2RD, UK
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License v2.0, as published by
#    the Free Software Foundation.
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
import commands
import subprocess
from win_lin import running_on_linux
from cal_path import get_exe_command
import socket 
import time
import urlparse
import re
import os
from ver import ver_core
from ver import ver_mat
from ver import ver_gui
import gobject
from util import find_data_file
from global_objects import global_object_register


class help_data():
	def __init__(self,token,icon,text):
		self.token=token
		self.icon=icon
		self.text=text

class help_class(gtk.Window):
	def move_window(self):
		s=gtk.gdk.screen_get_default()
		w,h=self.get_size()

		x=s.get_width()-w
		y=0#s.get_height()-h

		self.move(x,y)

	def help_show(self):
		self.show_all()
		self.move_window()

	def init(self):
		self.last_icons=[]
		self.last_text=[]
		self.pos=-1
		self.help_lib=[]
		self.help_lib.append(help_data("#Dos","none","This tab contains the electrical model parameters, such as mobility, tail slope energy, and band gap."))
		self.help_lib.append(help_data("#device","none","This tab contains information about the device, such as width breadth, carrier density on the contacts, shunt and contact resistance."))
		self.help_lib.append(help_data("#jv","none","This tab controls the JV curve simulation."))
		self.help_lib.append(help_data("#jv_simple","none","The 'jv simple' model does not use opvdm's full device model instead it uses the diode equation to simulate a solar cell.  Sometimes for papers it is useful to do this."))
		self.help_lib.append(help_data("#dump","none","The dump tab controls what the simulation writes disk, generally writing to disk is a slow process so by default the model dumps relitavly little data."))
		self.help_lib.append(help_data("#celiv","none","The CELIV tab controls the the parameters for a CELIV simulation."))
		self.help_lib.append(help_data("#thermal","none","Use this tab to set the simulation temperature."))
		self.help_lib.append(help_data("#terminal","none","The simulations are run in this tab."))
		self.help_lib.append(help_data("#welcome","none","The welcome screen."))
		self.help_lib.append(help_data("#devcie_structure","none","the device structure tab"))


		self.move_window()
		global_object_register("help_set_help",self.help_set_help)
		global_object_register("help_window",self)
		self.vbox=gtk.VBox()
		self.vbox.show()
		self.box=gtk.HBox()
		self.add(self.vbox)
		self.image = gtk.Image()
		#self.image.set_from_file(find_data_file("gui/play.png"))
		self.image.show()

		self.label = gtk.Label()
		#self.text="<big>Hi!</big>\n I'm the on-line help system :) .\n Click on the play icon to start a simulation."
		#self.label.set_markup(self.text)
		self.label.show()

		self.box.pack_start(self.image, True, True, 0)
		self.box.pack_start(self.label, True, True, 0)



		toolbar = gtk.Toolbar()
		toolbar.set_style(gtk.TOOLBAR_ICONS)
		toolbar.set_size_request(100, 50)
		toolbar.show()

		pos=0
		image = gtk.Image()
   		image.set_from_file(find_data_file(os.path.join("gui","qe.png")))

		self.back = gtk.ToolButton(gtk.STOCK_GO_BACK)
		toolbar.insert(self.back, pos)
		self.back.show_all()
		self.back.set_sensitive(False)
		self.back.connect("clicked", self.callback_back)
		pos=pos+1

		self.forward = gtk.ToolButton(gtk.STOCK_GO_FORWARD)
		toolbar.insert(self.forward, pos)
		self.forward.set_sensitive(False)
		self.forward.show_all()
		self.forward.connect("clicked", self.callback_forward)
		pos=pos+1

		sep = gtk.SeparatorToolItem()
		sep.set_draw(False)
		sep.set_expand(True)
		sep.show()
		toolbar.insert(sep, pos)
		pos=pos+1

		close = gtk.ToolButton(gtk.STOCK_CLOSE)
		toolbar.insert(close, pos)
		close.connect("clicked", self.callback_close)
		close.show_all()
		pos=pos+1

		#self.tooltips.set_tip(self.qe_button, "Quantum efficiency")

		self.vbox.pack_start(toolbar, False, False, 0)
		self.vbox.pack_start(self.box, False, False, 0)

		self.box.show()


		self.set_border_width(10)
		self.set_title("Help")
		self.resize(300,100)
		self.set_decorated(False)
		self.set_border_width(0)

		self.help_set_help(find_data_file("gui/play.png"),"<big>Hi!</big>\n I'm the on-line help system :) .\n Click on the play icon to start a simulation.")

		self.show()


	def callback_close(self,widget):
		self.hide()

	def callback_forward(self,widget):
		self.pos=self.pos+1
		if self.pos>=len(self.last_text):
			self.pos=len(self.last_text)-1

		self.update()

	def callback_back(self,widget):
		self.pos=self.pos-1
		if self.pos<0:
			self.pos=0
		print self.pos,self.last_icons
		self.update()

	def update(self):
		self.image.set_from_file(self.last_icons[self.pos])
		self.label.set_markup(self.last_text[self.pos])
		print "rod",self.pos,len(self.last_text)-1

		self.forward.set_sensitive(True)
		self.back.set_sensitive(True)

		if self.pos==0:
			self.back.set_sensitive(False)

		if self.pos==len(self.last_text)-1:
			self.forward.set_sensitive(False)

	def help_set_help(self,file_name,input_text):
		self.pos=self.pos+1
		self.last_icons.append(file_name)
		self.last_text.append(input_text)
		self.update()
		self.move_window()



		
